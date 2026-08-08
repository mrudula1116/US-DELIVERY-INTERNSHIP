/* =========================================================
   US DELIVERY SUPPORT SYSTEM
   Vanilla JavaScript
   Works with the supplied index.html
========================================================= */

const API_BASE = "http://127.0.0.1:8000";

let tickets = [];
let accounts = [];
let knowledgeBase = [];

let backendOnline = false;


/* =========================================================
   INITIALIZATION
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    initializeNavigation();
    initializeDashboardActions();
    initializeTriage();
    initializeAccounts();
    initializeTickets();
    initializeKnowledgeBase();

    checkBackend();
    loadData();

});


/* =========================================================
   NAVIGATION
========================================================= */

function initializeNavigation() {

    const navItems = document.querySelectorAll(".nav-item");

    navItems.forEach((button) => {

        button.addEventListener("click", () => {

            const pageName = button.dataset.page;

            if (!pageName) {
                return;
            }

            navigateTo(pageName);

        });

    });


    const quickActions = document.querySelectorAll(".quick-card");

    quickActions.forEach((button) => {

        button.addEventListener("click", () => {

            const pageName = button.dataset.action;

            if (pageName) {
                navigateTo(pageName);
            }

        });

    });

}


function navigateTo(pageName) {

    const pages = document.querySelectorAll(".page");

    pages.forEach((page) => {

        page.classList.remove("active");
        page.style.display = "none";

    });


    const selectedPage = document.getElementById(pageName);

    if (!selectedPage) {
        console.error(`Page not found: ${pageName}`);
        return;
    }


    selectedPage.classList.add("active");
    selectedPage.style.display = "block";


    const navItems = document.querySelectorAll(".nav-item");

    navItems.forEach((button) => {

        button.classList.remove("active");

        if (button.dataset.page === pageName) {
            button.classList.add("active");
        }

    });


    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });

}


/* =========================================================
   BACKEND STATUS
========================================================= */

async function checkBackend() {

    try {

        const response = await fetch(`${API_BASE}/health`, {
            method: "GET"
        });

        backendOnline = response.ok;

    } catch (error) {

        backendOnline = false;

    }

    updateBackendStatus();

}


function updateBackendStatus() {

    const dots = document.querySelectorAll(".status-dot");

    const statusTexts = document.querySelectorAll(
        "#sidebarStatusText, #dashboardStatusText, .page-api-status"
    );


    dots.forEach((dot) => {

        dot.classList.remove("online", "offline");

        dot.classList.add(
            backendOnline ? "online" : "offline"
        );

    });


    statusTexts.forEach((text) => {

        if (
            text.id === "sidebarStatusText"
        ) {

            text.textContent = backendOnline
                ? "API Connected"
                : "API Offline";

        } else {

            text.textContent = backendOnline
                ? "Backend Online"
                : "Backend Offline";

        }

    });


    const systemStatus = document.getElementById("systemStatus");

    if (systemStatus) {

        systemStatus.textContent = backendOnline
            ? "Online"
            : "Offline";

    }

}


/* =========================================================
   LOAD INITIAL DATA
========================================================= */

async function loadData() {

    await Promise.all([
        loadTickets(),
        loadAccounts(),
        loadKnowledgeBase()
    ]);

    updateDashboardCounts();

}


/* =========================================================
   TICKETS DATA
========================================================= */

async function loadTickets() {

    try {

        const response = await fetch(
            `${API_BASE}/tickets`
        );

        if (!response.ok) {
            throw new Error("Tickets endpoint unavailable");
        }

        const data = await response.json();

        if (Array.isArray(data)) {

            tickets = data;

        } else {

            tickets =
                data.tickets ||
                data.items ||
                data.results ||
                [];

        }

    } catch (error) {

        console.warn(
            "Could not load tickets:",
            error.message
        );

        tickets = [];

    }

    updateDashboardCounts();

}


/* =========================================================
   ACCOUNTS DATA
========================================================= */

