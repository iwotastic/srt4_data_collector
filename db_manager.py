import psycopg2
import json
from uuid import uuid4

class DatabaseManager:
  _default = None

  def __init__(self):
    """Initialize database connection. This method should *never* be called
    directly, the singleton methods manage the makeshift connection pool,
    ensuring only one connection is active at a time, creating cursors when
    necessary.
    """
    with open("dbconfig.json") as config_file:
      config = json.load(config_file)

    self.dev_mode = config["env"] == "dev"

    if not self.dev_mode:
      self.conn = psycopg2.connect(
        database="srt4_data",
        user="iwotastic",
        password=config["password"],
        host="localhost"
      )

  def lookup_invitee(self, invitee):
    if self.dev_mode:
      return "Dev Mode Group"

    with self.conn:
      with self.conn.cursor() as c:
        try:
          c.execute("SELECT description FROM invite_groups WHERE id=%s", (invitee,))
        except:
          return None

        result = c.fetchone()
        if result:
          return result[0]
        
    return None

  def add_submission(self, session_id, submission_data):
    if self.dev_mode:
      return

    with self.conn:
      with self.conn.cursor() as c:
        try:
          c.execute("INSERT INTO submissions VALUES (%s, %s)", (
            session_id,
            submission_data
          ))
        except:
          pass
  
  def add_bot_submission(self, session, submission_data):
    if self.dev_mode:
      with open(f"bot_log/{uuid4()}.json", "w") as log_file:
        log_file.write(submission_data)
      return

    with self.conn:
      with self.conn.cursor() as c:
        try:
          c.execute("INSERT INTO bot_submissions VALUES (%s, %s)", (
            session.bot_source,
            submission_data
          ))
        except:
          pass

  def add_submitter(self, session):
    if self.dev_mode:
      return

    with self.conn:
      with self.conn.cursor() as c:
        try:
          c.execute("INSERT INTO submitters VALUES (%s, %s, %s)", (
            session.id,
            session.invitee_id,
            session.user_name
          ))
        except:
          pass

  @classmethod
  def default(cls):
    """Method to return singleton database connection. This method will also
    auto re-open a closed connection without failing.
    """
    if cls._default != None:
      return cls._default
    else:
      cls._default = cls()
      return cls._default

  @classmethod
  def close(cls):
    """Method to close any open connection to the server on the singleton
    database connection.
    """
    if cls._default != None:
      cls._default.conn.close()