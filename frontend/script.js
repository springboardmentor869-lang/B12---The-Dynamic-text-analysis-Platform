/**
 * Functions:
 * - showProcessing()                   — renders a spinner in the output panel
 * - showError(msg)                     — renders an error message in the output panel
 * - bindFileLabel(inputId, displayId)  — syncs file name display to file input
 * - uploadAndClassify()                — handles topic classification flow
 * - uploadAndConvert()                 — handles PDF/DOCX → Markdown conversion flow
 * - uploadAndAnalyzeSentiment()        — handles sentiment analysis flow
 * - uploadAndSummarize()               — handles document summarization flow
 * - escapeHtml(str)                    — sanitizes strings before inserting into DOM
 */

const API_BASE = "http://127.0.0.1:8000";


function showProcessing() {
    document.getElementById("output").innerHTML =
        `<div class="processing"><div class="spinner"></div> Processing, please wait…</div>`;
}

function showError(msg) {
    document.getElementById("output").innerHTML =
        `<div class="error-msg">⚠ ${msg}</div>`;
}

function bindFileLabel(inputId, displayId) {
    const input = document.getElementById(inputId);
    const display = document.getElementById(displayId);
    if (!input || !display) return;
    input.addEventListener("change", () => {
        display.textContent = input.files[0] ? input.files[0].name : "";
    });
}
document.addEventListener("DOMContentLoaded", () => bindFileLabel("fileInput", "fileNameDisplay"));

/* ── Topic Classification ── */

async function uploadAndClassify() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];
    if (!file) { alert("Please select a file first"); return; }

    const formData = new FormData();
    formData.append("file", file);
    showProcessing();

    try {
        const res = await fetch(`${API_BASE}/classify-file`, { method: "POST", body: formData });
        const data = await res.json();

        document.getElementById("output").innerHTML = `
            <div class="classify-result">
                <span class="classify-label">Detected Topic</span>
                <span class="classify-topic">${data.label}</span>
            </div>`;
    } catch (err) {
        showError(err);
    }
}

/* PDF to Markdown Conversion */

async function uploadAndConvert() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];
    if (!file) { alert("Please select a file first"); return; }

    const formData = new FormData();
    formData.append("file", file);
    showProcessing();

    try {
        const res = await fetch(`${API_BASE}/convert-file`, { method: "POST", body: formData });
        const data = await res.json();

        if (data.error) { showError(data.error); return; }

        document.getElementById("output").innerHTML =
            `<div class="text-output">${escapeHtml(data.markdown)}</div>`;
    } catch (err) {
        showError(err);
    }
}

/* Sentiment Analysis */

async function uploadAndAnalyzeSentiment() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];
    if (!file) { alert("Please select a file first"); return; }

    const formData = new FormData();
    formData.append("file", file);
    showProcessing();

    try {
        const res = await fetch(`${API_BASE}/sentiment-file`, { method: "POST", body: formData });
        const data = await res.json();

        if (data.error) { showError(data.error); return; }

        // data.result is expected to have a label like "Positive" / "Negative" / "Neutral"
        const rawLabel = (typeof data.result === "object" ? data.result.label : data.result) || "Unknown";
        const label    = rawLabel.trim();
        const cls      = label.toLowerCase(); // "positive" | "negative" | "neutral"

        document.getElementById("output").innerHTML = `
            <div class="sentiment-result">
                <span class="sentiment-label">The uploaded file is</span>
                <span class="sentiment-value ${cls}">${label}</span>
            </div>`;
    } catch (err) {
        showError(err);
    }
}

/* Summarization */

async function uploadAndSummarize() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];
    if (!file) { alert("Please select a file first"); return; }

    const formData = new FormData();
    formData.append("file", file);
    document.getElementById("output").innerHTML =
        `<div class="processing"><div class="spinner"></div> Generating summary — this may take a moment…</div>`;

    try {
        const res = await fetch(`${API_BASE}/summarize-file`, { method: "POST", body: formData });
        const data = await res.json();

        if (data.error) { showError(data.error); return; }

        document.getElementById("output").innerHTML =
            `<div class="text-output">${escapeHtml(data.summary)}</div>`;
    } catch (err) {
        showError(err);
    }
}


function escapeHtml(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}