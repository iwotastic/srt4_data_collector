initForm([
  {
    selector: "#name",
    func: el => el.value.trim() !== "" ? null : "Please enter a name."
  },
  {
    selector: "#pass",
    func: el => el.value.trim() !== "" ? null : "Please enter a password."
  }
])