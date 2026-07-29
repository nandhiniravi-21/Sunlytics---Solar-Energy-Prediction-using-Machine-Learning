/* Sunlytics - main.js
   Handles dark/light theme toggle (persisted), live date/time display,
   and generic UI niceties used across all pages. */

(function () {
  "use strict";

  // ---------------- Theme toggle ----------------
  const root = document.documentElement;
  const themeToggle = document.getElementById("themeToggle");
  const savedTheme = localStorage.getItem("sunlytics-theme") || "light";
  root.setAttribute("data-theme", savedTheme);
  updateThemeIcon(savedTheme);

  if (themeToggle) {
    themeToggle.addEventListener("click", function () {
      const current = root.getAttribute("data-theme");
      const next = current === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      localStorage.setItem("sunlytics-theme", next);
      updateThemeIcon(next);
    });
  }

  function updateThemeIcon(theme) {
    if (!themeToggle) return;
    const icon = themeToggle.querySelector("i");
    if (!icon) return;
    icon.className = theme === "dark" ? "fa-solid fa-sun" : "fa-solid fa-moon";
  }

  // ---------------- Live clock (used on multiple pages) ----------------
  function updateClock() {
    const clockEl = document.getElementById("liveClock");
    const dateEl = document.getElementById("liveDate");
    if (!clockEl && !dateEl) return;

    const now = new Date();
    if (clockEl) {
      clockEl.textContent = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    }
    if (dateEl) {
      dateEl.textContent = now.toLocaleDateString([], { weekday: "long", year: "numeric", month: "long", day: "numeric" });
    }
  }
  updateClock();
  setInterval(updateClock, 1000);

  // ---------------- Auto-dismiss alerts ----------------
  document.querySelectorAll(".sunlytics-alert").forEach(function (alertEl) {
    setTimeout(function () {
      if (window.bootstrap && window.bootstrap.Alert) {
        const instance = window.bootstrap.Alert.getOrCreateInstance(alertEl);
        instance.close();
      }
    }, 6000);
  });
})();
