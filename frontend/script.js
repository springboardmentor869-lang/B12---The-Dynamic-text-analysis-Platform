const API_BASE = "http://localhost:8000/api";

function showOutput(data) {
    document.getElementById("output").innerText =
        JSON.stringify(data, null, 2);
}

async function uploadAndClassify() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file first");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    // Show loading state
    document.getElementById("file_name").innerText = "...";
    document.getElementById("topic_label").innerText = "Processing...";
    document.getElementById("confidence").innerText = "...";

    try {
        const res = await fetch(`${API_BASE}/inference`, {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        console.log("API RESPONSE:", data);

        if (data.status === "error") {
            document.getElementById("topic_label").innerText = data.error;
            return;
        }

        // ✅ Fill UI fields (LIKE SENTIMENT)
        document.getElementById("file_name").innerText = data.filename;
        document.getElementById("topic_label").innerText = data.topic_label;
        document.getElementById("confidence").innerText =
            (data.confidence * 100).toFixed(1) + "%";

    } catch (err) {
        document.getElementById("topic_label").innerText = "Error: " + err;
        console.error(err);
    }
}

async function uploadAndConvert() {
    const fileInput = document.getElementById("fileInput");
    const output = document.getElementById("output");
    const downloadBox = document.getElementById("downloadButtons");

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    output.innerText = "Processing...";

    const response = await fetch("/api/convert-file", {
        method: "POST",
        body: formData
    });

    const data = await response.json();

    if (data.status === "success") {
        output.innerText = data.markdown;

        // Show download buttons
        downloadBox.style.display = "block";

        document.getElementById("downloadMD").onclick = () => {
            window.open(data.download_md, "_blank");
        };

        document.getElementById("downloadTXT").onclick = () => {
            window.open(data.download_txt, "_blank");
        };

    } else {
        output.innerText = "Error: " + data.error;
    }

    /*
    document.getElementById("downloadMD").onclick = () => {
        const a = document.createElement("a");
        a.href = data.download_md;   // from backend
        a.download = "";             // forces download
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    };

    document.getElementById("downloadTXT").onclick = () => {
        const a = document.createElement("a");
        a.href = data.download_txt;
        a.download = "";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    };
    */
}

async function uploadAndAnalyzeSentiment() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file first");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    document.getElementById("overall_sentiment").innerText = "Processing...";

    try {
        const res = await fetch(`${API_BASE}/sentiment-file`, {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        console.log("API RESPONSE:", data); 

        const el = document.getElementById("overall_sentiment");
        if (el) {
            el.innerText = "Processing...";
        }

        if (data.error) {
            document.getElementById("overall_sentiment").innerText = data.error;
            return;
        }

        renderSentiment(data);

    } catch (err) {
        document.getElementById("overall_sentiment").innerText = "Error: " + err;
        console.error(err);
    }
}

function renderSentiment(data) {
    console.log("Render called", data);

    const s = data.sentiments;

    document.getElementById("positive_count").innerText = s.positive_count || 0;
    document.getElementById("negative_count").innerText = s.negative_count || 0;
    document.getElementById("neutral_count").innerText = s.neutral_count || 0;
    document.getElementById("overall_sentiment").innerText = s.overall_sentiment || "—";
}

async function uploadAndSummarize() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file first");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    // Loading state
    document.getElementById("summary_file").innerText = "...";
    document.getElementById("summary_text").innerText = "Processing... (this may take time)";

    try {
        const res = await fetch(`${API_BASE}/summarize-file`, {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        console.log("API RESPONSE:", data);

        if (data.status === "error" || data.error) {
            document.getElementById("summary_text").innerText = data.error;
            return;
        }

        // ✅ Fill structured UI
        document.getElementById("summary_file").innerText = data.filename;
        document.getElementById("summary_text").innerText = data.summary;

    } catch (err) {
        document.getElementById("summary_text").innerText = "Error: " + err;
        console.error(err);
    }
}