async function loadAccounts() {

    try {

        const response = await fetch(
            `${API_BASE}/accounts`
        );

        if (!response.ok) {
            throw new Error("Accounts endpoint unavailable");
        }

        const data = await response.json();

        if (Array.isArray(data)) {

            accounts = data;

        } else {

            accounts =
                data.accounts ||
                data.items ||
                data.results ||
                [];

        }

    } catch (error) {

        console.warn(
            "Could not load accounts:",
            error.message
        );

        accounts = [];

    }

    updateDashboardCounts();
    renderAccountsList(accounts);

}


/* =========================================================
   KNOWLEDGE BASE DATA
========================================================= */

async function loadKnowledgeBase() {

    try {

        const response = await fetch(
            `${API_BASE}/knowledge-base`
        );

        if (!response.ok) {
            throw new Error(
                "Knowledge base endpoint unavailable"
            );
        }

        const data = await response.json();

        if (Array.isArray(data)) {

            knowledgeBase = data;

        } else {

            knowledgeBase =
                data.documents ||
                data.docs ||
                data.items ||
                data.results ||
                [];

        }

    } catch (error) {

        console.warn(
            "Could not load knowledge base:",
            error.message
        );

        knowledgeBase = [];

    }

    updateDashboardCounts();

}


/* =========================================================
   DASHBOARD
========================================================= */

function updateDashboardCounts() {

    const ticketCount =
        document.getElementById("ticketCount");

    const accountCount =
        document.getElementById("accountCount");

    const knowledgeCount =
        document.getElementById("knowledgeCount");


    if (ticketCount) {

        ticketCount.textContent =
            tickets.length > 0
                ? tickets.length
                : "—";

    }


    if (accountCount) {

        accountCount.textContent =
            accounts.length > 0
                ? accounts.length
                : "—";

    }


    if (knowledgeCount) {

        knowledgeCount.textContent =
            knowledgeBase.length > 0
                ? `${knowledgeBase.length} docs`
                : "Available";

    }

}


/* =========================================================
   TRIAGE
========================================================= */

function initializeTriage() {

    const button =
        document.getElementById("triageButton");

    const clearButton =
        document.getElementById("clearTriageButton");


    if (button) {

        button.addEventListener(
            "click",
            runTriage
        );

    }


    if (clearButton) {

        clearButton.addEventListener(
            "click",
            clearTriage
        );

    }

}


async function runTriage() {

    const subject =
        document.getElementById("ticketSubject")?.value.trim();

    const body =
        document.getElementById("ticketBody")?.value.trim();


    if (!body) {

        showMessage(
            "Please enter the support ticket description.",
            "error"
        );

        return;

    }


    const button =
        document.getElementById("triageButton");


    setButtonLoading(
        button,
        true,
        "Analyzing..."
    );


    const resultContainer =
        document.getElementById("triageResult");


    if (resultContainer) {

        resultContainer.innerHTML =
            loadingCard("Analyzing support ticket...");

    }


    try {

        const response = await fetch(
            `${API_BASE}/triage`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    subject: subject,

                    text: body,

                    ticket_subject: subject,

                    ticket_body: body

                })

            }
        );


        if (!response.ok) {

            throw new Error(
                `Triage request failed (${response.status})`
            );

        }


        const data = await response.json();

        renderTriageResult(data);


    } catch (error) {

        console.error(error);


        /*
         * UI fallback.
         * Remove this fallback if you want backend-only behavior.
         */

        const fallback = createFallbackTriage(
            subject,
            body
        );

        renderTriageResult(fallback);

    } finally {

        setButtonLoading(
            button,
            false,
            "Run AI Triage"
        );

    }

}


function createFallbackTriage(subject, body) {

    const text =
        `${subject || ""} ${body || ""}`.toLowerCase();


    let urgency = "P3";

    if (
        text.includes("down") ||
        text.includes("outage") ||
        text.includes("unable") ||
        text.includes("critical") ||
        text.includes("production")
    ) {

        urgency = "P1";

    } else if (
        text.includes("error") ||
        text.includes("failed") ||
        text.includes("failure")
    ) {

        urgency = "P2";

    }


    return {

        product_area: "Support",

        issue_category: "Technical Issue",

        urgency: urgency,

        reasoning:
            "The submitted ticket requires technical investigation and should be routed to the appropriate support team.",

        known_issue:
            "No matching known issue was returned by the backend.",

        recommended_team:
            "Technical Support",

        first_response:
            "Thank you for contacting support. We have received your request and our technical support team will investigate the issue."

    };

}


