from flask import Flask, request, render_template

app = Flask(__name__)

def calc(op, a, b):
    a = float(a); b = float(b)
    if op == 'add': return a + b
    if op == 'sub': return a - b
    if op == 'mul': return a * b
    if op == 'div': return a / b
    raise ValueError("Unknown op")

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    a = b = op = ""
    if request.method == "POST":
        a = request.form.get("a", "")
        b = request.form.get("b", "")
        op = request.form.get("op", "add")
        try:
            result = calc(op, a, b)
        except Exception as e:
            error = str(e)
    return render_template("index.html", result=result, error=error, a=a, b=b, op=op)
