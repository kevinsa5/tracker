from flask import Flask, request, g
import sqlite3

app = Flask(__name__)

DB_PATH = r'/root/tracker/database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/register')
def register():
    username = request.args.get('username')
    if username is None:
        return 'Go away'
    ip_addr = request.remote_addr
    get_db().execute('INSERT OR REPLACE INTO tracker (username, ip_addr) VALUES (?, ?)',[username, ip_addr])
    get_db().commit()
    return "OK"

@app.route('/lookup')
def lookup():
    username = request.args.get('username')
    if username is None:
        return 'Go away'
    row = query_db('SELECT ip_addr from tracker WHERE username = ?', [username], one=True)
    if row is None:
        return ''
    return row['ip_addr']

@app.route('/ping')
def hello_world():
    return 'pong'

if __name__ == "__main__":

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''DROP TABLE IF EXISTS tracker''')
    c.execute('''CREATE TABLE tracker (id INTEGER PRIMARY KEY, username TEXT NOT NULL, ip_addr TEXT NOT NULL);''')
    #c.execute('''INSERT INTO tracker VALUES (0, 'test', '192.168.0.0')''')
    conn.commit()
    conn.close()
    app.run(port=8080, host='0.0.0.0')
