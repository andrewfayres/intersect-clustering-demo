# INTERSECT RabbitMQ Clustering Demo

This demo showcases how to use INTERSECT SDK with RabbitMQ clustering for improved resilience. The system demonstrates automatic failover between RabbitMQ cluster nodes when the primary node fails.

## Features

- RabbitMQ 2-node cluster configuration
- Support for both MQTT and AMQP protocols
- Time-based counter that continues across failovers
- Automatic failover between cluster nodes
- Demonstrates resilience concepts for service-service communication

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- INTERSECT SDK

## Setup

### MQTT Protocol (Default)

1. Start the entire stack with Docker Compose:

```bash
docker-compose up --build
```

This will start:
- Two RabbitMQ nodes in a cluster
- MinIO for object storage
- The counting service
- The client that polls the counting service

### AMQP Protocol

To run the demo with AMQP protocol instead:

```bash
PROTOCOL=amqp docker-compose up --build
```

This uses the same infrastructure but configures the services to use AMQP instead of MQTT.

## Testing Automatic Failover

To test the cluster's automatic failover capability:

1. Start the stack with either MQTT or AMQP protocol as described above
2. Wait until messages are being exchanged and the counter is incrementing
3. Simulate a node failure by stopping the primary RabbitMQ container:

```bash
# Stop the first RabbitMQ node
docker-compose stop rabbitmq1
```

4. Watch as the client and service automatically detect the failure and reconnect to rabbitmq2
5. The counter should continue with minimal disruption
6. The service should continue from where it left off (the counter value is based on elapsed time)

## Architecture

The demo consists of:

- 2 RabbitMQ nodes in a cluster
- 1 MinIO container for object storage
- 1 INTERSECT service (counting example)
- 1 INTERSECT client interacting with the service

The RabbitMQ nodes share a common Erlang cookie for cluster formation. The client and service are designed to automatically fail over to the backup node when the primary node fails.

## Implementation Notes

1. **Time-Based Counter**: The counter is based on elapsed time since the service started, ensuring it's consistent even after restarts or failovers.

2. **Protocol Options**: 
   - MQTT: Standard implementation using port 1883
   - AMQP: Uses port 5672 and requires additional dependencies

3. **Automatic Failover**: The SDK has been updated to support automatic failover:
   - Both MQTT and AMQP clients can detect disconnections
   - Services and clients automatically attempt to reconnect to alternate brokers
   - Connection parameters allow listing multiple broker endpoints

4. **Cluster Configuration**: The demo uses a simple 2-node RabbitMQ cluster with:
   - Shared Erlang cookie for authentication between nodes
   - Automatic node discovery and clustering
   - Both MQTT and AMQP protocols enabled

## Monitoring

You can access the RabbitMQ management interfaces at:
- Node 1: http://localhost:15672 
- Node 2: http://localhost:15673

Use these credentials:
- Username: `intersect_username`
- Password: `intersect_password`