from flask import Flask, request
import mysql.connector


app = Flask(__name__)

USER = "flask_http_root"
PASSWORD = "pmNNGs0BpAM0puoszOhO"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def get_latest_log_text(path):
    with mysql.connector.connect(host="localhost", user=USER, passwd=PASSWORD, database="check") as conn:
        c = conn.cursor()
        c.execute("select * from log order by date desc limit 1;")
        res = c.fetchone()
        return res[2]
    return "Error fetching latest log text", 500


if __name__ == '__main__': 
    app.run()

