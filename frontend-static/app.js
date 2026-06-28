/**
 * Personalized Networking Assistant - Frontend JavaScript Logic
 * Works in API mode (connected to FastAPI) or local Demo Sandbox Mode
 */

// Application State
const state = {
    backendUrl: "http://127.0.0.1:8000",
    isDemoMode: true,
    currentGeneration: null,
    // Predefined facts for common searches in Demo Sandbox
    demoFacts: {
        "zero shot learning": {
            title: "Zero-shot learning",
            summary: "Zero-shot learning (ZSL) is a machine learning setup where, at test time, a learner observes samples from classes that were not observed during training, and needs to predict the class they belong to. Zero-shot methods generally work by associating observed and non-observed classes through some form of auxiliary information, which encodes distinguishable properties of objects.\n\nSource Reference: https://en.wikipedia.org/wiki/Zero-shot_learning"
        },
        "blockchain in healthcare": {
            title: "Blockchain in Healthcare",
            summary: "Blockchain technology is increasingly investigated for securing electronic health records, managing pharmaceutical supply chains, and tracking clinical trials. Its decentralized and cryptographic nature ensures data integrity and security across disparate healthcare systems.\n\nSource Reference: https://en.wikipedia.org/wiki/Blockchain"
        },
        "microgrids": {
            title: "Microgrid",
            summary: "A microgrid is a localized group of electricity sources and sinks that traditionally operates connected to and in synchrony with the traditional wide-area synchronous grid (macrogrid), but can also disconnect to 'island mode' and function autonomously as physical or economic conditions dictate.\n\nSource Reference: https://en.wikipedia.org/wiki/Microgrid"
        },
        "climate change": {
            title: "Climate Change",
            summary: "Climate change includes both global warming driven by human-induced emissions of greenhouse gases and the resulting large-scale shifts in weather patterns. Though there have been previous periods of climatic change, since the mid-20th century humans have had an unprecedented impact on Earth's climate system.\n\nSource Reference: https://en.wikipedia.org/wiki/Climate_change"
        }
    }
};

// ==========================================================================
// INITIALIZATION & EVENT LISTENERS
// ==========================================================================
document.addEventListener("DOMContentLoaded", () => {
    // Load Backend URL from localStorage if it exists
    const savedUrl = localStorage.getItem("pns_backend_url");
    if (savedUrl) {
        state.backendUrl = savedUrl;
        document.getElementById("backend-url-input").value = savedUrl;
    }

    // Check backend connection
    checkBackendConnection();

    // Register Tab Navigation Click Events
    const tabLinks = document.querySelectorAll(".tab-link");
    tabLinks.forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();
            switchTab(link.getAttribute("data-tab"));
        });
    });

    // Save Settings Button
    document.getElementById("save-settings-btn").addEventListener("click", () => {
        const inputUrl = document.getElementById("backend-url-input").value.trim();
        if (inputUrl) {
            state.backendUrl = inputUrl;
            localStorage.setItem("pns_backend_url", inputUrl);
            showToast("Settings saved. Connecting...", "info");
            checkBackendConnection();
        }
    });

    // Tab 1: Smart Starters Form Submit
    document.getElementById("starters-form").addEventListener("submit", handleGenerateStarters);

    // Tab 2: Fact Verification Form Submit
    document.getElementById("factcheck-form").addEventListener("submit", handleFactCheck);

    // Tab 3: Refresh Logs Button
    document.getElementById("refresh-history-btn").addEventListener("click", () => {
        loadHistoryLogs();
        showToast("Strategy logs refreshed", "success");
    });

    // Thumbs feedback buttons on starters result view
    document.getElementById("feedback-useful-btn").addEventListener("click", () => submitStarterFeedback(true));
    document.getElementById("feedback-notuseful-btn").addEventListener("click", () => submitStarterFeedback(false));
});

