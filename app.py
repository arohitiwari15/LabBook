
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = "labbook-project-secret-key"
DATABASE = "bookings.db"

LABS = [
    "Computer Laboratory 1",
    "Computer Laboratory 2",
    "Electronics Laboratory",
    "Physics Laboratory",
    "Chemistry Laboratory"
]

SLOTS = [
    "09:00-10:00",
    "10:00-11:00",
    "11:00-12:00",
    "12:00-13:00",
    "14:00-15:00",
    "15:00-16:00"
]


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                lab TEXT NOT NULL,
                booking_date TEXT NOT NULL,
                slot TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Confirmed',
                UNIQUE(lab, booking_date, slot)
            )
        """)


@app.route("/")
def home():
    with get_db() as conn:
        total_bookings = conn.execute(
            "SELECT COUNT(*) FROM bookings"
        ).fetchone()[0]

        upcoming_count = conn.execute(
            "SELECT COUNT(*) FROM bookings WHERE booking_date >= ?",
            (date.today().isoformat(),)
        ).fetchone()[0]

        recent_bookings = conn.execute("""
            SELECT * FROM bookings
            WHERE booking_date >= ?
            ORDER BY booking_date, slot
            LIMIT 4
        """, (date.today().isoformat(),)).fetchall()

    return render_template(
        "index.html",
        labs=LABS,
        total_labs=len(LABS),
        total_bookings=total_bookings,
        upcoming_bookings=upcoming_count,
        recent_bookings=recent_bookings
    )


@app.route("/labs")
def laboratories():
    return render_template("labs.html", labs=LABS)


@app.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        lab = request.form.get("lab", "")
        booking_date = request.form.get("date", "")
        slot = request.form.get("slot", "")

        if not name or not email or lab not in LABS or slot not in SLOTS:
            flash("Please enter valid booking details.", "error")
            return redirect(url_for("book"))

        if booking_date < date.today().isoformat():
            flash("Please select today or a future date.", "error")
            return redirect(url_for("book"))

        try:
            with get_db() as conn:
                conn.execute("""
                    INSERT INTO bookings
                    (name, email, lab, booking_date, slot)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, email, lab, booking_date, slot))

            flash("Your laboratory booking was confirmed!", "success")
            return redirect(url_for("bookings"))

        except sqlite3.IntegrityError:
            flash(
                "That laboratory is already booked for this date and time.",
                "error"
            )

    return render_template(
        "book.html",
        labs=LABS,
        slots=SLOTS,
        today=date.today().isoformat()
    )


@app.route("/bookings")
def bookings():
    with get_db() as conn:
        records = conn.execute("""
            SELECT * FROM bookings
            ORDER BY booking_date DESC, slot
        """).fetchall()

    return render_template("bookings.html", bookings=records)


@app.route("/admin")
def admin():
    with get_db() as conn:
        total_bookings = conn.execute(
            "SELECT COUNT(*) FROM bookings"
        ).fetchone()[0]

        upcoming = conn.execute("""
            SELECT * FROM bookings
            WHERE booking_date >= ?
            ORDER BY booking_date, slot
        """, (date.today().isoformat(),)).fetchall()

    return render_template(
        "admin.html",
        total_bookings=total_bookings,
        total_labs=len(LABS),
        upcoming_bookings=upcoming
    )


init_db()

if __name__ == "__main__":
    app.run(debug=False)