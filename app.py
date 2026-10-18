#Bring in the Flask tools: Flask (builds the app), render_template (shows an HTML page),
#request (reads what the user sent), redirect (sends the user to another page).
import sqlite3
from flask import Flask, render_template, request, redirect
#Create the web application. __name__ tells Flask where it is
#From here on, "app" is the website.
app = Flask(__name__)
#Reusable thing that opens a database connection set up the way we want it. Called at the start
#of every route instead of repeating lines each time.
def get_connection():
    """Create and configure a SQLite database connection."""
    #opens the database file
    conn = sqlite3.connect("Filmavault.db")
    #make SQLite enforce and use foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    #let us read columns by name, e.g. row of "film_name"
    conn.row_factory = sqlite3.Row
    #hand the connection back to the caller
    return conn
#Home page (dashboard with live totals=stat cards)
#runs when someone visits the main address "/"
@app.route("/")
def home():
    conn = get_connection()
    #counts all rows in a table. fetchone() grabs the single result row and [0] takes the
    #first (only) value out of it.
    film_count = conn.execute("SELECT COUNT(*) FROM Film").fetchone()[0]
    cinema_count = conn.execute("SELECT COUNT(*) FROM Cinema").fetchone()[0]
    ticket_count = conn.execute("SELECT COUNT(*) FROM Ticket").fetchone()[0]
    #always close the connection when done
    conn.close()
    #Shows home.html and pass the three counts so the page can display them.
    return render_template("home.html",
        film_count=film_count,
        cinema_count=cinema_count,
        ticket_count=ticket_count)
#Films list (with search)
@app.route("/films")
def films():
    conn = get_connection()
    #Read the search term "q" from the URL (e.g. /films?q=action).
    #If it is not there, use "" instead. .strip() trims spaces.
    search = request.args.get("q", "").strip()
    if search:
        #Join Film to Director to get the director's name, and only keep films whose
        #name OR genre contains the search text. The ? marks are filled safely by the
        #values in the tuple below, which prevents SQL injection. The % are wildcards
        #meaning "any characters", so the match is partial.
        film_list = conn.execute("""
            SELECT f.film_id, f.film_name, f.genre, d.director_name
            FROM Film f
            JOIN Director d ON f.director_id = d.director_id
            WHERE f.film_name LIKE ? OR f.genre LIKE ?
            ORDER BY f.film_name
        """, (
            "%" + search + "%",
            "%" + search + "%",
        )).fetchall()
    #if no search then show every film
    else:
        film_list = conn.execute("""
            SELECT f.film_id, f.film_name, f.genre, d.director_name
            FROM Film f
            JOIN Director d ON f.director_id = d.director_id
            ORDER BY f.film_name
        """).fetchall()
    conn.close()
    #Pass the films and the search term this makes the box keeps what was typed.
    return render_template("films.html", films=film_list, search=search)
#Screenings list
@app.route("/screenings")
def screenings():
    conn = get_connection()
    #Joins Screening to Film (for the title) and to Cinema (for the city).
    screening_list = conn.execute("""
         SELECT f.film_name, c.city, s.session_time
        FROM Screening s
        JOIN Film f   ON s.film_id = f.film_id
        JOIN Cinema c ON s.cinema_id = c.cinema_id
        ORDER BY f.film_name
    """).fetchall()
    conn.close()
    return render_template("screenings.html", screenings=screening_list)
# Cinemas list
@app.route("/cinemas")
def cinemas():
    conn = get_connection()
    # Simplest query: one table, no join.
    cinema_list = conn.execute("""
        SELECT cinema_id, city
        FROM Cinema
        ORDER BY city
    """).fetchall()
    conn.close()
    return render_template("cinemas.html", cinemas=cinema_list)
# Bookings list (with search)
@app.route("/bookings")
def bookings():
    conn = get_connection()
    # read the search term from the URL
    search = request.args.get("q", "").strip()
    if search:
        # Five-table join: a Ticket links to its Viewer, its Screening, and from that screening to the Film and Cinema. This turns the stored IDs into readable names. Search matches first name, last name, the full name joined together (|| joins text), or film.
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
        # if no search: show every booking
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
#About page (static, no database)
@app.route("/about")
def about():
    return render_template("about.html")
