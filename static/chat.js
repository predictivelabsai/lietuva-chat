/* lietuva.chat -- chat client (SSE streaming, 3-pane interactions). */

(() => {
    const $ = (sel) => document.querySelector(sel);
    const $$ = (sel) => Array.from(document.querySelectorAll(sel));

    let currentSessionId = getSidFromURL();
    let currentAgentSlug = null;
    let streaming = false;

    const AGENT_PROMPTS = readJsonScript("agent-prompts-data") || {};
    const AGENT_NAMES = readJsonScript("agent-names-data") || {};
    const AGENT_PREFIX_MAP = readJsonScript("agent-prefix-map") || {};
    const I18N = readJsonScript("i18n-data") || {};

    function readJsonScript(id) {
        const el = document.getElementById(id);
        if (!el) return null;
        try { return JSON.parse(el.textContent); }
        catch (e) { return null; }
    }

    function getSidFromURL() {
        const p = new URLSearchParams(window.location.search);
        return p.get("sid") || "";
    }
    function getQuestionFromURL() {
        const p = new URLSearchParams(window.location.search);
        return (p.get("q") || "").trim();
    }
    function syncActiveAgent(slug) {
        $$(".agent-item").forEach((item) => {
            item.classList.toggle("active", item.dataset.slug === slug);
        });
    }
    function setSid(sid) {
        currentSessionId = sid;
        const u = new URL(window.location);
        u.searchParams.set("sid", sid);
        history.replaceState(null, "", u);
    }

    function addBubble(role, text, agentSlug) {
        const wrap = document.createElement("div");
        wrap.className = `msg msg-${role}`;
        if (role === "assistant" && agentSlug) {
            const hdr = document.createElement("div");
            hdr.className = "msg-agent";
            const nice = AGENT_NAMES[agentSlug] || agentSlug;
            hdr.innerHTML = `<svg class="msg-agent-icon" width="20" height="20" viewBox="6 6 52 52" aria-hidden="true" focusable="false"><path d="M6 58V22A16 16 0 0 1 22 6h20a16 16 0 0 1 16 16v20a16 16 0 0 1-16 16Z" fill="#1E5B3F"/><path d="M28.5 14v24a8.5 8.5 0 0 0 8.5 8.5" fill="none" stroke="#FFFFFF" stroke-width="9.5" stroke-linecap="round"/></svg><span class="msg-agent-label">${nice}</span>`;
            wrap.appendChild(hdr);
        }
        const bubble = document.createElement("div");
        bubble.className = "msg-bubble";
        bubble.textContent = text;
        wrap.appendChild(bubble);
        $("#messages").appendChild(wrap);
        scrollMessagesBottom();
        return bubble;
    }

    function i18n(key, fallback) {
        return I18N[key] || fallback;
    }

    function bindFeedbackRow(row) {
        if (!row || row.dataset.bound) return;
        row.dataset.bound = "1";
        row.querySelectorAll(".feedback-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                if (row.dataset.submitted) return;
                row.dataset.submitted = "1";
                const buttons = Array.from(row.querySelectorAll(".feedback-btn"));
                buttons.forEach(button => { button.disabled = true; });
                fetch("/app/feedback", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        sid: currentSessionId || "",
                        rating: btn.dataset.rating,
                        agent_slug: row.dataset.agentSlug || currentAgentSlug || "",
                        content: row.dataset.content || "",
                    }),
                }).then(resp => resp.json()).then(data => {
                    if (!data.ok) throw new Error("feedback rejected");
                    btn.classList.add("active");
                    buttons.forEach(button => { button.style.display = "none"; });
                    const note = row.querySelector(".feedback-note");
                    if (note) {
                        note.style.display = "inline";
                        setTimeout(() => {
                            note.classList.add("fading");
                            setTimeout(() => { if (row.parentElement) row.remove(); }, 280);
                        }, 2500);
                    }
                }).catch(() => {
                    delete row.dataset.submitted;
                    buttons.forEach(button => { button.disabled = false; });
                });
            });
        });
    }

    function addRetryControl(wrap) {
        if (!wrap || wrap.querySelector(".retry-row")) return;
        const row = document.createElement("div");
        row.className = "retry-row";
        const button = document.createElement("button");
        button.type = "button";
        button.className = "retry-btn";
        button.textContent = i18n("chat_retry", "Try again");
        button.setAttribute("aria-label", button.textContent);
        button.addEventListener("click", () => retryFailedTurn(wrap));
        row.appendChild(button);
        wrap.appendChild(row);
    }

    function retryFailedTurn(wrap) {
        if (streaming || !wrap) return;
        let userWrap = wrap.previousElementSibling;
        while (userWrap && !userWrap.classList.contains("msg-user")) {
            userWrap = userWrap.previousElementSibling;
        }
        const userBubble = userWrap && userWrap.querySelector(".msg-bubble");
        const message = userBubble ? userBubble.textContent.trim() : "";
        if (!message) return;
        wrap.remove();
        sendMessage(null, { message, reuseUserBubble: true });
    }

    function appendToolLog(bubble, name, args) {
        // Don't surface tool calls (e.g. web_search) to the user — only in trace mode.
        if (!document.body.classList.contains("show-trace")) return;
        let log = bubble.parentElement.querySelector(".tool-log");
        if (!log) {
            log = document.createElement("div");
            log.className = "tool-log";
            bubble.parentElement.appendChild(log);
        }
        const step = document.createElement("div");
        step.className = "tool-step";
        step.innerHTML = `-> <span class="tool-name">${name}</span>`;
        log.appendChild(step);
    }

    function scrollMessagesBottom() {
        const m = $("#messages");
        if (m) m.scrollTop = m.scrollHeight;
    }

    function renderMarkdownLite(text) {
        // Model output can echo text from searched web pages, so the HTML is always sanitised.
        if (window.marked && window.DOMPurify) {
            return DOMPurify.sanitize(marked.parse(text), { ADD_ATTR: ["target"] });
        }
        return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
            .replace(/\n/g, "<br>");
    }

    function tableToCSV(table) {
        const rows = [];
        table.querySelectorAll("tr").forEach(tr => {
            const cells = [];
            tr.querySelectorAll("th, td").forEach(td => {
                cells.push('"' + td.textContent.trim().replace(/"/g, '""') + '"');
            });
            rows.push(cells.join(","));
        });
        return rows.join("\n");
    }

    function enhanceTables(container) {
        if (!container) return;
        container.querySelectorAll("table").forEach(table => {
            if (table.dataset.enhanced) return;
            table.dataset.enhanced = "1";
            const toolbar = document.createElement("div");
            toolbar.className = "table-toolbar";
            const copyBtn = document.createElement("button");
            copyBtn.textContent = "Copy CSV";
            copyBtn.className = "table-action-btn";
            copyBtn.onclick = () => {
                navigator.clipboard.writeText(tableToCSV(table)).then(() => {
                    copyBtn.textContent = "Copied!";
                    setTimeout(() => { copyBtn.textContent = "Copy CSV"; }, 1500);
                });
            };
            const dlBtn = document.createElement("button");
            dlBtn.textContent = "Download CSV";
            dlBtn.className = "table-action-btn";
            dlBtn.onclick = () => {
                const blob = new Blob([tableToCSV(table)], { type: "text/csv" });
                const a = document.createElement("a");
                a.href = URL.createObjectURL(blob);
                a.download = "lietuva-chat-data.csv";
                a.click();
                URL.revokeObjectURL(a.href);
            };
            toolbar.appendChild(copyBtn);
            toolbar.appendChild(dlBtn);
            table.parentNode.insertBefore(toolbar, table);
        });
    }

    // -- Working status: plain words for each phase, plus elapsed seconds --
    let thinker = null;
    function showThinking(bubble) {
        if (!bubble) return;
        thinker = { started: Date.now(), label: i18n("status_understanding", "Understanding your question"), el: document.createElement("div"), timerId: null };
        thinker.el.className = "thinking-indicator";
        thinker.el.setAttribute("role", "status");
        thinker.el.innerHTML = '<span class="dot"></span><span class="label"></span><span class="secs"></span>';
        bubble.parentElement.insertBefore(thinker.el, bubble);
        updateThinking();
        thinker.timerId = setInterval(updateThinking, 500);
    }
    function updateThinking() {
        if (!thinker) return;
        thinker.el.querySelector(".label").textContent = thinker.label + "…";
        thinker.el.querySelector(".secs").textContent = Math.floor((Date.now() - thinker.started) / 1000) + "s";
    }
    function setThinkingTool(name, args) {
        if (!thinker) return;
        const query = args && (args.query || args.q);
        thinker.label = i18n("status_searching", "Searching official websites") + (query ? ": “" + String(query).slice(0, 60) + "”" : "");
        updateThinking();
    }
    function hideThinking() {
        if (!thinker) return;
        clearInterval(thinker.timerId);
        if (thinker.el && thinker.el.parentElement) thinker.el.parentElement.removeChild(thinker.el);
        thinker = null;
    }

    // -- Under every answer: Sources, then Copy / Listen / Was this helpful? --
    const AGENCY_NAMES = {
        "epaslaugos.lt": "E-government gateway", "migracija.lt": "Migration Department (MIGRIS)",
        "migracija.lrv.lt": "Migration Department", "vmi.lt": "State Tax Inspectorate (VMI)", "sodra.lt": "Sodra",
        "ligoniukasa.lrv.lt": "National Health Insurance Fund", "vlk.lt": "National Health Insurance Fund",
        "registrucentras.lt": "Centre of Registers", "e-tar.lt": "Register of Legal Acts (e-TAR)",
        "globalilietuva.urm.lt": "Global Lithuania", "keliauk.urm.lt": "Consular information", "urm.lt": "Ministry of Foreign Affairs",
        "uzt.lt": "Employment Service", "vrk.lt": "Central Electoral Commission", "lrs.lt": "Seimas",
        "vilnius.lt": "Vilnius City Municipality", "kaunas.lt": "Kaunas City Municipality", "klaipeda.lt": "Klaipėda City Municipality",
    };
    function sourceLinks(content) {
        const seen = new Set(), out = [];
        const re = /https?:\/\/[^\s)\]>"']+/g;
        let m;
        while ((m = re.exec(content || "")) && out.length < 6) {
            let url;
            try { url = new URL(m[0].replace(/[.,;:]+$/, "")); } catch (e) { continue; }
            if (url.protocol !== "https:" && url.protocol !== "http:") continue;
            const host = url.hostname.replace(/^www\./, "");
            if (seen.has(host)) continue;
            seen.add(host);
            out.push({ href: url.href, host: host, name: AGENCY_NAMES[host] || host });
        }
        return out;
    }
    function addSources(wrap, content) {
        const links = sourceLinks(content);
        if (!links.length || wrap.querySelector(".msg-sources")) return;
        const box = document.createElement("div");
        box.className = "msg-sources";
        const title = document.createElement("p");
        title.className = "msg-sources-title";
        title.textContent = i18n("sources", "Sources");
        const list = document.createElement("ol");
        links.forEach(l => {
            const li = document.createElement("li");
            const a = document.createElement("a");
            a.href = l.href; a.target = "_blank"; a.rel = "noopener noreferrer";
            a.textContent = l.name;
            const host = document.createElement("span");
            host.textContent = l.host;
            a.appendChild(host);
            li.appendChild(a);
            list.appendChild(li);
        });
        const note = document.createElement("p");
        note.className = "msg-sources-note";
        note.textContent = i18n("sources_note", "Check these official pages before you act.");
        box.append(title, list, note);
        wrap.appendChild(box);
    }
    function actionButton(label, onClick) {
        const b = document.createElement("button");
        b.type = "button"; b.className = "msg-action"; b.textContent = label;
        b.addEventListener("click", () => onClick(b));
        return b;
    }
    function addActions(wrap, content, agentSlug) {
        if (!wrap || wrap.querySelector(".msg-actions")) return;
        addSources(wrap, content);
        const bubble = wrap.querySelector(".msg-bubble");
        const row = document.createElement("div");
        row.className = "msg-actions";
        row.appendChild(actionButton(i18n("copy", "Copy"), (b) => {
            _copyToClipboard(bubble ? bubble.innerText : content, () => {
                b.textContent = i18n("copied", "Copied");
                setTimeout(() => { b.textContent = i18n("copy", "Copy"); }, 1600);
            });
        }));
        if ("speechSynthesis" in window) {
            row.appendChild(actionButton(i18n("listen", "Listen"), (b) => {
                if (speechSynthesis.speaking) { speechSynthesis.cancel(); b.textContent = i18n("listen", "Listen"); return; }
                const u = new SpeechSynthesisUtterance(bubble ? bubble.innerText : content);
                u.lang = speechLang();
                u.onend = () => { b.textContent = i18n("listen", "Listen"); };
                b.textContent = i18n("stop", "Stop");
                speechSynthesis.speak(u);
            }));
        }
        const fb = document.createElement("span");
        fb.className = "feedback-row";
        fb.dataset.content = content || "";
        fb.dataset.agentSlug = agentSlug || "";
        fb.innerHTML = '<span class="feedback-q"></span>'
            + '<button type="button" class="feedback-btn msg-action" data-rating="up"></button>'
            + '<button type="button" class="feedback-btn msg-action" data-rating="down"></button>'
            + '<span class="feedback-note" style="display:none"></span>';
        fb.querySelector(".feedback-q").textContent = i18n("helpful", "Was this helpful?");
        fb.querySelector('[data-rating="up"]').textContent = i18n("yes", "Yes");
        fb.querySelector('[data-rating="down"]').textContent = i18n("no", "No");
        fb.querySelector(".feedback-note").textContent = i18n("chat_fb_thanks", "Thank you");
        row.appendChild(fb);
        wrap.appendChild(row);
        bindFeedbackRow(fb);
    }
    function speechLang() {
        const form = $(".chat-form");
        const code = (form && form.dataset.lang) || "en";
        return ({ lt: "lt-LT", en: "en-GB", ru: "ru-RU", de: "de-DE", fr: "fr-FR", sv: "sv-SE", lv: "lv-LV", fi: "fi-FI", et: "et-EE" })[code] || "en-GB";
    }

    // -- Text size: A / A+ / A++, remembered on this device --
    window.setTextSize = (size) => {
        document.documentElement.dataset.textSize = size;
        $$(".size-btn").forEach(b => b.setAttribute("aria-pressed", b.dataset.size === size ? "true" : "false"));
        try { localStorage.setItem("lc-text-size", size); } catch (e) {}
    };
    (function initTextSize() {
        let size = "m";
        try { size = localStorage.getItem("lc-text-size") || "m"; } catch (e) {}
        window.setTextSize(size);
    })();

    // -- Voice input (only where the browser supports it) --
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognizer = null;
    if (Recognition && $("#mic-btn")) $("#mic-btn").hidden = false;
    window.toggleVoice = () => {
        const mic = $("#mic-btn"), ta = $("#chat-input");
        if (!Recognition || !mic || !ta) return;
        if (recognizer) { recognizer.stop(); return; }
        recognizer = new Recognition();
        recognizer.lang = speechLang();
        recognizer.interimResults = true;
        const before = ta.value;
        mic.classList.add("listening");
        ta.placeholder = i18n("listening", "Listening… speak now");
        recognizer.onresult = (e) => {
            const text = Array.from(e.results).map(r => r[0].transcript).join("");
            ta.value = (before ? before + " " : "") + text;
            autoResize(ta);
        };
        recognizer.onend = () => { mic.classList.remove("listening"); recognizer = null; ta.focus(); };
        recognizer.onerror = () => { mic.classList.remove("listening"); recognizer = null; };
        recognizer.start();
    };

    // -- Sample cards --
    window.updateSampleCards = (slug) => {
        const row = $("#sample-cards-row");
        if (!row) return;

        let prompts = (slug && AGENT_PROMPTS[slug]) || [];
        if (!prompts.length) {
            prompts = [I18N.sug1, I18N.sug2, I18N.sug3, I18N.sug4, I18N.sug5].filter(Boolean);
            if (!prompts.length) {
                prompts = [
                    "How do I get a temporary residence permit to work in Lithuania?",
                    "How do I register a UAB company online?",
                    "What Sodra contributions does a self-employed person pay?",
                    "How do I log in to epaslaugos.lt with Smart-ID?",
                    "How do I declare my residence after moving to Vilnius?",
                ];
            }
        }
        row.innerHTML = "";
        prompts.slice(0, 6).forEach(p => {
            const b = document.createElement("button");
            b.className = "sample-card";
            b.title = p;
            const span = document.createElement("span");
            span.className = "sample-card-text";
            span.textContent = p;
            b.appendChild(span);
            b.onclick = () => { fillChat(p); sendMessage(null); };
            row.appendChild(b);
        });
    };

    window.onInputChange = (ta) => {};

    // -- Follow-up / starter chips under the composer (always present) --
    function followupDefaults() {
        const d = [I18N.sug1, I18N.sug2, I18N.sug3, I18N.sug4, I18N.sug5].filter(Boolean);
        if (d.length) return d.slice(0, 4);
        return [
            "How do I get a residence permit in Lithuania?",
            "What Sodra contributions does a self-employed person pay?",
            "How do I log in to epaslaugos.lt with Smart-ID?",
        ];
    }
    window.renderFollowups = (items) => {
        const host = $("#followups");
        if (!host) return;
        let list = Array.isArray(items) ? items.filter(Boolean) : [];
        if (!list.length) list = followupDefaults();   // never leave the user stuck
        host.innerHTML = "";
        const label = document.createElement("span");
        label.className = "followups-label";
        label.textContent = i18n("followups_label", "You could also ask");
        host.appendChild(label);
        list.slice(0, 4).forEach(p => {
            const b = document.createElement("button");
            b.type = "button";
            b.className = "followup-chip";
            b.title = p;
            b.textContent = p;
            b.onclick = () => { fillChat(p); sendMessage(null); };
            host.appendChild(b);
        });
    };

    if ($("#sample-cards-row")) updateSampleCards(null);
    // On the empty welcome screen the big cards cover suggestions; the under-box
    // chips kick in once a conversation is underway (and after every answer).
    (function initFollowups() {
        const wh = $("#welcome-hero");
        const welcomeVisible = wh && wh.style.display !== "none";
        if ($("#followups") && !welcomeVisible) renderFollowups([]);
    })();

    // -- SSE send --
    async function sendMessage(evt, options = {}) {
        if (evt) evt.preventDefault();
        const langMenu = document.getElementById("lang-dd-menu");
        if (langMenu) langMenu.classList.remove("open");
        const langTrigger = document.querySelector(".lang-trigger");
        if (langTrigger) langTrigger.setAttribute("aria-expanded", "false");
        if (streaming) return;
        const ta = $("#chat-input");
        if (!ta) return;
        const msg = (options.message !== undefined ? options.message : ta.value).trim();
        if (!msg) return;

        streaming = true;
        const sendBtn = $("#send-btn");
        if (sendBtn) sendBtn.disabled = true;

        const wh = $("#welcome-hero");
        if (wh) wh.style.display = "none";

        if (!options.reuseUserBubble) addBubble("user", msg);
        ta.value = "";
        ta.style.height = "";

        let bubble = null;
        let accumulated = "";
        let failed = false;
        let doneReceived = false;
        let terminalWithoutStream = false;

        const markFailed = (message) => {
            failed = true;
            hideThinking();
            if (!bubble) bubble = addBubble("assistant", "", currentAgentSlug || "");
            bubble.classList.remove("streaming");
            if (!bubble.textContent.trim() && message) bubble.textContent = message;
            const wrap = bubble.parentElement;
            if (wrap) {
                wrap.classList.add("msg-failed");
                addRetryControl(wrap);
            }
            scrollMessagesBottom();
        };

        try {
            const body = new URLSearchParams({ msg, sid: currentSessionId || "" });
            const resp = await fetch("/app/chat", { method: "POST", body });
            if (resp.status === 402) {
                // Free-query limit reached — prompt sign in.
                let data = {};
                try { data = await resp.json(); } catch (e) {}
                addBubble("assistant", data.message ||
                    "You've reached the free limit. Please sign in to continue.");
                terminalWithoutStream = true;
                if (typeof showSignIn === "function") showSignIn();
                return;
            }
            if (!resp.ok) {
                let data = {};
                try { data = await resp.json(); } catch (e) {}
                markFailed(data.message || "Error: " + resp.status);
                return;
            }

            const reader = resp.body && resp.body.getReader();
            if (!reader) {
                markFailed("Connection lost. Please try again.");
                return;
            }
            const decoder = new TextDecoder();
            let buffer = "";

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, { stream: true });

                let idx;
                while ((idx = buffer.indexOf("\n\n")) !== -1) {
                    const raw = buffer.slice(0, idx);
                    buffer = buffer.slice(idx + 2);
                    handleEvent(raw, (type, payload) => {
                        if (type === "agent_route") {
                            const nice = payload.agent || AGENT_NAMES[payload.slug] || payload.slug;
                            const label = $("#current-agent-label");
                            if (label) label.textContent = nice;
                            currentAgentSlug = payload.slug;
                            syncActiveAgent(payload.slug);
                            updateSampleCards(payload.slug);
                            bubble = addBubble("assistant", "", payload.slug);
                            bubble.classList.add("streaming");
                            showThinking(bubble);
                        } else if (type === "token") {
                            if (!bubble) bubble = addBubble("assistant", "", currentAgentSlug || "");
                            if (accumulated === "") hideThinking();
                            accumulated += payload.text;
                            bubble.innerHTML = renderMarkdownLite(accumulated);
                            scrollMessagesBottom();
                        } else if (type === "tool_start") {
                            setThinkingTool(payload.name, payload.args);
                            appendToolLog(bubble || addBubble("assistant", "", currentAgentSlug || ""), payload.name, payload.args);
                        } else if (type === "tool_end") {
                            // noop
                        } else if (type === "artifact_show") {
                            showArtifact(payload);
                        } else if (type === "error") {
                            markFailed("Error: " + (payload.message || "unknown"));
                        } else if (type === "session") {
                            if (payload.sid) setSid(payload.sid);
                        } else if (type === "suggestions") {
                            if (Array.isArray(payload.items) && payload.items.length) renderFollowups(payload.items);
                        } else if (type === "done") {
                            doneReceived = true;
                            hideThinking();
                            if (failed) return;
                            if (bubble) {
                                bubble.classList.remove("streaming");
                                // Hide the "-> web_search" trace once the answer is complete
                                // (kept only while streaming / when a thinking trace is enabled).
                                const tl = bubble.parentElement && bubble.parentElement.querySelector(".tool-log");
                                if (tl && !document.body.classList.contains("show-trace")) tl.remove();
                                enhanceTables(bubble);
                                addActions(bubble.parentElement, accumulated, currentAgentSlug);
                            }
                            // Ensure chips are present immediately; a trailing
                            // "suggestions" event will replace them with context-sensitive ones.
                            if (!failed) renderFollowups([]);
                            const fr = payload.free_remaining;
                            if (typeof fr === "number" && fr >= 0 && fr <= 2) {
                                const note = fr === 0
                                    ? "That was your last free question. Sign in to keep asking."
                                    : fr + " free question" + (fr === 1 ? "" : "s") + " left — sign in for unlimited.";
                                const el = addBubble("assistant", note);
                                el.style.opacity = "0.6";
                                el.style.fontSize = "13px";
                            }
                        }
                    });
                }
            }
        } catch (e) {
            if (!terminalWithoutStream) markFailed("Connection lost. Please try again.");
        } finally {
            if (!doneReceived && !failed && !terminalWithoutStream) {
                markFailed("Connection lost. Please try again.");
            }
            streaming = false;
            if (sendBtn) sendBtn.disabled = false;
        }
    }

    function handleEvent(raw, cb) {
        let type = null; let data = "";
        for (const line of raw.split("\n")) {
            if (line.startsWith("event: ")) type = line.slice(7).trim();
            else if (line.startsWith("data: ")) data += line.slice(6);
        }
        if (!type) return;
        try { cb(type, data ? JSON.parse(data) : {}); }
        catch (e) { console.error("bad sse line", raw, e); }
    }

    // -- Artifacts --
    function showArtifact(payload) {
        const body = $("#artifact-body");
        const empty = $("#artifact-empty");
        if (empty) empty.style.display = "none";
        if (body) body.style.display = "block";

        const sub = $("#artifact-subtitle");
        if (sub) sub.textContent = payload.subtitle || "";

        const card = document.createElement("div");
        card.className = "artifact-card";
        const title = payload.title || "Canvas";
        const kind = payload.kind || "note";
        card.innerHTML = `
            <div class="meta">${kind}</div>
            <h4>${title}</h4>
            <div class="body">${renderArtifactHTML(payload)}</div>
        `;
        body.prepend(card);
        enhanceTables(card);

        const isMobile = window.innerWidth <= 768;
        if (!isMobile) {
            document.querySelector(".app").classList.remove("pane-closed");
            const rp = $("#right-pane");
            if (rp) rp.classList.add("open");
            const ab = $("#artifact-btn");
            if (ab) ab.classList.add("active");
        } else {
            const tog = $("#right-pane-toggle-btn");
            if (tog) tog.classList.add("has-results");
        }
    }

    function renderArtifactHTML(p) {
        if (p.kind === "table" && Array.isArray(p.rows)) {
            if (!p.rows.length) return '<p><em>No rows.</em></p>';
            const cols = p.columns || Object.keys(p.rows[0]);
            const head = "<tr>" + cols.map(c => `<th>${c}</th>`).join("") + "</tr>";
            const tbody = p.rows.map(r => "<tr>" + cols.map(c => `<td>${formatCell(r[c])}</td>`).join("") + "</tr>").join("");
            return `<table class="artifact-table">${head}${tbody}</table>`;
        }
        if (p.kind === "citations" && Array.isArray(p.items)) {
            return p.items.map(it => `
                <div style="margin-bottom:.6rem;">
                    <div style="color:var(--ink);font-size:.8rem;font-weight:500;">${it.title || ""}</div>
                    <div style="color:var(--ink-dim);font-size:.68rem;font-family:monospace;">${it.url ? `<a href="${it.url}" target="_blank" rel="noopener noreferrer" style="color:var(--ink-muted)">link</a>` : ""} ${it.score ? `score ${Number(it.score).toFixed(2)}` : ""}</div>
                    <div style="color:var(--ink-muted);font-size:.75rem;margin-top:.25rem;">${(it.snippet || "").replace(/\n/g,"<br>")}</div>
                </div>
            `).join("");
        }
        if (p.body_md) {
            return renderMarkdownLite(p.body_md);
        }
        return `<pre style="font-size:11px;overflow-x:auto">${JSON.stringify(p, null, 2)}</pre>`;
    }

    function formatCell(v) {
        if (v === null || v === undefined) return "--";
        if (typeof v === "number") return v.toLocaleString();
        if (typeof v === "object") return JSON.stringify(v);
        return String(v);
    }

    // -- UI helpers --
    window.toggleLeftPane = () => {
        const lp = $(".left-pane");
        const lo = $(".left-overlay");
        if (lp) lp.classList.toggle("open");
        if (lo) lo.classList.toggle("visible");
        const menuBtn = $(".mobile-menu-btn");
        if (menuBtn) menuBtn.setAttribute("aria-expanded", lp && lp.classList.contains("open") ? "true" : "false");
        const rp = $("#right-pane");
        if (rp && rp.classList.contains("open")) {
            rp.classList.remove("open");
            const ro = $("#right-overlay");
            if (ro) ro.classList.remove("visible");
            const app = $(".app");
            if (app) app.classList.add("pane-closed");
        }
    };
    window.toggleArtifactPane = () => {
        const r = $("#right-pane");
        const app = $(".app");
        const ro = $("#right-overlay");
        if (!r) return;
        if (r.classList.contains("open")) {
            r.classList.remove("open");
            if (app) app.classList.add("pane-closed");
            if (ro) ro.classList.remove("visible");
            const ab = $("#artifact-btn");
            if (ab) ab.classList.remove("active");
        } else {
            r.classList.add("open");
            if (app) app.classList.remove("pane-closed");
            if (ro && window.innerWidth <= 768) ro.classList.add("visible");
            const ab = $("#artifact-btn");
            if (ab) ab.classList.add("active");
        }
    };
    window.toggleGroup = (ev, id) => {
        ev.stopPropagation();
        const el = document.getElementById(id);
        if (el) {
            const isOpen = el.classList.toggle("open");
            if (ev.currentTarget) ev.currentTarget.setAttribute("aria-expanded", isOpen ? "true" : "false");
        }
    };
    window.handleKey = (ev) => {
        if (ev.key === "Enter" && !ev.shiftKey) { ev.preventDefault(); sendMessage(ev); }
    };
    window.autoResize = (el) => {
        el.style.height = "auto";
        el.style.height = Math.min(el.scrollHeight, 240) + "px";
    };
    function primeQuestionFromURL() {
        const question = getQuestionFromURL();
        const ta = $("#chat-input");
        if (!question || !ta) return;
        ta.value = question;
        window.autoResize(ta);
        setTimeout(() => sendMessage(null), 0);
    }
    window.fillChat = (text) => {
        const ta = $("#chat-input");
        if (!ta) return;
        ta.value = text;
        ta.focus();
        autoResize(ta);
        const prefix = text.trim().replace(/:.*/, "").toLowerCase();
        const slug = AGENT_PREFIX_MAP[prefix];
        if (slug) {
            currentAgentSlug = slug;
            syncActiveAgent(slug);
            const label = $("#current-agent-label");
            if (label) label.textContent = AGENT_NAMES[slug] || slug;
            updateSampleCards(slug);
        }
    };
    window.newChat = () => { window.location.href = "/app"; };
    const _checkSvg = '<svg class="icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M4.5 12.5l5 5 10-10.5"/></svg>';
    const _shareSvg = '<svg class="icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M12 3v12M7.5 7.5 12 3l4.5 4.5M8 11H6v9h12v-9h-2"/></svg>';
    const _copySvg = '<svg class="icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M9 9h9.5a1.5 1.5 0 0 1 1.5 1.5v8a1.5 1.5 0 0 1-1.5 1.5h-8A1.5 1.5 0 0 1 9 18.5zM15 6v-.5A1.5 1.5 0 0 0 13.5 4h-8A1.5 1.5 0 0 0 4 5.5v8A1.5 1.5 0 0 0 5.5 15H6"/></svg>';
    const _linkSvg = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>';

    function _flashIcon(btn, origSvg, duration) {
        btn.innerHTML = _checkSvg;
        btn.classList.add("copied");
        setTimeout(() => { btn.innerHTML = origSvg; btn.classList.remove("copied"); }, duration || 2000);
    }
    function _copyToClipboard(text, cb) {
        try {
            navigator.clipboard.writeText(text).then(cb, () => { _fallbackCopy(text); cb(); });
        } catch(e) { _fallbackCopy(text); cb(); }
    }
    function _fallbackCopy(text) {
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand("copy"); } catch(e) {}
        document.body.removeChild(ta);
    }

    window.copyChat = () => {
        const msgs = document.querySelectorAll(".msg");
        const lines = [];
        msgs.forEach(m => {
            const role = m.classList.contains("msg-user") ? "You" : "lietuva.chat";
            const bubble = m.querySelector(".msg-bubble");
            if (bubble) lines.push(`${role}: ${bubble.textContent.trim()}`);
        });
        const btn = $("#copy-chat-btn");
        _copyToClipboard(lines.join("\n\n"), () => { if (btn) _flashIcon(btn, _copySvg); });
    };
    window.shareChat = () => {
        if (!currentSessionId) return;
        const btn = $("#share-chat-btn");
        fetch("/api/share/" + currentSessionId, { method: "POST" })
            .then(r => r.json())
            .then(data => {
                if (data.url) {
                    const full = window.location.origin + data.url;
                    _copyToClipboard(full, () => { if (btn) _flashIcon(btn, _shareSvg); });
                }
            })
            .catch(() => {});
    };
    window.shareSession = (sid, btn) => {
        fetch("/api/share/" + sid, { method: "POST" })
            .then(r => r.json())
            .then(data => {
                if (data.url) {
                    const full = window.location.origin + data.url;
                    _copyToClipboard(full, () => { if (btn) _flashIcon(btn, _linkSvg); });
                }
            })
            .catch(() => {});
    };

    document.querySelectorAll(".msg-assistant .msg-bubble").forEach(b => {
        if (!b.dataset.rendered) { b.innerHTML = renderMarkdownLite(b.textContent); b.dataset.rendered = "1"; }
    });
    document.querySelectorAll(".msg-bubble").forEach(b => enhanceTables(b));
    document.querySelectorAll(".msg-assistant > .feedback-row").forEach(old => {
        const wrap = old.parentElement, content = old.dataset.content || "", slug = old.dataset.agentSlug || "";
        old.remove();
        addActions(wrap, content, slug);
    });

    window.toggleLangDropdown = (ev) => {
        ev.stopPropagation();
        const menu = document.getElementById("lang-dd-menu");
        const trigger = ev.currentTarget;
        if (menu) {
            const isOpen = menu.classList.toggle("open");
            if (trigger) trigger.setAttribute("aria-expanded", isOpen ? "true" : "false");
        }
    };
    document.addEventListener("click", () => {
        const menu = document.getElementById("lang-dd-menu");
        if (menu) menu.classList.remove("open");
        const trigger = document.querySelector(".lang-trigger");
        if (trigger) trigger.setAttribute("aria-expanded", "false");
    });

    // On mobile, ensure right pane starts closed
    if (window.innerWidth <= 768) {
        const rp = $("#right-pane");
        if (rp) rp.classList.remove("open");
        const app = $(".app");
        if (app) app.classList.add("pane-closed");
    }

    window.sendMessage = sendMessage;
    window.retryFailedTurn = retryFailedTurn;
    window.renderMarkdownLite = renderMarkdownLite;
    window.enhanceTables = enhanceTables;
    window.addActions = addActions;
    primeQuestionFromURL();

})();

