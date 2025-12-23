const API_BASE = "http://localhost:8000";
const token = localStorage.getItem("token");

// 🔐 Route protection
if (!token) {
    window.location.href = "/login";
}

// 🚪 Logout
function logout() {
    localStorage.removeItem("token");
    window.location.href = "/login";
}

// ▶ Start Interview (redirect only)
function startInterview() {
    window.location.href = "/start-interview";
}

function goToSetup() {
    window.location.href = "/start-interview";
}

// 📜 Load interview history
async function loadHistory() {
    try {
        const res = await fetch(`${API_BASE}/my-interviews`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!res.ok) return;

        const data = await res.json();
        const historyList = document.getElementById("history");

        if (!historyList) return;

        historyList.innerHTML = "";

        data.forEach(interview => {
            const li = document.createElement("li");
            li.innerText = `${interview.job_title || "Interview"} | Score: ${interview.final_score ?? "Pending"}`;
            historyList.appendChild(li);
        });

    } catch (err) {
        console.error(err);
    }
}

// 👤 Load logged-in user name
async function loadUserName() {
    try {
        const res = await fetch(`${API_BASE}/me`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!res.ok) throw new Error("Unauthorized");

        const data = await res.json();

        const usernameEl = document.getElementById("username");
        if (usernameEl) {
            usernameEl.innerText = data.name;
        }

    } catch (err) {
        console.error(err);
    }
}

// ✅ SINGLE window.onload
window.onload = () => {
    loadUserName();
    loadHistory();
};
