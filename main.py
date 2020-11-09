from flask import Flask, render_template
app = Flask(__name__)

@app.route("/test_form")
def test_form():
  return render_template("form.html", title="Hello World!", content="<h1>Hello World</h1>", form_id="0")

@app.route("/directions")
def directions():
  return render_template("directions.html", name="Ian")

@app.route("/welcome")
def welcome():
  return render_template("welcome.html")

if __name__ == "__main__":
  app.run()
