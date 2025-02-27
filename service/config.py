"""
Configuration for the INTERSECT service with RabbitMQ clustering support.
"""

from intersect_sdk.config.service import IntersectServiceConfig
from intersect_sdk.config.shared import (
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

# Create the service config
SERVICE_CONFIG = IntersectServiceConfig(
    hierarchy=hierarchy,
    brokers=brokers,
    data_stores=data_stores,
    status_interval=30.0,
)