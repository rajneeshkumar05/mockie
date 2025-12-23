const API_BASE = "http://127.0.0.1:8000";

async function signup() {
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const res = await fetch(`${API_BASE}/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password })
    });

    const data = await res.json();

    if (!res.ok) {
        document.getElementById("error").innerText = data.detail;
        return;
    }

    window.location.href = "/login";
}

async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const res = await fetch(`${API_BASE}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (!res.ok) {
        document.getElementById("error").innerText = data.detail;
        return;
    }

    // 🔥 YAHI LINE ADD KARNI HAI
    localStorage.setItem("token", data.access_token);
    window.location.href = "/dashboard";
}
