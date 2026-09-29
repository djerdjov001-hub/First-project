
from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import platform
import socket
import flask
import os

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash


# =========================================================
# FLASK
# =========================================================

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "fallback-secret-key-change-this"
)


# =========================================================
# DATABASE
# =========================================================

DATABASE = "database.db"


def get_db():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# =========================================================
# INIT DATABASE
# =========================================================

def init_db():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            is_admin INTEGER DEFAULT 0

        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            title TEXT NOT NULL,

            description TEXT NOT NULL,

            category TEXT NOT NULL,

            priority TEXT NOT NULL,

            status TEXT DEFAULT 'Open',

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
            REFERENCES users(id)

        )
    """)

    conn.commit()

    conn.close()


# =========================================================
# ADMIN COLUMN
# =========================================================

def add_admin_column():

    conn = get_db()

    try:

        conn.execute("""
            ALTER TABLE users
            ADD COLUMN is_admin INTEGER DEFAULT 0
        """)

        conn.commit()

    except sqlite3.OperationalError:

        pass

    conn.close()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    if "user_id" in session:

        return redirect("/dashboard")

    return redirect("/login")


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if (
            not username
            or not email
            or not password
            or not confirm_password
        ):

            flash(
                "Sva polja su obavezna.",
                "error"
            )

            return redirect("/register")

        if len(username) < 3:

            flash(
                "Korisničko ime mora imati najmanje 3 karaktera.",
                "error"
            )

            return redirect("/register")

        if "@" not in email or "." not in email:

            flash(
                "Unesite ispravnu email adresu.",
                "error"
            )

            return redirect("/register")

        if len(password) < 8:

            flash(
                "Lozinka mora imati najmanje 8 karaktera.",
                "error"
            )

            return redirect("/register")

        if not any(
            char.isdigit()
            for char in password
        ):

            flash(
                "Lozinka mora sadržati najmanje jedan broj.",
                "error"
            )

            return redirect("/register")

        if password != confirm_password:

            flash(
                "Lozinke se ne poklapaju.",
                "error"
            )

            return redirect("/register")

        conn = get_db()

        try:

            password_hash = generate_password_hash(
                password
            )

            conn.execute("""
                INSERT INTO users
                (
                    username,
                    email,
                    password
                )
                VALUES (?, ?, ?)
            """, (
                username,
                email,
                password_hash
            ))

            conn.commit()

            conn.close()

            flash(
                "Registracija je uspešna! Sada se možete prijaviti.",
                "success"
            )

            return redirect("/login")

        except sqlite3.IntegrityError:

            conn.close()

            flash(
                "Email adresa je već registrovana.",
                "error"
            )

            return redirect("/register")

    return render_template(
        "register.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        conn = get_db()

        user = conn.execute("""
            SELECT *
            FROM users
            WHERE email = ?
        """, (
            email,
        )).fetchone()

        conn.close()

        if user is None:

            flash(
                "Email ili lozinka nisu ispravni.",
                "error"
            )

            return redirect("/login")

        if not check_password_hash(
            user["password"],
            password
        ):

            flash(
                "Email ili lozinka nisu ispravni.",
                "error"
            )

            return redirect("/login")

        session["user_id"] = user["id"]

        session["username"] = user["username"]

        session["is_admin"] = user["is_admin"]

        return redirect("/dashboard")

    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect("/login")

    conn = get_db()

    user_id = session["user_id"]

    total = conn.execute("""
        SELECT COUNT(*)
        FROM tickets
        WHERE user_id = ?
    """, (
        user_id,
    )).fetchone()[0]

    open_tickets = conn.execute("""
        SELECT COUNT(*)
        FROM tickets
        WHERE user_id = ?
        AND status = 'Open'
    """, (
        user_id,
    )).fetchone()[0]

    in_progress = conn.execute("""
        SELECT COUNT(*)
        FROM tickets
        WHERE user_id = ?
        AND status = 'In Progress'
    """, (
        user_id,
    )).fetchone()[0]

    resolved = conn.execute("""
        SELECT COUNT(*)
        FROM tickets
        WHERE user_id = ?
        AND status = 'Resolved'
    """, (
        user_id,
    )).fetchone()[0]

    critical = conn.execute("""
        SELECT COUNT(*)
        FROM tickets
        WHERE user_id = ?
        AND priority = 'Critical'
    """, (
        user_id,
    )).fetchone()[0]

    recent_tickets = conn.execute("""
        SELECT
            id,
            title,
            category,
            priority,
            status,
            created_at
        FROM tickets
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 5
    """, (
        user_id,
    )).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",

        total=total,

        open_tickets=open_tickets,

        in_progress=in_progress,

        resolved=resolved,

        critical=critical,

        recent_tickets=recent_tickets
    )


# =========================================================
# PROFILE
# =========================================================

@app.route("/profile")
def profile():

    if "user_id" not in session:

        return redirect("/login")

    conn = get_db()

    user = conn.execute("""
        SELECT *
        FROM users
        WHERE id = ?
    """, (
        session["user_id"],
    )).fetchone()

    conn.close()

    if user is None:

        session.clear()

        return redirect("/login")

    return render_template(
        "profile.html",
        user=user
    )


# =========================================================
# CHANGE PASSWORD
# =========================================================

@app.route("/change-password", methods=["GET", "POST"])
def change_password():

    if "user_id" not in session:

        return redirect("/login")

    if request.method == "POST":

        old_password = request.form.get(
            "old_password",
            ""
        )

        new_password = request.form.get(
            "new_password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if (
            not old_password
            or not new_password
            or not confirm_password
        ):

            flash(
                "Sva polja su obavezna.",
                "error"
            )

            return redirect("/change-password")

        if len(new_password) < 8:

            flash(
                "Nova lozinka mora imati najmanje 8 karaktera.",
                "error"
            )

            return redirect("/change-password")

        if not any(
            char.isdigit()
            for char in new_password
        ):

            flash(
                "Nova lozinka mora sadržati najmanje jedan broj.",
                "error"
            )

            return redirect("/change-password")

        if new_password != confirm_password:

            flash(
                "Nove lozinke se ne poklapaju.",
                "error"
            )

            return redirect("/change-password")

        conn = get_db()

        user = conn.execute("""
            SELECT *
            FROM users
            WHERE id = ?
        """, (
            session["user_id"],
        )).fetchone()

        if user is None:

            conn.close()

            session.clear()

            return redirect("/login")

        if not check_password_hash(
            user["password"],
            old_password
        ):

            conn.close()

            flash(
                "Stara lozinka nije ispravna.",
                "error"
            )

            return redirect("/change-password")

        new_password_hash = generate_password_hash(
            new_password
        )

        conn.execute("""
            UPDATE users
            SET password = ?
            WHERE id = ?
        """, (
            new_password_hash,
            session["user_id"]
        ))

        conn.commit()

        conn.close()

        flash(
            "Lozinka je uspešno promenjena!",
            "success"
        )

        return redirect("/profile")

    return render_template(
        "change_password.html"
    )


# =========================================================
# CREATE TICKET
# =========================================================

@app.route("/create-ticket", methods=["GET", "POST"])
def create_ticket():

    if "user_id" not in session:

        return redirect("/login")

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        priority = request.form.get(
            "priority",
            ""
        ).strip()

        allowed_categories = [
            "Hardware",
            "Software",
            "Network",
            "Account",
            "Other"
        ]

        allowed_priorities = [
            "Low",
            "Medium",
            "High",
            "Critical"
        ]

        if not title or not description:

            flash(
                "Naslov i opis su obavezni.",
                "error"
            )

            return redirect("/create-ticket")

        if category not in allowed_categories:

            flash(
                "Izabrana kategorija nije ispravna.",
                "error"
            )

            return redirect("/create-ticket")

        if priority not in allowed_priorities:

            flash(
                "Izabrani prioritet nije ispravan.",
                "error"
            )

            return redirect("/create-ticket")

        conn = get_db()

        conn.execute("""
            INSERT INTO tickets
            (
                user_id,
                title,
                description,
                category,
                priority
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            title,
            description,
            category,
            priority
        ))

        conn.commit()

        conn.close()

        flash(
            "Ticket je uspešno kreiran!",
            "success"
        )

        return redirect("/my-tickets")

    return render_template(
        "create_ticket.html"
    )


