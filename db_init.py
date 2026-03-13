"""
Database initialization script.

Usage:
  python db_init.py                # create tables if missing (safe)
  python db_init.py --reset --yes  # drop all tables and recreate (destructive)
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url

from db.database import ormar_config
from db.models import (
    Member, Spam, BotOwner, ManagedChat, LinkedChannel,
    BotSetting, ChatSetting, SettingsAuditLog
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _to_sync_url(url: str) -> str:
    return (
        url.replace("+aiosqlite", "")
        .replace("+asyncpg", "")
        .replace("+aiomysql", "")
    )


def _ensure_sqlite_path(url: str) -> None:
    parsed = make_url(url)
    if not parsed.drivername.startswith("sqlite"):
        return
    if not parsed.database or parsed.database == ":memory:":
        return

    db_path = Path(parsed.database)
    if not db_path.is_absolute():
        db_path = Path.cwd() / db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.touch(exist_ok=True)
    logger.info("SQLite file ready: %s", db_path)


def init_db_tables(reset: bool = False) -> None:
    db_url = str(ormar_config.database.url)
    _ensure_sqlite_path(db_url)

    sync_url = _to_sync_url(db_url)
    logger.info("Creating sync engine for DB init...")
    engine = create_engine(sync_url)

    if reset:
        logger.warning("Dropping all tables...")
        ormar_config.metadata.drop_all(engine)

    logger.info("Creating tables...")
    ormar_config.metadata.create_all(engine)
    engine.dispose()
    logger.info("Database init finished successfully.")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize database tables.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop all existing tables before creating (destructive).",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm destructive actions when using --reset.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    if args.reset and not args.yes:
        raise SystemExit("Refusing to reset DB without --yes.")
    init_db_tables(reset=args.reset)
