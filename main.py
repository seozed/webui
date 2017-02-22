from flask import Flask
from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/survive/')
def survive():
    return render_template('survive.html')

if __name__ == '__main__':
    app.run()