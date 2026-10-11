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
if __name__ == "__main__":
    app.run(debug=True)