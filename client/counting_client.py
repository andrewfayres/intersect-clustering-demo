import logging
import time

from intersect_sdk import (
    INTERSECT_JSON_VALUE,
    IntersectClient,
    IntersectClientCallback,
    IntersectDirectMessageParams,
    default_intersect_lifecycle_loop,
)

# Import our clustering configuration
from config import CLIENT_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SampleOrchestrator:
    """This class contains the callback function.

    It uses a class because we want to modify our own state from the callback function.

    State is managed through a message stack. We initialize a request-reply-request-reply... chain with the Service,
    and the chain ends once we've popped all messages from our message stack.
    """

    def __init__(self) -> None:
        """Basic constructor for the orchestrator class, call before creating the IntersectClient."""
        # Create our messages
        self.get_count_message = IntersectDirectMessageParams(
            destination='intersect.resilience.clustering-demo.-.counting-service',
            operation='CountingExample.get_count',
            payload=None,
        )
        
        # Message to start the counter 
        self.start_count_message = IntersectDirectMessageParams(
            destination='intersect.resilience.clustering-demo.-.counting-service',
            operation='CountingExample.start_count',
            payload=None,
        )
        
        # Flag to track if we need to start the counter initially
        self.counter_started = False
        
        # Track the last count we received to detect skips
        self.last_count = -1
        
        # Track when we started to display elapsed time in client
        self.start_time = None
        
        # Track when we last received a message
        self.last_message_time = 0
        
    def check_for_reconnection_needed(self, client):
        """Check if we need to restart the message chain (called periodically by the lifecycle loop)."""
        current_time = time.time()
        
        # Check if it's been too long since we received a message
        if self.last_message_time > 0 and current_time - self.last_message_time > 5:
            print(f"\nNo messages for {current_time - self.last_message_time:.1f} seconds, restarting chain...")
            self.last_message_time = current_time  # Reset to avoid multiple restarts
            
            # Restart the client to force reconnection
            try:
                client.shutdown()
                time.sleep(1.0)
                client.startup()
                
                # Force restart of the message chain
                if self.counter_started:
                    print("Restarting count chain...")
                    return IntersectClientCallback(messages_to_send=[self.get_count_message])
                else:
                    print("Starting counter...")
                    return IntersectClientCallback(messages_to_send=[self.start_count_message])
            except Exception as e:
                print(f"Error during reconnection: {e}")
        
        return None
        
    def client_callback(
        self, source: str, operation: str, has_error: bool, payload: INTERSECT_JSON_VALUE
    ) -> IntersectClientCallback:
        """Simplified callback that just polls the counter value periodically.
        
        We'll start the counter on the first call if needed, then just keep getting the count.
        """
        try:
            # Update last message time whenever we receive any message
            self.last_message_time = time.time()
            
            # If this is our first response and we need to start the counter
            if not self.counter_started:
                if operation == "CountingExample.start_count":
                    self.counter_started = True
                    self.start_time = time.time()
                    
                    # Check the response payload
                    if isinstance(payload, dict) and 'success' in payload:
                        if payload['success'] is False:
                            print("Counter was already running. That's fine!")
                        else:
                            print("Successfully started the counter.")
                    
                    # Send the first get_count message immediately
                    print("Starting to poll the counter...")
                    return IntersectClientCallback(messages_to_send=[self.get_count_message])
            
            # For all subsequent responses, we just get the current count
            elif operation == "CountingExample.get_count":
                # Extract the count value
                count_value = payload
                client_elapsed = int(time.time() - self.start_time)
                
                # Check for skips (more than 1 second difference)
                if self.last_count >= 0 and count_value > self.last_count + 1:
                    skipped = count_value - self.last_count - 1
                    print(f"\rSkipped {skipped} count(s)! Server: {count_value}, Client: {client_elapsed}    ")
                
                self.last_count = count_value
                
                # Clear the line and print the updated value (keeps output clean)
                print(f"\rCurrent count: {count_value} (client elapsed: {client_elapsed}s)    ", end="", flush=True)
                
                # Send next request immediately for more accurate results
                return IntersectClientCallback(messages_to_send=[self.get_count_message])
                
            # This handles unexpected operations
            else:
                print(f"\nReceived unexpected response: {operation}")
                # Always continue the chain by asking for the count
                return IntersectClientCallback(messages_to_send=[self.get_count_message])
                
        except Exception as e:
            # Safer error handling
            print(f"\nError in callback: {e}")
            # Always continue the chain even on errors
            return IntersectClientCallback(messages_to_send=[self.get_count_message])


if __name__ == '__main__':
    # Initial message to start the counter
    initial_messages = [
        IntersectDirectMessageParams(
            destination='intersect.resilience.clustering-demo.-.counting-service',
            operation='CountingExample.start_count',
            payload=None,
        )
    ]
    
    # Make sure initial messages are retried on reconnection
    CLIENT_CONFIG.resend_initial_messages_on_secondary_startup = True
    
    # Configure the client to send the start_count message initially
    CLIENT_CONFIG.initial_message_event_config = IntersectClientCallback(messages_to_send=initial_messages)
    
    # Create the orchestrator and client
    orchestrator = SampleOrchestrator()
    client = IntersectClient(
        config=CLIENT_CONFIG,
        user_callback=orchestrator.client_callback,
    )
    
    print("\n-------------------------------------------------")
    print("| INTERSECT RabbitMQ Clustering Resilience Demo |")
    print("-------------------------------------------------\n")
    print("This client will continuously poll the counter.")
    print("The counter increments once per second based on elapsed time.")
    print("\nTo test automatic failover:")
    print("  1. Let it run for a while to establish the connection")
    print("  2. From another terminal run: docker-compose stop rabbitmq1")
    print("  3. The client should automatically detect the disconnect")
    print("  4. It will switch to rabbitmq2 and continue polling")
    print("  5. You should see minimal disruption in the counter values")
    print("\nPress Ctrl+C to exit when done\n")
    
    try:
        # Define a waiting callback that monitors message flow and restarts the chain if needed
        def waiting_callback(client_instance):
            # Check if we need to restart the message chain
            result = orchestrator.check_for_reconnection_needed(client_instance)
            if result:
                # If we need to restart, handle the callback result
                # In this case, add the message to the queue
                message = result.messages_to_send[0]
                try:
                    # Try to send a message directly to restart the chain
                    client_instance._send_userspace_message(message)
                except:
                    pass
                    
        # Start the client with a short delay between lifecycle checks and our waiting callback
        default_intersect_lifecycle_loop(
            client,
            delay=1.0,  # Check status frequently for faster recovery
            waiting_callback=waiting_callback
        )
    except KeyboardInterrupt:
        print("\n\nExiting demo. Thanks for using INTERSECT with RabbitMQ clustering!")