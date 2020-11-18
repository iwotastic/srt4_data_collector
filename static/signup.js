initForm([
  {
    selector: "#name",
    func: el => el.value.trim() !== "" ? null : "Please enter a name."
  },
  {
    selector: "#pass1",
    func: el => el.value.trim() !== "" ? null : "Please enter a password."
  },
  {
    selector: "#pass2",
    func: el => el.value.trim() !== "" ? (
      el.value === $("#pass1").value ? null : "Passwords must match."
    ) : "Please retype your password."
  }
])