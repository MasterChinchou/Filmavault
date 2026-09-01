import sqlite3
import hashlib
import os 
demo_password = "FilmaVault123"
conn = sqlite3.connect("Filmavault.db")
cursor = conn.cursor()
cursor.execute("select viewer_id from viewer")
viewers=cursor.fetchall()
for viewer in viewers:
    viewer_id = viewer[0]
    salt = os.urandom(8).hex()
    digest = hashlib.sha256((salt + demo_password).encode()).hexdigest()
    password_hash = f"{salt}:{digest}"
    cursor.execute("update viewer set password_hash = ? where viewer_id = ?", (password_hash, viewer_id))
conn.commit()
conn.close()
print("all viewer passwords have been hashed, salted and updated in the database.")

