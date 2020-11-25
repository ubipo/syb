from flask import Flask, request
app = Flask(__name__)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def hello_world(path):
    code = request.args.get('code')
    if code is None:
        return ''
    return code.upper()


if __name__ == '__main__': 
    app.run()

