"""
Configuration for the INTERSECT service with RabbitMQ clustering support.
"""

from intersect_sdk.config.service import IntersectServiceConfig
from intersect_sdk.config.shared import (
    BrokerConfig,
    ControlPlaneConfig,
    DataStoreConfig,
    DataStoreConfigMap,
    HierarchyConfig,
)

# Define hierarchy for discovery
hierarchy = HierarchyConfig(
    service="counting-service",
    system="clustering-demo",
    facility="resilience",
    organization="intersect",
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

# Create the service config
SERVICE_CONFIG = IntersectServiceConfig(
    hierarchy=hierarchy,
    brokers=brokers,
    data_stores=data_stores,
    status_interval=30.0,
)