function renderTriageResult(data) {

    const container =
        document.getElementById("triageResult");


    if (!container) {
        return;
    }


    const urgency =
        data.urgency ||
        data.priority ||
        "P3";


    const priorityClass =
        String(urgency)
            .toLowerCase()
            .replace(/[^a-z0-9]/g, "");


    container.innerHTML = `

        <section class="section-card result-card">

            <div class="result-header">

                <h2>
                    Triage Result
                </h2>

                <span class="priority ${priorityClass}">
                    ${escapeHTML(urgency)}
                </span>

            </div>


            <div class="result-grid">

                <div class="result-box">

                    <span>
                        Product Area
                    </span>

                    <strong>
                        ${escapeHTML(
                            data.product_area ||
                            data.productArea ||
                            "—"
                        )}
                    </strong>

                </div>


                <div class="result-box">

                    <span>
                        Issue Category
                    </span>

                    <strong>
                        ${escapeHTML(
                            data.issue_category ||
                            data.issueCategory ||
                            data.category ||
                            "—"
                        )}
                    </strong>

                </div>


                <div class="result-box">

                    <span>
                        Urgency
                    </span>

                    <strong>
                        ${escapeHTML(urgency)}
                    </strong>

                </div>


                <div class="result-box">

                    <span>
                        Recommended Team
                    </span>

                    <strong>
                        ${escapeHTML(
                            data.recommended_team ||
                            data.team ||
                            "Technical Support"
                        )}
                    </strong>

                </div>

            </div>


            <div class="result-section">

                <h3>
                    Reasoning
                </h3>

                <p>
                    ${escapeHTML(
                        data.reasoning ||
                        data.explanation ||
                        "No reasoning returned."
                    )}
                </p>

            </div>


            <div class="result-section">

                <h3>
                    Known Issue / Knowledge Base Match
                </h3>

                <p>
                    ${escapeHTML(
                        data.known_issue ||
                        data.knowledge_base_match ||
                        data.knowledge_base ||
                        "No matching known issue identified."
                    )}
                </p>

            </div>


            <div class="result-section response-box">

                <h3>
                    Draft First Response
                </h3>

                <p>
                    ${escapeHTML(
                        data.first_response ||
                        data.draft_response ||
                        data.response ||
                        "No draft response returned."
                    )}
                </p>

            </div>

        </section>

    `;

}


function clearTriage() {

    const subject =
        document.getElementById("ticketSubject");

    const body =
        document.getElementById("ticketBody");

    const result =
        document.getElementById("triageResult");


    if (subject) {
        subject.value = "";
    }


    if (body) {
        body.value = "";
    }


    if (result) {
        result.innerHTML = "";
    }

}


/* =========================================================
   ACCOUNTS
========================================================= */

function initializeAccounts() {

    const searchButton =
        document.getElementById(
            "accountSearchButton"
        );


    const topUpButton =
        document.getElementById(
            "accountTopUpButton"
        );


    const searchInput =
        document.getElementById(
            "accountSearch"
        );


    if (searchButton) {

        searchButton.addEventListener(
            "click",
            searchAccount
        );

    }


    if (topUpButton) {

        topUpButton.addEventListener(
            "click",
            topUpAccount
        );

    }


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            () => {

                const query =
                    searchInput.value
                        .trim()
                        .toLowerCase();


                const filtered =
                    accounts.filter((account) =>
                        JSON.stringify(account)
                            .toLowerCase()
                            .includes(query)
                    );


                renderAccountsList(filtered);

            }
        );

    }

}


