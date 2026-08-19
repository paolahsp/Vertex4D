# database.py - SQLite database setup
import sqlite3
from datetime import datetime
import hashlib
import os
import json

DATABASE_PATH = os.getenv("VERTEX4D_DATABASE_PATH", "vertex4d.db")

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database with teams table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Teams table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            challenge_desc TEXT,
            photo_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Team members table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL DEFAULT 'founder',
            FOREIGN KEY (team_id) REFERENCES teams (id)
        )
    ''')
    cursor.execute("PRAGMA table_info(team_members)")
    team_member_columns = {row[1] for row in cursor.fetchall()}
    if 'role' not in team_member_columns:
        cursor.execute("ALTER TABLE team_members ADD COLUMN role TEXT NOT NULL DEFAULT 'founder'")
    
    
    # Golden Path runs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            team_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            stage TEXT NOT NULL DEFAULT 'project_record',
            status TEXT NOT NULL DEFAULT 'active',
            FOREIGN KEY (team_id) REFERENCES teams (id)
        )
    ''')

    # One current artifact per type per run
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS run_artifacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            artifact_type TEXT NOT NULL,
            artifact_id TEXT NOT NULL,
            path TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (run_id) REFERENCES runs (run_id),
            UNIQUE (run_id, artifact_type)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            run_id TEXT,
            module TEXT NOT NULL,
            tokens INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES teams (id),
            FOREIGN KEY (run_id) REFERENCES runs (run_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            team_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES teams (id),
            FOREIGN KEY (run_id) REFERENCES runs (run_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_prefs (
            email TEXT PRIMARY KEY,
            theme TEXT NOT NULL DEFAULT 'dark',
            motion TEXT NOT NULL DEFAULT 'full',
            focus TEXT NOT NULL DEFAULT 'off',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

VALID_MEMBER_ROLES = {"founder", "facilitator", "admin"}


VALID_PREFS = {
    "theme": {"dark", "light"},
    "motion": {"full", "reduced", "none"},
    "focus": {"on", "off"},
}
DEFAULT_PREFS = {"theme": "dark", "motion": "full", "focus": "off"}


def normalize_user_prefs(prefs: dict | None) -> dict:
    normalized = dict(DEFAULT_PREFS)
    if isinstance(prefs, dict):
        for key, allowed in VALID_PREFS.items():
            value = str(prefs.get(key) or "").strip().lower()
            if value in allowed:
                normalized[key] = value
    return normalized


def get_user_prefs(email: str | None) -> dict:
    if not email:
        return dict(DEFAULT_PREFS)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT theme, motion, focus FROM user_prefs WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return dict(DEFAULT_PREFS)
    return normalize_user_prefs(dict(row))


def upsert_user_prefs(email: str, prefs: dict) -> dict:
    normalized = normalize_user_prefs(prefs)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO user_prefs (email, theme, motion, focus)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET
            theme = excluded.theme,
            motion = excluded.motion,
            focus = excluded.focus,
            updated_at = CURRENT_TIMESTAMP
        ''',
        (email, normalized["theme"], normalized["motion"], normalized["focus"]),
    )
    conn.commit()
    conn.close()
    return normalized


def normalize_member_role(role: str | None) -> str:
    value = str(role or "founder").strip().lower()
    return value if value in VALID_MEMBER_ROLES else "founder"


def login_data_for_email(email: str) -> dict | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT team_id, role, name, email FROM team_members WHERE email = ?", (email,))
    member = cursor.fetchone()
    if not member:
        conn.close()
        return None
    team_id = member["team_id"]
    cursor.execute("SELECT id, team_name, challenge_desc, photo_url FROM teams WHERE id = ?", (team_id,))
    team = cursor.fetchone()
    if not team:
        conn.close()
        return None
    cursor.execute("SELECT name, email, role FROM team_members WHERE team_id = ?", (team_id,))
    members = [dict(row) for row in cursor.fetchall()]
    conn.close()
    member_email = member["email"] if "email" in member.keys() else None
    return {
        "team_id": team["id"],
        "team_name": team["team_name"],
        "challenge_desc": team["challenge_desc"],
        "photo_url": team["photo_url"],
        "role": normalize_member_role(member["role"] if "role" in member.keys() else "founder"),
        "member_name": member["name"] if "name" in member.keys() else None,
        "member_email": member_email,
        "prefs": get_user_prefs(member_email),
        "members": members,
    }

def create_team(team_name: str, password: str, members: list, challenge_desc: str = None, photo_url: str = None) -> tuple:
    """
    Create a new team with members
    members: list of dicts with 'name' and 'email' keys
    Returns: (success: bool, message: str, team_id: int or None)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if team name already exists
        cursor.execute("SELECT id FROM teams WHERE team_name = ?", (team_name,))
        if cursor.fetchone():
            conn.close()
            return (False, "Team name already exists", None)
        
        # Check if any email already exists
        for member in members:
            cursor.execute("SELECT id FROM team_members WHERE email = ?", (member['email'],))
            if cursor.fetchone():
                conn.close()
                return (False, f"Email {member['email']} already registered", None)
        
        # Create team
        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO teams (team_name, password_hash, challenge_desc, photo_url) VALUES (?, ?, ?, ?)",
            (team_name, password_hash, challenge_desc, photo_url)
        )
        team_id = cursor.lastrowid
        
        # Add members
        for member in members:
            cursor.execute(
                "INSERT INTO team_members (team_id, name, email, role) VALUES (?, ?, ?, ?)",
                (team_id, member['name'], member['email'], normalize_member_role(member.get('role')))
            )
        
        conn.commit()
        conn.close()
        return (True, "Team created successfully", team_id)
    
    except Exception as e:
        return (False, f"Error: {str(e)}", None)

def verify_login(email: str, password: str) -> tuple:
    """
    Verify login credentials
    Returns: (success: bool, message: str, team_data: dict or None)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT team_id FROM team_members WHERE email = ?", (email,))
        member = cursor.fetchone()
        if not member:
            conn.close()
            return (False, "Email not found", None)
        cursor.execute("SELECT password_hash FROM teams WHERE id = ?", (member["team_id"],))
        team = cursor.fetchone()
        if not team or team["password_hash"] != hash_password(password):
            conn.close()
            return (False, "Incorrect password", None)
        conn.close()
        team_data = login_data_for_email(email)
        if not team_data:
            return (False, "Team not found", None)
        return (True, "Client Login successful", team_data)
    except Exception as e:
        return (False, f"Error: {str(e)}", None)

def get_team_by_id(team_id: int) -> dict:
    """
    Get team data by ID
    Returns: team_data dict or None
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, team_name, challenge_desc, photo_url FROM teams WHERE id = ?", (team_id,))
        team = cursor.fetchone()
        
        if not team:
            conn.close()
            return None
            
        cursor.execute("SELECT name, email, role FROM team_members WHERE team_id = ?", (team_id,))
        members = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'team_id': team['id'],
            'team_name': team['team_name'],
            'challenge_desc': team['challenge_desc'],
            'photo_url': team['photo_url'],
            'members': members
        }
    except Exception:
        return None

def get_all_teams():
    """Get all teams for display in The Orbit"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, team_name, created_at FROM teams")
        teams = []
        
        for team_row in cursor.fetchall():
            team = dict(team_row)
            
            # Get members for this team
            cursor.execute("SELECT name, email, role FROM team_members WHERE team_id = ?", (team['id'],))
            team['members'] = [dict(row) for row in cursor.fetchall()]
            teams.append(team)
        
        conn.close()
        return teams
    
    except Exception as e:
        print(f"Error getting teams: {e}")
        return []

# Initialize database when module is imported
init_database()


def create_run(run_id: str, team_id: int, title: str, stage: str = "project_record", status: str = "active") -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO runs (run_id, team_id, title, stage, status) VALUES (?, ?, ?, ?, ?)",
        (run_id, team_id, title, stage, status),
    )
    conn.commit()
    conn.close()
    return get_run(run_id, team_id)


def get_run(run_id: str, team_id: int) -> dict | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM runs WHERE run_id = ? AND team_id = ?", (run_id, team_id))
    run = cursor.fetchone()
    if not run:
        conn.close()
        return None
    cursor.execute("SELECT artifact_type, artifact_id, path, status, created_at, updated_at FROM run_artifacts WHERE run_id = ?", (run_id,))
    artifacts = {row["artifact_type"]: dict(row) for row in cursor.fetchall()}
    result = dict(run)
    result["artifacts"] = artifacts
    conn.close()
    return result


def list_runs(team_id: int) -> list[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM runs WHERE team_id = ? ORDER BY created_at DESC", (team_id,))
    runs = [dict(row) for row in cursor.fetchall()]
    for run in runs:
        cursor.execute("SELECT artifact_type, artifact_id, status, updated_at FROM run_artifacts WHERE run_id = ?", (run["run_id"],))
        run["artifacts"] = {row["artifact_type"]: dict(row) for row in cursor.fetchall()}
    conn.close()
    return runs


def list_runs_for_facilitator(team_id: int, include_all: bool = False) -> list[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    if include_all:
        cursor.execute(
            """
            SELECT runs.*, teams.team_name
            FROM runs
            JOIN teams ON teams.id = runs.team_id
            ORDER BY runs.created_at DESC
            """
        )
    else:
        cursor.execute(
            """
            SELECT runs.*, teams.team_name
            FROM runs
            JOIN teams ON teams.id = runs.team_id
            WHERE runs.team_id = ?
            ORDER BY runs.created_at DESC
            """,
            (team_id,),
        )
    runs = [dict(row) for row in cursor.fetchall()]
    for run in runs:
        cursor.execute("SELECT artifact_type, artifact_id, status, updated_at FROM run_artifacts WHERE run_id = ?", (run["run_id"],))
        run["artifacts"] = {row["artifact_type"]: dict(row) for row in cursor.fetchall()}
    conn.close()
    return runs


def list_events_for_runs(run_ids: list[str]) -> dict[str, list[dict]]:
    if not run_ids:
        return {}
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholders = ",".join("?" for _ in run_ids)
    cursor.execute(
        f"SELECT run_id, event_type, payload_json, created_at FROM events WHERE run_id IN ({placeholders}) ORDER BY created_at ASC",
        run_ids,
    )
    grouped = {run_id: [] for run_id in run_ids}
    for row in cursor.fetchall():
        payload = {}
        try:
            payload = json.loads(row["payload_json"] or "{}")
        except json.JSONDecodeError:
            payload = {"unparseable": True}
        grouped.setdefault(row["run_id"], []).append({
            "event_type": row["event_type"],
            "payload": payload,
            "created_at": row["created_at"],
        })
    conn.close()
    return grouped


def get_ai_usage_by_runs(run_ids: list[str]) -> dict[str, dict]:
    if not run_ids:
        return {}
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholders = ",".join("?" for _ in run_ids)
    cursor.execute(
        f"""
        SELECT run_id, COUNT(*) AS calls, COALESCE(SUM(tokens), 0) AS tokens
        FROM ai_usage
        WHERE run_id IN ({placeholders})
        GROUP BY run_id
        """,
        run_ids,
    )
    usage = {run_id: {"calls": 0, "tokens": 0} for run_id in run_ids}
    for row in cursor.fetchall():
        usage[row["run_id"]] = {"calls": int(row["calls"] or 0), "tokens": int(row["tokens"] or 0)}
    conn.close()
    return usage


def upsert_run_artifact(run_id: str, artifact_type: str, artifact_id: str, path: str, status: str) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO run_artifacts (run_id, artifact_type, artifact_id, path, status)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(run_id, artifact_type) DO UPDATE SET
            artifact_id = excluded.artifact_id,
            path = excluded.path,
            status = excluded.status,
            updated_at = CURRENT_TIMESTAMP
        ''',
        (run_id, artifact_type, artifact_id, path, status),
    )
    stage_order = ["project_record", "problem_frame", "system_map", "predictive_hypothesis", "financial_scenario", "decision_record"]
    if artifact_type in stage_order:
        cursor.execute("UPDATE runs SET stage = ? WHERE run_id = ?", (artifact_type, run_id))
    conn.commit()
    conn.close()


def record_event(team_id: int, event_type: str, payload: dict, run_id: str | None = None) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO events (run_id, team_id, event_type, payload_json) VALUES (?, ?, ?, ?)",
        (run_id, team_id, event_type, json_dumps(payload)),
    )
    conn.commit()
    conn.close()


def record_ai_usage(team_id: int, module: str, tokens: int = 0, run_id: str | None = None) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO ai_usage (team_id, run_id, module, tokens) VALUES (?, ?, ?, ?)",
        (team_id, run_id, module, tokens),
    )
    conn.commit()
    conn.close()


def get_ai_usage_summary(team_id: int, run_id: str | None = None) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    if run_id:
        cursor.execute("SELECT COUNT(*) AS calls, COALESCE(SUM(tokens), 0) AS tokens FROM ai_usage WHERE team_id = ? AND run_id = ?", (team_id, run_id))
    else:
        cursor.execute("SELECT COUNT(*) AS calls, COALESCE(SUM(tokens), 0) AS tokens FROM ai_usage WHERE team_id = ?", (team_id,))
    row = cursor.fetchone()
    conn.close()
    return {"calls": int(row["calls"] or 0), "tokens": int(row["tokens"] or 0)}


def json_dumps(payload: dict) -> str:
    import json
    return json.dumps(payload, sort_keys=True)
