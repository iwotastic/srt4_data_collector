from flask import Flask, abort, render_template, request, make_response
from session_manager import sessions
app = Flask(__name__)

@app.route("/test_form")
def test_form():
  return render_template("form.html", title="Hello World!", content="<h1>Hello World</h1>", form_id="0")

@app.route("/directions")
def directions():
  session_id = request.cookies["sessionID"]
  if not session_id in sessions:
    abort(403)

  session = sessions[session_id]
  return render_template("directions.html", name=session.user_name)

@app.route("/set-name", methods=["POST"])
def set_name():
  session_id = request.cookies["sessionID"]
  if session_id in sessions and request.is_json and "name" in request.json:
    if request.json["name"].strip() != "":
      sessions[session_id].user_name = request.json["name"]
      return {"continue": True}
    else:
      return {"continue": False, "message": "Please enter a name"}
  else:
    abort(403)

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
