$("#next").addEventListener("click", e => {
  const userName = $("#invitee-name").value
  if (userName.trim() === "") {
    alert("Make sure you enter a valid username.")
  }
})