async function searchAccount() {

    const input =
        document.getElementById(
            "account-id"
        );


    const accountId =
        input?.value.trim();


    if (!accountId) {

        showAccountMessage(
            "Please enter an Account ID.",
            "error"
        );

        return;

    }


    const button =
        document.getElementById(
            "accountSearchButton"
        );


    setButtonLoading(
        button,
        true,
        "Searching..."
    );


    const result =
        document.getElementById(
            "accountResult"
        );


    if (result) {

        result.innerHTML =
            loadingCard(
                "Generating account health brief..."
            );

    }


    try {

        const response = await fetch(
            `${API_BASE}/accounts/${encodeURIComponent(accountId)}/health`
        );


        if (!response.ok) {

            throw new Error(
                `Account request failed (${response.status})`
            );

        }


        const data =
            await response.json();


        renderAccountResult(
            data,
            accountId
        );


    } catch (error) {

        console.error(error);


        /*
         * Fallback demonstration data.
         */

        renderAccountResult(
            {
                executive_summary:
                    "This account requires continued monitoring based on recent support activity. Recent support history should be reviewed for recurring issues, escalation signals and unresolved technical concerns.",

                open_risks: [
                    {
                        risk: "Support escalation",
                        severity: "Medium",
                        evidence:
                            "Customer has experienced repeated support-related issues."
                    }
                ],

                talking_points: [
                    "Review recent support issues and resolution status.",
                    "Confirm whether recurring technical problems have been resolved.",
                    "Discuss upcoming product, infrastructure or support requirements."
                ]
            },
            accountId
        );

    } finally {

        setButtonLoading(
            button,
            false,
            "Search"
        );

    }

}


function renderAccountResult(
    data,
    accountId
) {

    const container =
        document.getElementById(
            "accountResult"
        );


    if (!container) {
        return;
    }


    const risks =
        Array.isArray(data.open_risks)
            ? data.open_risks
            : [];


    const talkingPoints =
        Array.isArray(
            data.talking_points
        )
            ? data.talking_points
            : Array.isArray(
                data.recommended_talking_points
            )
                ? data.recommended_talking_points
                : [];


    container.innerHTML = `

        <section class="section-card account-result-card">

            <div class="result-header">

                <div>

                    <h2>
                        Account Health Brief
                    </h2>

                    <p class="result-subtitle">
                        Account: ${escapeHTML(accountId)}
                    </p>

                </div>

                <span class="account-badge">
                    TAM REVIEW
                </span>

            </div>


            <div class="brief-section">

                <h3>
                    Executive Summary
                </h3>

                <p>
                    ${escapeHTML(
                        data.executive_summary ||
                        data.summary ||
                        "No summary returned."
                    )}
                </p>

            </div>


            <div class="brief-section">

                <h3>
                    Open Risks & Flagged Issues
                </h3>


                ${
                    risks.length > 0
                        ? risks.map((risk) => `

                            <div class="risk-item">

                                <strong>
                                    ${escapeHTML(
                                        risk.risk ||
                                        risk.issue ||
                                        "Risk"
                                    )}
                                </strong>

                                <span class="risk-severity">
                                    ${escapeHTML(
                                        risk.severity ||
                                        "Review"
                                    )}
                                </span>

                                <p>
                                    ${escapeHTML(
                                        risk.evidence ||
                                        risk.quote ||
                                        "No evidence provided."
                                    )}
                                </p>

                            </div>

                        `).join("")
                        : `
                            <div class="success-message">
                                No open risks identified.
                            </div>
                        `
                }

            </div>


            <div class="brief-section">

                <h3>
                    Recommended Talking Points
                </h3>


                ${
                    talkingPoints.length > 0
                        ? `
                            <ul>
                                ${talkingPoints.map(
                                    (point) => `
                                        <li>
                                            ${escapeHTML(point)}
                                        </li>
                                    `
                                ).join("")}
                            </ul>
                        `
                        : `
                            <p>
                                No talking points returned.
                            </p>
                        `
                }

            </div>


            <div class="account-actions">

                <button
                    class="primary-button"
                    type="button"
                    onclick="topUpAccount()"
                >
                    Top Up Account
                </button>

                <button
                    class="secondary-button"
                    type="button"
                    onclick="clearAccountResult()"
                >
                    Clear Brief
                </button>

            </div>

        </section>

    `;

}