// ==========================================================================
// TABS NAVIGATION
// ==========================================================================
function switchTab(tabId) {
    // Deactivate all tabs and panels
    document.querySelectorAll(".tab-link").forEach(link => {
        link.classList.remove("active");
        link.setAttribute("aria-selected", "false");
    });
    document.querySelectorAll(".tab-panel").forEach(panel => {
        panel.classList.remove("active");
    });

    // Activate selected tab and panel
    const activeLink = document.querySelector(`[data-tab="${tabId}"]`);
    if (activeLink) {
        activeLink.classList.add("active");
        activeLink.setAttribute("aria-selected", "true");
    }
    
    const activePanel = document.getElementById(tabId);
    if (activePanel) {
        activePanel.classList.add("active");
    }

    // Refresh history logs specifically when history tab opens
    if (tabId === "tab-history") {
        loadHistoryLogs();
    }
}

// ==========================================================================
// API / CONNECTION LOGIC
// ==========================================================================
async function checkBackendConnection() {
    const statusDot = document.getElementById("status-dot");
    const statusText = document.getElementById("status-text");
    const modeBadge = document.getElementById("mode-badge");
    const banner = document.getElementById("connection-banner");

    statusDot.className = "status-dot";
    statusText.innerText = "Connecting...";

    try {
        const response = await fetch(`${state.backendUrl}/`, { 
            method: "GET",
            headers: { "Accept": "application/json" }
        });
        
        if (response.ok) {
            state.isDemoMode = false;
            statusDot.className = "status-dot online";
            statusText.innerText = "Connected";
            modeBadge.innerText = "API Live Mode";
            modeBadge.className = "mode-badge connected";
            banner.style.display = "none";
        } else {
            throw new Error("Backend response error status");
        }
    } catch (error) {
        console.warn("FastAPI backend offline, switching to Local Sandbox Demo Mode:", error.message);
        state.isDemoMode = true;
        statusDot.className = "status-dot offline";
        statusText.innerText = "Offline";
        modeBadge.innerText = "Demo Mode";
        modeBadge.className = "mode-badge demo";
        banner.style.display = "block";
    }
}

// ==========================================================================
// TAB 1: GENERATE CONVERSATION STARTERS
// ==========================================================================
async function handleGenerateStarters(e) {
    e.preventDefault();
    const eventDesc = document.getElementById("event-desc").value.trim();
    const interestsStr = document.getElementById("interests-input").value.trim();

    if (!eventDesc || !interestsStr) {
        showToast("Please enter both an event description and interests.", "error");
        return;
    }

    const interestsList = interestsStr.split(",").map(i => i.trim()).filter(i => i.length > 0);
    if (interestsList.length === 0) {
        showToast("Please enter at least one valid interest.", "error");
        return;
    }

    // Show loading state
    const btn = document.getElementById("generate-btn");
    const spinner = document.getElementById("generate-spinner");
    btn.disabled = true;
    spinner.style.display = "inline-block";

    // Clear previous results
    document.getElementById("starters-placeholder").style.display = "flex";
    document.getElementById("starters-results").style.display = "none";

    try {
        let result;
        if (state.isDemoMode) {
            // Simulate generation locally
            result = simulateMLStarters(eventDesc, interestsList);
            // Wait 1.2s to simulate model inference
            await new Promise(resolve => setTimeout(resolve, 1200));
        } else {
            // Make API request to FastAPI
            const response = await fetch(`${state.backendUrl}/api/generate-conversation`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ description: eventDesc, interests: interestsList })
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || "Server error generating starters");
            }
            result = await response.json();
        }

        state.currentGeneration = result;
        renderStartersResults(result);
        showToast("Conversation starters generated!", "success");
    } catch (err) {
        console.error(err);
        showToast(err.message || "Failed to generate starters.", "error");
    } finally {
        btn.disabled = false;
        spinner.style.display = "none";
    }
}

function renderStartersResults(data) {
    document.getElementById("starters-placeholder").style.display = "none";
    document.getElementById("starters-results").style.display = "flex";

    // Reset feedback buttons UI
    document.getElementById("feedback-useful-btn").className = "btn btn-success btn-outline";
    document.getElementById("feedback-notuseful-btn").className = "btn btn-danger btn-outline";
    document.getElementById("generation-feedback-section").style.display = data.id ? "block" : "none";

    // Render topics
    const topicsContainer = document.getElementById("extracted-topics-container");
    topicsContainer.innerHTML = "";
    data.topics.forEach(topic => {
        const badge = document.createElement("span");
        badge.className = "theme-badge";
        badge.innerText = topic;
        topicsContainer.appendChild(badge);
    });

    // Render starters list
    const listContainer = document.getElementById("suggestions-list");
    listContainer.innerHTML = "";
    data.suggestions.forEach(starter => {
        const card = document.createElement("div");
        card.className = "starter-card";
        card.innerHTML = `<div class="starter-text">“${starter}”</div>`;
        listContainer.appendChild(card);
    });
}

