from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------- MYSQL CONNECTION ----------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Hariharan@123",
    database="event_db",
    auth_plugin='mysql_native_password'
)

cursor = db.cursor(buffered=True)


@app.route('/')
def home():
    return redirect(url_for('login'))


# ================= USER REGISTER =================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            return "Email already registered"

        cursor.execute(
            "INSERT INTO users (name,email,password) VALUES (%s,%s,%s)",
            (name, email, password)
        )
        db.commit()
        return redirect(url_for('login'))

    return render_template('register.html')


# ================= LOGIN (UPDATED WITH UI) =================
@app.route('/login', methods=['GET', 'POST'])
def login():
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
            return redirect(url_for('events'))
        else:
            return render_template("invalid_login.html")

    return render_template('login.html')


# ================= EVENTS PAGE =================
@app.route('/events')
def events():
    if 'user' not in session:
        return redirect(url_for('login'))

    cursor.execute("SELECT * FROM events")
    all_events = cursor.fetchall()
    return render_template('events.html', events=all_events)


# ================= EVENT REGISTRATION =================
@app.route('/register_event/<int:event_id>', methods=['GET', 'POST'])
def register_event(event_id):

    if 'user' not in session:
        return redirect(url_for('login'))

    cursor.execute("SELECT * FROM events WHERE id=%s", (event_id,))
    event = cursor.fetchone()

    if not event:
        return "Event not found"

    if request.method == 'POST':
        name = request.form.get('name')
        college = request.form.get('college')
        phone = request.form.get('phone')
        email = session['user']

        # Duplicate check
        cursor.execute(
            "SELECT id FROM registrations WHERE event_id=%s AND email=%s",
            (event_id, email)
        )

        if cursor.fetchone():
            return render_template("already_registered.html", event=event)

        cursor.execute("""
            INSERT INTO registrations (event_id, name, college, phone, email)
            VALUES (%s, %s, %s, %s, %s)
        """, (event_id, name, college, phone, email))

        db.commit()

        return render_template("success.html", event=event)

    return render_template('event_register.html', event=event)


# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run()