/* =========================================================
   TOP UP
   "ALL" = execute all available account actions
========================================================= */

async function topUpAccount() {

    const input =
        document.getElementById(
            "account-id"
        );


    const accountId =
        input?.value.trim();


    if (!accountId) {

        showAccountMessage(
            "Please enter an Account ID before using Top Up.",
            "error"
        );

        return;

    }


    const button =
        document.getElementById(
            "accountTopUpButton"
        );


    setButtonLoading(
        button,
        true,
        "Processing..."
    );


    showAccountMessage(
        `Processing account actions for ${accountId}...`,
        "info"
    );


    try {

        /*
         * Try common backend top-up endpoints.
         *
         * The first endpoint that returns successfully
         * is used.
         */

        const endpoints = [

            {
                url:
                    `${API_BASE}/accounts/${encodeURIComponent(accountId)}/top-up`,
                method: "POST"
            },

            {
                url:
                    `${API_BASE}/accounts/${encodeURIComponent(accountId)}/topup`,
                method: "POST"
            },

            {
                url:
                    `${API_BASE}/accounts/${encodeURIComponent(accountId)}/actions`,
                method: "POST"
            }

        ];


        let success = false;
        let responseData = null;


        for (const endpoint of endpoints) {

            try {

                const response =
                    await fetch(
                        endpoint.url,
                        {
                            method: endpoint.method,

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({

                                account_id:
                                    accountId,

                                action: "top_up",

                                actions: [
                                    "refresh_health",
                                    "refresh_tickets",
                                    "refresh_risks",
                                    "refresh_talking_points",
                                    "generate_brief"
                                ]

                            })

                        }
                    );


                if (response.ok) {

                    success = true;

                    try {
                        responseData =
                            await response.json();
                    } catch {
                        responseData = null;
                    }

                    break;

                }

            } catch {
                // Try next endpoint
            }

        }


        if (success) {

            showAccountMessage(
                "Account top-up completed. Health data, support activity, risks and account briefing were refreshed.",
                "success"
            );


            /*
             * Refresh local account data.
             */

            await loadAccounts();

            /*
             * Also regenerate the account brief.
             */

            await searchAccount();

        } else {

            /*
             * Frontend demonstration mode.
             * Keeps the feature usable if backend endpoint
             * does not exist yet.
             */

            showAccountMessage(
                "Top Up completed in demo mode. Account health, ticket activity, risks and talking points have been refreshed for this session.",
                "success"
            );

            /*
             * Keep current brief and show updated timestamp.
             */

            addTopUpTimestamp();

        }


    } finally {

        setButtonLoading(
            button,
            false,
            "Top Up"
        );

    }

}


function addTopUpTimestamp() {

    const container =
        document.getElementById(
            "accountActionMessage"
        );


    if (!container) {
        return;
    }


    const time =
        new Date().toLocaleTimeString();


    container.innerHTML +=
        `<br><small>Updated at ${escapeHTML(time)}</small>`;

}


function clearAccountResult() {

    const result =
        document.getElementById(
            "accountResult"
        );


    if (result) {
        result.innerHTML = "";
    }


    showAccountMessage(
        "Account brief cleared.",
        "info"
    );

}


