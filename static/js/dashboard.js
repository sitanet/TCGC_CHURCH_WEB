/**
 * Custom Administrative Dashboard Interactions
 */
document.addEventListener("DOMContentLoaded", () => {
  // Sidebar toggle
  const sidebarToggle = document.getElementById("sidebarToggle");
  const sidebar = document.querySelector(".dashboard-sidebar");
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener("click", () => {
      sidebar.classList.toggle("collapsed");
    });
  }

  // Auto-dismiss server flash messages into toast notifications
  const djangoAlerts = document.querySelectorAll(".django-flash-message");
  djangoAlerts.forEach((alert) => {
    const msg = alert.getAttribute("data-message");
    const tag = alert.getAttribute("data-tag") || "info";
    if (window.CityGate && window.CityGate.toast) {
      window.CityGate.toast.show(msg, tag);
    }
  });

  // Action confirmations
  document.addEventListener("click", (e) => {
    const confirmTrigger = e.target.closest("[data-confirm]");
    if (confirmTrigger) {
      const promptText = confirmTrigger.getAttribute("data-confirm") || "Are you sure you want to proceed?";
      if (!window.confirm(promptText)) {
        e.preventDefault();
      }
    }
  });
});
