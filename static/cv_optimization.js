console.log("CV Optimization JS Loaded");

async function analyzeCV() {
    const file = document.getElementById("resume").files[0];
    if (!file) {
        alert("Please upload a resume");
        return;
    }

    const formData = new FormData();
    formData.append("resume", file);

    const res = await fetch("/cv-optimization/analyze", {
        method: "POST",
        headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`
        },
        body: formData
    });

    const data = await res.json();

    // 🔥 UPDATE CARDS
    document.getElementById("ats-score").innerText = data.ats + "%";
    document.getElementById("keyword-score").innerText = data.keywords + "%";
    document.getElementById("formatting-score").innerText = data.formatting + "%";
    document.getElementById("clarity-score").innerText = data.clarity + "%";

    // 🔥 SUGGESTIONS
    const list = document.getElementById("suggestions");
    list.innerHTML = "";
    data.suggestions.forEach(item => {
        const li = document.createElement("li");
        li.innerText = item;
        list.appendChild(li);
    });
}