async function submitStarterFeedback(isUseful) {
    if (!state.currentGeneration || !state.currentGeneration.id) return;
    
    const dbId = state.currentGeneration.id;
    const usefulBtn = document.getElementById("feedback-useful-btn");
    const notUsefulBtn = document.getElementById("feedback-notuseful-btn");

    try {
        if (state.isDemoMode) {
            updateMockFeedback(dbId, isUseful);
        } else {
            const response = await fetch(`${state.backendUrl}/api/history/${dbId}/feedback`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ feedback: isUseful })
            });

            if (!response.ok) throw new Error("Failed to send feedback to API server");
        }

        // Update button styles to reflect active feedback state
        if (isUseful) {
            usefulBtn.className = "btn btn-success";
            notUsefulBtn.className = "btn btn-danger btn-outline";
            showToast("Marked as useful! Saved to logs.", "success");
        } else {
            usefulBtn.className = "btn btn-success btn-outline";
            notUsefulBtn.className = "btn btn-danger";
            showToast("Logged feedback. Suggestion marked as needing work.", "info");
        }
    } catch (err) {
        console.error(err);
        showToast("Error updating feedback: " + err.message, "error");
    }
}

// ==========================================================================
// TAB 2: FACT VERIFICATION
// ==========================================================================
async function handleFactCheck(e) {
    e.preventDefault();
    const query = document.getElementById("factcheck-query").value.trim();

    if (!query) {
        showToast("Please enter a term or concept to verify.", "error");
        return;
    }

    const btn = document.getElementById("factcheck-btn");
    const spinner = document.getElementById("factcheck-spinner");
    btn.disabled = true;
    spinner.style.display = "inline-block";

    document.getElementById("factcheck-placeholder").style.display = "flex";
    document.getElementById("factcheck-result").style.display = "none";

    try {
        let result;
        if (state.isDemoMode) {
            result = simulateFactCheck(query);
            // Simulate API round-trip delay
            await new Promise(resolve => setTimeout(resolve, 800));
        } else {
            const response = await fetch(`${state.backendUrl}/api/fact-check`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: query })
            });

            if (!response.ok) throw new Error("Server factcheck request failed");
            result = await response.json();
        }

        renderFactCheckResult(query, result.summary);
        showToast("Fact checked successfully", "success");
    } catch (err) {
        console.error(err);
        showToast(err.message || "Failed to perform fact verification.", "error");
    } finally {
        btn.disabled = false;
        spinner.style.display = "none";
    }
}

function renderFactCheckResult(query, summary) {
    document.getElementById("factcheck-placeholder").style.display = "none";
    const resultCard = document.getElementById("factcheck-result");
    resultCard.style.display = "block";

    document.getElementById("factcheck-result-title").innerText = query.charAt(0).toUpperCase() + query.slice(1);
    
    // Split references if source exists to highlight links
    const textElement = document.getElementById("factcheck-result-text");
    
    // Highlight Wiki Link
    const sourceMarker = "Source Reference:";
    if (summary.includes(sourceMarker)) {
        const parts = summary.split(sourceMarker);
        const urlStr = parts[1].trim();
        textElement.innerHTML = `${parts[0]}<br><br><strong>Source Reference:</strong> <a href="${urlStr}" target="_blank" class="wiki-link">${urlStr}</a>`;
    } else {
        textElement.innerText = summary;
    }
}

// ==========================================================================
// TAB 3: STRATEGY LOGS (HISTORY)
// ==========================================================================
async function loadHistoryLogs() {
    const container = document.getElementById("history-container");
    container.innerHTML = `<div class="results-placeholder"><div class="btn-spinner"></div><p>Loading history records...</p></div>`;

    try {
        let history = [];
        if (state.isDemoMode) {
            history = getMockHistory();
        } else {
            const response = await fetch(`${state.backendUrl}/api/history`);
            if (response.ok) {
                history = await response.json();
            } else {
                throw new Error("Failed to load backend logs");
            }
        }

        renderHistoryLogs(history);
    } catch (err) {
        console.error(err);
        container.innerHTML = `
            <div class="results-placeholder">
                <div class="placeholder-icon">⚠️</div>
                <p>Failed to retrieve logs. Server might be offline. Try reloading once backend is connected.</p>
            </div>
        `;
    }
}

