from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"


# ================= DATABASE CONNECTION FUNCTION =================
def get_db():
    return mysql.connector.connect(
        host=os.environ.get("MYSQLHOST"),
        user=os.environ.get("MYSQLUSER"),
        password=os.environ.get("MYSQLPASSWORD"),
        database=os.environ.get("MYSQLDATABASE"),
        port=int(os.environ.get("MYSQLPORT", 3306))
    )


@app.route('/')
def home():
    return redirect(url_for('login'))


# ================= USER REGISTER =================
@app.route('/register', methods=['GET', 'POST'])
def register():
    db = get_db()
    cursor = db.cursor(buffered=True)

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            cursor.close()
            db.close()
            return "Email already registered"

        cursor.execute(
            "INSERT INTO users (name,email,password) VALUES (%s,%s,%s)",
            (name, email, password)
        )
        db.commit()

        cursor.close()
        db.close()
        return redirect(url_for('login'))

    cursor.close()
    db.close()
    return render_template('register.html')


# ================= LOGIN =================
@app.route('/login', methods=['GET', 'POST'])
def login():
    db = get_db()
    cursor = db.cursor(buffered=True)

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )

        user = cursor.fetchone()

        if user:
            session['user'] = email
            cursor.close()
            db.close()
            return redirect(url_for('events'))
        else:
            cursor.close()
            db.close()
            return render_template("invalid_login.html")

    cursor.close()
    db.close()
    return render_template('login.html')


# ================= EVENTS PAGE =================
@app.route('/events')
def events():
    if 'user' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor(buffered=True)

    cursor.execute("SELECT * FROM events")
    all_events = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('events.html', events=all_events)


# ================= EVENT REGISTRATION =================
@app.route('/register_event/<int:event_id>', methods=['GET', 'POST'])
def register_event(event_id):

    if 'user' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor(buffered=True)

    cursor.execute("SELECT * FROM events WHERE id=%s", (event_id,))
    event = cursor.fetchone()

    if not event:
        cursor.close()
        db.close()
        return "Event not found"

    if request.method == 'POST':
        name = request.form.get('name')
        college = request.form.get('college')
        phone = request.form.get('phone')
        email = session['user']

        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if not user:
            cursor.close()
            db.close()
            return "User not found"

        user_id = user[0]

        cursor.execute(
            "SELECT id FROM registrations WHERE event_id=%s AND email=%s",
            (event_id, email)
        )

        if cursor.fetchone():
            cursor.close()
            db.close()
            return render_template("already_registered.html", event=event)

        cursor.execute("""
            INSERT INTO registrations (event_id, user_id, name, college, phone, email)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (event_id, user_id, name, college, phone, email))

        db.commit()

        cursor.close()
        db.close()

        return render_template("success.html", event=event)

    cursor.close()
    db.close()
    return render_template('event_register.html', event=event)


# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run()