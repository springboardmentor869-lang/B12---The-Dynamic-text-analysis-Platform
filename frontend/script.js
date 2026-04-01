const API_BASE = "http://127.0.0.1:8000";

// Display JSON output in a formatted way
function showOutput(data) {
    document.getElementById("output").innerText =
        JSON.stringify(data, null, 2);
}

async function uploadAndClassify() {

    // Get selected file from input
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file first");
        return;
    }

    // Prepare form data for API request
    const formData = new FormData();
    formData.append("file", file);

    document.getElementById("output").innerText = "Processing...";

    try {
        // Send file to backend classification endpoint
        const res = await fetch("http://127.0.0.1:8000/classify-file", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        // Display classification result    
        document.getElementById("output").innerText =
            `File: ${file.name}\nTopic: ${data.label}`;

    } catch (err) {
        document.getElementById("output").innerText = "Error: " + err;
    }
}

async function uploadAndConvert() {

    // Get selected file
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file first");
        return;
    }

    // Prepare request payload
    const formData = new FormData();
    formData.append("file", file);

    document.getElementById("output").innerText = "Processing...";

    try {
        // Call convert endpoint
        const res = await fetch("http://127.0.0.1:8000/convert-file", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        if (data.error) {
            document.getElementById("output").innerText = data.error;
            return;
        }

        // Display markdown result
        document.getElementById("output").innerText =
            `File: ${data.filename}\n\n${data.markdown}`;

    } catch (err) {
        document.getElementById("output").innerText = "Error: " + err;
    }
}

async function uploadAndAnalyzeSentiment() {

    // Get file input
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file first");
        return;
    }

    // Prepare form data
    const formData = new FormData();
    formData.append("file", file);

    document.getElementById("output").innerText = "Processing...";

    try {
        // Call sentiment endpoint
        const res = await fetch("http://127.0.0.1:8000/sentiment-file", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        if (data.error) {
            document.getElementById("output").innerText = data.error;
            return;
        }

        // Display sentiment analysis result
        document.getElementById("output").innerText =
            `File: ${data.filename}\n\nSentiment:\n${JSON.stringify(data.result, null, 2)}`;

    } catch (err) {
        document.getElementById("output").innerText = "Error: " + err;
    }
}

async function uploadAndSummarize() {

    // Get selected file
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file first");
        return;
    }

    // Prepare form data
    const formData = new FormData();
    formData.append("file", file);

    document.getElementById("output").innerText = "Processing... (this may take time)";

    try {
        // Call summarization endpoint
        const res = await fetch("http://127.0.0.1:8000/summarize-file", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        if (data.error) {
            document.getElementById("output").innerText = data.error;
            return;
        }

        // Call summarization endpoint
        document.getElementById("output").innerText =
            `File: ${data.filename}\n\nSummary:\n\n${data.summary}`;

    } catch (err) {
        document.getElementById("output").innerText = "Error: " + err;
    }
}