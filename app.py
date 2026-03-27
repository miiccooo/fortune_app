from flask import Flask, render_template, request
from main import fortune_from_birthdate

app = Flask(__name__)

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/result")
def result():
    birth = request.form.get("birthdate", "")
    try:
        data = fortune_from_birthdate(birth)
        return render_template("result.html", data=data, error=None)
    except Exception as e:
        return render_template("index.html", error=str(e), birthdate=birth)

if __name__ == "__main__":
    app.run(debug=True)