
"""
SQLite MCP server for lecture 10 in the course Ethical Hacking.

The database contains fictional employee records.
"""

import sqlite3
from pathlib import Path

from mcp.server.mcpserver import MCPServer

# Database stored alongside this script
DB_PATH = Path(__file__).parent / "employees.db"

# Create MCP server (SDK v2)
mcp = MCPServer("SQLite Employee Database")


def get_connection():
    """Create a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """Create and populate the database if it does not exist."""

    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                email TEXT NOT NULL,
                salary INTEGER NOT NULL
            )
        """)

        count = conn.execute(
            "SELECT COUNT(*) FROM employees"
        ).fetchone()[0]

        if count == 0:
            employees = [
                ("Alice Jensen", "IT", "alice@example.com", 52000),
                ("Bob Hansen", "HR", "bob@example.com", 45000),
                ("Charlie Nielsen", "IT", "charlie@example.com", 61000),
                ("Diana Larsen", "Finance", "diana@example.com", 58000),
                ("Erik Petersen", "Management", "erik@example.com", 85000),
            ]

            conn.executemany("""
                INSERT INTO employees
                (name, department, email, salary)
                VALUES (?, ?, ?, ?)
            """, employees)


# --------------------------------------------------
# MCP TOOLS
# --------------------------------------------------

@mcp.tool()
def list_employees() -> list[dict]:
    """List all employees in the database."""

    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, department, email FROM employees"
        ).fetchall()

        return [dict(row) for row in rows]


@mcp.tool()
def search_employees(query: str) -> list[dict]:
    """
    Search employees by name or department.
    Uses parameterized SQL queries.
    """

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, name, department, email
            FROM employees
            WHERE name LIKE ? OR department LIKE ?
        """, (f"%{query}%", f"%{query}%")).fetchall()

        return [dict(row) for row in rows]


@mcp.tool()
def get_employee(employee_id: int) -> dict | None:
    """Get employee details, including salary, by employee ID."""

    with get_connection() as conn:
        row = conn.execute("""
            SELECT * FROM employees WHERE id = ?
        """, (employee_id,)).fetchone()

        return dict(row) if row else None


# --------------------------------------------------
# INTENTIONALLY VULNERABLE TOOL
# --------------------------------------------------

@mcp.tool()
def unsafe_search_employees(query: str) -> list[dict]:
    """
    Search employees using dynamically constructed SQL.
    """

    sql = f"""
        SELECT id, name, department, email
        FROM employees
        WHERE name LIKE '%{query}%'
        OR department LIKE '%{query}%'
    """

    with get_connection() as conn:
        rows = conn.execute(sql).fetchall()

        return [dict(row) for row in rows]


# --------------------------------------------------
# MCP RESOURCE
# --------------------------------------------------

@mcp.resource("database://employees/schema")
def get_database_schema() -> str:
    """Return information about the employee database."""

    return """
    Table: employees

    Columns:
    - id: INTEGER, primary key
    - name: TEXT
    - department: TEXT
    - email: TEXT
    - salary: INTEGER
    """


# --------------------------------------------------
# START SERVER
# --------------------------------------------------

if __name__ == "__main__":
    initialize_database()
    mcp.run(transport="streamable-http")
