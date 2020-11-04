from flask import Flask, render_template
app = Flask(__name__)

@app.route("/test_form")
def begin_page():
  return render_template("form.html", title="Hello World!")

if __name__ == "__main__":
  app.run()
