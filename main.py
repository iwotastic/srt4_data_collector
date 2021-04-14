from flask import Flask, abort, redirect, render_template, request, make_response, url_for
from session_manager import sessions
from db_manager import DatabaseManager
from evaluate_submission import evaluate_submission
import functools
import random
import json

# Initial setup
app = Flask(__name__)

with open("form_index.json") as form_index:
  forms = json.load(form_index)

num_forms_to_show = 5

# Human routes
@app.route("/thanks")
def thanks():
  """Route to render "Thank You" page, completing the navigation flow.
  """
  session_id = request.cookies["sessionID"]
  if not session_id in sessions:
    abort(403)

  session = sessions[session_id]
  raw_scores = session.scores
  name = session.user_name
  del sessions[session_id]

  scores = [{
    "browser": "human" if page_scores["browser"][0][0] > page_scores["browser"][0][1] else "bot",
    "keyboard_human": functools.reduce(lambda accum, batch: accum + (1 if batch[0][0] > batch[0][1] else 0), page_scores["keyboard"], 0),
    "keyboard_bot": functools.reduce(lambda accum, batch: accum + (1 if batch[0][0] < batch[0][1] else 0), page_scores["keyboard"], 0),
    "mouse_human": functools.reduce(lambda accum, batch: accum + (1 if batch[0][0] > batch[0][1] else 0), page_scores["mouse"], 0),
    "mouse_bot": functools.reduce(lambda accum, batch: accum + (1 if batch[0][0] < batch[0][1] else 0), page_scores["mouse"], 0)
  } for page_scores in raw_scores]

  return render_template("thankyou.html", name=name, scores=enumerate(scores))

@app.route("/submit-interaction-data", methods=["POST"])
def submit_interaction_data():
  """Route to collect interaction data and log it to the database.
  """
  session_id = request.cookies["sessionID"]
  if not session_id in sessions:
    abort(403)
  
  session = sessions[session_id]
  if request.is_json:
    session.scores.append(evaluate_submission(str(request.data)[2:-1]))
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
  """Route to dynamically fetch the correct form to display to the user based
  on their pre-selected order. This will be called `num_forms_to_show` times.
  """
  session_id = request.cookies["sessionID"]
  if not session_id in sessions:
    abort(403)

  session = sessions[session_id]
  if session.user_name == "":
    # Wow! The user discovered teleportation, they still need to enter their
    # name though...
    return redirect(url_for("welcome"))
  elif session.current_form == num_forms_to_show:
    # The user was somehow sent back here from the last form, not sure how
    # that would happen, but, let's send them to thank you again...
    return redirect(url_for("thanks"))

  form_data = forms[session.form_sequence[session.current_form]]

  with open("forms/" + form_data["name"] + ".html") as content_file:
    content = content_file.read()

  return render_template(
    "form.html",
    title=(
      "Ian's SRT4 Project - Form "
      f"{session.current_form + 1}/{num_forms_to_show} - "
      f"{form_data['displayName']}"
    ),
    content=content,
    form_script=form_data["name"] + ".js"
  )

@app.route("/directions")
def directions():
  """Route to display initial directions before loading the forms.
  """
  session_id = request.cookies["sessionID"]
  if not session_id in sessions:
    abort(403)

  session = sessions[session_id]
  if session.user_name == "":
    # Wow! The user discovered teleportation, they still need to enter their
    # name though...
    return redirect(url_for("welcome"))
  elif session.current_form == num_forms_to_show:
    # The user was somehow sent back here from the last form, not sure how
    # that would happen, but, let's send them to thank you again...
    return redirect(url_for("thanks"))
  elif session.current_form > 0:
    # The user should be on a form, so send them there...
    return redirect(url_for("form"))

  session.form_sequence = random.sample(range(len(forms)), num_forms_to_show)
  return render_template("directions.html", name=session.user_name)

