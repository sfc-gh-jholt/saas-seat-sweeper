"""Read-only participant runtime inspection. No connection or query on import."""
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import json
import math
import re

METRICS = {
    'container.cpu.usage', 'container.cpu.requested', 'container.cpu.limit',
    'container.memory.usage', 'container.memory.requested', 'container.memory.limit',
    'container.restarts', 'container.state.running', 'container.state.pending',
}


def participant_service(service_fqn):
    if not isinstance(service_fqn, str) or not re.fullmatch(
        r'SAAS_SEAT_SWEEPER\.APP\.SEAT_SWEEPER_[A-Z0-9_]+', service_fqn
    ) or service_fqn == 'SAAS_SEAT_SWEEPER.APP.SEAT_SWEEPER_REF':
        raise ValueError('Enter your exact uppercase participant service FQN, not the reference target.')
    return service_fqn


def inspect_runtime(lab, service_fqn, kind, *, backend='UNKNOWN'):
    service = participant_service(service_fqn)
    if kind == 'status':
        sql = f'DESCRIBE APPLICATION SERVICE {service}'
    elif kind == 'logs':
        sql = f"CALL SYSTEM$GET_APPLICATION_SERVICE_LOGS('{service}', 30)"
    elif kind == 'metrics':
        if backend != 'MANAGED_COMPUTE_POOL':
            raise ValueError('Metrics require a facilitator-verified managed-pool backend. Use status/logs for serverless or unknown backends.')
        sql = f"CALL SYSTEM$GET_APPLICATION_SERVICE_EVENT_TABLE_DATA('{service}', 'METRIC')"
    else:
        raise ValueError('Choose status, logs or metrics; no write operations are supported.')
    lab.check_identity()
    rows = lab._rows(sql)
    if kind == 'status':
        fields = ('name', 'database_name', 'schema_name', 'status', 'source',
                  'is_upgrading', 'current_instances', 'min_instances', 'max_instances',
                  'auto_resume', 'auto_suspend_secs', 'query_warehouse', 'compute_pool')
        normalized = [{key.lower(): value for key, value in row.items()} for row in rows]
        return [{key: row.get(key) for key in fields} for row in normalized]
    if len(rows) != 1 or len(rows[0]) != 1:
        raise ValueError('Unexpected telemetry response. Keep the error and ask the facilitator.')
    payload = next(iter(rows[0].values()))
    return latest_metrics(payload) if kind == 'metrics' else payload


def sample_time(value):
    try:
        seconds = Decimal(str(value))
    except InvalidOperation:
        moment = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        if moment.tzinfo is None:
            raise ValueError('Telemetry timestamp lacks a timezone; cannot infer freshness.')
        return moment.astimezone(timezone.utc)
    if not seconds.is_finite():
        raise ValueError('Invalid numeric telemetry timestamp')
    return datetime.fromtimestamp(float(seconds), timezone.utc)


def latest_metrics(payload, now=None):
    """Latest available sample per metric/container/instance, not aligned ratios."""
    records = json.loads(payload) if isinstance(payload, str) else payload
    if not isinstance(records, list):
        raise ValueError('Expected a telemetry array')
    now = now or datetime.now(timezone.utc)
    latest = {}
    for record in records:
        if not isinstance(record, list) or len(record) < 6:
            raise ValueError('Unexpected telemetry tuple shape')
        if record[1] not in METRICS or record[5] != 'runner':
            continue
        moment = sample_time(record[0])
        value = float(record[2])
        if not math.isfinite(value):
            raise ValueError('Non-finite telemetry value')
        key = (str(record[4]), record[5], record[1])
        if key not in latest or moment > latest[key][0]:
            latest[key] = (moment, value, record[3])
    samples = []
    for (instance, container, metric), (moment, value, unit) in sorted(latest.items()):
        samples.append({
            'instance': instance, 'container': container, 'metric': metric,
            'value': value, 'unit': unit, 'sample_utc': moment.isoformat(),
            'age_seconds': round((now - moment).total_seconds(), 1),
            'memory_mib': round(value / 1024 ** 2, 1) if metric.startswith('container.memory.') and unit == 'byte' else None,
        })
    return {
        'retrieved_utc': now.isoformat(),
        'note': 'Latest available samples in a capped response, not a full history. Different metrics can have different timestamps. Empty or stale data is not proof of health; restart counters are not lifetime totals.',
        'samples': samples,
    }