# =========================================================
# MY TICKETS
# =========================================================

@app.route("/my-tickets")
def my_tickets():

    if "user_id" not in session:

        return redirect("/login")

    conn = get_db()

    tickets = conn.execute("""
        SELECT
            id,
            title,
            description,
            category,
            priority,
            status,
            created_at
        FROM tickets
        WHERE user_id = ?
        ORDER BY id DESC
    """, (
        session["user_id"],
    )).fetchall()

    conn.close()

    return render_template(
        "my_tickets.html",
        tickets=tickets
    )


# =========================================================
# MARK TICKET AS DONE
# =========================================================

@app.route(
    "/ticket/done/<int:ticket_id>",
    methods=["POST"]
)
def ticket_done(ticket_id):

    if "user_id" not in session:

        return redirect("/login")

    conn = get_db()

    ticket = conn.execute("""
        SELECT
            id,
            status
        FROM tickets
        WHERE id = ?
        AND user_id = ?
    """, (
        ticket_id,
        session["user_id"]
    )).fetchone()

    if ticket is None:

        conn.close()

        flash(
            "Ticket ne postoji.",
            "error"
        )

        return redirect("/my-tickets")

    if ticket["status"] == "Closed":

        conn.close()

        flash(
            "Ticket je već zatvoren.",
            "error"
        )

        return redirect("/my-tickets")

    conn.execute("""
        UPDATE tickets
        SET status = 'Closed'
        WHERE id = ?
        AND user_id = ?
    """, (
        ticket_id,
        session["user_id"]
    ))

    conn.commit()

    conn.close()

    flash(
        "Ticket je označen kao urađen.",
        "success"
    )

    return redirect("/my-tickets")