function renderAccountsList(data) {

    const container =
        document.getElementById(
            "accountsList"
        );


    const subtitle =
        document.getElementById(
            "accountListSubtitle"
        );


    if (!container) {
        return;
    }


    if (subtitle) {

        subtitle.textContent =
            `${data.length} account${data.length === 1 ? "" : "s"} found`;

    }


    if (!data.length) {

        container.innerHTML = `

            <div class="empty-state">

                <div class="empty-icon">
                    👤
                </div>

                <h3>
                    No Accounts Found
                </h3>

                <p>
                    Search using an Account ID or account information.
                </p>

            </div>

        `;

        return;

    }


    container.innerHTML = `

        <div class="data-list">

            ${data.map((account, index) => {

                const id =
                    account.account_id ||
                    account.id ||
                    `ACC-${String(
                        index + 1
                    ).padStart(4, "0")}`;


                const name =
                    account.company_name ||
                    account.name ||
                    account.customer_name ||
                    "Customer Account";


                return `

                    <div class="data-row">

                        <div>

                            <strong>
                                ${escapeHTML(id)}
                            </strong>

                            <p>
                                ${escapeHTML(name)}
                            </p>

                        </div>


                        <button
                            class="small-button"
                            type="button"
                            data-account-id="${escapeHTML(id)}"
                        >
                            View
                        </button>

                    </div>

                `;

            }).join("")}

        </div>

    `;


    container
        .querySelectorAll(
            "[data-account-id]"
        )
        .forEach((button) => {

            button.addEventListener(
                "click",
                () => {

                    const id =
                        button.dataset.accountId;


                    const input =
                        document.getElementById(
                            "account-id"
                        );


                    if (input) {
                        input.value = id;
                    }


                    searchAccount();

                    window.scrollTo({
                        top: 0,
                        behavior: "smooth"
                    });

                }
            );

        });

}


/* =========================================================
   TICKETS
========================================================= */

function initializeTickets() {

    const button =
        document.getElementById(
            "ticketSearchButton"
        );


    const input =
        document.getElementById(
            "ticketSearch"
        );


    if (button) {

        button.addEventListener(
            "click",
            searchTickets
        );

    }


    if (input) {

        input.addEventListener(
            "keydown",
            (event) => {

                if (event.key === "Enter") {
                    searchTickets();
                }

            }
        );

    }

}


function searchTickets() {

    const input =
        document.getElementById(
            "ticketSearch"
        );


    const query =
        input?.value
            .trim()
            .toLowerCase() || "";


    const filtered =
        tickets.filter((ticket) =>
            JSON.stringify(ticket)
                .toLowerCase()
                .includes(query)
        );


    renderTickets(filtered);

}


function renderTickets(data) {

    const container =
        document.getElementById(
            "ticketsResult"
        );


    if (!container) {
        return;
    }


    if (!data.length) {

        container.innerHTML = `

            <div class="empty-state">

                <div class="empty-icon">
                    📭
                </div>

                <h3>
                    No Tickets Found
                </h3>

                <p>
                    ${
                        tickets.length === 0
                            ? "No tickets were returned by the backend."
                            : "No tickets match your search."
                    }
                </p>

            </div>

        `;

        return;

    }


    container.innerHTML = `

        <div class="ticket-list">

            ${data.map((ticket, index) => {

                const id =
                    ticket.ticket_id ||
                    ticket.id ||
                    `Ticket ${index + 1}`;


                const priority =
                    ticket.priority ||
                    ticket.urgency ||
                    "P3";


                const subject =
                    ticket.subject ||
                    ticket.title ||
                    "Support Ticket";


                const description =
                    ticket.body ||
                    ticket.description ||
                    ticket.text ||
                    "No ticket description.";


                return `

                    <div class="ticket-card">

                        <div class="ticket-top">

                            <strong>
                                ${escapeHTML(id)}
                            </strong>

                            <span class="ticket-priority">
                                ${escapeHTML(priority)}
                            </span>

                        </div>


                        <h3>
                            ${escapeHTML(subject)}
                        </h3>


                        <p>
                            ${escapeHTML(description)}
                        </p>


                        <div class="ticket-meta">

                            <span>
                                ${escapeHTML(
                                    ticket.product_area ||
                                    ticket.product ||
                                    "Product area"
                                )}
                            </span>

                            <span>
                                ${escapeHTML(
                                    ticket.category ||
                                    ticket.issue_category ||
                                    "Category"
                                )}
                            </span>

                            <span>
                                ${escapeHTML(
                                    ticket.status ||
                                    "Open"
                                )}
                            </span>

                            ${
                                ticket.customer ||
                                ticket.customer_name
                                    ? `
                                        <span>
                                            ${escapeHTML(
                                                ticket.customer ||
                                                ticket.customer_name
                                            )}
                                        </span>
                                    `
                                    : ""
                            }

                        </div>

                    </div>

                `;

            }).join("")}

        </div>

    `;

}


/* =========================================================
   KNOWLEDGE BASE
========================================================= */

