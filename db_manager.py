import psycopg2
import json

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

    self.conn = psycopg2.connect(
      database="srt4_data",
      user="iwotastic",
      password=config["password"],
      host="localhost"
    )

  def check_for_invitee(self, invitee):
    with self.conn:
      with self.conn.cursor() as c:
        c.execute("SELECT id FROM invite_groups WHERE id=%s", (invitee,))
        if c.fetchone():
          return True

    return False

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