from flask import Flask, abort, render_template, request, make_response
from session_manager import sessions
from db_manager import DatabaseManager
import random
import json
app = Flask(__name__)

with open("form_index.json") as form_index:
  forms = json.load(form_index)

num_forms_to_show = 2

@app.route("/thanks")
def thanks():
  session_id = request.cookies["sessionID"]
  if not session_id in sessions:
    abort(403)

  session = sessions[session_id]
  name = session.user_name
  del sessions[session_id]
  return render_template("thankyou.html", name=name)

@app.route("/submit-interaction-data", methods=["POST"])
def submit_interaction_data():
  session_id = request.cookies["sessionID"]
  if not session_id in sessions:
    abort(403)
  
  session = sessions[session_id]
  if request.is_json:
    DatabaseManager.default().add_submission(session_id, str(request.data))
    session.current_form += 1

    if session.current_form < num_forms_to_show:
      return {"action": "reload"}
    else:
      return {"action": "thank_you"}
  
  else:
    abort(404)

@app.route("/form")
def form():
  session_id = request.cookies["sessionID"]
  if not session_id in sessions:
    abort(403)

  session = sessions[session_id]

  form_data = forms[session.form_sequence[session.current_form]]

  with open("forms/" + form_data["name"] + ".html") as content_file:
    content = content_file.read()

  return render_template(
    "form.html",
    title=f"Ian's SRT4 Project - Form {session.current_form + 1}/{num_forms_to_show} - {form_data['displayName']}",
    content=content,
    form_script=form_data["name"] + ".js"
  )

@app.route("/directions")
def directions():
  session_id = request.cookies["sessionID"]
  if not session_id in sessions:
    abort(403)

  session = sessions[session_id]
  session.form_sequence = random.sample(range(len(forms)), num_forms_to_show)
  return render_template("directions.html", name=session.user_name)

@app.route("/set-name", methods=["POST"])
def set_name():
  session_id = request.cookies["sessionID"]
  if session_id in sessions and request.is_json and "name" in request.json:
    if request.json["name"].strip() != "":
      sessions[session_id].user_name = request.json["name"]
      DatabaseManager.default().add_submitter(sessions[session_id])
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

  invitee_desc = DatabaseManager.default().lookup_invitee(invitee_id)
  if invitee_desc == None:
    abort(403)

  session = sessions.add_session(invitee_id)
  resp = make_response(render_template("welcome.html", num_forms_to_show=num_forms_to_show))
  resp.set_cookie("sessionID", session.id)
  return resp

if __name__ == "__main__":
  app.run()
