# INTERSECT RabbitMQ Clustering Demo

This demo showcases how to use INTERSECT SDK with RabbitMQ clustering for improved resilience. The system demonstrates manual failover between RabbitMQ cluster nodes when the primary node fails.

## Features

- RabbitMQ 2-node cluster configuration
- Time-based counter that continues across failovers
- Manual failover script to switch to backup node
- Demonstrates resilience concepts for service-service communication

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- INTERSECT SDK

## Setup

1. Start the RabbitMQ cluster and MinIO:

```bash
docker-compose up -d
```

2. In separate terminals, start the service and client:

```bash
# Terminal 1 - Start the service
cd service
python counting_service.py

# Terminal 2 - Start the client
cd client
python counting_client.py
```

## Testing Manual Failover

To test the cluster's manual failover capability:

1. Start both the service and client
2. Wait until messages are being exchanged and counter is incrementing
3. Simulate a node failure by stopping the primary RabbitMQ container:

```bash
# Stop the first RabbitMQ node
docker-compose stop rabbitmq1
```

4. The service and client will lose connection to RabbitMQ
5. Run the failover script to update configurations to use the backup node:

```bash
python switch_to_backup.py
```

6. Restart both the service and client to connect to the backup node:

```bash
# Terminal 1 (service)
python counting_service.py

# Terminal 2 (client)
python counting_client.py
```

7. The service should continue from where it left off (the counter value is based on elapsed time)

## Architecture

The demo consists of:

- 2 RabbitMQ nodes in a cluster
- 1 MinIO container for object storage
- 1 INTERSECT service (counting example)
- 1 INTERSECT client interacting with the service

The RabbitMQ nodes share a common Erlang cookie for cluster formation. Although the MQTT client doesn't automatically fail over between brokers, our script helps simulate what this would look like in a production environment with proper failover mechanisms.

## Implementation Notes

1. **Time-Based Counter**: The counter is based on elapsed time since the service started, ensuring it's consistent even after restarts or failovers.

2. **Manual Failover**: The `switch_to_backup.py` script updates configuration files to point to the backup RabbitMQ node.

3. **MQTT Limitations**: MQTT in the current INTERSECT SDK doesn't support automatic failover between multiple brokers, which is why we use the manual approach in this demo.

4. **Future Improvements**: A future enhanced version of the SDK could:
   - Implement automatic failover for MQTT clients
   - Support true clustering for both AMQP and MQTT clients
   - Handle reconnection to multiple brokers transparently