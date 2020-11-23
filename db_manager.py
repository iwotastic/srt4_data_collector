import psycopg2
import json

class DatabaseManager:
  _default = None

  def __init__(self):
    with open("dbconfig.json") as config_file:
      config = json.load(config_file)

    self.conn = psycopg2.connect(database="srt4_data", user="iwotastic", password=config["password"], host="localhost")

  def check_for_invitee(self, invitee):
    with self.conn:
      with self.conn.cursor() as c:
        c.execute("SELECT id FROM invite_groups WHERE id=%s", (invitee,))
        if c.fetchone():
          return True

    return False

  @classmethod
  def default(cls):
    if cls._default != None:
      return cls._default
    else:
      cls._default = cls()
      return cls._default

  @classmethod
  def close(cls):
    if cls._default != None:
      cls._default.conn.close()