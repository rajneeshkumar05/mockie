const API_BASE = "http://localhost:8000";
const token = localStorage.getItem("token");

async function submitSetup() {
    const jobTitle = document.getElementById("job_title").value.trim();
    const jobDesc = document.getElementById("job_desc").value.trim();
    const resume = document.getElementById("resume").files[0];

    // 🔴 VALIDATION LOGIC
    if (!resume && (!jobTitle || !jobDesc)) {
        alert(
            "Please either:\n• Fill Job Title & Job Description\nOR\n• Upload your Resume"
        );
        return;
    }

    const formData = new FormData();

    // send only if available
    if (jobTitle) formData.append("job_title", jobTitle);
    if (jobDesc) formData.append("job_description", jobDesc);
    if (resume) formData.append("resume", resume);

    const res = await fetch(`${API_BASE}/start-interview`, {
        method: "POST",
        headers: {
            Authorization: `Bearer ${token}`
        },
        body: formData
    });

    if (!res.ok) {
        alert("Failed to start interview");
        return;
    }

    const data = await res.json();

    // ✅ DIRECT REDIRECT TO INTERVIEW PAGE
    window.location.href = `/interview?interview_id=${data.interview_id}`;
}
