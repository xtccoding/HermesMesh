# Configuration Guide

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

### Required Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | - |
| `HERMES_MODEL` | Hermes model name | `hermes-3-llama-3.1-8b` |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka broker addresses | `localhost:9092` |
| `NATS_URL` | NATS server URL | `nats://localhost:4222` |
| `REDIS_HOST` | Redis host | `localhost` |
| `DATABASE_URL` | PostgreSQL connection string | - |

## Configuration Files

### Ingestion Configuration

```yaml
# config/ingestion/default.yaml
ingestion:
  max_workers: 10
  batch_size: 100
  timeout: 30
  kafka_topic: hermesmesh-ingestion
  output_format: json
  enable_cleaning: true
  cleaning_threshold: 0.8
```

### Worker Configuration

```yaml
# config/workers/cluster_a.yaml
cluster_a:
  max_instances: 50
  min_instances: 5
  scaling_factor: 1.5
  max_queue_size: 1000
  processing_timeout: 60
```

### Supervisor Configuration

```yaml
# config/supervisor/rules.yaml
supervision:
  enable_debate: true
  debate_rounds: 3
  voting_threshold: 0.7
  alignment_checks:
    - numeric_verification
    - logical_consistency
    - temporal_alignment
```

## Running the Pipeline

```bash
# Basic run
python -m hermesmesh.cli run

# With custom config
python -m hermesmesh.cli run \
  --ingestion-config config/ingestion/default.yaml \
  --worker-config config/workers/cluster_a.yaml \
  --worker-instances 20 \
  --log-level DEBUG
```
