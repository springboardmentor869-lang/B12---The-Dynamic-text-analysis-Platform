const backendURL = "http://127.0.0.1:8000";

// Get file
function getFile() {
    const fileInput = document.getElementById("fileInput");

    if (!fileInput.files.length) {
        alert("Please select a file first!");
        return null;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    return formData;
}

// Loader
function showLoader() {
    document.getElementById("loader").classList.remove("hidden");
    document.getElementById("result").innerText = "";
}

function hideLoader() {
    document.getElementById("loader").classList.add("hidden");
}

// Reset
function resetUI() {
    document.getElementById("result").innerText = "The analysis will appear here...";
    document.getElementById("backBtn").classList.add("hidden");
}

// ----------------------
// 📌 SUMMARY
// ----------------------
function getSummary() {
    const formData = getFile();
    if (!formData) return;

    showLoader();

    fetch(`${backendURL}/summary/`, {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        hideLoader();

        document.getElementById("result").innerText = data.summary || "No summary available";

        document.getElementById("backBtn").classList.remove("hidden");
    })
    .catch(() => {
        hideLoader();
        document.getElementById("result").innerText = "❌ Error fetching summary";
    });
}

// ----------------------
// 📊 SENTIMENT (FIXED 🔥)
// ----------------------
function getSentiment() {
    const formData = getFile();
    if (!formData) return;

    showLoader();

    fetch(`${backendURL}/sentiment/`, {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        hideLoader();

        let html = `<h3>📊 Sentiment Analysis</h3>`;

        const s = data.sentiment_summary;

        html += `
            <div class="sentiment-card">
                <b>Summary:</b><br>
                Total: ${s.total}<br>
                Positive: ${s.positive}<br>
                Negative: ${s.negative}<br>
                Neutral: ${s.neutral}
            </div>
        `;

        function renderSection(title, arr, cls, id) {
            let section = `<div class="sentiment-card ${cls}">
                <div class="section-title">${title} (${arr.length})</div>`;

            if (!arr || arr.length === 0) {
                section += `<div class="sentence">No data</div>`;
            } else {
                const firstFive = arr.slice(0, 5);

                section += `<div id="${id}">`;

                firstFive.forEach(item => {
                    section += `<div class="sentence">• ${item.text} (${item.score}%)</div>`;
                });

                section += `</div>`;

                if (arr.length > 5) {
                    section += `
                        <button class="show-btn" onclick="toggleSentences('${id}', ${JSON.stringify(arr).replace(/"/g, '&quot;')})">
                            Show More
                        </button>
                    `;
                }
            }

            section += `</div>`;
            return section;
        }

        html += renderSection("🟢 Positive", data.sample_sentiments.positive, "positive", "posSection");
        html += renderSection("🔴 Negative", data.sample_sentiments.negative, "negative", "negSection");
        html += renderSection("🟡 Neutral", data.sample_sentiments.neutral, "neutral", "neuSection");

        document.getElementById("result").innerHTML = html;
        document.getElementById("backBtn").classList.remove("hidden");
    })
    .catch(err => {
        hideLoader();
        console.error(err);
        document.getElementById("result").innerText = "❌ Error fetching sentiment";
    });
}

// ----------------------
// 📌 TOPIC
// ----------------------
function getTopic() {
    const formData = getFile();
    if (!formData) return;

    showLoader();

    fetch(`${backendURL}/topic/`, {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        hideLoader();

       let html = `<h3>📊 Topic Distribution</h3>`;

if (data.topics && data.topics.length > 0) {
    data.topics.forEach(t => {
        html += `
            <div class="sentiment-card">
                📌 <b>${t.topic}</b><br>
                Confidence: ${t.percentage}%
            </div>
        `;
    });
} else {
    html += "No topics found";
}

document.getElementById("result").innerHTML = html;

        document.getElementById("backBtn").classList.remove("hidden");
    })
    .catch(() => {
        hideLoader();
        document.getElementById("result").innerText = "❌ Error fetching topic";
    });
}
function toggleSentences(id, data) {
    const container = document.getElementById(id);
    const button = container.nextElementSibling;

    if (button.innerText === "Show More") {
        container.innerHTML = "";

        data.forEach(item => {
            container.innerHTML += `<div class="sentence">• ${item.text} (${item.score}%)</div>`;
        });

        button.innerText = "Show Less";
    } else {
        container.innerHTML = "";

        data.slice(0, 5).forEach(item => {
            container.innerHTML += `<div class="sentence">• ${item.text} (${item.score}%)</div>`;
        });

        button.innerText = "Show More";
    }
}

// ----------------------
// 📄 EXTRACT TEXT
// ----------------------
function getText() {
    const formData = getFile();
    if (!formData) return;

    showLoader();

    fetch(`${backendURL}/extract-text/`, {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        hideLoader();

        document.getElementById("result").innerText =
            data.text || "No text extracted";

        document.getElementById("backBtn").classList.remove("hidden");
    })
    .catch(() => {
        hideLoader();
        document.getElementById("result").innerText = "❌ Error extracting text";
    });
}