/* -- Auth functions (global, called from onclick handlers) -- */

function switchAuthTab(tab) {
    document.getElementById('auth-form-login').style.display = tab === 'login' ? '' : 'none';
    document.getElementById('auth-form-register').style.display = tab === 'register' ? '' : 'none';
    document.getElementById('auth-form-forgot').style.display = tab === 'forgot' ? '' : 'none';
    document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
    const tabEl = document.getElementById('auth-tab-' + tab);
    if (tabEl) tabEl.classList.add('active');
}

function showForgotPassword(e) {
    e && e.preventDefault();
    switchAuthTab('forgot');
}

function showSignIn() {
    const overlay = document.getElementById('signin-overlay');
    overlay.classList.add('visible');
    switchAuthTab('login');
    const first = Array.from(overlay.querySelectorAll('.auth-panel input')).find(input => input.offsetParent !== null);
    if (first) first.focus();
}

async function doLogin() {
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;
    const errEl = document.getElementById('login-error');
    errEl.textContent = '';
    if (!email || !password) { errEl.textContent = 'Email and password required'; return; }

    const resp = await fetch('/auth/login', {
        method: 'POST',
        body: new URLSearchParams({ email, password }),
    });
    const data = await resp.json();
    if (data.ok) {
        location.reload();
    } else if (data.error === 'no_password') {
        errEl.innerHTML = 'No password set. <a href="#" onclick="showSetPassword(\'' + email + '\');return false" style="color:var(--blue);font-weight:700;">Set one now</a>';
    } else {
        errEl.textContent = data.error || 'Login failed';
    }
}

