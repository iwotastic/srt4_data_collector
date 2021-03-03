import numpy as np
import tensorflow as tf
import json

# Preload the models
browser_attributes = tf.keras.models.load_model("model/browser_attributes")
keyboard_events = tf.keras.models.load_model("model/keyboard_events")
mouse_movements = tf.keras.models.load_model("model/mouse_movements")

# Helper functions
def to_binary_number(boolean):
  return 1.0 if boolean else 0.0

# Preprocessor functions
def preprocess_browser_data(data):
  return np.array([
    to_binary_number(data["oneTimeChecks"]["mouseEventsPossible"]),
    to_binary_number(data["oneTimeChecks"]["touchEventsPossible"]),
    to_binary_number(data["oneTimeChecks"]["keyEventsPossible"]),
    to_binary_number(data["oneTimeChecks"]["lightMode"]),
    to_binary_number(data["oneTimeChecks"]["isSRGB"]),
    to_binary_number(data["oneTimeChecks"]["hasFinePointer"]),
    to_binary_number(data["oneTimeChecks"]["hasVibration"]),
    to_binary_number(data["oneTimeChecks"]["notReducedMotion"]),
    to_binary_number(data["oneTimeChecks"]["hasWebGL"]),
    to_binary_number(data["oneTimeChecks"]["hasWebGL2"]),
    to_binary_number(data["oneTimeChecks"]["hasGamepads"]),
  ])

def preprocess_keyboard_data(data):
  run_length = 16

  if not isinstance(data["keyboardEvents"], list) or len(data["keyboardEvents"]) < run_length:
    # Fail-safe for non-existent or too small keyboard data
    return []

  keyboard_events = data["keyboardEvents"]
  arrays = []

  for i in range(len(keyboard_events) // run_length):
    kbd_run = keyboard_events[i * run_length : (i + 1) * run_length]

    min_ts = kbd_run[0]["timestamp"]
    max_ts = kbd_run[run_length - 1]["timestamp"]

    arrays.append(np.array([[to_binary_number(ev["down"]), (ev["timestamp"] - min_ts) / (max_ts - min_ts)] for ev in kbd_run]))

  return arrays

def preprocess_mouse_data(data):
  if not isinstance(data["mouseMovements"], list) or len(data["mouseMovements"]) == 0:
    # Fail-safe for non-existent mouse movement data
    return []

  no_clicks = ("mouseClicks" not in data) or (len(data["mouseClicks"]) == 0)

  split_mouse_movements = []
  movement_buffer = []
  movement_cursor = 0
  click_cursor = 0

  while movement_cursor < len(data["mouseMovements"]):
    movement = data["mouseMovements"][movement_cursor]

    if no_clicks:
      movement_buffer.append((movement["x"], movement["y"], movement["timestamp"]))
    elif click_cursor >= len(data["mouseClicks"]):
      movement_buffer.append((movement["x"], movement["y"], movement["timestamp"]))
    elif movement["timestamp"] < data["mouseClicks"][click_cursor]["timestamp"]:
      movement_buffer.append((movement["x"], movement["y"], movement["timestamp"]))
    elif movement["timestamp"] > data["mouseClicks"][click_cursor]["timestamp"]:
      click = data["mouseClicks"][click_cursor]
      movement_buffer.append((click["x"], click["y"], click["timestamp"]))
      split_mouse_movements.append(movement_buffer)
      movement_buffer = []
      click_cursor += 1
      movement_buffer.append((movement["x"], movement["y"], movement["timestamp"]))

    movement_cursor += 1

  if click_cursor < len(data["mouseClicks"]):
    click = data["mouseClicks"][click_cursor]
    movement_buffer.append((click["x"], click["y"], click["timestamp"]))

  split_mouse_movements.append(movement_buffer)

  arrays = []

  for mouse_movement in split_mouse_movements:
    array = np.zeros((600, 600, 3))

    xs = [x for x, _, _ in mouse_movement]
    ys = [y for _, y, _ in mouse_movement]
    timestamps = [timestamp for _, _, timestamp in mouse_movement]

    # Set up key values
    min_x = min(xs)
    max_x = max(xs) if max(xs) != min_x else min_x + 1
    min_y = min(ys)
    max_y = max(ys) if max(ys) != min_y else min_y + 1
    min_timestamp = min(timestamps)
    max_timestamp = max(timestamps) if max(timestamps) != min_timestamp else min_timestamp + 1

    # Set up normalizers
    normalize_x = lambda x: int(((x - min_x) / (max_x - min_x)) * 600)
    normalize_y = lambda y: int(((y - min_y) / (max_y - min_y)) * 600)
    normalize_timestamp = lambda timestamp: (timestamp - min_timestamp) / (max_timestamp - min_timestamp)

    for index, point in enumerate(mouse_movement):
      nx = normalize_x(point[0])
      ny = normalize_y(point[1])

      # Red (index-based scaling)
      array[(nx - 3 if nx - 3 > -1 else 0) : (nx + 3 if nx + 3 < 600 else 600),
        (ny - 3 if ny - 3 > -1 else 0) : (ny + 3 if ny + 3 < 600 else 600), 0] = index / len(mouse_movement)

      # Green (Time-based scaling)
      array[(nx - 3 if nx - 3 > -1 else 0) : (nx + 3 if nx + 3 < 600 else 600),
        (ny - 3 if ny - 3 > -1 else 0) : (ny + 3 if ny + 3 < 600 else 600), 1] = normalize_timestamp(point[2])

      # Blue (Statically valued indicator of mouse path)
      array[(nx - 3 if nx - 3 > -1 else 0) : (nx + 3 if nx + 3 < 600 else 600),
        (ny - 3 if ny - 3 > -1 else 0) : (ny + 3 if ny + 3 < 600 else 600), 2] = 0.5

    arrays.append(array)

  return arrays

# Evaluation function
def evaluate_submission(json_string):
  """Evaluates a JSON-formatted string against all models. Note: this function
  does not accept "b'{...}'" strings.
  """
  data = json.loads(json_string)

  browser_data = preprocess_browser_data(data)
  keyboard_data = preprocess_keyboard_data(data)
  mouse_data = preprocess_mouse_data(data)

  return {
    "browser": browser_attributes(browser_data[np.newaxis, :]).numpy().tolist(),
    "keyboard": [keyboard_events(block[np.newaxis, :, :]).numpy().tolist() for block in keyboard_data],
    "mouse": [mouse_movements(block[np.newaxis, :, :, :]).numpy().tolist() for block in mouse_data]
  }