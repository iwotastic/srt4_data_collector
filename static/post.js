initForm([
  {
    selector: "#name",
    func: el => el.value.trim() !== "" ? null : "Please enter a name."
  },
  {
    selector: "#tags",
    func: el => el.value.trim() !== "" ? null : "Please add at least one tag."
  },
  {
    selector: "#msg",
    func: el => el.value.trim() !== "" ? (
      el.value.length > 100 ? "Please type a shorter message." : null
    ) : "Please enter a message."
  }
])