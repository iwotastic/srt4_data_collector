from fabric import Connection, task
from pathlib import Path
import json

@task
def deploy(c):
  # Stop service
  try:
    c.run("systemctl --user stop srt4_data_collector.service")
  except:
    pass # Ignore any errors, push through!

  # Delete files
  try:
    c.run("rm -rf srt4_data_collector/")
  except:
    pass # Ignore any errors, push through!

  # Delete static files
  try:
    c.run("rm -rf /var/www/srt4project/static")
  except:
    pass # Ignore any errors, push through!
  
  # Re-create directory
  c.run("mkdir srt4_data_collector/")

  # Upload files in project root
  c.put("main.py", "srt4_data_collector/")
  c.put("form_index.json", "srt4_data_collector/")
  c.put("session_manager.py", "srt4_data_collector/")
  c.put("db_manager.py", "srt4_data_collector/")
  c.put("requirements.txt", "srt4_data_collector/")

  # Create prod config
  with open("dbconfig.json") as config_file:
    conf = json.load(config_file)
    conf["env"] = "prod"
    c.run(f"echo '{json.dumps(conf)}' > srt4_data_collector/dbconfig.json")

  # Init venv
  c.run("python3 -m venv srt4_data_collector/")
  c.run("srt4_data_collector/bin/pip install -r srt4_data_collector/requirements.txt")

  # Upload templates
  c.run("mkdir -p ~/srt4_data_collector/templates/")

  for file in Path("templates").iterdir():
    c.put(str(file.absolute()), "srt4_data_collector/templates/")

  # Upload forms
  c.run("mkdir -p ~/srt4_data_collector/forms/")

  for file in Path("forms").iterdir():
    c.put(str(file.absolute()), "srt4_data_collector/forms/")

  # Upload static files
  c.run("mkdir -p /var/www/srt4project/static/")

  for file in Path("static").iterdir():
    c.put(str(file.absolute()), "/var/www/srt4project/static/")

  # Finally... start the service back up
  c.run("systemctl --user start srt4_data_collector.service")