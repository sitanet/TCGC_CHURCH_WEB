/**
 * THE CITYGATE CHURCH - CUSTOM ADMINISTRATIVE DASHBOARD JAVASCRIPT
 * Handles mobile sidebar drawer, form tabs, audio previews, modal confirmations, and dynamic inlines.
 */

document.addEventListener('DOMContentLoaded', () => {
  initMobileSidebar();
  initFormTabs();
  initAudioPlayers();
  initDeleteConfirmModals();
  initScriptureInlines();
});

/**
 * 1. Mobile Sidebar Toggle & Backdrop
 */
function initMobileSidebar() {
  const sidebar = document.getElementById('dashboardSidebar');
  const backdrop = document.getElementById('sidebarBackdrop');
  const toggleBtn = document.getElementById('mobileSidebarToggle');
  const closeBtn = document.getElementById('sidebarCloseBtn');

  if (!sidebar) return;

  function openSidebar() {
    sidebar.classList.add('is-open');
    if (backdrop) backdrop.classList.add('is-open');
  }

  function closeSidebar() {
    sidebar.classList.remove('is-open');
    if (backdrop) backdrop.classList.remove('is-open');
  }

  if (toggleBtn) toggleBtn.addEventListener('click', openSidebar);
  if (closeBtn) closeBtn.addEventListener('click', closeSidebar);
  if (backdrop) backdrop.addEventListener('click', closeSidebar);
}

/**
 * 2. Multi-Section Form Tabs
 */
function initFormTabs() {
  const tabBtns = document.querySelectorAll('[data-form-tab]');
  const tabPanes = document.querySelectorAll('[data-form-pane]');

  if (!tabBtns.length) return;

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetPaneId = btn.getAttribute('data-form-tab');

      tabBtns.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetPane = document.getElementById(targetPaneId);
      if (targetPane) {
        targetPane.classList.add('active');
      }
    });
  });
}

/**
 * 3. Dedicated HTML5 Audio Player Controller
 */
function initAudioPlayers() {
  const audioCards = document.querySelectorAll('[data-audio-player]');

  audioCards.forEach(card => {
    const audio = card.querySelector('audio');
    const playBtn = card.querySelector('[data-audio-play]');
    const progressFill = card.querySelector('[data-audio-fill]');
    const progressBar = card.querySelector('[data-audio-bar]');
    const timeDisplay = card.querySelector('[data-audio-time]');
    const speedSelect = card.querySelector('[data-audio-speed]');

    if (!audio || !playBtn) return;

    playBtn.addEventListener('click', () => {
      if (audio.paused) {
        // Pause any other playing audio
        document.querySelectorAll('audio').forEach(a => {
          if (a !== audio) a.pause();
        });
        audio.play();
        playBtn.textContent = '⏸';
      } else {
        audio.pause();
        playBtn.textContent = '▶';
      }
    });

    audio.addEventListener('timeupdate', () => {
      if (audio.duration) {
        const percent = (audio.currentTime / audio.duration) * 100;
        if (progressFill) progressFill.style.width = `${percent}%`;
        if (timeDisplay) {
          timeDisplay.textContent = `${formatTime(audio.currentTime)} / ${formatTime(audio.duration)}`;
        }
      }
    });

    audio.addEventListener('ended', () => {
      playBtn.textContent = '▶';
      if (progressFill) progressFill.style.width = '0%';
    });

    if (progressBar) {
      progressBar.addEventListener('click', (e) => {
        const rect = progressBar.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const percent = clickX / rect.width;
        if (audio.duration) {
          audio.currentTime = percent * audio.duration;
        }
      });
    }

    if (speedSelect) {
      speedSelect.addEventListener('change', () => {
        audio.playbackRate = parseFloat(speedSelect.value) || 1.0;
      });
    }
  });

  function formatTime(seconds) {
    if (isNaN(seconds)) return '00:00';
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  }
}

/**
 * 4. Generic Delete Confirmation Modal Trigger
 */
function initDeleteConfirmModals() {
  const deleteModal = document.getElementById('deleteConfirmModal');
  const deleteForm = document.getElementById('deleteConfirmForm');
  const deleteMsg = document.getElementById('deleteConfirmMessage');

  if (!deleteModal || !deleteForm) return;

  document.querySelectorAll('[data-delete-trigger]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const actionUrl = btn.getAttribute('data-delete-url');
      const itemTitle = btn.getAttribute('data-item-title') || 'this item';

      deleteForm.setAttribute('action', actionUrl);
      if (deleteMsg) {
        deleteMsg.textContent = `Are you sure you want to permanently delete "${itemTitle}"? This operation is immediate.`;
      }
      deleteModal.classList.add('is-open');
    });
  });
}

/**
 * 5. Dynamic Scripture Reference Inlines in Teachings Form
 */
function initScriptureInlines() {
  const addBtn = document.getElementById('addScriptureRowBtn');
  const container = document.getElementById('scriptureRowsContainer');

  if (!addBtn || !container) return;

  addBtn.addEventListener('click', () => {
    const row = document.createElement('div');
    row.className = 'scripture-row';
    row.style.cssText = 'display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 4fr auto; gap: var(--space-2); margin-bottom: var(--space-3); align-items: center;';
    row.innerHTML = `
      <input type="text" name="scripture_book[]" class="form-input" placeholder="Book (e.g. Romans)" required>
      <input type="number" name="scripture_chapter[]" class="form-input" placeholder="Chap." min="1" required>
      <input type="number" name="scripture_verse_start[]" class="form-input" placeholder="From" min="1" required>
      <input type="number" name="scripture_verse_end[]" class="form-input" placeholder="To" min="1">
      <input type="text" name="scripture_text[]" class="form-input" placeholder="Scripture quote / text">
      <button type="button" class="btn btn-sm btn-ghost" style="color: var(--color-danger);" onclick="this.closest('.scripture-row').remove();">&times;</button>
    `;
    container.appendChild(row);
  });
}