function renderHistoryLogs(historyList) {
    const container = document.getElementById("history-container");
    container.innerHTML = "";

    if (historyList.length === 0) {
        container.innerHTML = `
            <div class="results-placeholder">
                <div class="placeholder-icon">📜</div>
                <p>No strategy logs found. Start generating conversation starters in the first tab!</p>
            </div>
        `;
        return;
    }

    historyList.forEach(item => {
        const card = document.createElement("div");
        card.className = "history-item-card";
        
        // Formulate feedback status badge
        let badgeHtml = "";
        if (item.feedback === true) {
            badgeHtml = '<span class="feedback-status-badge useful">👍 Useful</span>';
        } else if (item.feedback === false) {
            badgeHtml = '<span class="feedback-status-badge notuseful">👎 Needs Work</span>';
        } else {
            badgeHtml = '<span class="feedback-status-badge unrated">⏳ Unrated</span>';
        }

        // Format dates
        const dateFormatted = new Date(item.created_at).toLocaleString();

        // Render tags
        const interestTags = item.interests.map(i => `<span class="interest-tag">${i}</span>`).join("");
        const topicBadges = item.topics.map(t => `<span class="theme-badge">${t}</span>`).join("");

        // Render starter items
        const starterListItems = item.suggestions.map(s => `<blockquote>“${s}”</blockquote>`).join("");

        card.innerHTML = `
            <div class="history-item-header">
                <h3>Event: ${escapeHtml(item.description)}</h3>
                <span class="history-time">${dateFormatted}</span>
            </div>
            
            <div class="history-meta-section">
                <div class="history-meta-row">
                    <span class="history-meta-label">Interests</span>
                    <div class="tags-container">${interestTags}</div>
                </div>
                <div class="history-meta-row">
                    <span class="history-meta-label">Extracted Themes</span>
                    <div class="tags-container">${topicBadges}</div>
                </div>
            </div>

            <div class="history-starters-expander" id="expander-${item.id}">
                <div class="expander-header" onclick="toggleExpander(${item.id})">
                    <span>Show Generated Conversation Starters (${item.suggestions.length})</span>
                    <span class="expander-icon">▼</span>
                </div>
                <div class="expander-content">
                    ${starterListItems}
                </div>
            </div>

            <div class="history-item-footer">
                <div>
                    <span style="font-size: 0.85rem; color: var(--text-muted); margin-right: 0.5rem;">Status:</span>
                    ${badgeHtml}
                </div>
                <div class="history-actions">
                    <button class="btn btn-secondary btn-sm" onclick="rateLogItem(${item.id}, true)">Useful 👍</button>
                    <button class="btn btn-secondary btn-sm" onclick="rateLogItem(${item.id}, false)">Needs Work 👎</button>
                </div>
            </div>
        `;

        container.appendChild(card);
    });
}

window.toggleExpander = function(itemId) {
    const expander = document.getElementById(`expander-${itemId}`);
    if (expander) {
        expander.classList.toggle("open");
        const icon = expander.querySelector(".expander-icon");
        if (expander.classList.contains("open")) {
            icon.innerText = "▲";
        } else {
            icon.innerText = "▼";
        }
    }
};

window.rateLogItem = async function(itemId, isUseful) {
    try {
        if (state.isDemoMode) {
            updateMockFeedback(itemId, isUseful);
        } else {
            const response = await fetch(`${state.backendUrl}/api/history/${itemId}/feedback`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ feedback: isUseful })
            });

            if (!response.ok) throw new Error("Failed to record rating on the server");
        }

        showToast("Log feedback updated successfully", "success");
        // Reload list to update view
        loadHistoryLogs();
    } catch (err) {
        console.error(err);
        showToast("Could not update rating: " + err.message, "error");
    }
};

