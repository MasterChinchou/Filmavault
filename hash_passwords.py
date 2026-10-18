# tool for talking to the SQLite database
import sqlite3
# hashing functions live here (SHA-256 is one of them)
import hashlib
# operating-system tools; we use it to make random bytes
import os 
# one plain demo password given every account
demo_password = "FilmaVault123"
# open a connection to the database file
conn = sqlite3.connect("Filmavault.db")
cursor = conn.cursor()
 # a cursor runs SQL commands and holds the results
# asks for the id of every row in the viewer table
cursor.execute("select viewer_id from viewer")
# pull all those rows back as a list
viewers = cursor.fetchall()
#repeat the indented block once per viewer
for viewer in viewers:
# take the first (only) value in the row = this viewer's id
    viewer_id = viewer[0]
    salt = os.urandom(8).hex()
# make 8 random bytes, turn them into text = a unique "salt"
    digest = hashlib.sha256((salt + demo_password).encode()).hexdigest()
# stick salt+password together, turn to bytes (.encode()),
# run SHA-256 on it, then express the result as hex text
    password_hash = f"{salt}:{digest}"
# keep the salt and the hash together as "salt:hash"
    cursor.execute("update viewer set password_hash = ? where viewer_id = ?", (password_hash, viewer_id))
 # save that value into this viewer's row (? filled safely)

conn.commit()
# write all the changes permanently to the database file
conn.close()
# close the connection
print("all viewer passwords have been hashed, salted and updated in the database.")
# confirmation