const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "/login";
}

async function loadRecentInterviews() {
    const res = await fetch("http://localhost:8000/my-interviews", {
        headers: {
            Authorization: `Bearer ${token}`
        }
    });

    const data = await res.json();
    const tableBody = document.getElementById("recent-body");

    tableBody.innerHTML = "";

    if (data.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="4">No interviews conducted yet</td>
            </tr>
        `;
        return;
    }

    data.forEach(interview => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${new Date(interview.created_at).toLocaleDateString()}</td>
            <td>${interview.job_title || "General Interview"}</td>
            <td>${interview.final_score ?? "Pending"}</td>
            <td>
                <a href="/result?interview_id=${interview.id}">View</a>
            </td>
        `;

        tableBody.appendChild(tr);
    });
}

window.onload = loadRecentInterviews;
