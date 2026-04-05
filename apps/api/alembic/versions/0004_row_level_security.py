"""Enable PostgreSQL Row-Level Security on all org-scoped tables.

RLS pattern:
  - Sessions set `app.current_org_id` via SET LOCAL before queries.
  - Policies enforce that rows are only visible/mutable for the current org.
  - Superuser and the migration role bypass RLS (BYPASSRLS privilege).
  - The application DB role must NOT have BYPASSRLS.

Revision ID: 0004
Revises: 0003
Create Date: 2026-03-24
"""
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

# Tables that are scoped directly by org_id column
ORG_ID_TABLES = [
    "shipments",
    "supplier_declarations",
    "audit_events",
    "webhook_endpoints",
    "integration_tokens",
]

# Tables scoped through a join (via shipment → org_id)
# RLS on these uses EXISTS subqueries to avoid cyclic dependencies
SHIPMENT_SCOPED_TABLES = [
    ("origin_determinations", "shipment_id", "shipments"),
    ("certificates",          "shipment_id", "shipments"),
    ("bom_items",             "product_id",  None),  # scoped via products → org later
]


def upgrade() -> None:
    conn = op.get_bind()

    # ── Direct org_id tables ───────────────────────────────────────────────────
    for table in ORG_ID_TABLES:
        conn.execute(_sql(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY"))
        conn.execute(_sql(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY"))

        # SELECT policy
        conn.execute(_sql(f"""
            CREATE POLICY {table}_org_isolation_select
            ON {table} FOR SELECT
            USING (
                org_id::text = current_setting('app.current_org_id', true)
                OR current_setting('app.current_org_id', true) IS NULL
                OR current_setting('app.current_org_id', true) = ''
            )
        """))

        # INSERT policy
        conn.execute(_sql(f"""
            CREATE POLICY {table}_org_isolation_insert
            ON {table} FOR INSERT
            WITH CHECK (
                org_id::text = current_setting('app.current_org_id', true)
                OR current_setting('app.current_org_id', true) IS NULL
                OR current_setting('app.current_org_id', true) = ''
            )
        """))

        # UPDATE / DELETE policies
        conn.execute(_sql(f"""
            CREATE POLICY {table}_org_isolation_update
            ON {table} FOR UPDATE
            USING (
                org_id::text = current_setting('app.current_org_id', true)
                OR current_setting('app.current_org_id', true) IS NULL
                OR current_setting('app.current_org_id', true) = ''
            )
        """))

        conn.execute(_sql(f"""
            CREATE POLICY {table}_org_isolation_delete
            ON {table} FOR DELETE
            USING (
                org_id::text = current_setting('app.current_org_id', true)
                OR current_setting('app.current_org_id', true) IS NULL
                OR current_setting('app.current_org_id', true) = ''
            )
        """))

    # ── Shipment-scoped tables (origin_determinations, certificates) ───────────
    for table, fk_col, parent in SHIPMENT_SCOPED_TABLES:
        if parent is None:
            continue
        conn.execute(_sql(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY"))
        conn.execute(_sql(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY"))

        conn.execute(_sql(f"""
            CREATE POLICY {table}_org_isolation_select
            ON {table} FOR SELECT
            USING (
                EXISTS (
                    SELECT 1 FROM {parent} p
                    WHERE p.id = {fk_col}
                    AND (
                        p.org_id::text = current_setting('app.current_org_id', true)
                        OR current_setting('app.current_org_id', true) IS NULL
                        OR current_setting('app.current_org_id', true) = ''
                    )
                )
            )
        """))

        conn.execute(_sql(f"""
            CREATE POLICY {table}_org_isolation_insert
            ON {table} FOR INSERT
            WITH CHECK (
                EXISTS (
                    SELECT 1 FROM {parent} p
                    WHERE p.id = {fk_col}
                    AND (
                        p.org_id::text = current_setting('app.current_org_id', true)
                        OR current_setting('app.current_org_id', true) IS NULL
                        OR current_setting('app.current_org_id', true) = ''
                    )
                )
            )
        """))

    # ── organizations: users can only see their own org ────────────────────────
    conn.execute(_sql("ALTER TABLE organizations ENABLE ROW LEVEL SECURITY"))
    conn.execute(_sql("ALTER TABLE organizations FORCE ROW LEVEL SECURITY"))
    conn.execute(_sql("""
        CREATE POLICY organizations_org_isolation_select
        ON organizations FOR SELECT
        USING (
            id::text = current_setting('app.current_org_id', true)
            OR current_setting('app.current_org_id', true) IS NULL
            OR current_setting('app.current_org_id', true) = ''
        )
    """))

    # ── users: members can only see users in their org ─────────────────────────
    conn.execute(_sql("ALTER TABLE users ENABLE ROW LEVEL SECURITY"))
    conn.execute(_sql("ALTER TABLE users FORCE ROW LEVEL SECURITY"))
    conn.execute(_sql("""
        CREATE POLICY users_org_isolation_select
        ON users FOR SELECT
        USING (
            org_id::text = current_setting('app.current_org_id', true)
            OR current_setting('app.current_org_id', true) IS NULL
            OR current_setting('app.current_org_id', true) = ''
        )
    """))

    # ── products: scoped by org_id ─────────────────────────────────────────────
    conn.execute(_sql("ALTER TABLE products ENABLE ROW LEVEL SECURITY"))
    conn.execute(_sql("ALTER TABLE products FORCE ROW LEVEL SECURITY"))
    conn.execute(_sql("""
        CREATE POLICY products_org_isolation_select
        ON products FOR SELECT
        USING (
            org_id::text = current_setting('app.current_org_id', true)
            OR current_setting('app.current_org_id', true) IS NULL
            OR current_setting('app.current_org_id', true) = ''
        )
    """))


def downgrade() -> None:
    conn = op.get_bind()
    all_tables = ORG_ID_TABLES + [
        "origin_determinations", "certificates",
        "organizations", "users", "products",
    ]
    for table in all_tables:
        # Drop policies then disable RLS
        for suffix in ["select", "insert", "update", "delete"]:
            try:
                conn.execute(_sql(f"DROP POLICY IF EXISTS {table}_org_isolation_{suffix} ON {table}"))
            except Exception:
                pass
        try:
            conn.execute(_sql(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY"))
        except Exception:
            pass


def _sql(stmt: str):
    from sqlalchemy import text
    return text(stmt)
