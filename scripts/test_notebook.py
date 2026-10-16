"""Offline notebook and runner tests. Fake connections only; no Snowflake calls."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import notebook_lab
from validate_notebook import validate_notebook, validate_links_and_prompts

ROOT = Path(__file__).resolve().parents[1]


def fixture_notebook():
    return {'nbformat': 4, 'nbformat_minor': 5, 'metadata': {}, 'cells': [
        {'id': 'abc12345', 'cell_type': 'code', 'source': ['value = 1'],
         'metadata': {}, 'outputs': [], 'execution_count': None}]}


class FakeConnection:
    def __init__(self, identity=('TRAINING-DEMO', 'LEARNER', 'ACCOUNTADMIN')):
        self.identity = identity
        self.executed = []
        self.collision = None
        self.fail_block = False
        self.closed = False

    def cursor(self):
        return FakeCursor(self)

    def close(self):
        self.closed = True


class FakeCursor:
    sfqid = 'synthetic-query-id'

    def __init__(self, connection):
        self.connection = connection
        self.description = []
        self.rows = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def execute(self, sql):
        self.connection.executed.append(sql)
        if sql == notebook_lab.IDENTITY_SQL:
            self.description = [('ACCOUNT',), ('USER_NAME',), ('ROLE_NAME',)]
            self.rows = [self.connection.identity]
        elif sql.startswith('SHOW '):
            self.description = [('name',)]
            self.rows = [(self.connection.collision,)] if self.connection.collision else []
        elif sql.startswith('EXECUTE IMMEDIATE') and self.connection.fail_block:
            raise KeyboardInterrupt('synthetic uncertain outcome')

    def fetchmany(self, count):
        return self.rows[:count]


class NotebookTests(unittest.TestCase):
    def test_distributed_notebook_and_canonical_prompts(self):
        notebook = validate_notebook((ROOT / 'START_HERE.ipynb').read_bytes())
        validate_links_and_prompts(notebook, ROOT)
        text = '\n'.join(''.join(cell['source']) for cell in notebook['cells'])
        self.assertEqual(text.count('<!-- prompt:'), 4)
        self.assertNotIn('%%sql', text)
        self.assertNotIn('workshop-orient', text)
        for expected in ('135–150', "'status'", "'metrics'", "'logs'", "runtime_backend = 'UNKNOWN'", 'raw SPCS', 'synthetic incident'):
            self.assertIn(expected, text)

    def test_reject_outputs_counts_metadata_ids_and_connection_values(self):
        for change in ('output', 'count', 'metadata', 'id', 'connection', 'duplicate', 'widgets'):
            notebook = fixture_notebook()
            cell = notebook['cells'][0]
            if change == 'output':
                cell['outputs'] = [{'output_type': 'stream', 'name': 'stdout', 'text': 'private'}]
            elif change == 'count':
                cell['execution_count'] = 1
            elif change == 'metadata':
                cell['metadata'] = {'execution': {'private': 'value'}}
            elif change == 'id':
                cell['id'] = 'bad-id'
            elif change == 'connection':
                cell['source'] = ["expected_account = 'TRAINING-DEMO'"]
            elif change == 'duplicate':
                notebook['cells'].append(copy.deepcopy(cell))
            else:
                notebook['metadata']['widgets'] = {'private': 'value'}
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_notebook(json.dumps(notebook))

    def test_identity_mismatch_and_internal_account_rejected(self):
        for identity in (('OTHER-DEMO', 'LEARNER', 'ACCOUNTADMIN'),
                         ('TRAINING-DEMO', 'OTHER', 'ACCOUNTADMIN'),
                         ('TRAINING-DEMO', 'LEARNER', 'PUBLIC'),
                         ('TRAINING-SNOWHOUSE', 'LEARNER', 'ACCOUNTADMIN')):
            with self.subTest(identity=identity), self.assertRaises(RuntimeError):
                notebook_lab.Lab(FakeConnection(identity), 'TRAINING-DEMO', 'LEARNER')

    def test_placeholders_rejected_before_connector_import(self):
        for value in ('', 'REPLACE_WITH_CONNECTION'):
            with self.assertRaises(ValueError):
                notebook_lab.connect_lab(value, 'TRAINING-DEMO', 'LEARNER')

    def test_close(self):
        connection = FakeConnection()
        notebook_lab.Lab(connection, 'TRAINING-DEMO', 'LEARNER').close()
        self.assertTrue(connection.closed)


try:
    import snowflake.connector
    HAS_CONNECTOR = True
except ImportError:
    HAS_CONNECTOR = False


@unittest.skipUnless(HAS_CONNECTOR, 'Install the notebook connector in the selected test environment')
class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.connection = FakeConnection()
        self.lab = notebook_lab.Lab(self.connection, 'TRAINING-DEMO', 'LEARNER', confirm=self.approve)

    @staticmethod
    def approve(prompt):
        return prompt.removeprefix('Type exactly ').split(' to approve this step')[0]

    def test_whole_blocks_and_all_three_scripts_in_order(self):
        for name in notebook_lab.SCRIPTS:
            parsed = notebook_lab.statements((ROOT / 'sql' / name).read_text())
            blocks = [sql for sql in parsed if sql.startswith('EXECUTE IMMEDIATE $$')]
            self.assertEqual(len(blocks), 1, name)
            self.assertTrue(blocks[0].endswith('$$;'))
            self.assertIn('END;', blocks[0])
            self.lab.bootstrap(name)
        self.assertEqual(self.lab.completed, list(notebook_lab.SCRIPTS))
        blocks = [sql for sql in self.connection.executed if sql.startswith('EXECUTE IMMEDIATE $$')]
        self.assertEqual(len(blocks), 3)
        with self.assertRaises(ValueError):
            self.lab.bootstrap('02_seed_data.sql')

    def test_cancellation_and_missing_input_fail_closed(self):
        for confirmation in (lambda prompt: '', lambda prompt: (_ for _ in ()).throw(EOFError())):
            self.lab.confirm = confirmation
            with self.assertRaises((RuntimeError, EOFError)):
                self.lab.bootstrap('01_setup.sql')
        self.assertFalse(any(sql.startswith('EXECUTE ') for sql in self.connection.executed))

    def test_all_fixed_collisions_block_before_mutations(self):
        for name in ('SAAS_SEAT_SWEEPER', 'SAAS_SWEEPER_WH', 'SAAS_SWEEPER_MANAGER', 'SAAS_SWEEPER_RESTRICTED'):
            self.connection.collision = name
            with self.subTest(name=name), self.assertRaisesRegex(RuntimeError, 'Existing object'):
                self.lab.bootstrap('01_setup.sql')
        self.assertFalse(any(sql.startswith('EXECUTE ') for sql in self.connection.executed))

    def test_identity_changes_during_confirmation(self):
        def changed(prompt):
            self.connection.identity = ('OTHER-DEMO', 'LEARNER', 'ACCOUNTADMIN')
            return self.approve(prompt)
        self.lab.confirm = changed
        with self.assertRaises(RuntimeError):
            self.lab.bootstrap('01_setup.sql')
        self.assertFalse(any(sql.startswith('EXECUTE ') for sql in self.connection.executed))

    def test_interrupt_latches_failure_and_prevents_retry(self):
        self.connection.fail_block = True
        with self.assertRaises(KeyboardInterrupt):
            self.lab.bootstrap('01_setup.sql')
        self.assertTrue(self.lab.failed)
        self.connection.fail_block = False
        with self.assertRaisesRegex(RuntimeError, 'Previous step failed'):
            self.lab.bootstrap('01_setup.sql')

    def test_wrong_order_or_path_rejected(self):
        for name in ('02_seed_data.sql', '../01_setup.sql', '05_ai_objects.sql'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.lab.bootstrap(name)

    def test_multiple_statements_and_dml_rejected_by_query_helper(self):
        for sql in ('SELECT 1; SELECT 2;', "UPDATE example SET status = 'Flagged'"):
            with self.subTest(sql=sql), self.assertRaises(ValueError):
                self.lab.query(sql)

    def test_connector_receives_only_explicit_profile_and_empty_context(self):
        with patch('snowflake.connector.connect', return_value=self.connection) as connect:
            notebook_lab.connect_lab('training-profile', 'TRAINING-DEMO', 'LEARNER')
        connect.assert_called_once_with(connection_name='training-profile', role='ACCOUNTADMIN',
                                        database=None, schema=None, warehouse=None)
        with patch('snowflake.connector.connect', side_effect=ValueError('Unknown connection')) as connect:
            with self.assertRaises(ValueError):
                notebook_lab.connect_lab('missing-profile', 'TRAINING-DEMO', 'LEARNER')
        self.assertEqual(connect.call_count, 1)


if __name__ == '__main__':
    unittest.main()
