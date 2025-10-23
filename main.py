import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for, flash, g
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.secret_key = 'my_secret_club_system_key_2025'

DATABASE = 'club_system.db'


def get_db_connection():
    """Establishes a connection to the SQLite database."""

    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_connection(exception):
    """Closes the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    """Renders the main page (Login/Register Forms) or redirects to dashboard if logged in."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    """Handles new member registration (CRUD: CREATE Member)."""
    fullname = request.form['fullname']
    email = request.form['new_email']
    password = request.form['new_password']
    hashed_pw = generate_password_hash(password)

    db = get_db_connection()
    try:
        # Check if user already exists
        user = db.execute("SELECT id FROM member WHERE email = ?", (email,)).fetchone()

        if user:
            flash("Email already registered. Please log in.", "warning")
            return redirect(url_for('index'))
        else:
            # Create users - default role is 'student'
            db.execute(
                "INSERT INTO member (fullname, email, password, role) VALUES (?, ?, ?, ?)",
                (fullname, email, hashed_pw, 'student')
            )
            db.commit()
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for('index'))

    except sqlite3.Error as e:
        flash(f"A database error occurred during registration: {e}", "danger")
        return redirect(url_for('index'))


@app.route('/login', methods=['POST'])
def login():
    """Handles member login and session setup."""
    email = request.form['email']
    password = request.form['password']

    db = get_db_connection()
    user = db.execute("SELECT * FROM member WHERE email = ?", (email,)).fetchone()

    if user and check_password_hash(user['password'], password):
        # Set session data
        session['user_id'] = user['id']
        session['user_name'] = user['fullname']
        session['user_role'] = user['role']
        flash(f"Welcome, {user['fullname']}! You are logged in as a {user['role']}.", "success")
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid email or password.", "danger")
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    """Clears the session and logs the user out."""
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_role', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))


# --- Club Management Routes (CRUD: Club) ---

@app.route('/dashboard')
def dashboard():
    """
    Main authenticated page. Displays member info and all clubs (CRUD: READ Club).
    Also includes the CREATE Club form.
    """
    if 'user_id' not in session:
        flash("Please log in to view the dashboard.", "warning")
        return redirect(url_for('index'))

    db = get_db_connection()
    # Read all clubs
    clubs = db.execute(
        "SELECT c.*, m.fullname as officer_name FROM club c JOIN member m ON c.officer_id = m.id ORDER BY c.name"
    ).fetchall()

    return render_template('dashboard.html',
                           clubs=clubs,
                           current_user_id=session.get('user_id'),
                           current_user_name=session.get('user_name'),
                           current_user_role=session.get('user_role'))


@app.route('/create_club', methods=['POST'])
def create_club():
    """Handles creating a new club (CRUD: CREATE Club)."""
    if 'user_id' not in session:
        flash("You must be logged in to create a club.", "danger")
        return redirect(url_for('index'))

    name = request.form['club_name']
    description = request.form['club_description']
    officer_id = session['user_id']
    officer_name = session['user_name']

    if not name or not description:
        flash("Club name and description are required.", "warning")
        return redirect(url_for('dashboard'))

    db = get_db_connection()
    try:
        db.execute(
            "INSERT INTO club (name, description, officer_id, created_by_name) VALUES (?, ?, ?, ?)",
            (name, description, officer_id, officer_name)
        )
        db.commit()
        flash(f"Club '{name}' created successfully!", "success")
    except sqlite3.IntegrityError:
        flash(f"Error: A club named '{name}' already exists.", "danger")
    except sqlite3.Error as e:
        flash(f"A database error occurred: {e}", "danger")

    return redirect(url_for('dashboard'))


@app.route('/edit_club/<int:club_id>', methods=['POST'])
def edit_club(club_id):
    """Handles updating a club's details (CRUD: UPDATE Club)."""
    if 'user_id' not in session:
        flash("Unauthorized.", "danger")
        return redirect(url_for('index'))

    db = get_db_connection()
    club = db.execute("SELECT * FROM club WHERE id = ?", (club_id,)).fetchone()

    # Security check: only the officer who created it can edit it.
    if club and club['officer_id'] == session['user_id']:
        try:
            name = request.form.get('club_name')
            description = request.form.get('club_description')

            db.execute(
                "UPDATE club SET name = ?, description = ? WHERE id = ?",
                (name, description, club_id)
            )
            db.commit()
            flash(f"Club '{name}' updated successfully.", "success")
        except sqlite3.Error as e:
            flash(f"Error updating club: {e}", "danger")
    else:
        flash("You are not authorized to edit this club.", "danger")

    return redirect(url_for('dashboard'))


@app.route('/delete_club/<int:club_id>')
def delete_club(club_id):
    """Handles deleting a club (CRUD: DELETE Club)."""
    if 'user_id' not in session:
        flash("Unauthorized.", "danger")
        return redirect(url_for('index'))

    db = get_db_connection()
    club = db.execute("SELECT * FROM club WHERE id = ?", (club_id,)).fetchone()

    # Security check: only the officer who created it can delete it.
    if club and club['officer_id'] == session['user_id']:
        try:
            db.execute("DELETE FROM club WHERE id = ?", (club_id,))
            db.commit()
            flash(f"Club '{club['name']}' successfully deleted (DELETE).", "success")
        except sqlite3.Error as e:
            flash(f"Error deleting club: {e}", "danger")
    else:
        flash("You are not authorized to delete this club.", "danger")

    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