@app.route("/set-name", methods=["POST"])
def set_name():
  """Route to set the user's name. This will update their name in their
  `Session` and add a row to the `submitters` table.
  """
  session_id = request.cookies["sessionID"]
  if session_id in sessions and request.is_json and "name" in request.json:
    # Check if the user has already set a name
    if sessions[session_id].user_name != "":
      # If so, return with with a continue to bump them to directions. It is
      # assumed that no database transaction is required because that will
      # have already occured if their user_name isn't blank.
      return {"continue": True}

    # Did the user actually enter a name...
    if request.json["name"].strip() != "":
      # If they did, add them to the database...
      sessions[session_id].user_name = request.json["name"]
      DatabaseManager.default().add_submitter(sessions[session_id])
      return {"continue": True}
    else:
      # If they didn't, hit them with an error...
      return {"continue": False, "message": "Please enter a name"}
  else:
    abort(403)

@app.route("/welcome")
def welcome():
  """Route to welcome users to the project and request their name. 
  """

  # If the user went back a page, let's put them where they belong...
  session_id = ""
  if "sessionID" in request.cookies:
    session_id = request.cookies["sessionID"]

  send_new_session = True
  if session_id in sessions:
    session = sessions[session_id]

    if session.user_name == "":
      # The user simply reloaded the welcome page, fall through, but don't
      # create a new session.
      send_new_session = False
    elif session.current_form == 0:
      # The user was on either directions or form 0, send them to directions...
      return redirect(url_for("directions"))
    elif session.current_form == num_forms_to_show:
      # The user was somehow sent back here from the last form, not sure how
      # that would happen, but, let's send them to thank you again...
      return redirect(url_for("thanks"))
    else:
      # By process of elimination, the user should be on a form...
      return redirect(url_for("form"))

  invitee_id = request.args["invitee_id"]
  if invitee_id == None:
    abort(403)

  invitee_desc = DatabaseManager.default().lookup_invitee(invitee_id)
  if invitee_desc == None:
    abort(403)

  resp = make_response(render_template(
    "welcome.html",
    num_forms_to_show=num_forms_to_show
  ))

  if send_new_session:
    session = sessions.add_session(invitee_id)
    resp.set_cookie("sessionID", session.id)

  return resp

# Bot routes
@app.route("/submit", methods=["POST"])
def submit_bot_interaction_data():
  """Route to collect bot interaction data and log it to the database.
  """
  session_id = request.cookies["sessionID"]
  if not session_id in sessions:
    abort(403)
  
  session = sessions[session_id]
  if not session.is_bot:
    abort(403)

  if request.is_json:
    DatabaseManager.default().add_bot_submission(session, str(request.data))

    resp = make_response({"status": "success"})

    resp.set_cookie("sessionID", "", expires=0)
    return resp
  
  else:
    abort(404)

@app.route("/done")
def bot_done_page():
  """Route to show a fake confirmation page to bots.
  """
  return render_template("done.html", return_url=request.args["return_url"])

def bot_form_route_for(form):
  """Generates a route handler for a given `form`.
  """
  def render_route():
    """Render page to load `form` upon request.
    """
    with open("forms/" + form["name"] + ".html") as content_file:
      content = content_file.read()

    resp = make_response(render_template(
      "form.html",
      title=form['displayName'],
      content=content,
      form_script=form["name"] + ".js"
    ))

    # Initialize and send bot session
    bot_source = "internet"
    if "bot_source" in request.args:
      bot_source = str(request.args["bot_source"])[:10]

    session = sessions.add_session(bot_source=bot_source)
    resp.set_cookie("sessionID", session.id)

    return resp

  return render_route

for form in forms:
  app.add_url_rule(
    f"/{form['name']}",
    f"bot_form.{form['name']}",
    bot_form_route_for(form)
  )

# Home page for either bots or humans
@app.route("/")
def index():
  """Route to show index page to bots.
  """
  return render_template("index.html", forms=forms)

# Finally, run the server, assuming this is the called file...
if __name__ == "__main__":
  app.run(host="0.0.0.0")
