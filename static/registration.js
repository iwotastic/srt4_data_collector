initForm([
  {
    selector: "#first",
    func: el => el.value.trim() !== "" ? null : "Please enter a first name."
  },
  {
    selector: "#last",
    func: el => el.value.trim() !== "" ? null : "Please enter a last name."
  },
  {
    selector: "#email",
    func: el => el.value.trim() !== "" ? null : "Please enter an email."
  }
])