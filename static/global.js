// Helpful constant that aliases $ to querySelector
const $ = q => doument.querySelector(q)

// Helper function to submit data to the server
const submitData = (url, data) => {
  return fetch(url, {
    method: "POST",
    credentials: "same-origin",
    body: JSON.stringify(data),
    headers: {
      "Content-Type": "application/json"
    }
  })
}