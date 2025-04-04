"""
Configuration for the INTERSECT client with RabbitMQ clustering support.
"""

from intersect_sdk.config.client import IntersectClientConfig
from intersect_sdk.config.shared import (
    BrokerConfig,
    ControlPlaneConfig,
    DataStoreConfig,
    DataStoreConfigMap,
)

# Use RabbitMQ cluster configuration with Docker service names
broker_configs = [
    {"host": "rabbitmq1", "port": 1883},
    {"host": "rabbitmq2", "port": 1883},
]

brokers = [
    ControlPlaneConfig(
        protocol="mqtt3.1.1",
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
    initial_message_event_config=IntersectClientCallback(messages_to_send=[], subscribe_to_events=[]),
    organization="intersect",
    facility="resilience",
    system="clustering-demo",
)