# =========================================================
# ADMIN CHECK
# =========================================================

def is_admin():

    if "user_id" not in session:

        return False

    conn = get_db()

    user = conn.execute("""
        SELECT is_admin
        FROM users
        WHERE id = ?
    """, (
        session["user_id"],
    )).fetchone()

    conn.close()

    if user is None:

        return False

    return user["is_admin"] == 1


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
def admin():

    if not is_admin():

        return "Nemate dozvolu za pristup admin panelu."

    conn = get_db()

    total_users = conn.execute("""
        SELECT COUNT(*)
        FROM users
    """).fetchone()[0]

    total_admins = conn.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE is_admin = 1
    """).fetchone()[0]

    total_tickets = conn.execute("""
        SELECT COUNT(*)
        FROM tickets
    """).fetchone()[0]

    open_tickets = conn.execute("""
        SELECT COUNT(*)
        FROM tickets
        WHERE status = 'Open'
    """).fetchone()[0]

    in_progress = conn.execute("""
        SELECT COUNT(*)
        FROM tickets
        WHERE status = 'In Progress'
    """).fetchone()[0]

    resolved = conn.execute("""
        SELECT COUNT(*)
        FROM tickets
        WHERE status = 'Resolved'
    """).fetchone()[0]

    critical = conn.execute("""
        SELECT COUNT(*)
        FROM tickets
        WHERE priority = 'Critical'
    """).fetchone()[0]

    recent_tickets = conn.execute("""
        SELECT
            tickets.id,
            tickets.title,
            tickets.category,
            tickets.priority,
            tickets.status,
            tickets.created_at,
            users.username
        FROM tickets
        JOIN users
        ON tickets.user_id = users.id
        ORDER BY tickets.id DESC
        LIMIT 8
    """).fetchall()

    conn.close()

    return render_template(
        "admin.html",

        total_users=total_users,

        total_admins=total_admins,

        total_tickets=total_tickets,

        open_tickets=open_tickets,

        in_progress=in_progress,

        resolved=resolved,

        critical=critical,

        recent_tickets=recent_tickets
    )


# =========================================================
# ADMIN DELETE USER
# =========================================================

@app.route(
    "/admin/delete-user/<int:user_id>"
)
def admin_delete_user(user_id):

    if not is_admin():

        return "Nemate dozvolu."

    if user_id == session["user_id"]:

        return "Ne možete obrisati sami sebe."

    conn = get_db()

    user = conn.execute("""
        SELECT *
        FROM users
        WHERE id = ?
    """, (
        user_id,
    )).fetchone()

    if user is None:

        conn.close()

        return "Korisnik ne postoji."

    conn.execute("""
        DELETE FROM tickets
        WHERE user_id = ?
    """, (
        user_id,
    ))

    conn.execute("""
        DELETE FROM users
        WHERE id = ?
    """, (
        user_id,
    ))

    conn.commit()

    conn.close()

    return redirect("/admin")


# =========================================================
# ADMIN TOGGLE ADMIN
# =========================================================

@app.route(
    "/admin/toggle-admin/<int:user_id>"
)
def admin_toggle_admin(user_id):

    if not is_admin():

        return "Nemate dozvolu."

    if user_id == session["user_id"]:

        return "Ne možete promeniti sopstvenu admin dozvolu."

    conn = get_db()

    user = conn.execute("""
        SELECT is_admin
        FROM users
        WHERE id = ?
    """, (
        user_id,
    )).fetchone()

    if user is None:

        conn.close()

        return "Korisnik ne postoji."

    new_status = (
        0
        if user["is_admin"] == 1
        else 1
    )

    conn.execute("""
        UPDATE users
        SET is_admin = ?
        WHERE id = ?
    """, (
        new_status,
        user_id
    ))

    conn.commit()

    conn.close()

    return redirect("/admin")


# =========================================================
# ADMIN EDIT USER
# =========================================================

@app.route(
    "/admin/edit-user/<int:user_id>",
    methods=["GET", "POST"]
)
def admin_edit_user(user_id):

    if not is_admin():

        return "Nemate dozvolu."

    conn = get_db()

    user = conn.execute("""
        SELECT *
        FROM users
        WHERE id = ?
    """, (
        user_id,
    )).fetchone()

    if user is None:

        conn.close()

        return "Korisnik ne postoji."

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        if not username or not email:

            conn.close()

            flash(
                "Korisničko ime i email su obavezni.",
                "error"
            )

            return redirect(
                f"/admin/edit-user/{user_id}"
            )

        try:

            conn.execute("""
                UPDATE users
                SET username = ?,
                    email = ?
                WHERE id = ?
            """, (
                username,
                email,
                user_id
            ))

            conn.commit()

        except sqlite3.IntegrityError:

            conn.close()

            flash(
                "Email adresa je već zauzeta.",
                "error"
            )

            return redirect(
                f"/admin/edit-user/{user_id}"
            )

        conn.close()

        flash(
            "Korisnik je uspešno izmenjen.",
            "success"
        )

        return redirect("/admin")

    conn.close()

    return render_template(
        "edit_user.html",
        user=user
    )


# =========================================================
# ADMIN TICKETS
# =========================================================

@app.route("/admin/tickets")
def admin_tickets():

    if not is_admin():

        return "Nemate dozvolu."

    conn = get_db()

    tickets = conn.execute("""
        SELECT
            tickets.id,
            tickets.title,
            tickets.description,
            tickets.category,
            tickets.priority,
            tickets.status,
            tickets.created_at,
            users.username,
            users.email
        FROM tickets
        JOIN users
        ON tickets.user_id = users.id
        ORDER BY tickets.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "admin_tickets.html",
        tickets=tickets
    )


