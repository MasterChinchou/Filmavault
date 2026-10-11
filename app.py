from flask import Flask, render_template
import sqlite3
app = Flask(__name__)
def get_connection():
    conn = sqlite3.connect("Filmavault.db")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn
@app.route("/")
def home():
    return render_template("home.html")
@app.route("/films")
def films():
    conn = get_connection()
    film_list = conn.execute("""
        SELECT f.film_name, f.genre, d.director_name
        FROM Film f
        JOIN Director d ON f.director_id = d.director_id
        ORDER BY f.film_name
    """).fetchall()
    conn.close()
    return render_template("films.html", films=film_list)
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
if __name__ == "__main__":
    app.run(debug=True)