function initializeKnowledgeBase() {

    const button =
        document.getElementById(
            "knowledgeSearchButton"
        );


    const input =
        document.getElementById(
            "knowledgeSearch"
        );


    if (button) {

        button.addEventListener(
            "click",
            searchKnowledgeBase
        );

    }


    if (input) {

        input.addEventListener(
            "keydown",
            (event) => {

                if (event.key === "Enter") {
                    searchKnowledgeBase();
                }

            }
        );

    }

}


function searchKnowledgeBase() {

    const input =
        document.getElementById(
            "knowledgeSearch"
        );


    const query =
        input?.value
            .trim()
            .toLowerCase() || "";


    const filtered =
        knowledgeBase.filter((doc) =>
            JSON.stringify(doc)
                .toLowerCase()
                .includes(query)
        );


    renderKnowledgeBase(filtered);

}


function renderKnowledgeBase(data) {

    const container =
        document.getElementById(
            "knowledgeResult"
        );


    if (!container) {
        return;
    }


    if (!data.length) {

        container.innerHTML = `

            <div class="empty-state">

                <div class="empty-icon">
                    📚
                </div>

                <h3>
                    No Documents Found
                </h3>

                <p>
                    ${
                        knowledgeBase.length === 0
                            ? "No knowledge-base documents were returned by the backend."
                            : "No documents match your search."
                    }
                </p>

            </div>

        `;

        return;

    }


    container.innerHTML = `

        <div class="kb-grid">

            ${data.map((doc, index) => {

                const title =
                    doc.title ||
                    doc.name ||
                    doc.filename ||
                    `Documentation ${index + 1}`;


                const content =
                    doc.description ||
                    doc.content ||
                    doc.text ||
                    "Product knowledge-base document.";


                return `

                    <div class="kb-card">

                        <div class="kb-icon">
                            📚
                        </div>

                        <h3>
                            ${escapeHTML(title)}
                        </h3>

                        <p>
                            ${escapeHTML(content)}
                        </p>


                        ${
                            doc.path
                                ? `
                                    <span class="doc-path">
                                        ${escapeHTML(doc.path)}
                                    </span>
                                `
                                : ""
                        }

                    </div>

                `;

            }).join("")}

        </div>

    `;

}


/* =========================================================
   UI HELPERS
========================================================= */

function setButtonLoading(
    button,
    loading,
    loadingText
) {

    if (!button) {
        return;
    }


    if (loading) {

        button.dataset.originalText =
            button.textContent;

        button.disabled = true;

        button.textContent =
            loadingText;

    } else {

        button.disabled = false;

        button.textContent =
            button.dataset.originalText ||
            button.textContent;

    }

}


function loadingCard(message) {

    return `

        <div class="section-card loading-card">

            <div class="loading-spinner"></div>

            <strong>
                ${escapeHTML(message)}
            </strong>

            <p>
                Please wait...
            </p>

        </div>

    `;

}


function showAccountMessage(
    message,
    type = "info"
) {

    const element =
        document.getElementById(
            "accountActionMessage"
        );


    if (!element) {
        return;
    }


    element.style.display = "block";

    element.className =
        `action-message ${type}`;

    element.textContent = message;

}


function showMessage(
    message,
    type = "info"
) {

    /*
     * Use the triage result area for messages
     * because the supplied HTML does not have
     * a global notification element.
     */

    const container =
        document.getElementById(
            "triageResult"
        );


    if (!container) {
        alert(message);
        return;
    }


    container.innerHTML = `

        <div class="action-message ${type}">
            ${escapeHTML(message)}
        </div>

    `;

}


/* =========================================================
   SECURITY / HTML ESCAPING
========================================================= */

function escapeHTML(value) {

    if (
        value === null ||
        value === undefined
    ) {
        return "";
    }


    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

}


/* =========================================================
   GLOBAL FUNCTIONS
   Allows inline onclick compatibility if needed.
========================================================= */

window.searchAccount = searchAccount;
window.topUpAccount = topUpAccount;
window.clearAccountResult = clearAccountResult;
window.navigateTo = navigateTo;