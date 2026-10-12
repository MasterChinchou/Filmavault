from flask import Flask, render_template, request, redirect
import sqlite3
app = Flask(__name__)
def get_connection():
    conn = sqlite3.connect("Filmavault.db")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn
@app.route("/")
def home():
    conn = get_connection()
    film_count = conn.execute("SELECT COUNT(*) FROM Film").fetchone()[0]
    cinema_count = conn.execute("SELECT COUNT(*) FROM Cinema").fetchone()[0]
    ticket_count = conn.execute("SELECT COUNT(*) FROM Ticket").fetchone()[0]
    conn.close()
    return render_template("home.html",
        film_count=film_count,
        cinema_count=cinema_count,
        ticket_count=ticket_count)
@app.route("/films")
def films():
    conn = get_connection()
    search = request.args.get("q", "").strip()
    if search:
        film_list = conn.execute("""
            SELECT f.film_id, f.film_name, f.genre, d.director_name
            FROM Film f
            JOIN Director d ON f.director_id = d.director_id
            WHERE f.film_name LIKE ? OR f.genre LIKE ?
            ORDER BY f.film_name
        """, ('%' + search + '%', '%' + search + '%')).fetchall()
    else:
        film_list = conn.execute("""
            SELECT f.film_id, f.film_name, f.genre, d.director_name
            FROM Film f
            JOIN Director d ON f.director_id = d.director_id
            ORDER BY f.film_name
        """).fetchall()
    conn.close()
    return render_template("films.html", films=film_list, search=search)
@app.route("/screenings")
def screenings():
    conn = get_connection()
    screening_list = conn.execute("""
         SELECT f.film_name, c.city, s.session_time
        FROM Screening s
        JOIN Film f   ON s.film_id = f.film_id
        JOIN Cinema c ON s.cinema_id = c.cinema_id
        ORDER BY f.film_name
    """).fetchall()
    conn.close()
    return render_template("screenings.html", screenings=screening_list)
@app.route("/cinemas")
def cinemas():
    conn = get_connection()
    cinema_list = conn.execute("""
        SELECT cinema_id, city
        FROM Cinema
        ORDER BY city
    """).fetchall()
    conn.close()
    return render_template("cinemas.html", cinemas=cinema_list)
@app.route("/bookings")
def bookings():
    conn = get_connection()
    search = request.args.get("q", "").strip()
    if search:
        booking_list = conn.execute("""
            SELECT t.ticket_no, v.first_name, v.last_name,
                   f.film_name, c.city, s.session_time, t.seat_no
            FROM Ticket t
            JOIN Viewer v    ON t.viewer_id = v.viewer_id
            JOIN Screening s ON t.screening_id = s.screening_id
            JOIN Film f      ON s.film_id = f.film_id
            JOIN Cinema c    ON s.cinema_id = c.cinema_id
            WHERE v.first_name LIKE ?
               OR v.last_name LIKE ?
               OR (v.first_name || ' ' || v.last_name) LIKE ?
               OR f.film_name LIKE ?
            ORDER BY v.last_name
        """, ('%' + search + '%', '%' + search + '%', '%' + search + '%', '%' + search + '%')).fetchall()
    else:
        booking_list = conn.execute("""
            SELECT t.ticket_no, v.first_name, v.last_name,
                   f.film_name, c.city, s.session_time, t.seat_no
            FROM Ticket t
            JOIN Viewer v    ON t.viewer_id = v.viewer_id
            JOIN Screening s ON t.screening_id = s.screening_id
            JOIN Film f      ON s.film_id = f.film_id
            JOIN Cinema c    ON s.cinema_id = c.cinema_id
            ORDER BY v.last_name
        """).fetchall()
    conn.close()
    return render_template("bookings.html", bookings=booking_list, search=search)
@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/add_film", methods=["GET", "POST"])
def add_film():
    conn = get_connection()
    directors = conn.execute("SELECT director_id, director_name FROM Director ORDER BY director_name").fetchall()
    if request.method == "POST":
        film_id = request.form["film_id"].strip()
        film_name = request.form["film_name"].strip()
        genre = request.form["genre"].strip()
        director_id = request.form["director_id"]
        if not film_id or not film_name or not genre:
            conn.close()
            return render_template("add_film.html", directors=directors,
                error="All fields are required. Please fill in every box.")
        try:
            conn.execute(
                "INSERT INTO Film (film_id, film_name, genre, director_id) VALUES (?, ?, ?, ?)",
                (film_id, film_name, genre, director_id)
            )
            conn.commit()
            conn.close()
            return redirect("/films")
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("add_film.html", directors=directors,
                error="That Film ID already exists. Please use a different ID.")
    conn.close()
    return render_template("add_film.html", directors=directors)
@app.route("/edit_film/<film_id>", methods=["GET", "POST"])
def edit_film(film_id):
    conn = get_connection()
    film = conn.execute("SELECT * FROM Film WHERE film_id = ?", (film_id,)).fetchone()
    directors = conn.execute("SELECT director_id, director_name FROM Director ORDER BY director_name").fetchall()
    if request.method == "POST":
        film_name = request.form["film_name"].strip()
        genre = request.form["genre"].strip()
        director_id = request.form["director_id"]
        if not film_name or not genre:
            conn.close()
            return render_template("edit_film.html", film=film, directors=directors,
                error="All fields are required. Please fill in every box.")
        conn.execute(
            "UPDATE Film SET film_name = ?, genre = ?, director_id = ? WHERE film_id = ?",
            (film_name, genre, director_id, film_id)
        )
        conn.commit()
        conn.close()
        return redirect("/films")

    conn.close()
    return render_template("edit_film.html", film=film, directors=directors, error=None)
@app.route("/delete_film/<film_id>", methods=["GET", "POST"])
def delete_film(film_id):
    conn = get_connection()
    film = conn.execute("SELECT * FROM Film WHERE film_id = ?", (film_id,)).fetchone()
    if request.method == "POST":
        try:
            conn.execute("DELETE FROM Film WHERE film_id = ?", (film_id,))
            conn.commit()
            conn.close()
            return redirect("/films")
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("delete_film.html", film=film,
                error="This film can't be deleted — it still has screenings linked to it.")
    conn.close()
    return render_template("delete_film.html", film=film, error=None)
@app.route("/popular")
def popular():
    conn = get_connection()
    popular_list = conn.execute("""
        SELECT f.film_name, COUNT(t.ticket_no) AS tickets_sold
        FROM Ticket t
        JOIN Screening s ON t.screening_id = s.screening_id
        JOIN Film f      ON s.film_id      = f.film_id
        GROUP BY f.film_name
        ORDER BY tickets_sold DESC
    """).fetchall()
    conn.close()
    return render_template("popular.html", films=popular_list)
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
if __name__ == "__main__":
    app.run(debug=True)