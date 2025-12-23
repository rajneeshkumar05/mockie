const API_BASE = "http://localhost:8000";
const token = localStorage.getItem("token");
const interviewId = new URLSearchParams(window.location.search).get("interview_id");

console.log("interview.js loaded");

let recognition;
let currentQuestion = "";

// ---------------- CAMERA ----------------
// ================= CAMERA TOGGLE (FINAL) =================
let cameraStream = null;
let cameraEnabled = false;

window.startCamera = async function () {
    const video = document.getElementById("camera");
    const btn = document.querySelector(".camera-btn");

    console.log("Camera button clicked. Enabled:", cameraEnabled);

    // ENABLE
    if (!cameraEnabled) {
        try {
            cameraStream = await navigator.mediaDevices.getUserMedia({
                video: true
            });

            video.srcObject = cameraStream;
            await video.play();

            cameraEnabled = true;

            btn.innerText = "🚫 Disable Camera";
            btn.style.background = "#e74c3c";

            console.log("Camera enabled");
        } catch (err) {
            console.error("Camera error:", err);
            alert("Camera permission denied");
        }
    }
    // DISABLE
    else {
        cameraStream.getTracks().forEach(track => track.stop());
        video.srcObject = null;

        cameraStream = null;
        cameraEnabled = false;

        btn.innerText = "📷 Enable Camera";
        btn.style.background = "#5b2be0";

        console.log("Camera disabled");
    }
};


// ---------------- TEXT TO SPEECH ----------------
function speak(text) {
    const speech = new SpeechSynthesisUtterance(text);
    speech.lang = "en-US";
    speechSynthesis.speak(speech);
}

// ---------------- LOAD QUESTION ----------------
async function loadQuestion() {
    const loading = document.getElementById("loading");
    if (loading) loading.style.display = "block";

    const res = await fetch(
        `${API_BASE}/next-question?interview_id=${interviewId}`,
        { headers: { "Authorization": `Bearer ${token}` } }
    );

    const data = await res.json();

    if (data.end) {
        window.location.href = `/result?interview_id=${interviewId}`;
        return;
    }

    currentQuestion = data.question;
    document.getElementById("question").innerText =
        `Question ${data.question_number}: ${currentQuestion}`;

    speak(currentQuestion);

    if (loading) loading.style.display = "none";
}

// ---------------- SPEECH TO TEXT ----------------
window.startMic = function () {
    console.log("startMic called");

    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(() => {
            console.log("Mic permission granted");

            const SpeechRecognition =
                window.SpeechRecognition || window.webkitSpeechRecognition;

            if (!SpeechRecognition) {
                alert("Speech API not supported. Use Chrome.");
                return;
            }

            recognition = new SpeechRecognition();
            recognition.lang = "en-US";
            recognition.continuous = true;

            recognition.onresult = (event) => {
                let text = "";
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    text += event.results[i][0].transcript;
                }
                document.getElementById("answer").value = text;
            };

            recognition.start();
        })
        .catch(err => {
            alert("Mic blocked");
            console.error(err);
        });
};


// ---------------- SUBMIT ANSWER ----------------
async function submitAnswer() {
    const answer = document.getElementById("answer").value.trim();
    if (!answer) return;

    const loading = document.getElementById("loading");
    if (loading) loading.style.display = "block";

    const res = await fetch(`${API_BASE}/submit-answer`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            interview_id: interviewId,
            question: currentQuestion,
            answer: answer
        })
    });

    const data = await res.json();

    document.getElementById("feedback").innerText =
        `Score: ${data.score}/10 | ${data.feedback}`;

    document.getElementById("answer").value = "";

    setTimeout(loadQuestion, 2000);
}

// ---------------- SKIP QUESTION ----------------
async function skipQuestion() {
    if (!currentQuestion) return;

    document.getElementById("loading").style.display = "block";

    await fetch(`${API_BASE}/skip-question`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            interview_id: interviewId,
            question: currentQuestion,
            answer: ""
        })
    });

    document.getElementById("feedback").innerText =
        "Question skipped.";

    setTimeout(loadQuestion, 1000);
}

// ---------------- END INTERVIEW ----------------
async function endInterview() {
    const confirmEnd = confirm(
        "Are you sure you want to end the interview? You cannot resume it."
    );

    if (!confirmEnd) return;

    await fetch(`${API_BASE}/end-interview?interview_id=${interviewId}`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    window.location.href = `/result?interview_id=${interviewId}`;
}

// ---------------- INIT ----------------
window.onload = loadQuestion;
