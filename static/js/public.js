/**
 * Public Website Interactive Behaviors
 */
document.addEventListener("DOMContentLoaded", () => {
  // Sticky header scroll detection
  const header = document.querySelector(".site-header");
  if (header) {
    window.addEventListener("scroll", () => {
      if (window.scrollY > 30) {
        header.classList.add("is-scrolled");
      } else {
        header.classList.remove("is-scrolled");
      }
    });
  }

  // Mobile menu toggle
  const mobileToggle = document.querySelector(".mobile-menu-toggle");
  const navMenu = document.querySelector(".nav-menu");
  if (mobileToggle && navMenu) {
    mobileToggle.addEventListener("click", () => {
      navMenu.classList.toggle("is-open");
      const isExpanded = navMenu.classList.contains("is-open");
      mobileToggle.setAttribute("aria-expanded", isExpanded);
    });
  }
});
