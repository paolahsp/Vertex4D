# database.py - SQLite database setup
import sqlite3
from datetime import datetime
import hashlib
import os

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
            FOREIGN KEY (team_id) REFERENCES teams (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

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
                "INSERT INTO team_members (team_id, name, email) VALUES (?, ?, ?)",
                (team_id, member['name'], member['email'])
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
        
        # Find team member by email
        cursor.execute("SELECT team_id FROM team_members WHERE email = ?", (email,))
        member = cursor.fetchone()
        
        if not member:
            conn.close()
            return (False, "Email not found", None)
        
        team_id = member['team_id']
        
        # Verify password
        cursor.execute("SELECT id, team_name, password_hash, challenge_desc, photo_url FROM teams WHERE id = ?", (team_id,))
        team = cursor.fetchone()
        
        password_hash = hash_password(password)
        if team['password_hash'] != password_hash:
            conn.close()
            return (False, "Incorrect password", None)
        
        # Get all team members
        cursor.execute("SELECT name, email FROM team_members WHERE team_id = ?", (team_id,))
        members = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        team_data = {
            'team_id': team['id'],
            'team_name': team['team_name'],
            'challenge_desc': team['challenge_desc'],
            'photo_url': team['photo_url'],
            'members': members
        }
        
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
            
        cursor.execute("SELECT name, email FROM team_members WHERE team_id = ?", (team_id,))
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
            cursor.execute("SELECT name, email FROM team_members WHERE team_id = ?", (team['id'],))
            team['members'] = [dict(row) for row in cursor.fetchall()]
            teams.append(team)
        
        conn.close()
        return teams
    
    except Exception as e:
        print(f"Error getting teams: {e}")
        return []

# Initialize database when module is imported
if not os.path.exists(DATABASE_PATH):
    init_database()
    print("Database initialized")
