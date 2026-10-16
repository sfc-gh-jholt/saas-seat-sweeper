"""Local notebook helpers. Importing this module never connects or executes SQL.

The runner accepts only the three supplied bootstrap scripts. Each write requires
fresh interactive confirmation; it never resets, resumes or retries a failed step.
"""
from pathlib import Path
import hashlib
import io

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ("01_setup.sql", "02_seed_data.sql", "03_rbac_demo.sql")
IDENTITY_SQL = """SELECT CURRENT_ORGANIZATION_NAME() || '-' || CURRENT_ACCOUNT_NAME()
AS ACCOUNT, CURRENT_USER() AS USER_NAME, CURRENT_ROLE() AS ROLE_NAME"""


def statements(text):
    from snowflake.connector.util_text import split_statements
    return [sql.strip() for sql, _ in split_statements(io.StringIO(text), remove_comments=True)
            if sql.strip().strip(';')]


class Lab:
    def __init__(self, connection, expected_account, expected_user, confirm=input):
        self.connection = connection
        self.expected = (expected_account.upper(), expected_user.upper(), "ACCOUNTADMIN")
        self.confirm = confirm
        self.completed = []
        self.failed = False
        self.check_identity()

    def _rows(self, sql):
        with self.connection.cursor() as cursor:
            cursor.execute(sql)
            names = [column[0] for column in cursor.description] if cursor.description else []
            rows = cursor.fetchmany(51) if names else []
            if len(rows) > 50:
                raise RuntimeError("Result exceeds 50 rows; add a LIMIT or aggregate in SQL.")
            return [dict(zip(names, row)) for row in rows]

    def check_identity(self):
        rows = self._rows(IDENTITY_SQL)
        if len(rows) != 1:
            raise RuntimeError("Could not verify session identity.")
        row = rows[0]
        actual = tuple(str(row[key]).upper() for key in ("ACCOUNT", "USER_NAME", "ROLE_NAME"))
        if actual != self.expected or "SNOWHOUSE" in actual[0]:
            raise RuntimeError("Wrong account, user or role. Stop and check your workshop connection.")
        return row

    def query(self, sql):
        self.check_identity()
        parsed = statements(sql)
        if len(parsed) != 1 or not parsed[0].upper().startswith("SELECT "):
            raise ValueError("Use this helper only for one supplied SELECT query.")
        return self._rows(parsed[0])

    def _check_empty(self):
        for sql, name in (
            ("SHOW DATABASES LIKE 'SAAS_SEAT_SWEEPER'", "SAAS_SEAT_SWEEPER"),
            ("SHOW WAREHOUSES LIKE 'SAAS_SWEEPER_WH'", "SAAS_SWEEPER_WH"),
            ("SHOW ROLES LIKE 'SAAS_SWEEPER_MANAGER'", "SAAS_SWEEPER_MANAGER"),
            ("SHOW ROLES LIKE 'SAAS_SWEEPER_RESTRICTED'", "SAAS_SWEEPER_RESTRICTED"),
        ):
            rows = self._rows(sql)
            if any(str(row.get("name", row.get("NAME", ""))).upper() == name for row in rows):
                raise RuntimeError(f"Existing object: {name}. Ask the facilitator; nothing was reset.")

    def bootstrap(self, name):
        if self.failed:
            raise RuntimeError("Previous step failed or was interrupted. Ask the facilitator to inspect partial state.")
        if name not in SCRIPTS or len(self.completed) >= len(SCRIPTS) or name != SCRIPTS[len(self.completed)]:
            raise ValueError("Run the supplied scripts once, in order: 01, 02, 03. Never reseed.")
        path = ROOT / "sql" / name
        if path.is_symlink():
            raise ValueError("Bootstrap source must not be a symlink.")
        content = path.read_text(encoding="utf-8")
        parsed = statements(content)
        # Verification SELECTs remain separate notebook cells, not hidden script effects.
        setup = [sql for sql in parsed if not sql.upper().startswith("SELECT ")]
        if sum(sql.upper().startswith("EXECUTE IMMEDIATE $$") for sql in setup) != 1:
            raise ValueError("Expected exactly one supplied scripting block; review the source.")
        if any(not sql.upper().startswith(("USE ", "EXECUTE IMMEDIATE $$")) for sql in setup):
            raise ValueError("Unexpected statement outside the bootstrap block.")
        self.check_identity()
        if not self.completed:
            self._check_empty()
        digest = hashlib.sha256(content.encode()).hexdigest()[:12]
        approval = f"RUN {name} IN {self.expected[0]} {digest}"
        print(f"Review sql/{name} before continuing. DDL may partially commit on error.")
        print(f"Source SHA-256 prefix: {digest}")
        if self.confirm(f"Type exactly {approval} to approve this step (anything else cancels): ") != approval:
            raise RuntimeError("Cancelled. No bootstrap statements executed.")
        self.check_identity()
        if not self.completed:
            self._check_empty()
        # Latch before the first statement: interrupts must also block accidental retry.
        self.failed = True
        for sql in setup:
            with self.connection.cursor() as cursor:
                cursor.execute(sql)
                print(f"Completed statement; query ID: {cursor.sfqid}")
        self.completed.append(name)
        self.failed = False
        return f"Completed {name}. Continue to the next step; do not rerun this cell."

    def close(self):
        self.connection.close()


def connect_lab(connection_name, expected_account, expected_user):
    values = (connection_name, expected_account, expected_user)
    if any(not value.strip() or value.startswith("REPLACE_") for value in values):
        raise ValueError("Fill all three connection fields with your assigned workshop details first.")
    import snowflake.connector
    # An unknown explicit connection must fail, never select the default profile.
    connection = snowflake.connector.connect(
        connection_name=connection_name, role="ACCOUNTADMIN",
        database=None, schema=None, warehouse=None,
    )
    try:
        return Lab(connection, expected_account, expected_user)
    except BaseException:
        connection.close()
        raise
