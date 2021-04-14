# SRT IV Data Collector
The fontend and backend that serve the fake forms for my SRT IV project.

## Requirements
* *Exactly* Python 3.8
* A PostgreSQL database compatible with the database calls in [`db_manager.py`](/db_manager.py)

## Development set-up
Clone the repo to your own computer and run the following:
```bash
# Initialize the venv
python -m venv .

# Activate the venv
source ./bin/activate

# Install requirements with pip
pip install -r ./requirements.txt
```

**Note:** You may need to switch out the `tensorflow` entry in [`requirements.txt`](/requirements.txt) if your machine is not an Intel-based Mac running a recent macOS. If it is, well good job, you shouldn't have to change a thing.