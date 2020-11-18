const initForm = (validators) => {
  // Begin data logging

  let mouseMovements = []
  let mouseClicks = []
  let keyboardEvents = []
  let touchEvents = []

  let oneTimeChecks = {
    mouseEventsPossible: typeof MouseEvent === "function",
    touchEventsPossible: typeof TouchEvent === "function",
    keyEventsPossible: typeof KeyboardEvent === "function",
    lightMode: matchMedia("(prefers-color-scheme: light)").matches,
    isSRGB: matchMedia("(color-gamut: srgb)").matches,
    hasFinePointer: matchMedia("(pointer: fine)").matches,
    hasVibration: typeof navigator.vibrate === "function",
    notReducedMotion: matchMedia("(prefers-reduced-motion)").matches,
    hasWebGL: typeof WebGLRenderingContext === "function",
    hasWebGL2: typeof WebGL2RenderingContext === "function",
    hasGamepads: typeof navigator.getGamepads === "function" && navigator.getGamepads() !== []
  }
  
  // mouse movements

  window.onmousemove = e => {
    mouseMovements.push({
      x: e.pageX,
      y: e.pageY,
      timestamp: Date.now()
    })
  }

  window.onmousedown = e => {
    mouseClicks.push({
      x: e.pageX,
      y: e.pageY,
      timestamp: Date.now()
    })
  }

  // keyboard events

  window.onkeydown = e => {
    keyboardEvents.push({
      down: true,
      timestamp: Date.now()
    })
  }

  window.onkeyup = e => {
    keyboardEvents.push({
      down: false,
      timestamp: Date.now()
    })
  }

  // touch events

  window.ontouchdown = e => {
    touches = []

    for (let i = 0; i < e.touches.length; i++) {
      let touch = e.touches.item(i)
      touches.push({
        x: touch.pageX,
        y: touch.pageY,
        radiusX: touch.radiusX,
        radiusY: touch.radiusY
      })
    }

    touchEvents.push({
      type: "down",
      touches,
      timestamp: Date.now()
    })
  }

  window.ontouchmove = e => {
    touches = []

    for (let i = 0; i < e.touches.length; i++) {
      let touch = e.touches.item(i)
      touches.push({
        x: touch.pageX,
        y: touch.pageY,
        radiusX: touch.radiusX,
        radiusY: touch.radiusY
      })
    }

    touchEvents.push({
      type: "move",
      touches,
      timestamp: Date.now()
    })
  }

  window.ontouchup = e => {
    touches = []

    for (let i = 0; i < e.touches.length; i++) {
      let touch = e.touches.item(i)
      touches.push({
        x: touch.pageX,
        y: touch.pageY,
        radiusX: touch.radiusX,
        radiusY: touch.radiusY
      })
    }

    touchEvents.push({
      type: "up",
      touches,
      timestamp: Date.now()
    })
  }

  // Form submission

  $("form").onsubmit = e => {
    e.preventDefault()

    // Collect form status
    const formError = validators.reduce((err, validator) => {
      if (typeof err === "string") return err

      const res = validator.func($(validator.selector))
      if (typeof res === "string") {
        return res
      }else{
        return null
      }
    }, null)

    if (typeof formError === "string") {
      $("#alert-container").textContent = ""
      const alertView = document.createElement("div")
      alertView.className = "alert alert-danger"
      alertView.textContent = formError
      $("#alert-container").appendChild(alertView)
    }else{
      $("#alert-container").textContent = ""
      const alertView = document.createElement("div")
      alertView.className = "alert alert-info"
      alertView.textContent = "Please wait... Submitting form..."
      $("#alert-container").appendChild(alertView)

      submitData("/submit-interaction-data", {
        mouseMovements,
        mouseClicks,
        keyboardEvents,
        touchEvents,
        oneTimeChecks
      }).then(r => r.json()).then(resp => {
        if (resp.action === "reload") {
          location.reload()
        }else if (resp.action === "thank_you") {
          location.href = "/thanks"
        }
      })
    }
  }
}