from flask import Flask, render_template
from flask_pymongo import PyMongo

app = Flask(__name__)
mongo = PyMongo(app, uri="mongodb://localhost:27018/ekstrah")
db = mongo.db


@app.route("/")
def hello_world():
    col = db['msg']
    return render_template('index.html', dbData=col.find())

if __name__ == "__main__":
     app.run(host='0.0.0.0', port=5000)