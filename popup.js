document.getElementById("summarizeBtn").addEventListener("click", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  const url = new URL(tab.url);
  const videoId = url.searchParams.get("v");

  if (!videoId) {
    document.getElementById("status").innerText = "Not a YouTube video!";
    return;
  }

  document.getElementById("status").innerText = "Summarizing...";

  try {
    const response = await fetch("http://127.0.0.1:5000/summarize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ video_id: videoId }),
    });

    const result = await response.json();

    if (result.status === "done") {
      document.getElementById("status").innerText = "Added to Notion ✅";
    } else {
      document.getElementById("status").innerText = "Error adding to Notion ❌";
    }
  } catch (error) {
    document.getElementById("status").innerText = "Server error 🚨";
    console.error(error);
  }
});
