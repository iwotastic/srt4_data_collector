from uuid import uuid4

class Session:
  """Class that encapsulates the state of one session of project participation
  """

  def __init__(self, invitee_id=None):
    """Initialize a new session with a given `invitee_id`. Other properties
    will be initialized later on. If `invitee_id` equals `None`, then the
    session will be initialized for a bot.
    """
    self.id = str(uuid4())
    self.invitee_id = invitee_id
    self.user_name = ""
    self.is_bot = invitee_id == None
    self.current_page = "welcome"

class SessionManager:
  """Class that should only be initialized once to manage project participation
  sessions.
  """

  def __init__(self):
    self.sessions = {}

  def add_session(self, *args, **kwargs):
    """Adds a new session, passes through arguments to the `Session` initializer.
    """
    new_session = Session(*args, *kwargs)
    self.sessions[new_session.id] = new_session
    return new_session

  def clear_session(self, session_id):
    """Deletes the session associated with `session_id`.
    """
    del self.sessions[session_id]

  def __getitem__(self, key):
    """Gets the session assoicated with session ID `key`.
    """
    return self.sessions[key]

  def __contains__(self, session_id):
    """Checks if `session_id` is in the session map.
    """
    return session_id in self.sessions.keys()

sessions = SessionManager()