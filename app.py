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
    return "Hello from Filmavault!"
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
if __name__ == "__main__":
    app.run(debug=True)