async function doRegister() {
    const name = document.getElementById('reg-name').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;
    const errEl = document.getElementById('reg-error');
    const okEl = document.getElementById('reg-success');
    errEl.textContent = ''; okEl.textContent = '';
    if (!email || !password) { errEl.textContent = 'Email and password required'; return; }

    const resp = await fetch('/auth/register', {
        method: 'POST',
        body: new URLSearchParams({ email, password, name }),
    });
    const data = await resp.json();
    if (data.ok) {
        okEl.textContent = data.message || 'Check your email to verify';
    } else {
        errEl.textContent = data.error || 'Registration failed';
    }
}

async function doForgot() {
    const email = document.getElementById('forgot-email').value.trim();
    const msgEl = document.getElementById('forgot-msg');
    msgEl.textContent = '';
    if (!email) { msgEl.textContent = 'Enter your email'; msgEl.style.color = 'var(--danger)'; return; }

    const resp = await fetch('/auth/forgot', {
        method: 'POST',
        body: new URLSearchParams({ email }),
    });
    const data = await resp.json();
    msgEl.style.color = 'var(--success)';
    msgEl.textContent = data.message || 'Reset link sent if account exists';
}

function showSetPassword(email) {
    const form = document.getElementById('auth-form-login');
    form.innerHTML = '<p style="font-size:13px;color:var(--ink-2);margin-bottom:12px;">Set a password for <strong>' + email + '</strong></p>'
        + '<input type="password" id="set-pw-input" placeholder="New password (min 6 chars)" aria-label="New password (min 6 chars)" style="width:100%;padding:8px 12px;border:1px solid var(--line);border-radius:4px;font-size:14px;margin-bottom:12px;">'
        + '<div id="set-pw-error" role="alert" style="color:var(--danger);font-size:12px;margin-bottom:8px;"></div>'
        + '<button onclick="doSetPassword(\'' + email + '\')" style="padding:8px 16px;background:var(--blue);color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:13px;">Set Password</button>';
}

document.addEventListener('keydown', function(e) {
    const overlay = document.getElementById('signin-overlay');
    if (e.key === 'Escape') {
        if (overlay) overlay.classList.remove('visible');
        return;
    }
    if (e.key !== 'Tab') return;
    if (!overlay || !overlay.classList.contains('visible')) return;
    const focusable = Array.from(overlay.querySelectorAll('button, a[href], input, select, textarea, [tabindex]:not([tabindex="-1"])')).filter(el => !el.disabled && el.offsetParent !== null);
    if (!focusable.length) return;
    const first = focusable[0], last = focusable[focusable.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
});

async function doSetPassword(email) {
    const password = document.getElementById('set-pw-input').value;
    const errEl = document.getElementById('set-pw-error');
    if (!password || password.length < 6) { errEl.textContent = 'Min 6 characters'; return; }

    const resp = await fetch('/auth/set-password', {
        method: 'POST',
        body: new URLSearchParams({ email, password }),
    });
    const data = await resp.json();
    if (data.ok) location.reload();
    else errEl.textContent = data.error || 'Failed';
}

function signOut() {
    fetch('/auth/logout', { method: 'POST' }).then(() => location.reload());
}

/* Legacy compat */
function doSignIn() { doLogin(); }
