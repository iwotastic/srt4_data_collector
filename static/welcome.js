$("#next").addEventListener("click", e => {
  const userName = $("#invitee-name").value
  if (userName.trim() === "") {
    alert("Make sure you enter a valid username.")
  }else{
    $("#next").disabled = true
    $("#next").textContent = "Please Wait..."
    submitData("/set-name", {name: userName}).then(resp => resp.json()).then(status => {
      if (status.continue) {
        location.href = "/directions"
      }else{
        $("#next").disabled = false
        $("#next").textContent = "Next"
        alert(status.message)
      }
    }).catch(err => {
      $("#next").disabled = false
      $("#next").textContent = "Next"
      alert("An error occured")
      console.log(err)
    })
  }
})