# database.py - SQLite database setup
import sqlite3
from datetime import datetime
import hashlib
import os
import json
import uuid

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
    cursor.execute("PRAGMA table_info(runs)")
    run_columns = {row[1] for row in cursor.fetchall()}
    run_migrations = {
        "case_title": "ALTER TABLE runs ADD COLUMN case_title TEXT",
        "mode": "ALTER TABLE runs ADD COLUMN mode TEXT NOT NULL DEFAULT 'solo'",
        "cohort_id": "ALTER TABLE runs ADD COLUMN cohort_id TEXT",
        "deadline": "ALTER TABLE runs ADD COLUMN deadline TEXT",
        "baseline_locked_at": "ALTER TABLE runs ADD COLUMN baseline_locked_at TIMESTAMP",
        "completed_at": "ALTER TABLE runs ADD COLUMN completed_at TIMESTAMP",
    }
    for column, statement in run_migrations.items():
        if column not in run_columns:
            cursor.execute(statement)

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS decision_baselines (
            run_id TEXT PRIMARY KEY,
            team_id INTEGER NOT NULL,
            payload_json TEXT NOT NULL,
            locked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (run_id) REFERENCES runs (run_id),
            FOREIGN KEY (team_id) REFERENCES teams (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cohorts (
            cohort_id TEXT PRIMARY KEY,
            cohort_name TEXT NOT NULL,
            institution_name TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT,
            status TEXT NOT NULL DEFAULT 'planned',
            owner_team_id INTEGER NOT NULL,
            owner_email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_team_id) REFERENCES teams (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cohort_memberships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cohort_id TEXT NOT NULL,
            team_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cohort_id) REFERENCES cohorts (cohort_id),
            FOREIGN KEY (team_id) REFERENCES teams (id),
            UNIQUE (cohort_id, team_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS case_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            team_id INTEGER NOT NULL,
            author_email TEXT,
            author_role TEXT NOT NULL,
            artifact_type TEXT,
            comment_text TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            FOREIGN KEY (run_id) REFERENCES runs (run_id),
            FOREIGN KEY (team_id) REFERENCES teams (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS decision_quality_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            reviewer_email TEXT,
            score_stage TEXT NOT NULL,
            framing INTEGER NOT NULL,
            system_awareness INTEGER NOT NULL,
            evidence_quality INTEGER NOT NULL,
            behavioral_logic INTEGER NOT NULL,
            economic_coherence INTEGER NOT NULL,
            decision_action INTEGER NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (run_id) REFERENCES runs (run_id)
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


def create_run(
    run_id: str,
    team_id: int,
    title: str,
    stage: str = "project_record",
    status: str = "active",
    mode: str = "solo",
    cohort_id: str | None = None,
    deadline: str | None = None,
) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO runs (run_id, team_id, title, case_title, stage, status, mode, cohort_id, deadline)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (run_id, team_id, title, title, stage, status, mode, cohort_id, deadline),
    )
    if cohort_id:
        cursor.execute(
            """
            INSERT OR IGNORE INTO cohort_memberships (cohort_id, team_id)
            VALUES (?, ?)
            """,
            (cohort_id, team_id),
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


def get_run_any(run_id: str) -> dict | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT runs.*, teams.team_name
        FROM runs
        JOIN teams ON teams.id = runs.team_id
        WHERE runs.run_id = ?
        """,
        (run_id,),
    )
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
            SELECT runs.*, teams.team_name, cohorts.cohort_name, cohorts.institution_name
            FROM runs
            JOIN teams ON teams.id = runs.team_id
            LEFT JOIN cohorts ON cohorts.cohort_id = runs.cohort_id
            ORDER BY runs.created_at DESC
            """
        )
    else:
        cursor.execute(
            """
            SELECT runs.*, teams.team_name, cohorts.cohort_name, cohorts.institution_name
            FROM runs
            JOIN teams ON teams.id = runs.team_id
            LEFT JOIN cohorts ON cohorts.cohort_id = runs.cohort_id
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


def list_runs_for_cohort(cohort_id: str) -> list[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT runs.*, teams.team_name
        FROM runs
        JOIN teams ON teams.id = runs.team_id
        WHERE runs.cohort_id = ?
        ORDER BY runs.created_at DESC
        """,
        (cohort_id,),
    )
    runs = [dict(row) for row in cursor.fetchall()]
    for run in runs:
        cursor.execute("SELECT artifact_type, artifact_id, status, updated_at FROM run_artifacts WHERE run_id = ?", (run["run_id"],))
        run["artifacts"] = {row["artifact_type"]: dict(row) for row in cursor.fetchall()}
    conn.close()
    return runs


def lock_decision_baseline(run_id: str, team_id: int, baseline: dict) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT run_id FROM decision_baselines WHERE run_id = ?", (run_id,))
    if cursor.fetchone():
        conn.close()
        raise ValueError("Decision Snapshot is already locked for this Decision Case.")
    locked_at = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    cursor.execute(
        """
        INSERT INTO decision_baselines (run_id, team_id, payload_json, locked_at)
        VALUES (?, ?, ?, ?)
        """,
        (run_id, team_id, json_dumps(baseline), locked_at),
    )
    cursor.execute("UPDATE runs SET baseline_locked_at = ? WHERE run_id = ?", (locked_at, run_id))
    conn.commit()
    conn.close()
    result = dict(baseline)
    result["locked_at"] = locked_at
    return result


def get_decision_baseline(run_id: str) -> dict | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT payload_json, locked_at FROM decision_baselines WHERE run_id = ?", (run_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    try:
        baseline = json.loads(row["payload_json"] or "{}")
    except json.JSONDecodeError:
        baseline = {"unparseable": True}
    baseline["locked_at"] = row["locked_at"]
    return baseline


def mark_run_completed(run_id: str) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE runs SET completed_at = COALESCE(completed_at, CURRENT_TIMESTAMP), status = 'complete' WHERE run_id = ?", (run_id,))
    conn.commit()
    conn.close()


def create_cohort(payload: dict, owner_team_id: int, owner_email: str | None) -> dict:
    cohort_id = f"cohort_{uuid.uuid4().hex[:10]}"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO cohorts (cohort_id, cohort_name, institution_name, start_date, end_date, status, owner_team_id, owner_email)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            cohort_id,
            str(payload.get("cohort_name") or payload.get("name") or "").strip(),
            str(payload.get("institution_name") or "").strip(),
            str(payload.get("start_date") or "").strip() or None,
            str(payload.get("end_date") or "").strip() or None,
            str(payload.get("status") or "planned").strip().lower(),
            owner_team_id,
            owner_email,
        ),
    )
    conn.commit()
    conn.close()
    return get_cohort(cohort_id)


def get_cohort(cohort_id: str) -> dict | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cohorts WHERE cohort_id = ?", (cohort_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    cohort = dict(row)
    cursor.execute(
        """
        SELECT cohort_memberships.team_id, teams.team_name
        FROM cohort_memberships
        JOIN teams ON teams.id = cohort_memberships.team_id
        WHERE cohort_memberships.cohort_id = ?
        ORDER BY teams.team_name
        """,
        (cohort_id,),
    )
    cohort["members"] = [dict(member) for member in cursor.fetchall()]
    conn.close()
    return cohort


def list_cohorts_for_user(team_id: int, include_all: bool = False) -> list[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    if include_all:
        cursor.execute("SELECT * FROM cohorts ORDER BY created_at DESC")
    else:
        cursor.execute(
            """
            SELECT DISTINCT cohorts.*
            FROM cohorts
            JOIN cohort_memberships ON cohort_memberships.cohort_id = cohorts.cohort_id
            WHERE cohort_memberships.team_id = ?
            ORDER BY cohorts.created_at DESC
            """,
            (team_id,),
        )
    cohorts = [dict(row) for row in cursor.fetchall()]
    for cohort in cohorts:
        cursor.execute("SELECT COUNT(*) AS count FROM cohort_memberships WHERE cohort_id = ?", (cohort["cohort_id"],))
        cohort["member_count"] = int(cursor.fetchone()["count"] or 0)
        cursor.execute("SELECT COUNT(*) AS count FROM runs WHERE cohort_id = ?", (cohort["cohort_id"],))
        cohort["case_count"] = int(cursor.fetchone()["count"] or 0)
    conn.close()
    return cohorts


def add_cohort_member(cohort_id: str, team_id: int) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO cohort_memberships (cohort_id, team_id) VALUES (?, ?)", (cohort_id, team_id))
    conn.commit()
    conn.close()
    return get_cohort(cohort_id)


def team_in_cohort(cohort_id: str, team_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM cohort_memberships WHERE cohort_id = ? AND team_id = ?", (cohort_id, team_id))
    found = cursor.fetchone() is not None
    conn.close()
    return found


def add_case_comment(run_id: str, team_id: int, author_email: str | None, author_role: str, artifact_type: str | None, comment_text: str) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO case_comments (run_id, team_id, author_email, author_role, artifact_type, comment_text)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (run_id, team_id, author_email, author_role, artifact_type, comment_text),
    )
    comment_id = cursor.lastrowid
    conn.commit()
    cursor.execute("SELECT * FROM case_comments WHERE id = ?", (comment_id,))
    comment = dict(cursor.fetchone())
    conn.close()
    return comment


def list_case_comments(run_id: str) -> list[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM case_comments WHERE run_id = ? ORDER BY created_at DESC", (run_id,))
    comments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return comments


def open_comment_counts(run_ids: list[str]) -> dict[str, int]:
    if not run_ids:
        return {}
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholders = ",".join("?" for _ in run_ids)
    cursor.execute(
        f"SELECT run_id, COUNT(*) AS count FROM case_comments WHERE status = 'open' AND run_id IN ({placeholders}) GROUP BY run_id",
        run_ids,
    )
    counts = {run_id: 0 for run_id in run_ids}
    for row in cursor.fetchall():
        counts[row["run_id"]] = int(row["count"] or 0)
    conn.close()
    return counts


def add_decision_quality_score(run_id: str, reviewer_email: str | None, score_stage: str, scores: dict, notes: str | None) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO decision_quality_scores (
            run_id, reviewer_email, score_stage, framing, system_awareness, evidence_quality,
            behavioral_logic, economic_coherence, decision_action, notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            reviewer_email,
            score_stage,
            scores["framing"],
            scores["system_awareness"],
            scores["evidence_quality"],
            scores["behavioral_logic"],
            scores["economic_coherence"],
            scores["decision_action"],
            notes,
        ),
    )
    score_id = cursor.lastrowid
    conn.commit()
    cursor.execute("SELECT * FROM decision_quality_scores WHERE id = ?", (score_id,))
    score = dict(cursor.fetchone())
    conn.close()
    return score


def list_decision_quality_scores(run_ids: list[str]) -> dict[str, list[dict]]:
    if not run_ids:
        return {}
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholders = ",".join("?" for _ in run_ids)
    cursor.execute(
        f"SELECT * FROM decision_quality_scores WHERE run_id IN ({placeholders}) ORDER BY created_at ASC",
        run_ids,
    )
    grouped = {run_id: [] for run_id in run_ids}
    for row in cursor.fetchall():
        grouped.setdefault(row["run_id"], []).append(dict(row))
    conn.close()
    return grouped


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
