from flask import Flask, render_template
from drive_func import get_summary
app = Flask(__name__)

@app.route('/')
def hello_world():
    # linelist = get_summary()
    # line = ''.join(linelist)
    with open("summary.txt", "r") as f:
        content = f.read()
    return render_template("basic_template.html", content=content)