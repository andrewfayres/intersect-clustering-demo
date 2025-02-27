"""
Configuration for the INTERSECT client with RabbitMQ clustering support.
"""

from intersect_sdk.config.client import IntersectClientConfig
from intersect_sdk.config.shared import (
    ControlPlaneConfig,
    DataStoreConfig,
    DataStoreConfigMap,
)

# Use RabbitMQ cluster configuration
brokers = [
    ControlPlaneConfig(
        protocol="mqtt3.1.1",
        # Configure the cluster with both nodes
        hosts=["localhost", "localhost"],  # Both nodes on localhost (in production, this would be different hostnames)
        ports=[1883, 1884],  # MQTT ports for rabbitmq1 and rabbitmq2
        username="intersect_username",
        password="intersect_password",
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
    initial_message_event_config=IntersectClientCallback(messages_to_send=[], subscribe_to_events=[]),
    organization="intersect",
    facility="resilience",
    system="clustering-demo",
)