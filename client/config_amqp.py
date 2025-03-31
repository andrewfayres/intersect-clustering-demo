"""
Configuration for the INTERSECT client with RabbitMQ clustering support using AMQP.
"""
from intersect_sdk.config.client import IntersectClientConfig
from intersect_sdk.config.shared import (
    BrokerConfig,
    ControlPlaneConfig,
    DataStoreConfig,
    DataStoreConfigMap,
)

# Use RabbitMQ cluster configuration with hostnames only
# For AMQP we use port 5672 
broker_configs = [
    {"host": "rabbitmq1", "port": 5672},
    {"host": "rabbitmq2", "port": 5672},
]

brokers = [
    ControlPlaneConfig(
        protocol="amqp0.9.1",  # Changed to AMQP protocol
        username="intersect_username",
        password="intersect_password",
        brokers=[BrokerConfig(**broker) for broker in broker_configs],
    )
]

# Empty data stores config (no MinIO for now to simplify testing)
data_stores = DataStoreConfigMap()

# We'll set the initial_message_event_config later in the client code
from intersect_sdk import IntersectClientCallback

# Create the client config
CLIENT_CONFIG = IntersectClientConfig(
    brokers=brokers,
    data_stores=data_stores,
    initial_message_event_config=IntersectClientCallback(messages_to_send=[], subscribe_to_events=["intersect.resilience.clustering-demo.-.counting-client.response"]),
    organization="intersect",
    facility="resilience",
    system="clustering-demo",
)