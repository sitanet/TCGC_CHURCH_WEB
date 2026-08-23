/**
 * THE CITYGATE CHURCH - CORE JAVASCRIPT SYSTEM
 * Vanilla JS Modular Component Architecture
 */

(function () {
  "use strict";

  // Global namespace
  window.CityGate = window.CityGate || {};

  /**
   * Toast Notification Controller
   */
  class ToastManager {
    constructor() {
      this.container = document.querySelector(".toast-container");
      if (!this.container) {
        this.container = document.createElement("div");
        this.container.className = "toast-container";
        document.body.appendChild(this.container);
      }
    }

    show(message, type = "info", duration = 5000) {
      const toast = document.createElement("div");
      toast.className = `toast toast-${type}`;
      toast.innerHTML = `
        <div class="toast-message">${message}</div>
        <button class="toast-close" aria-label="Close">&times;</button>
      `;

      const closeBtn = toast.querySelector(".toast-close");
      closeBtn.addEventListener("click", () => this.dismiss(toast));

      this.container.appendChild(toast);

      if (duration > 0) {
        setTimeout(() => this.dismiss(toast), duration);
      }
    }

    dismiss(toast) {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(40px)";
      setTimeout(() => {
        if (toast.parentElement) {
          toast.parentElement.removeChild(toast);
        }
      }, 300);
    }
  }

  /**
   * Modal Dialog Controller
   */
  class ModalManager {
    constructor() {
      this.init();
    }

    init() {
      // Open modal triggers
      document.addEventListener("click", (e) => {
        const trigger = e.target.closest("[data-modal-target]");
        if (trigger) {
          e.preventDefault();
          const targetId = trigger.getAttribute("data-modal-target");
          this.open(targetId);
        }

        // Close modal triggers
        const closeBtn = e.target.closest("[data-modal-close]");
        if (closeBtn) {
          e.preventDefault();
          const modal = closeBtn.closest(".modal-backdrop");
          if (modal) this.close(modal);
        }

        // Click outside modal container
        if (e.target.classList.contains("modal-backdrop")) {
          this.close(e.target);
        }
      });

      // Escape key listener
      document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
          const activeModal = document.querySelector(".modal-backdrop.is-active");
          if (activeModal) this.close(activeModal);
        }
      });
    }

    open(modalId) {
      const modal = document.getElementById(modalId);
      if (modal) {
        modal.classList.add("is-active");
        document.body.style.overflow = "hidden";
      }
    }

    close(modal) {
      modal.classList.remove("is-active");
      document.body.style.overflow = "";
    }
  }

  /**
   * CSRF Token & API Fetch Helper
   */
  function getCsrfToken() {
    const name = "csrftoken";
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  async function apiRequest(url, options = {}) {
    const defaultHeaders = {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    };

    options.headers = { ...defaultHeaders, ...options.headers };
    try {
      const response = await fetch(url, options);
      const data = await response.json();
      return { ok: response.ok, status: response.status, data };
    } catch (error) {
      console.error("API Request Error:", error);
      return { ok: false, error };
    }
  }

  /**
   * Copy to Clipboard Helper
   */
  function copyToClipboard(text, successMessage = "Copied to clipboard!") {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text).then(() => {
        window.CityGate.toast.show(successMessage, "success");
      });
    }
  }

  // Export to window
  window.CityGate.toast = new ToastManager();
  window.CityGate.modal = new ModalManager();
  window.CityGate.getCsrfToken = getCsrfToken;
  window.CityGate.apiRequest = apiRequest;
  window.CityGate.copyToClipboard = copyToClipboard;
})();
