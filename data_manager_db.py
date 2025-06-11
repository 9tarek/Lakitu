import aiosqlite
import asyncio
from pathlib import Path
from config import BASE_DIR

# Path to SQLite database file
DB_PATH = BASE_DIR / "times.db"

# Ensure only one connection and thread safety
_db_lock = asyncio.Lock()

async def init_db():
    """
    Initialize the database: create tables if they do not exist.
    """
    async with _db_lock:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS times (
                  track       TEXT NOT NULL,
                  mode        TEXT NOT NULL,
                  user_id     TEXT NOT NULL,
                  time_str    TEXT NOT NULL,
                  PRIMARY KEY (track, mode, user_id)
                );
                """
            )
            await db.execute(
                "CREATE INDEX IF NOT EXISTS idx_track_mode ON times(track, mode);"
            )
            await db.commit()

async def get_times(track: str, mode: str) -> list[tuple[str, str]]:
    """
    Fetch all (user_id, time_str) for given track and mode, sorted by parsed milliseconds.
    """
    async with _db_lock:
        async with aiosqlite.connect(DB_PATH) as db:
            # parse minutes:seconds.milliseconds into integer for ordering
            cursor = await db.execute(
                """
                SELECT user_id, time_str
                FROM times
                WHERE track = ? AND mode = ?
                ORDER BY (
                    CAST(substr(time_str, 1, instr(time_str, ':')-1) AS INTEGER) * 60000
                    + CAST(substr(time_str, instr(time_str, ':')+1, 2) AS INTEGER) * 1000
                    + CAST(substr(time_str, instr(time_str, '.')+1) AS INTEGER)
                ) ASC;
                """, (track, mode)
            )
            rows = await cursor.fetchall()
            await cursor.close()
            return rows

async def save_time(track: str, mode: str, user_id: str, time_str: str):
    """
    Insert or update a user's time for a given track and mode.
    """
    async with _db_lock:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                """
                INSERT INTO times (track, mode, user_id, time_str)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(track, mode, user_id)
                DO UPDATE SET time_str = excluded.time_str;
                """, (track, mode, user_id, time_str)
            )
            await db.commit()

async def delete_time(track: str, mode: str, user_id: str):
    """
    Delete a single user's time entry for a track and mode.
    """
    async with _db_lock:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "DELETE FROM times WHERE track = ? AND mode = ? AND user_id = ?;",
                (track, mode, user_id)
            )
            await db.commit()

async def delete_all_user_times(user_id: str):
    """
    Delete all time entries for a given user across all tracks and modes.
    """
    async with _db_lock:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "DELETE FROM times WHERE user_id = ?;",
                (user_id,)
            )
            await db.commit()
