from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    user = request.form['user']
    password = request.form['password']

    conn = sqlite3.connect('users.db')

    # SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE username='{user}' AND password='{password}'"

    result = conn.execute(query).fetchone()

    if result:
        return "Login successful"

    return "Invalid credentials"