# =========================================================
# ADMIN CHANGE TICKET STATUS
# =========================================================

@app.route(
    "/admin/tickets/status/<int:ticket_id>",
    methods=["POST"]
)
def admin_ticket_status(ticket_id):

    if not is_admin():

        return "Nemate dozvolu."

    status = request.form.get(
        "status",
        ""
    )

    allowed_statuses = [
        "Open",
        "In Progress",
        "Resolved",
        "Closed"
    ]

    if status not in allowed_statuses:

        return "Status nije ispravan."

    conn = get_db()

    ticket = conn.execute("""
        SELECT id
        FROM tickets
        WHERE id = ?
    """, (
        ticket_id,
    )).fetchone()

    if ticket is None:

        conn.close()

        return "Ticket ne postoji."

    conn.execute("""
        UPDATE tickets
        SET status = ?
        WHERE id = ?
    """, (
        status,
        ticket_id
    ))

    conn.commit()

    conn.close()

    flash(
        "Status ticketa je uspešno promenjen.",
        "success"
    )

    return redirect("/admin/tickets")


# =========================================================
# ADMIN DELETE TICKET
# =========================================================

@app.route(
    "/admin/tickets/delete/<int:ticket_id>"
)
def admin_delete_ticket(ticket_id):

    if not is_admin():

        return "Nemate dozvolu."

    conn = get_db()

    ticket = conn.execute("""
        SELECT id
        FROM tickets
        WHERE id = ?
    """, (
        ticket_id,
    )).fetchone()

    if ticket is None:

        conn.close()

        return "Ticket ne postoji."

    conn.execute("""
        DELETE FROM tickets
        WHERE id = ?
    """, (
        ticket_id,
    ))

    conn.commit()

    conn.close()

    return redirect("/admin/tickets")


# =========================================================
# SYSTEM INFO
# =========================================================

@app.route("/system-info")
def system_info():

    if "user_id" not in session:

        return redirect("/login")

    hostname = socket.gethostname()

    try:

        ip_address = socket.gethostbyname(
            hostname
        )

    except socket.gaierror:

        ip_address = "Nije dostupno"

    operating_system = platform.system()

    operating_system_version = platform.version()

    python_version = platform.python_version()

    flask_version = flask.__version__

    return render_template(
        "system_info.html",

        hostname=hostname,

        ip_address=ip_address,

        operating_system=operating_system,

        operating_system_version=operating_system_version,

        python_version=python_version,

        flask_version=flask_version
    )


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    init_db()

    add_admin_column()

    app.run(
        debug=True
    )

