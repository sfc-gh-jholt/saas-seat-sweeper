"""Offline runtime inspection tests; no Snowflake connection."""
from datetime import datetime, timezone
import json
import unittest
from unittest.mock import Mock

from notebook_runtime import inspect_runtime, latest_metrics, participant_service

TARGET = 'SAAS_SEAT_SWEEPER.APP.SEAT_SWEEPER_LEARNER'


class RuntimeTests(unittest.TestCase):
    def test_target_validation(self):
        self.assertEqual(participant_service(TARGET), TARGET)
        for bad in ('REPLACE_WITH_TARGET', 'SAAS_SEAT_SWEEPER.APP.SEAT_SWEEPER_REF',
                    TARGET + "; DROP DATABASE X", 'OTHER.APP.SEAT_SWEEPER_LEARNER', None):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                participant_service(bad)

    def test_status_is_scoped_and_identity_checked(self):
        lab = Mock()
        lab._rows.return_value = [{'STATUS': 'RUNNING', 'SOURCE': 'VERSION$1', 'private': 'omit'}]
        result = inspect_runtime(lab, TARGET, 'status')
        lab.check_identity.assert_called_once()
        lab._rows.assert_called_once_with(f'DESCRIBE APPLICATION SERVICE {TARGET}')
        self.assertEqual(result[0]['status'], 'RUNNING')
        self.assertNotIn('private', result[0])

    def test_wrong_identity_prevents_inspection(self):
        lab = Mock()
        lab.check_identity.side_effect = RuntimeError('wrong account')
        with self.assertRaises(RuntimeError):
            inspect_runtime(lab, TARGET, 'logs')
        lab._rows.assert_not_called()

    def test_unknown_serverless_or_bad_action_never_queries(self):
        for backend in ('UNKNOWN', 'SERVERLESS', None):
            lab = Mock()
            with self.subTest(backend=backend), self.assertRaises(ValueError):
                inspect_runtime(lab, TARGET, 'metrics', backend=backend)
            lab._rows.assert_not_called()
        with self.assertRaises(ValueError):
            inspect_runtime(Mock(), TARGET, 'restart')

    def test_logs_and_managed_metrics_use_only_fixed_calls(self):
        lab = Mock()
        lab._rows.return_value = [{'LOGS': 'synthetic startup'}]
        self.assertEqual(inspect_runtime(lab, TARGET, 'logs'), 'synthetic startup')
        lab._rows.assert_called_with(f"CALL SYSTEM$GET_APPLICATION_SERVICE_LOGS('{TARGET}', 30)")
        lab._rows.return_value = [{'METRIC': '[]'}]
        self.assertEqual(inspect_runtime(lab, TARGET, 'metrics', backend='MANAGED_COMPUTE_POOL')['samples'], [])
        lab._rows.assert_called_with(f"CALL SYSTEM$GET_APPLICATION_SERVICE_EVENT_TABLE_DATA('{TARGET}', 'METRIC')")

    def test_latest_samples_keep_instances_and_timestamps_separate(self):
        records = [
            ['100', 'container.memory.usage', '1048576', 'byte', '0', 'runner'],
            ['101', 'container.memory.usage', '2097152', 'byte', '0', 'runner'],
            ['99', 'container.memory.limit', '4194304', 'byte', '0', 'runner'],
            ['100', 'container.memory.usage', '3145728', 'byte', '1', 'runner'],
            ['102', 'container.memory.usage', '999', 'byte', '0', 'sidecar'],
            ['1970-01-01T00:01:41Z', 'container.restarts', '0', 'count', '0', 'runner'],
        ]
        result = latest_metrics(json.dumps(records), datetime.fromtimestamp(110, timezone.utc))
        self.assertEqual(len(result['samples']), 4)
        usage = [row for row in result['samples'] if row['metric'] == 'container.memory.usage']
        self.assertEqual([row['memory_mib'] for row in usage], [2, 3])
        self.assertEqual([row['age_seconds'] for row in usage], [9, 10])
        self.assertTrue(all('pct' not in row for row in result['samples']))

    def test_empty_malformed_or_unzoned_data(self):
        self.assertEqual(latest_metrics('[]')['samples'], [])
        for payload in ('{}', '[[]]', 'invalid',
                        '[["2026-10-16T03:00:00", "container.cpu.usage", 1, "cpu", 0, "runner"]]',
                        '[["100", "container.cpu.usage", "NaN", "cpu", 0, "runner"]]'):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                latest_metrics(payload)
        lab = Mock()
        lab._rows.return_value = []
        with self.assertRaises(ValueError):
            inspect_runtime(lab, TARGET, 'logs')


if __name__ == '__main__':
    unittest.main()
