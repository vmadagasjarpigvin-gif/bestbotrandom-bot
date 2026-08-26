import csv
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from .config import settings


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@contextmanager
def conn():
    db = sqlite3.connect(settings.db_path)
    db.row_factory = sqlite3.Row
    try:
        yield db
        db.commit()
    finally:
        db.close()


def init_db() -> None:
    with conn() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS participants(
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                joined_at TEXT NOT NULL,
                subscribed INTEGER NOT NULL DEFAULT 0,
                is_winner INTEGER NOT NULL DEFAULT 0,
                auto_win_sent_at TEXT,
                referred_by INTEGER,
                referral_count INTEGER NOT NULL DEFAULT 0,
                chances INTEGER NOT NULL DEFAULT 1,
                last_seen_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS broadcasts(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                started_at TEXT,
                finished_at TEXT,
                total INTEGER NOT NULL DEFAULT 0,
                sent INTEGER NOT NULL DEFAULT 0,
                failed INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS settings(
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS runtime_admins(
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                added_at TEXT NOT NULL
            );
            """
        )
        cols = [r[1] for r in db.execute("PRAGMA table_info(participants)").fetchall()]
        if "auto_win_sent_at" not in cols:
            db.execute("ALTER TABLE participants ADD COLUMN auto_win_sent_at TEXT")
        if "referred_by" not in cols:
            db.execute("ALTER TABLE participants ADD COLUMN referred_by INTEGER")
        if "referral_count" not in cols:
            db.execute("ALTER TABLE participants ADD COLUMN referral_count INTEGER NOT NULL DEFAULT 0")
        if "chances" not in cols:
            db.execute("ALTER TABLE participants ADD COLUMN chances INTEGER NOT NULL DEFAULT 1")


def upsert_participant(user_id: int, username: str | None, first_name: str | None, subscribed: bool, referred_by: int | None = None) -> None:
    ts = now_iso()
    if referred_by == user_id:
        referred_by = None
    with conn() as db:
        existing = db.execute("SELECT user_id, referred_by FROM participants WHERE user_id=?", (user_id,)).fetchone()
        db.execute(
            """
            INSERT INTO participants(user_id, username, first_name, joined_at, subscribed, referred_by, last_seen_at)
            VALUES(?,?,?,?,?,?,?)
            ON CONFLICT(user_id) DO UPDATE SET
              username=excluded.username,
              first_name=excluded.first_name,
              subscribed=excluded.subscribed,
              referred_by=COALESCE(participants.referred_by, excluded.referred_by),
              last_seen_at=excluded.last_seen_at
            """,
            (user_id, username or "", first_name or "", ts, int(subscribed), referred_by, ts),
        )
        if subscribed and referred_by and not existing:
            inviter = db.execute("SELECT user_id FROM participants WHERE user_id=?", (referred_by,)).fetchone()
            if inviter:
                db.execute("UPDATE participants SET referral_count=referral_count+1, chances=chances+1 WHERE user_id=?", (referred_by,))


def set_winner(user_id: int, value: bool = True) -> bool:
    with conn() as db:
        cur = db.execute("UPDATE participants SET is_winner=? WHERE user_id=?", (int(value), user_id))
        return cur.rowcount > 0


def stats() -> dict:
    with conn() as db:
        row = db.execute(
            "SELECT COUNT(*) total, SUM(subscribed) subscribed, SUM(is_winner) winners FROM participants"
        ).fetchone()
        return {"total": row["total"] or 0, "subscribed": row["subscribed"] or 0, "winners": row["winners"] or 0}


def participant_ids(only_subscribed: bool = True) -> list[int]:
    q = "SELECT user_id FROM participants"
    params = ()
    if only_subscribed:
        q += " WHERE subscribed=1"
    with conn() as db:
        return [r["user_id"] for r in db.execute(q, params).fetchall()]


def export_csv(path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with conn() as db, path.open("w", newline="", encoding="utf-8-sig") as f:
        rows = db.execute("SELECT * FROM participants ORDER BY joined_at DESC").fetchall()
        writer = csv.writer(f)
        writer.writerow(["user_id", "username", "first_name", "joined_at", "subscribed", "is_winner", "auto_win_sent_at", "referred_by", "referral_count", "chances", "last_seen_at"])
        for r in rows:
            writer.writerow([r[k] for k in r.keys()])
    return path



def mark_auto_win_sent(user_id: int) -> None:
    with conn() as db:
        db.execute("UPDATE participants SET is_winner=1, auto_win_sent_at=? WHERE user_id=?", (now_iso(), user_id))


def auto_win_was_sent(user_id: int) -> bool:
    with conn() as db:
        row = db.execute("SELECT auto_win_sent_at FROM participants WHERE user_id=?", (user_id,)).fetchone()
        return bool(row and row["auto_win_sent_at"])



def add_runtime_admin(user_id: int, username: str | None = None) -> None:
    with conn() as db:
        db.execute(
            "INSERT INTO runtime_admins(user_id, username, added_at) VALUES(?,?,?) ON CONFLICT(user_id) DO UPDATE SET username=excluded.username",
            (user_id, username or "", now_iso()),
        )


def is_runtime_admin(user_id: int) -> bool:
    with conn() as db:
        try:
            row = db.execute("SELECT user_id FROM runtime_admins WHERE user_id=?", (user_id,)).fetchone()
            return bool(row)
        except sqlite3.OperationalError:
            return False



def get_participant(user_id: int) -> dict | None:
    with conn() as db:
        row = db.execute("SELECT * FROM participants WHERE user_id=?", (user_id,)).fetchone()
        return dict(row) if row else None
