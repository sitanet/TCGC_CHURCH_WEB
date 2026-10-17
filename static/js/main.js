/**
 * The CityGate Church (TCGC Web) — Interactive Frontend Logic
 * Includes full IMGC 2026 Registration & Service Team Feeding Logic from TCGC_BACKEND
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Toast Notification Helper
    function showToast(message, type = 'success') {
        const container = document.getElementById('tcgc-toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `tcgc-toast tcgc-toast-${type}`;
        toast.innerHTML = `
            <span>${message}</span>
            <button type="button" class="tcgc-toast-close" aria-label="Close">&times;</button>
        `;
        toast.querySelector('.tcgc-toast-close').addEventListener('click', () => toast.remove());
        container.appendChild(toast);

        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 6000);
    }

    // =========================================================================
    // 2. IMGC 2026 Conference Registration Interactive Logic (from /imgc/)
    // =========================================================================
    const modeCards = document.querySelectorAll('.tcgc-mode-card');
    const modeInput = document.getElementById('selected_attendance_mode');
    const designationSelect = document.getElementById('reg_designation');
    const otherDesignationGroup = document.getElementById('otherDesignationGroup');
    const otherDesignationInput = document.getElementById('other_designation');
    const workerFeedingSection = document.getElementById('workerFeedingSection');
    const nonCampingFullLabel = document.getElementById('nonCampingFullLabel');

    const campingBox = document.getElementById('campingFeedingBox');
    const nonCampingBox = document.getElementById('nonCampingFeedingBox');
    const onlineBox = document.getElementById('onlineStreamingBox');
    const campingInputs = document.querySelectorAll('.camping-feed-input');
    const nonCampingInputs = document.querySelectorAll('.non-camping-feed-input');
    const onlineNoneInput = document.getElementById('feedOnlineNone');

    const formatNaira = (amt) =>
        '₦' + amt.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

    function updateWorkerPrice(selectedCount) {
        const rateInput = document.getElementById('serviceTeamDailyRate');
        const dailyRate = parseFloat(rateInput ? rateInput.value : '1500') || 1500;
        const count = selectedCount !== undefined && selectedCount !== null ? selectedCount : 5;
        const totalAmount = count * dailyRate;

        const totalDisplay = document.getElementById('workerTotalAmountDisplay');
        const rateCalcDisplay = document.getElementById('workerRateCalcDisplay');
        const daysCountLabel = document.getElementById('workerDaysCountLabel');
        const section3Badge = document.getElementById('section3PriceBadge');

        if (totalDisplay) totalDisplay.textContent = formatNaira(totalAmount);
        if (rateCalcDisplay) rateCalcDisplay.textContent = formatNaira(dailyRate) + ' / Day';
        if (daysCountLabel) {
            if (count === 5) {
                daysCountLabel.textContent = `All 5 Conference Days (${formatNaira(totalAmount)})`;
            } else if (count > 0) {
                daysCountLabel.textContent = `${count} Day${count > 1 ? 's' : ''} (${formatNaira(totalAmount)})`;
            } else {
                daysCountLabel.textContent = '0 Days Selected';
            }
        }
        if (section3Badge) {
            section3Badge.textContent = 'Total: ' + formatNaira(totalAmount);
        }
    }

    function handleLunchSelection(isLunchOnly) {
        const selector = document.getElementById('workerDaysSelector');
        if (!selector) return;
        const designation = designationSelect ? designationSelect.value : '';
        if (isLunchOnly && designation === 'church_worker') {
            selector.style.display = 'block';
        } else {
            selector.style.display = 'none';
        }
    }

    function selectAttendanceMode(mode) {
        if (!modeCards.length || !modeInput) return;

        modeCards.forEach((c) => {
            const isMatch = c.getAttribute('data-mode') === mode;
            c.classList.toggle('active', isMatch);
            c.setAttribute('aria-pressed', isMatch ? 'true' : 'false');
        });
        modeInput.value = mode;

        if (campingBox) campingBox.style.display = 'none';
        if (nonCampingBox) nonCampingBox.style.display = 'none';
        if (onlineBox) onlineBox.style.display = 'none';

        campingInputs.forEach((i) => (i.disabled = true));
        nonCampingInputs.forEach((i) => (i.disabled = true));
        if (onlineNoneInput) onlineNoneInput.disabled = true;

        if (mode === 'camping') {
            if (campingBox) campingBox.style.display = 'block';
            campingInputs.forEach((i) => (i.disabled = false));
            const hasChecked = Array.from(campingInputs).some((i) => i.checked);
            if (!hasChecked) {
                const defaultFeed = document.getElementById('feedCampingFull');
                if (defaultFeed) defaultFeed.checked = true;
            }
            handleLunchSelection(false);
        } else if (mode === 'non_camping') {
            if (nonCampingBox) nonCampingBox.style.display = 'block';
            nonCampingInputs.forEach((i) => (i.disabled = false));
            const hasChecked = Array.from(nonCampingInputs).some((i) => i.checked);
            if (!hasChecked) {
                const defaultFeed = document.getElementById('feedNonCampingLunch');
                if (defaultFeed) defaultFeed.checked = true;
            }
            const lunchRadio = document.getElementById('feedNonCampingLunch');
            handleLunchSelection(lunchRadio ? lunchRadio.checked : false);
        } else if (mode === 'online') {
            if (onlineBox) onlineBox.style.display = 'block';
            if (onlineNoneInput) onlineNoneInput.disabled = false;
            handleLunchSelection(false);
        }
    }

    function toggleDayScope(scope) {
        const container = document.getElementById('dayCheckboxesContainer');
        const hiddenInput = document.getElementById('finalFeedingDays');
        const badge = document.getElementById('selectedDaysBadge');
        const checkboxes = document.querySelectorAll('.day-check');

        if (scope === 'all') {
            if (container) container.style.display = 'none';
            checkboxes.forEach((cb) => {
                cb.checked = true;
                const parent = cb.closest('.tcgc-day-pill');
                if (parent) parent.classList.add('active');
            });
            if (hiddenInput) hiddenInput.value = 'All Days';
            if (badge) badge.textContent = 'All 5 Days';
            updateWorkerPrice(5);
        } else {
            if (container) container.style.display = 'grid';
            updateSelectedDaysSummary();
        }
    }

    function updateSelectedDaysSummary() {
        const checkboxes = document.querySelectorAll('.day-check');
        const hiddenInput = document.getElementById('finalFeedingDays');
        const badge = document.getElementById('selectedDaysBadge');
        const workerCbs = document.querySelectorAll('.worker-day-cb');
        const workerSummary = document.getElementById('workerDaysSummaryText');

        const selected = [];
        checkboxes.forEach((cb, idx) => {
            const parent = cb.closest('.tcgc-day-pill');
            if (cb.checked) {
                selected.push(cb.value);
                if (parent) parent.classList.add('active');
                if (workerCbs[idx]) {
                    workerCbs[idx].checked = true;
                    const wp = workerCbs[idx].closest('.tcgc-day-pill');
                    if (wp) wp.classList.add('active');
                }
            } else {
                if (parent) parent.classList.remove('active');
                if (workerCbs[idx]) {
                    workerCbs[idx].checked = false;
                    const wp = workerCbs[idx].closest('.tcgc-day-pill');
                    if (wp) wp.classList.remove('active');
                }
            }
        });

        if (selected.length === 0) {
            if (hiddenInput) hiddenInput.value = '';
            if (badge) badge.textContent = '0 Days Selected';
            if (workerSummary) workerSummary.textContent = 'No days selected (Please check at least 1 day)';
            updateWorkerPrice(0);
        } else if (selected.length === 5) {
            if (hiddenInput) hiddenInput.value = 'All Days';
            if (badge) badge.textContent = 'All 5 Days';
            if (workerSummary) workerSummary.textContent = 'Subscribing to Lunch for: All 5 Days';
            updateWorkerPrice(5);
        } else {
            const daysStr = selected.join(', ');
            if (hiddenInput) hiddenInput.value = daysStr;
            if (badge) badge.textContent = `${selected.length} Day${selected.length > 1 ? 's' : ''} (${daysStr})`;
            if (workerSummary) workerSummary.textContent = `Subscribing to Lunch for: ${selected.length} Day(s) (${daysStr})`;
            updateWorkerPrice(selected.length);
        }
    }

    function updateWorkerDays() {
        const workerCbs = document.querySelectorAll('.worker-day-cb');
        const section3Cbs = document.querySelectorAll('.day-check');
        const workerSummary = document.getElementById('workerDaysSummaryText');
        const selected = [];

        workerCbs.forEach((cb, idx) => {
            const parent = cb.closest('.tcgc-day-pill');
            if (cb.checked) {
                selected.push(cb.value);
                if (parent) parent.classList.add('active');
                if (section3Cbs[idx]) {
                    section3Cbs[idx].checked = true;
                    const p3 = section3Cbs[idx].closest('.tcgc-day-pill');
                    if (p3) p3.classList.add('active');
                }
            } else {
                if (parent) parent.classList.remove('active');
                if (section3Cbs[idx]) {
                    section3Cbs[idx].checked = false;
                    const p3 = section3Cbs[idx].closest('.tcgc-day-pill');
                    if (p3) p3.classList.remove('active');
                }
            }
        });

        const hiddenInput = document.getElementById('finalFeedingDays');
        const badge = document.getElementById('selectedDaysBadge');

        if (selected.length === 0) {
            if (hiddenInput) hiddenInput.value = '';
            if (badge) badge.textContent = '0 Days Selected';
            if (workerSummary) workerSummary.textContent = 'No days selected (Please select at least 1 day)';
            updateWorkerPrice(0);
        } else if (selected.length === 5) {
            if (hiddenInput) hiddenInput.value = 'All Days';
            if (badge) badge.textContent = 'All 5 Days';
            if (workerSummary) workerSummary.textContent = 'Subscribing to Lunch for: All 5 Days';
            updateWorkerPrice(5);
        } else {
            const daysStr = selected.join(', ');
            if (hiddenInput) hiddenInput.value = daysStr;
            if (badge) badge.textContent = `${selected.length} Day${selected.length > 1 ? 's' : ''} (${daysStr})`;
            if (workerSummary) workerSummary.textContent = `Subscribing to Lunch for: ${selected.length} Day(s) (${daysStr})`;
            updateWorkerPrice(selected.length);
        }
    }

    function setWorkerScope(scope) {
        const workerBoxes = document.getElementById('workerDayCheckboxes');
        const workerSummary = document.getElementById('workerDaysSummaryText');
        const workerCbs = document.querySelectorAll('.worker-day-cb');
        const scopeAll = document.getElementById('scopeAllDays');
        const scopeSelected = document.getElementById('scopeSelectedDays');

        if (scope === 'all') {
            if (workerBoxes) workerBoxes.style.display = 'none';
            workerCbs.forEach((cb) => {
                cb.checked = true;
                const parent = cb.closest('.tcgc-day-pill');
                if (parent) parent.classList.add('active');
            });
            if (scopeAll) scopeAll.checked = true;
            toggleDayScope('all');
            if (workerSummary) workerSummary.textContent = 'Subscribing to Lunch for: All 5 Days';
            updateWorkerPrice(5);
        } else {
            if (workerBoxes) workerBoxes.style.display = 'grid';
            if (scopeSelected) scopeSelected.checked = true;
            toggleDayScope('selected');
            updateWorkerDays();
        }
    }

    function handleWorkerLunchChoice(choice) {
        const innerContainer = document.getElementById('workerDaysInnerContainer');
        if (choice === 'lunch_only') {
            if (innerContainer) innerContainer.style.display = 'block';
            selectAttendanceMode('non_camping');
            const lunchRadio = document.getElementById('feedNonCampingLunch');
            if (lunchRadio) {
                lunchRadio.checked = true;
                handleLunchSelection(true);
            }
            updateWorkerDays();
        } else {
            if (innerContainer) innerContainer.style.display = 'none';
            const noneRadio = document.getElementById('feedNonCampingNone');
            if (noneRadio) {
                noneRadio.checked = true;
                handleLunchSelection(false);
            }
            const hiddenInput = document.getElementById('finalFeedingDays');
            if (hiddenInput) hiddenInput.value = '';
            updateWorkerPrice(0);
        }
    }

    function handleDesignationChange(value) {
        if (otherDesignationGroup) {
            const isOther = value === 'other';
            otherDesignationGroup.style.display = isOther ? 'block' : 'none';
            if (otherDesignationInput) otherDesignationInput.required = isOther;
        }

        if (value === 'church_worker') {
            if (workerFeedingSection) {
                workerFeedingSection.style.display = 'block';
                const currentMode = modeInput ? modeInput.value : 'camping';
                if (currentMode !== 'camping') {
                    selectAttendanceMode('non_camping');
                } else {
                    selectAttendanceMode('non_camping');
                }
                const lunchRadio = document.getElementById('feedNonCampingLunch');
                if (lunchRadio) {
                    lunchRadio.checked = true;
                    handleLunchSelection(true);
                }
                updateWorkerPrice(5);
            }
            if (nonCampingFullLabel) nonCampingFullLabel.style.display = 'none';
        } else {
            if (workerFeedingSection) workerFeedingSection.style.display = 'none';
            if (nonCampingFullLabel) nonCampingFullLabel.style.display = 'block';
            handleLunchSelection(false);
        }
    }

    // Wire up IMGC Registration event listeners if on the Registration page
    if (modeCards.length && modeInput) {
        modeCards.forEach((card) => {
            const triggerSelect = () => selectAttendanceMode(card.getAttribute('data-mode'));
            card.addEventListener('click', triggerSelect);
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    triggerSelect();
                }
            });
        });

        if (designationSelect) {
            designationSelect.addEventListener('change', (e) => handleDesignationChange(e.target.value));
        }

        const workerLunchYes = document.getElementById('workerLunchYes');
        const workerLunchNo = document.getElementById('workerLunchNo');
        if (workerLunchYes) workerLunchYes.addEventListener('change', () => handleWorkerLunchChoice('lunch_only'));
        if (workerLunchNo) workerLunchNo.addEventListener('change', () => handleWorkerLunchChoice('none'));

        const workerScopeAll = document.getElementById('workerScopeAll');
        const workerScopeSelected = document.getElementById('workerScopeSelected');
        if (workerScopeAll) workerScopeAll.addEventListener('change', () => setWorkerScope('all'));
        if (workerScopeSelected) workerScopeSelected.addEventListener('change', () => setWorkerScope('selected'));

        document.querySelectorAll('.worker-day-cb').forEach((cb) => {
            cb.addEventListener('change', updateWorkerDays);
        });

        const scopeAllDays = document.getElementById('scopeAllDays');
        const scopeSelectedDays = document.getElementById('scopeSelectedDays');
        if (scopeAllDays) scopeAllDays.addEventListener('change', () => toggleDayScope('all'));
        if (scopeSelectedDays) scopeSelectedDays.addEventListener('change', () => toggleDayScope('selected'));

        document.querySelectorAll('.day-check').forEach((cb) => {
            cb.addEventListener('change', updateSelectedDaysSummary);
        });

        nonCampingInputs.forEach((input) => {
            input.addEventListener('change', () => {
                const lunchRadio = document.getElementById('feedNonCampingLunch');
                handleLunchSelection(lunchRadio ? lunchRadio.checked : false);
            });
        });

        // Initialize initial state
        selectAttendanceMode(modeInput.value || 'camping');
        if (designationSelect && designationSelect.value) {
            handleDesignationChange(designationSelect.value);
        }
        updateWorkerPrice(5);
    }

    // 3. AJAX Form Submissions (Give Online, Conference Registration, Newsletter)
    const ajaxForms = [
        document.getElementById('give-online-form'),
        document.getElementById('conference-reg-form'),
        document.getElementById('newsletter-form'),
    ].filter(Boolean);

    ajaxForms.forEach((form) => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalHTML = submitBtn ? submitBtn.innerHTML : '';
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.style.opacity = '0.75';
                if (form.id === 'conference-reg-form') {
                    submitBtn.innerHTML = '<span>Processing Registration...</span>';
                }
            }

            try {
                const formData = new FormData(form);
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                });
                const data = await response.json();
                if (response.ok && (data.status === 'success' || data.success)) {
                    showToast(data.message || 'Submitted successfully!', 'success');
                    if (data.redirect_url) {
                        window.location.href = data.redirect_url;
                        return;
                    }
                    form.reset();
                } else {
                    showToast(data.message || 'Please check your input and try again.', 'error');
                    if (data.existing_code && data.redirect_url) {
                        // Show or update duplicate registration warning banner at top of card
                        let dupBanner = document.getElementById('duplicate-warning-banner');
                        if (!dupBanner) {
                            dupBanner = document.createElement('div');
                            dupBanner.id = 'duplicate-warning-banner';
                            dupBanner.className = 'tcgc-reg-group tcgc-dup-alert';
                            form.parentNode.insertBefore(dupBanner, form);
                        }
                        dupBanner.innerHTML = `
                            <h4 class="tcgc-dup-alert-title">Already Registered for IMGC 2026!</h4>
                            <p class="tcgc-dup-alert-desc">${data.errors?.duplicate || data.message}</p>
                            <div class="tcgc-dup-alert-actions">
                                <a href="${data.redirect_url}" class="tcgc-btn-dup-view">
                                    <span>View Existing Registration (${data.existing_code})</span>
                                    <span class="tcgc-arrow-long">&#8594;</span>
                                </a>
                            </div>
                        `;
                        dupBanner.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }
            } catch (err) {
                // Fallback to normal submit if network/JSON fails
                form.submit();
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.style.opacity = '1';
                    submitBtn.innerHTML = originalHTML;
                }
            }
        });
    });

    // 4. @dcitygatechurch YouTube Channel Integration (Home & Watch Live Pages)
    const buildEmbedUrlWithOrigin = (rawUrl) => {
        if (!rawUrl) {
            return `https://www.youtube-nocookie.com/embed/Pp7ehJeLbxw?autoplay=1&rel=0&enablejsapi=1&origin=${encodeURIComponent(window.location.origin)}`;
        }
        if (rawUrl.includes('origin=')) return rawUrl;
        const sep = rawUrl.includes('?') ? '&' : '?';
        return `${rawUrl}${sep}origin=${encodeURIComponent(window.location.origin)}`;
    };

    // 4a. Home Page Inline @dcitygatechurch YouTube Player
    const homePlayerCard = document.getElementById('home-video-player-card');
    const triggerHomeYtBtn = document.getElementById('trigger-home-youtube-embed');
    const homeYtContainer = document.getElementById('home-youtube-iframe-container');
    const homeYtIframe = document.getElementById('tcgc-home-yt-iframe');
    const homePosterOverlay = document.getElementById('home-video-poster-overlay');

    if (triggerHomeYtBtn && homeYtContainer && homeYtIframe && homePlayerCard) {
        triggerHomeYtBtn.addEventListener('click', () => {
            const embedUrl = homePlayerCard.getAttribute('data-embed-url');
            homeYtIframe.src = buildEmbedUrlWithOrigin(embedUrl);
            if (homePosterOverlay) homePosterOverlay.style.display = 'none';
            homeYtContainer.style.display = 'block';
        });
    }

    // 4b. Watch Live Page @dcitygatechurch YouTube Player, Source Switcher & Refresh
    const videoPlayerCard = document.getElementById('video-player-card');
    const triggerYtBtn = document.getElementById('trigger-youtube-embed');
    const ytContainer = document.getElementById('youtube-iframe-container');
    const ytIframe = document.getElementById('tcgc-yt-iframe');
    const posterOverlay = document.getElementById('video-poster-overlay');
    const btnSourceDirect = document.getElementById('btnSourceDirect');
    const btnSourceChannel = document.getElementById('btnSourceChannel');
    const btnRefreshLiveVideo = document.getElementById('btnRefreshLiveVideo');
    const refreshVideoIcon = document.getElementById('refreshVideoIcon');
    const liveVideoTitle = document.getElementById('liveVideoTitle');
    const liveBadgeIndicator = document.getElementById('liveBadgeIndicator');
    const openYouTubeBtn = document.getElementById('openYouTubeBtn');

    let currentVideoSourceMode = 'direct'; // 'direct' or 'channel'

    const startWatchLivePlayer = (customEmbedUrl = null) => {
        if (!videoPlayerCard || !ytContainer || !ytIframe) return;
        let targetUrl = customEmbedUrl;
        if (!targetUrl) {
            targetUrl =
                currentVideoSourceMode === 'channel'
                    ? videoPlayerCard.getAttribute('data-channel-embed-url')
                    : videoPlayerCard.getAttribute('data-embed-url');
        }
        ytIframe.src = buildEmbedUrlWithOrigin(targetUrl);
        if (posterOverlay) posterOverlay.style.display = 'none';
        ytContainer.style.display = 'block';
    };

    if (triggerYtBtn) {
        triggerYtBtn.addEventListener('click', () => {
            startWatchLivePlayer();
        });
    }

    if (btnSourceDirect && btnSourceChannel && videoPlayerCard) {
        btnSourceDirect.addEventListener('click', () => {
            currentVideoSourceMode = 'direct';
            btnSourceDirect.classList.add('active');
            btnSourceChannel.classList.remove('active');
            startWatchLivePlayer();
            showToast('Switched to @dcitygatechurch Live Video stream');
        });

        btnSourceChannel.addEventListener('click', () => {
            currentVideoSourceMode = 'channel';
            btnSourceChannel.classList.add('active');
            btnSourceDirect.classList.remove('active');
            startWatchLivePlayer();
            showToast('Switched to @dcitygatechurch Channel Stream feed');
        });
    }

    if (btnRefreshLiveVideo && videoPlayerCard) {
        btnRefreshLiveVideo.addEventListener('click', async () => {
            if (refreshVideoIcon) refreshVideoIcon.classList.add('tcgc-spin');
            showToast('Checking @dcitygatechurch for live broadcast updates...');
            try {
                const res = await fetch('/api/live-video/?force=1');
                if (res.ok) {
                    const data = await res.json();
                    if (data.embed_url) videoPlayerCard.setAttribute('data-embed-url', data.embed_url);
                    if (data.channel_embed_url) videoPlayerCard.setAttribute('data-channel-embed-url', data.channel_embed_url);
                    if (data.watch_url) {
                        videoPlayerCard.setAttribute('data-watch-url', data.watch_url);
                        if (openYouTubeBtn) openYouTubeBtn.href = data.watch_url;
                    }
                    if (data.thumbnail_url) {
                        videoPlayerCard.style.backgroundImage = `url('${data.thumbnail_url}')`;
                        if (homePlayerCard) homePlayerCard.style.backgroundImage = `url('${data.thumbnail_url}')`;
                    }
                    if (liveVideoTitle && data.video_title) {
                        liveVideoTitle.textContent = data.video_title;
                    }
                    if (liveBadgeIndicator) {
                        liveBadgeIndicator.classList.toggle('is-live', Boolean(data.is_live));
                        liveBadgeIndicator.textContent = data.is_live ? '● LIVE NOW' : '● SERVICE BROADCAST';
                    }
                    if (ytContainer && ytContainer.style.display !== 'none') {
                        startWatchLivePlayer();
                    }
                    showToast('Live broadcast synchronized with @dcitygatechurch!');
                }
            } catch (err) {
                showToast('Unable to refresh right now. Please try again.');
            } finally {
                if (refreshVideoIcon) refreshVideoIcon.classList.remove('tcgc-spin');
            }
        });
    }

    // Recent @dcitygatechurch Video Cards on Watch Live Page
    const recentVideoCards = document.querySelectorAll('.tcgc-yt-recent-card');
    recentVideoCards.forEach((card) => {
        const playRecentCard = () => {
            const embedUrl = card.getAttribute('data-embed-url');
            const watchUrl = card.getAttribute('data-watch-url');
            const title = card.getAttribute('data-video-title');
            const thumbImg = card.querySelector('img');
            const thumbUrl = thumbImg ? thumbImg.src : null;
            if (videoPlayerCard && embedUrl) {
                videoPlayerCard.setAttribute('data-embed-url', embedUrl);
                if (thumbUrl) videoPlayerCard.style.backgroundImage = `url('${thumbUrl}')`;
                if (liveVideoTitle && title) liveVideoTitle.textContent = title;
                if (openYouTubeBtn && watchUrl) openYouTubeBtn.href = watchUrl;
                currentVideoSourceMode = 'direct';
                if (btnSourceDirect && btnSourceChannel) {
                    btnSourceDirect.classList.add('active');
                    btnSourceChannel.classList.remove('active');
                }
                startWatchLivePlayer(embedUrl);
                videoPlayerCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        };
        card.addEventListener('click', playRecentCard);
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                playRecentCard();
            }
        });
    });

    // 5. Audio Streaming Page Interactive Broadcast Controls + Official Mixlr Embed (Node 138:633)
    const audioWidget = document.getElementById('audio-player-widget');
    const audioPlayBtn = document.getElementById('audio-play-btn');
    const audioMuteBtn = document.getElementById('audio-mute-btn');
    const audioLikeBtn = document.getElementById('audio-like-btn');
    const audioLikeCount = document.getElementById('audio-like-count');
    const audioStatusText = document.getElementById('audio-live-status');
    const mixlrContainer = document.getElementById('mixlr-live-container');
    const mixlrFrame = document.getElementById('mixlrLiveFrame');

    if (audioWidget && audioPlayBtn) {
        let isPlaying = false;
        let isMuted = false;
        let likes = 0;

        audioPlayBtn.addEventListener('click', () => {
            isPlaying = !isPlaying;
            audioWidget.classList.toggle('playing', isPlaying);

            if (isPlaying) {
                if (mixlrContainer && mixlrFrame) {
                    mixlrContainer.style.display = 'block';
                    if (!mixlrFrame.src || mixlrFrame.src === window.location.href) {
                        mixlrFrame.src = mixlrFrame.getAttribute('data-src') || 'https://dcitygatechurch.mixlr.com/embed';
                    }
                }
                if (audioStatusText) {
                    audioStatusText.textContent = '● Live Audio Stream Active — dcitygatechurch (Mixlr)';
                }
                showToast('Connected to dcitygatechurch Live Audio Broadcast.', 'success');
            } else {
                if (audioStatusText) {
                    audioStatusText.textContent = 'Stream Paused';
                }
            }
        });

        if (audioMuteBtn) {
            audioMuteBtn.addEventListener('click', () => {
                isMuted = !isMuted;
                if (audioStatusText && isPlaying) {
                    audioStatusText.textContent = isMuted
                        ? '● Live Audio Stream (Muted)'
                        : '● Live Audio Stream Active — dcitygatechurch (Mixlr)';
                }
            });
        }

        if (audioLikeBtn && audioLikeCount) {
            audioLikeBtn.addEventListener('click', () => {
                likes += 1;
                audioLikeCount.textContent = `+${likes}`;
            });
        }
    }

    // 6. Responsive Mobile Navigation Toggle
    const mobileToggles = document.querySelectorAll('.tcgc-mobile-toggle');
    mobileToggles.forEach((toggle) => {
        const header = toggle.closest('.tcgc-header');
        const nav = header ? header.querySelector('.tcgc-nav') : null;
        if (!nav) return;

        toggle.addEventListener('click', () => {
            const isOpen = nav.classList.toggle('is-open');
            toggle.classList.toggle('is-active', isOpen);
            toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });

        nav.querySelectorAll('a').forEach((link) => {
            link.addEventListener('click', () => {
                nav.classList.remove('is-open');
                toggle.classList.remove('is-active');
                toggle.setAttribute('aria-expanded', 'false');
            });
        });
    });
});
