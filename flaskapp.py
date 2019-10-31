from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def hello_world():
    with open("summary.txt", "r") as f:
        content = f.read()
    return render_template("basic_template.html", content=content)