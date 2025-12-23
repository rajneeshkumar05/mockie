const token = localStorage.getItem("token");

// 🔐 Only redirect if token hi nahi hai
if (!token) {
    window.location.href = "/login";
}

async function loadProfile() {
    try {
        const res = await fetch("http://localhost:8000/me", {
            headers: {
                Authorization: `Bearer ${token}`
            }
        });

        if (!res.ok) {
            console.error("Profile fetch failed");
            return; // ❌ redirect mat karo
        }

        const data = await res.json();

        document.getElementById("name").innerText = data.name;
        document.getElementById("email").innerText = data.email;
        document.getElementById("role").innerText = data.role;
        document.getElementById("joined").innerText = data.joined;

    } catch (err) {
        console.error(err);
    }
}

function logout() {
    localStorage.removeItem("token");
    window.location.href = "/login";
}

window.onload = loadProfile;
