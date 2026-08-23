/**
 * THE CITYGATE CHURCH - PUBLIC JAVASCRIPT CONTROLLERS
 * Interactive Audio, Video, Search Modal, Mobile Drawer & Transcripts
 * Enhanced for Keyboard Accessibility, Motion Sensitivity & Focus Trapping
 */

document.addEventListener("DOMContentLoaded", () => {
  // 1. Sticky Header Scroll Effect
  const header = document.querySelector(".site-header");
  if (header) {
    let ticking = false;
    window.addEventListener("scroll", () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          if (window.scrollY > 20) {
            header.classList.add("is-scrolled");
          } else {
            header.classList.remove("is-scrolled");
          }
          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });
  }

  // 2. Mobile Navigation Drawer & Focus Management
  const mobileToggle = document.querySelector(".mobile-nav-toggle");
  const mobileDrawer = document.getElementById("mobileNavDrawer");
  const mobileBackdrop = document.getElementById("mobileDrawerBackdrop");
  const mobileClose = document.getElementById("mobileDrawerClose");
  let lastActiveElement = null;

  function openMobileMenu() {
    if (mobileDrawer && mobileBackdrop) {
      lastActiveElement = document.activeElement;
      mobileDrawer.classList.add("is-open");
      mobileBackdrop.classList.add("is-open");
      document.body.style.overflow = "hidden";
      if (mobileClose) {
        setTimeout(() => mobileClose.focus(), 150);
      }
    }
  }

  function closeMobileMenu() {
    if (mobileDrawer && mobileBackdrop) {
      mobileDrawer.classList.remove("is-open");
      mobileBackdrop.classList.remove("is-open");
      document.body.style.overflow = "";
      if (lastActiveElement) {
        lastActiveElement.focus();
      }
    }
  }

  if (mobileToggle) mobileToggle.addEventListener("click", openMobileMenu);
  if (mobileClose) mobileClose.addEventListener("click", closeMobileMenu);
  if (mobileBackdrop) mobileBackdrop.addEventListener("click", closeMobileMenu);

  // 3. Global Search Modal (Ctrl/Cmd + K shortcut)
  const searchModal = document.getElementById("globalSearchModal");
  const searchTriggers = document.querySelectorAll("[data-search-trigger]");
  const searchClose = document.getElementById("searchModalClose");
  const searchInput = document.getElementById("globalSearchInput");

  function openSearchModal() {
    if (searchModal) {
      lastActiveElement = document.activeElement;
      searchModal.classList.add("is-open");
      document.body.style.overflow = "hidden";
      if (searchInput) {
        setTimeout(() => searchInput.focus(), 100);
      }
    }
  }

  function closeSearchModal() {
    if (searchModal) {
      searchModal.classList.remove("is-open");
      document.body.style.overflow = "";
      if (lastActiveElement) {
        lastActiveElement.focus();
      }
    }
  }

  searchTriggers.forEach(btn => btn.addEventListener("click", openSearchModal));
  if (searchClose) searchClose.addEventListener("click", closeSearchModal);

  if (searchModal) {
    searchModal.addEventListener("click", (e) => {
      if (e.target === searchModal) closeSearchModal();
    });
  }

  // Keyboard shortcut Ctrl+K or Cmd+K or Escape
  document.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      if (searchModal && searchModal.classList.contains("is-open")) {
        closeSearchModal();
      } else {
        openSearchModal();
      }
    }
    if (e.key === "Escape") {
      closeSearchModal();
      closeMobileMenu();
    }
  });

  // 4. Dedicated HTML5 Audio Player Controller
  const audioPlayers = document.querySelectorAll("[data-audio-player]");
  audioPlayers.forEach(player => {
    const audio = player.querySelector("audio");
    const playBtn = player.querySelector("[data-audio-play-btn]");
    const playIcon = player.querySelector("[data-audio-play-icon]");
    const progressFill = player.querySelector("[data-audio-progress-fill]");
    const progressBar = player.querySelector("[data-audio-progress-bar]");
    const currentTimeEl = player.querySelector("[data-audio-current-time]");
    const durationEl = player.querySelector("[data-audio-duration]");
    const speedBtn = player.querySelector("[data-audio-speed-btn]");

    if (!audio) return;

    function formatTime(seconds) {
      if (isNaN(seconds) || seconds === Infinity) return "00:00";
      const mins = Math.floor(seconds / 60);
      const secs = Math.floor(seconds % 60);
      return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
    }

    audio.addEventListener("loadedmetadata", () => {
      if (durationEl) durationEl.textContent = formatTime(audio.duration);
    });

    audio.addEventListener("timeupdate", () => {
      if (currentTimeEl) currentTimeEl.textContent = formatTime(audio.currentTime);
      if (progressFill && audio.duration) {
        const pct = (audio.currentTime / audio.duration) * 100;
        progressFill.style.width = `${pct}%`;
      }
    });

    audio.addEventListener("ended", () => {
      if (playIcon) playIcon.textContent = "▶";
      if (progressFill) progressFill.style.width = "0%";
    });

    if (playBtn) {
      playBtn.addEventListener("click", () => {
        if (audio.paused) {
          // Pause any other playing audio on the page
          document.querySelectorAll("audio").forEach(a => {
            if (a !== audio) a.pause();
          });
          audio.play().catch(err => console.warn("Audio playback error:", err));
          if (playIcon) playIcon.textContent = "⏸";
        } else {
          audio.pause();
          if (playIcon) playIcon.textContent = "▶";
        }
      });
    }

    if (progressBar) {
      progressBar.addEventListener("click", (e) => {
        const rect = progressBar.getBoundingClientRect();
        const clickPos = (e.clientX - rect.left) / rect.width;
        if (audio.duration) {
          audio.currentTime = Math.max(0, Math.min(clickPos * audio.duration, audio.duration));
        }
      });
    }

    // Speed cycling: 1.0x -> 1.25x -> 1.5x -> 2.0x -> 1.0x
    if (speedBtn) {
      const speeds = [1.0, 1.25, 1.5, 2.0];
      let speedIdx = 0;
      speedBtn.addEventListener("click", () => {
        speedIdx = (speedIdx + 1) % speeds.length;
        const newSpeed = speeds[speedIdx];
        audio.playbackRate = newSpeed;
        speedBtn.textContent = `${newSpeed}x`;
      });
    }
  });

  // 5. Transcript Font Sizing Controller
  const transcriptContent = document.getElementById("transcriptContent");
  const fontIncreaseBtn = document.getElementById("fontIncreaseBtn");
  const fontDecreaseBtn = document.getElementById("fontDecreaseBtn");

  if (transcriptContent && fontIncreaseBtn && fontDecreaseBtn) {
    let currentFontSize = 16;
    fontIncreaseBtn.addEventListener("click", () => {
      if (currentFontSize < 24) {
        currentFontSize += 2;
        transcriptContent.style.fontSize = `${currentFontSize}px`;
      }
    });
    fontDecreaseBtn.addEventListener("click", () => {
      if (currentFontSize > 12) {
        currentFontSize -= 2;
        transcriptContent.style.fontSize = `${currentFontSize}px`;
      }
    });
  }

  // 6. Social Share / Copy Link Helper
  const shareCopyBtns = document.querySelectorAll("[data-share-copy]");
  shareCopyBtns.forEach(btn => {
    btn.addEventListener("click", async () => {
      const url = btn.getAttribute("data-share-url") || window.location.href;
      try {
        await navigator.clipboard.writeText(url);
        if (window.CityGate && window.CityGate.toast) {
          window.CityGate.toast.show("Link copied to clipboard!", "success");
        } else {
          alert("Link copied to clipboard!");
        }
      } catch (err) {
        console.error("Clipboard copy failed:", err);
      }
    });
  });
});
