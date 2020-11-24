initForm([
  {
    selector: "#name",
    func: el => el.value.trim() !== "" ? null : "Please enter a name."
  },
  {
    selector: "#title",
    func: el => el.value.trim() !== "" ? null : "Please enter a title."
  },
  {
    selector: "#recommend",
    func: el => el.value !== "" ? null : "Please select whether you reccomend it."
  },
  {
    selector: "#msg",
    func: el => el.value.trim() !== "" ? (
      el.value.length < 20 ? "Please type a longer message." : null
    ) : "Please enter a message."
  }
])