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
  c.put("evaluate_submission.py", "srt4_data_collector/")

  # Create prod config
  with open("dbconfig.json") as config_file:
    conf = json.load(config_file)
    conf["env"] = "prod"
    c.run(f"echo '{json.dumps(conf)}' > srt4_data_collector/dbconfig.json")

  # Create prod requirements
  with open("requirements.txt") as reqs_file:
    reqs = reqs_file.read()
    reqs = reqs.replace(
      "\ntensorflow @ https://storage.googleapis.com/tensorflow/mac/cpu/tensorflow-2.4.0-cp38-cp38-macosx_10_14_x86_64.whl",
      ""
    )
    c.run(f"echo '{reqs}' > srt4_data_collector/requirements.txt")

  # Init venv
  c.run("python3 -m venv srt4_data_collector/")
  c.run("srt4_data_collector/bin/pip install --upgrade pip")
  c.run("srt4_data_collector/bin/pip install --upgrade setuptools")
  c.run("srt4_data_collector/bin/pip install --upgrade setuptools-rust")
  c.run("srt4_data_collector/bin/pip install --upgrade --no-cache-dir -vvv tensorflow")
  c.run("srt4_data_collector/bin/pip install -r srt4_data_collector/requirements.txt")

  def put_recursively(folder_name, target):
    c.run(f"mkdir -p {target}/")

    for file in Path(folder_name).iterdir():
      if file.is_file():
        print(f"Uploading {folder_name}/{file.name} to {target.replace('~/', '')}")
        c.put(str(file.absolute()), f"{target.replace('~/', '')}/")
      elif file.is_dir():
        put_recursively(folder_name + "/" + file.name, target + "/" + file.name)

  # Upload templates
  put_recursively("templates", "~/srt4_data_collector/templates")

  # Upload forms
  put_recursively("forms", "~/srt4_data_collector/forms")

  put_recursively("model", "~/srt4_data_collector/model")

  # Upload static files
  put_recursively("static", "/var/www/srt4project/static")

  # Finally... start the service back up
  c.run("systemctl --user start srt4_data_collector.service")