# Add a film (CREATE)
# Accepts GET (show the form) and POST (submit the form).
@app.route("/add_film", methods=["GET", "POST"])
def add_film():
    conn = get_connection()
    # Get the director list for the dropdown. Fetched at the top so it is ready whether the page is being shown or submitted.
    directors = conn.execute("SELECT director_id, director_name FROM Director ORDER BY director_name").fetchall()
    # the form was submitted
    if request.method == "POST":
        # Reads each box the user filled in .strip() trims spaces.
        film_id = request.form["film_id"].strip()
        film_name = request.form["film_name"].strip()
        genre = request.form["genre"].strip()
        director_id = request.form["director_id"]
        # Validation: if any required field is empty, re-show the form with a message instead of saving bad data.
        if not film_id or not film_name or not genre:
            conn.close()
            return render_template("add_film.html", directors=directors,
                error="All fields are required. Please fill in every box.")
        # try the insert, catch the error if the ID already exists.
        try:
            conn.execute(
                "INSERT INTO Film (film_id, film_name, genre, director_id) VALUES (?, ?, ?, ?)",
                (film_id, film_name, genre, director_id)
            )
            conn.commit()
            # save the new row to the database
            conn.close()
            # go back to the films list
            return redirect("/films")
        # the film_id already exists (duplicate key)
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("add_film.html", directors=directors,
                error="That Film ID already exists. Please use a different ID.")
    # GET: just show the blank form with the director dropdown.
    conn.close()
    return render_template("add_film.html", directors=directors)
# Edit a film (UPDATE)
# <film_id> is a variable part of the URL, like /edit_film/F007.
@app.route("/edit_film/<film_id>", methods=["GET", "POST"])
def edit_film(film_id):
    conn = get_connection()
    # Fetch the one film being edited (so the form can be pre-filled) and the director list for the dropdown.
    film = conn.execute("SELECT * FROM Film WHERE film_id = ?", (film_id,)).fetchone()
    directors = conn.execute("SELECT director_id, director_name FROM Director ORDER BY director_name").fetchall()
    # for when the user saved changes
    if request.method == "POST":
        film_name = request.form["film_name"].strip()
        genre = request.form["genre"].strip()
        director_id = request.form["director_id"]
        # Validation: block empty name or genre.
        if not film_name or not genre:
            conn.close()
            return render_template("edit_film.html", film=film, directors=directors,
                error="All fields are required. Please fill in every box.")
        # Update only the row whose film_id matches. The WHERE is vital because without it, every film would be overwritten.
        conn.execute(
            "UPDATE Film SET film_name = ?, genre = ?, director_id = ? WHERE film_id = ?",
            (film_name, genre, director_id, film_id)
        )
        conn.commit()
        conn.close()
        return redirect("/films")
    # GET: show the edit form pre-filled with this film's details.
    conn.close()
    return render_template("edit_film.html", film=film, directors=directors, error=None)
# Delete a film (DELETE)
@app.route("/delete_film/<film_id>", methods=["GET", "POST"])
def delete_film(film_id):
    conn = get_connection()
    # Fetch the film so the confirmation page can show its name.
    film = conn.execute("SELECT * FROM Film WHERE film_id = ?", (film_id,)).fetchone()
    # for when the user confirms the delete
    if request.method == "POST":
        try:
            conn.execute("DELETE FROM Film WHERE film_id = ?", (film_id,))
            conn.commit()
            conn.close()
            return redirect("/films")
        # blocked: screenings still depend on this film
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("delete_film.html", film=film,
                error="This film can't be deleted:it still has screenings linked to it.")
    # GET: show the "Are you sure?" confirmation page.
    conn.close()
    return render_template("delete_film.html", film=film, error=None)
#Most popular films
@app.route("/popular")
def popular():
    conn = get_connection()
    # Count how many tickets each film has. GROUP BY bundles all of one film's tickets together so COUNT counts per film; ORDER BY ... DESC puts the most popular first.
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
# For ustom 404 (page not found) handler runs whenever a request has no matching route. This hows our own 404 page and still returns the correct 404 status code.
@app.errorhandler(404)
def page_not_found(_error):
    return render_template("404.html"), 404
# Start the web server only when this file is run directly. debug=True shows detailed errors and auto-reloads on save (useful while building; turn it off for a real public site).
if __name__ == "__main__":
    app.run(debug=True)