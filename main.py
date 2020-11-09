from flask import Flask, abort, render_template, request, make_response
from session_manager import sessions
app = Flask(__name__)

@app.route("/test_form")
def test_form():
  return render_template("form.html", title="Hello World!", content="<h1>Hello World</h1>", form_id="0")

@app.route("/directions")
def directions():
  return render_template("directions.html", name="Ian")

@app.route("/welcome")
def welcome():
  invitee_id = request.args["invitee_id"]
  if invitee_id == None:
    abort(403)

  session = sessions.add_session(invitee_id)
  resp = make_response(render_template("welcome.html"))
  resp.set_cookie("sessionID", session.id)
  return resp

if __name__ == "__main__":
  app.run()
