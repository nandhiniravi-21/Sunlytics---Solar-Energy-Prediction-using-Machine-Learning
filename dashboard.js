/* Sunlytics - dashboard.js
   Fetches chart data from /api/chart-data and renders Line, Pie and Bar
   charts using Chart.js. Also renders a static Feature Importance chart
   from data injected by the dashboard template. */

(function () {
  "use strict";

  const cssVar = (name) =>
    getComputedStyle(document.documentElement).getPropertyValue(name).trim();

  const accent = cssVar("--accent") || "#0EA5E9";
  const success = cssVar("--success") || "#22C55E";
  const warning = cssVar("--warning") || "#F59E0B";
  const danger = cssVar("--danger") || "#EF4444";
  const textColor = cssVar("--text") || "#1E293B";

  Chart.defaults.color = textColor;
  Chart.defaults.font.family = "Inter, sans-serif";

  fetch("/api/chart-data")
    .then((res) => res.json())
    .then((data) => {
      renderLineChart(data.line);
      renderPieChart(data.pie);
      renderBarChart(data.bar);
    })
    .catch((err) => console.error("Failed to load chart data:", err));

  function renderLineChart(line) {
    const ctx = document.getElementById("lineChart");
    if (!ctx) return;
    new Chart(ctx, {
      type: "line",
      data: {
        labels: line.labels.length ? line.labels : ["No data"],
        datasets: [
          {
            label: "Predicted Output (kW)",
            data: line.values.length ? line.values : [0],
            borderColor: accent,
            backgroundColor: "rgba(14,165,233,0.12)",
            fill: true,
            tension: 0.35,
            pointRadius: 3,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } },
      },
    });
  }

  function renderPieChart(pie) {
    const ctx = document.getElementById("pieChart");
    if (!ctx) return;
    const colorMap = { "High Generation": success, "Moderate Generation": warning, "Low Generation": danger };
    new Chart(ctx, {
      type: "pie",
      data: {
        labels: pie.labels.length ? pie.labels : ["No data"],
        datasets: [
          {
            data: pie.values.length ? pie.values : [1],
            backgroundColor: pie.labels.length
              ? pie.labels.map((l) => colorMap[l] || accent)
              : ["#E2E8F0"],
            borderWidth: 2,
            borderColor: cssVar("--card") || "#fff",
          },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { position: "bottom", labels: { boxWidth: 12 } } },
      },
    });
  }

  function renderBarChart(bar) {
    const ctx = document.getElementById("barChart");
    if (!ctx) return;
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: bar.labels.length ? bar.labels : ["No data"],
        datasets: [
          {
            label: "Total Output (kW)",
            data: bar.values.length ? bar.values : [0],
            backgroundColor: accent,
            borderRadius: 6,
            maxBarThickness: 42,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } },
      },
    });
  }

  // Feature importance (static, from model metadata injected in template)
  const importanceData = window.SUNLYTICS_FEATURE_IMPORTANCE || [];
  const impCtx = document.getElementById("importanceChart");
  if (impCtx && importanceData.length) {
    const top5 = importanceData.slice(0, 5);
    new Chart(impCtx, {
      type: "bar",
      data: {
        labels: top5.map((f) => f.feature.replace(/_/g, " ")),
        datasets: [
          {
            label: "Importance",
            data: top5.map((f) => f.importance),
            backgroundColor: accent,
            borderRadius: 6,
          },
        ],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true } },
      },
    });
  }
})();
