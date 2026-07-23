from app.db.session import make_async_database_url, make_sync_database_url


def test_async_database_url_converts_driver_and_supabase_sslmode() -> None:
    url = make_async_database_url(
        "postgresql+psycopg://postgres:secret@db.example.com:5432/agroguard"
        "?sslmode=require"
    )

    assert url.drivername == "postgresql+asyncpg"
    assert url.query == {"ssl": "require"}


def test_async_database_url_preserves_pooler_query_options() -> None:
    url = make_async_database_url(
        "postgresql://postgres:secret@pooler.example.com:6543/postgres"
        "?sslmode=require&prepared_statement_cache_size=0"
    )

    assert url.drivername == "postgresql+asyncpg"
    assert url.query == {
        "ssl": "require",
        "prepared_statement_cache_size": "0",
    }


def test_copied_supabase_url_uses_installed_drivers_and_tls() -> None:
    database_url = (
        "postgresql://postgres.project:secret@"
        "aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"
    )

    sync_url = make_sync_database_url(database_url)
    async_url = make_async_database_url(database_url)

    assert sync_url.drivername == "postgresql+psycopg"
    assert sync_url.query == {"sslmode": "require"}
    assert async_url.drivername == "postgresql+asyncpg"
    assert async_url.query == {"ssl": "require"}
