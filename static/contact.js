initForm([
  {
    selector: "#name",
    func: el => el.value.trim() !== "" ? null : "Please enter a name."
  },
  {
    selector: "#subject",
    func: el => el.value.trim() !== "" ? null : "Please enter a subject."
  },
  {
    selector: "#msg",
    func: el => el.value.trim() !== "" ? (
      el.value.length < 20 ? "Please type a longer message." : null
    ) : "Please enter a message."
  }
])