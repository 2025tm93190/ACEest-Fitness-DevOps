import os
import sqlite3
from pathlib import Path
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash, g, abort

BASE_DIR = Path(__file__).resolve().parent

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "change-this-development-key"),
        DATABASE=os.environ.get("DATABASE_PATH", str(Path(app.instance_path) / "aceest.sqlite")),
    )
    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    def get_db():
        if "db" not in g:
            db_path = app.config["DATABASE"]
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            g.db = sqlite3.connect(db_path)
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
        return g.db

    @app.teardown_appcontext
    def close_db(exception=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def init_db():
        db = get_db()
        db.executescript("""
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT DEFAULT '',
                goal TEXT NOT NULL DEFAULT 'General Fitness',
                program TEXT NOT NULL DEFAULT 'Strength',
                joined_on TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER NOT NULL,
                workout TEXT NOT NULL,
                duration INTEGER NOT NULL,
                calories INTEGER NOT NULL DEFAULT 0,
                workout_date TEXT NOT NULL,
                notes TEXT DEFAULT '',
                FOREIGN KEY(member_id) REFERENCES members(id) ON DELETE CASCADE
            );
        """)
        db.commit()

    with app.app_context():
        init_db()

    def member_or_404(member_id):
        member = get_db().execute("SELECT * FROM members WHERE id = ?", (member_id,)).fetchone()
        if member is None:
            abort(404)
        return member

    @app.route("/")
    def index():
        db = get_db()
        stats = {
            "members": db.execute("SELECT COUNT(*) FROM members").fetchone()[0],
            "workouts": db.execute("SELECT COUNT(*) FROM workouts").fetchone()[0],
            "minutes": db.execute("SELECT COALESCE(SUM(duration), 0) FROM workouts").fetchone()[0],
            "calories": db.execute("SELECT COALESCE(SUM(calories), 0) FROM workouts").fetchone()[0],
        }
        recent_workouts = db.execute("""
            SELECT workouts.*, members.name AS member_name
            FROM workouts JOIN members ON members.id = workouts.member_id
            ORDER BY workout_date DESC, workouts.id DESC LIMIT 5
        """).fetchall()
        members = db.execute("SELECT * FROM members ORDER BY id DESC LIMIT 5").fetchall()
        return render_template("index.html", stats=stats, recent_workouts=recent_workouts, members=members)

    @app.route("/health")
    def health():
        return {"status": "healthy"}, 200

    @app.route("/members")
    def members():
        q = request.args.get("q", "").strip()
        db = get_db()
        if q:
            rows = db.execute(
                "SELECT * FROM members WHERE name LIKE ? OR email LIKE ? ORDER BY name",
                (f"%{q}%", f"%{q}%")
            ).fetchall()
        else:
            rows = db.execute("SELECT * FROM members ORDER BY id DESC").fetchall()
        return render_template("members.html", members=rows, q=q)

    @app.route("/members/new", methods=["GET", "POST"])
    def new_member():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            phone = request.form.get("phone", "").strip()
            goal = request.form.get("goal", "General Fitness").strip()
            program = request.form.get("program", "Strength").strip()
            if not name or not email:
                flash("Name and email are required.", "error")
                return render_template("member_form.html", member=request.form, page_title="Add member")
            try:
                db = get_db()
                db.execute(
                    "INSERT INTO members (name,email,phone,goal,program,joined_on) VALUES (?,?,?,?,?,?)",
                    (name, email, phone, goal, program, date.today().isoformat())
                )
                db.commit()
            except sqlite3.IntegrityError:
                flash("That email address is already registered.", "error")
                return render_template("member_form.html", member=request.form, page_title="Add member")
            flash("Member added successfully.", "success")
            return redirect(url_for("members"))
        return render_template("member_form.html", member={}, page_title="Add member")

    @app.route("/members/<int:member_id>")
    def member_detail(member_id):
        member = member_or_404(member_id)
        workouts = get_db().execute(
            "SELECT * FROM workouts WHERE member_id = ? ORDER BY workout_date DESC, id DESC",
            (member_id,)
        ).fetchall()
        totals = get_db().execute(
            "SELECT COUNT(*) AS count, COALESCE(SUM(duration),0) AS minutes, COALESCE(SUM(calories),0) AS calories FROM workouts WHERE member_id = ?",
            (member_id,)
        ).fetchone()
        return render_template("member_detail.html", member=member, workouts=workouts, totals=totals)

    @app.route("/members/<int:member_id>/edit", methods=["GET", "POST"])
    def edit_member(member_id):
        member = member_or_404(member_id)
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            phone = request.form.get("phone", "").strip()
            goal = request.form.get("goal", "General Fitness").strip()
            program = request.form.get("program", "Strength").strip()
            if not name or not email:
                flash("Name and email are required.", "error")
                return render_template("member_form.html", member=request.form, page_title="Edit member")
            try:
                db = get_db()
                db.execute(
                    "UPDATE members SET name=?, email=?, phone=?, goal=?, program=? WHERE id=?",
                    (name, email, phone, goal, program, member_id)
                )
                db.commit()
            except sqlite3.IntegrityError:
                flash("That email address is already registered to another member.", "error")
                return render_template("member_form.html", member=request.form, page_title="Edit member")
            flash("Member details updated.", "success")
            return redirect(url_for("member_detail", member_id=member_id))
        return render_template("member_form.html", member=member, page_title="Edit member")

    @app.route("/members/<int:member_id>/delete", methods=["POST"])
    def delete_member(member_id):
        member_or_404(member_id)
        db = get_db()
        db.execute("DELETE FROM members WHERE id=?", (member_id,))
        db.commit()
        flash("Member and associated workout records deleted.", "success")
        return redirect(url_for("members"))

    @app.route("/workouts", methods=["GET", "POST"])
    def workouts():
        db = get_db()
        if request.method == "POST":
            try:
                member_id = int(request.form.get("member_id", ""))
                duration = int(request.form.get("duration", ""))
                calories = int(request.form.get("calories", "0") or 0)
            except ValueError:
                flash("Please enter valid numbers for member, duration, and calories.", "error")
                return redirect(url_for("workouts"))
            workout = request.form.get("workout", "").strip()
            workout_date = request.form.get("workout_date", date.today().isoformat())
            notes = request.form.get("notes", "").strip()
            if not workout or duration < 1 or calories < 0:
                flash("Workout name is required, duration must be positive, and calories cannot be negative.", "error")
                return redirect(url_for("workouts"))
            exists = db.execute("SELECT id FROM members WHERE id=?", (member_id,)).fetchone()
            if not exists:
                flash("Select a valid member first.", "error")
                return redirect(url_for("workouts"))
            db.execute(
                "INSERT INTO workouts (member_id,workout,duration,calories,workout_date,notes) VALUES (?,?,?,?,?,?)",
                (member_id, workout, duration, calories, workout_date, notes)
            )
            db.commit()
            flash("Workout logged successfully.", "success")
            return redirect(url_for("workouts"))
        member_rows = db.execute("SELECT id,name FROM members ORDER BY name").fetchall()
        rows = db.execute("""
            SELECT workouts.*, members.name AS member_name
            FROM workouts JOIN members ON members.id = workouts.member_id
            ORDER BY workout_date DESC, workouts.id DESC
        """).fetchall()
        return render_template("workouts.html", members=member_rows, workouts=rows, today=date.today().isoformat())

    @app.route("/calculator", methods=["GET", "POST"])
    def calculator():
        result = None
        values = {}
        if request.method == "POST":
            try:
                age = int(request.form.get("age", ""))
                weight = float(request.form.get("weight", ""))
                height = float(request.form.get("height", ""))
                activity = float(request.form.get("activity", "1.2"))
                sex = request.form.get("sex", "female")
                if not (13 <= age <= 100 and 25 <= weight <= 350 and 100 <= height <= 250):
                    raise ValueError
                # Mifflin-St Jeor estimate; activity multiplier estimates maintenance calories.
                bmr = 10 * weight + 6.25 * height - 5 * age + (5 if sex == "male" else -161)
                maintenance = round(bmr * activity)
                result = {"bmr": round(bmr), "maintenance": maintenance,
                          "gentle_loss": round(maintenance * 0.90),
                          "gain": round(maintenance * 1.10)}
                values = request.form
            except (ValueError, TypeError):
                flash("Enter valid values. Age must be 13–100, weight 25–350 kg, and height 100–250 cm.", "error")
                values = request.form
        return render_template("calculator.html", result=result, values=values)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=os.environ.get("FLASK_DEBUG") == "1")
