async function loadResult() {
    const params = new URLSearchParams(window.location.search);
    const interviewId = params.get("interview_id");

    const res = await fetch(`/final-feedback?interview_id=${interviewId}`, {
        headers: {
            "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
    });

    const data = await res.json();

    // 🔥 YEHI LINE TUM PUCHH RAHE THE
    document.getElementById("score").innerText = data.score;
    document.getElementById("final-feedback").innerText = data.summary;
}

window.onload = loadResult;