// ==========================================================================
// CLIENT-SIDE MOCK SANDBOX SIMULATOR
// ==========================================================================
function simulateMLStarters(description, interests) {
    // 1. Extract mock topics from description and interests
    const commonTopics = ["Machine Learning", "Sustainable Systems", "Climate Science", "Urban Transit", "Digital Assets", "Medical Security", "AI Grids"];
    const descLower = description.toLowerCase();
    
    // Take matching topics, or dynamically extract noun phrases / capitalized phrases
    let topics = [];
    interests.forEach(interest => {
        if (interest.length > 3) {
            topics.push(interest.charAt(0).toUpperCase() + interest.slice(1).toLowerCase());
        }
    });

    // Add some random keywords from description
    const descWords = description.replace(/[^a-zA-Z\s]/g, "").split(/\s+/);
    descWords.forEach(word => {
        if (word.length > 5 && word.charAt(0) === word.charAt(0).toUpperCase() && !topics.includes(word)) {
            topics.push(word);
        }
    });

    // Limit to max 3-4 topics
    topics = [...new Set(topics)].slice(0, 4);
    if (topics.length === 0) {
        topics = ["Networking", "Modern Tech"];
    }

    // 2. Generate customized templates
    const suggestions = [];
    const interestSelected1 = interests[0] || "emerging technology";
    const interestSelected2 = interests[1] || interests[0] || "innovations";
    const themeSelected = topics[0] || "smart systems";
    
    suggestions.push(`“Hi! I read in the event briefing about the focus on ${themeSelected}. How do you see the role of ${interestSelected1} shaping its future development?”`);
    suggestions.push(`“Great session. I'm really curious: in your opinion, does the integration of ${interestSelected1} present more of an engineering hurdle or a policy roadblock here?”`);
    suggestions.push(`“I was just discussing how central ${interestSelected2} has become. Do you feel this event highlights that connection, or are there major details we're overlooking?”`);

    // 3. Save to mock local storage database
    const localHistory = getMockHistory();
    const newLogId = Date.now();
    const newLogItem = {
        id: newLogId,
        description: description,
        interests: interests,
        topics: topics,
        suggestions: suggestions,
        feedback: null,
        created_at: new Date().toISOString()
    };

    localHistory.unshift(newLogItem);
    saveMockHistory(localHistory);

    return {
        id: newLogId,
        topics: topics,
        suggestions: suggestions
    };
}

function simulateFactCheck(query) {
    const qLower = query.toLowerCase().trim();
    
    // Check if we have preset text
    for (const key in state.demoFacts) {
        if (qLower.includes(key) || key.includes(qLower)) {
            return {
                summary: state.demoFacts[key].summary
            };
        }
    }

    // Default dynamic summary generator
    const capitalized = query.charAt(0).toUpperCase() + query.slice(1);
    const wikiUrl = `https://en.wikipedia.org/wiki/${encodeURIComponent(query.replace(/\s+/g, "_"))}`;
    
    return {
        summary: `${capitalized} represents a notable subject matter within its professional discipline. While Wikipedia does not host a dedicated static fallback page for this exact custom query in our demo offline vault, it is generally defined as an evolving concept associated with state-of-the-art developments, research, and application parameters.\n\nSource Reference: ${wikiUrl}`
    };
}

function getMockHistory() {
    const data = localStorage.getItem("pns_history_logs");
    return data ? JSON.parse(data) : [];
}

function saveMockHistory(historyList) {
    localStorage.setItem("pns_history_logs", JSON.stringify(historyList));
}

function updateMockFeedback(historyId, feedback) {
    const list = getMockHistory();
    const index = list.findIndex(item => item.id == historyId);
    if (index !== -1) {
        list[index].feedback = feedback;
        saveMockHistory(list);
    }
}

// ==========================================================================
// TOAST NOTIFICATIONS & HTML HELPERS
// ==========================================================================
function showToast(message, type = "success") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    
    let icon = "🔔";
    if (type === "success") icon = "✅";
    else if (type === "error") icon = "❌";
    else if (type === "info") icon = "💡";

    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <span class="toast-message">${escapeHtml(message)}</span>
    `;

    container.appendChild(toast);
    
    // Force reflow and show
    setTimeout(() => toast.classList.add("show"), 50);
    
    // Hide and remove
    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 400);
    }, 3000);
}

function escapeHtml(text) {
    if (typeof text !== 'string') return '';
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
