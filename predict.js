/* Sunlytics - predict.js
   Handles the loading overlay animation on prediction submit and the
   reset button on the Predict page. */

(function () {
  "use strict";

  const form = document.getElementById("predictForm");
  const overlay = document.getElementById("loadingOverlay");
  const loadingText = document.getElementById("loadingText");
  const resetBtn = document.getElementById("resetBtn");

  if (form && overlay) {
    form.addEventListener("submit", function (e) {
      if (!form.checkValidity()) {
        return; // let native HTML5 validation surface errors
      }
      overlay.classList.add("active");
      loadingText.textContent = "Predicting...";
      // Simulate a brief "completed" flash before the page navigates away
      // (the actual navigation happens once the server responds).
    });
  }

  if (resetBtn && form) {
    resetBtn.addEventListener("click", function () {
      form.reset();
    });
  }
})();
