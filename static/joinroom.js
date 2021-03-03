initForm([
  {
    selector: "#room-code",
    func: el => /^[0-9a-zA-Z]{6}$/ ? null : "Please enter a valid join code (6 digits long)."
  },
  {
    selector: "#name",
    func: el => el.value.trim() !== "" ? null : "Please enter your name."
  },
])