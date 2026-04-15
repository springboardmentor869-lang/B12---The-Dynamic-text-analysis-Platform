const backendURL = "http://127.0.0.1:8000";

// 📂 Get file
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

// 📌 SUMMARY
function getSummary() {
    const formData = getFile();
    if (!formData) return;

    document.getElementById("result").innerText = "Loading Summary...";

    fetch(`${backendURL}/summary/`, {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("result").innerText = data.summary;
    })
    .catch(err => {
        console.error(err);
        document.getElementById("result").innerText = "❌ Error connecting to backend";
    });
}

// 📌 SENTIMENT
function getSentiment() {
    const formData = getFile();
    if (!formData) return;

    document.getElementById("result").innerText = "Analyzing Sentiment...";

    fetch(`${backendURL}/sentiment/`, {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("result").innerText =
            "Sentiment Summary:\n" +
            JSON.stringify(data.sentiment_summary, null, 2) +
            "\n\nSample:\n" +
            JSON.stringify(data.sample_sentiments, null, 2);
    })
    .catch(err => {
        console.error(err);
        document.getElementById("result").innerText = "❌ Error connecting to backend";
    });
}

// 📌 TOPIC
function getTopic() {
    const formData = getFile();
    if (!formData) return;

    document.getElementById("result").innerText = "Detecting Topic...";

    fetch(`${backendURL}/topic/`, {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("result").innerText = "Topic: " + data.topic;
    })
    .catch(err => {
        console.error(err);
        document.getElementById("result").innerText = "❌ Error connecting to backend";
    });
}