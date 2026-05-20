# Troubleshooting Guide

## Common Issues

### Connection Errors

**Kafka Connection Refused**
```
Error: KafkaConnectionError: Connection refused
```
Solution: Ensure Kafka is running and `KAFKA_BOOTSTRAP_SERVERS` is correct.

**NATS Connection Timeout**
```
Error: NATS connection timeout
```
Solution: Check NATS server status and `NATS_URL` configuration.

### Performance Issues

**High Memory Usage**
- Reduce `batch_size` in ingestion config
- Decrease `max_instances` for workers
- Enable data streaming instead of batch processing

**Slow Processing**
- Increase `worker_instances`
- Check for bottlenecks in supervision layer
- Monitor queue sizes

### Validation Errors

**High Disagreement Rate**
- Increase `debate_rounds` in supervisor config
- Lower `voting_threshold`
- Check source data quality

## Debug Mode

Enable debug logging:

```bash
python -m hermesmesh.cli run --log-level DEBUG --log-file debug.log
```

## Health Checks

Check component health:

```python
from hermesmesh import create_mesh

mesh = create_mesh()
metrics = await mesh["control"].get_metrics()
print(metrics)
```

## Getting Help

- GitHub Issues: https://github.com/hermesmesh/hermesmesh/issues
- Documentation: https://hermesmesh.readthedocs.io
