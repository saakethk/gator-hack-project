
const params = new URLSearchParams(window.location.search);
const conceptName = params.get("name");


document.getElementById("back-btn").addEventListener("click", () => {
  window.location.href = "main.html"; // adjust to your actual main page
});


async function fetchConceptData(name) {
  try {
    const res = await fetch(`YOUR_API_ENDPOINT?name=${encodeURIComponent(name)}`);
    if (!res.ok) throw new Error("Network error");
    const data = await res.json();
    return data;
  } catch (err) {
    console.error("Error fetching concept data:", err);
    return null;
  }
}

function renderConceptDetails(data) {
  document.querySelector("h1.jersey-10-title").textContent = data.name || conceptName;
  document.getElementById("summary").textContent = data.summary || "No summary available.";

  document.getElementById("pros-list").innerHTML = Array.isArray(data.pros)
    ? data.pros.map(item => `<li>${item}</li>`).join("")
    : "";

  document.getElementById("cons-list").innerHTML = Array.isArray(data.cons)
    ? data.cons.map(item => `<li>${item}</li>`).join("")
    : "";
}

function renderQuiz(questions) {
  const form = document.getElementById("mcq-form");
  const submitBtn = document.getElementById("submit-answer");
  const feedback = document.getElementById("feedback");

  if (!questions || questions.length === 0) {
    document.getElementById("quiz").style.display = "none";
    return;
  }

  questions.forEach((q, index) => {
    const block = document.createElement("div");
    block.className = "question-block";

    const p = document.createElement("p");
    p.textContent = q.question;
    block.appendChild(p);

    q.options.forEach((opt, i) => {
      const letter = String.fromCharCode(65 + i); 
      const label = document.createElement("label");
      label.innerHTML = `<input type="radio" name="answer${index}" value="${letter}"> ${opt}`;
      block.appendChild(label);
      block.appendChild(document.createElement("br"));
    });

    form.insertBefore(block, submitBtn);
  });

  submitBtn.addEventListener("click", () => {
    let score = 0;
    questions.forEach((q, index) => {
      const selected = document.querySelector(`input[name="answer${index}"]:checked`);
      if (selected && selected.value === q.correct) {
        score++;
      }
    });

    feedback.textContent = `You scored ${score} out of ${questions.length}`;
    feedback.style.fontWeight = "bold";
    feedback.style.marginTop = "10px";

    if (score === questions.length) {
      feedback.style.color = "green";
    } else if (score >= questions.length / 2) {
      feedback.style.color = "orange";
    } else {
      feedback.style.color = "red";
    }
  });
}

// --- Main flow ---
(async () => {
  if (!conceptName) return;

  const data = await fetchConceptData(conceptName);
  if (!data) return;

  renderConceptDetails(data);

  if (data.questions && data.questions.length > 0) {
    renderQuiz(data.questions);
  } else {
    document.getElementById("quiz").style.display = "none";
  }
})();
const chatToggle = document.getElementById("chat-toggle");
const chatPopup = document.getElementById("chat-popup");

chatToggle.addEventListener("click", () => {
  const isVisible = chatPopup.classList.contains("visible");

  if (isVisible) {
    chatPopup.classList.remove("visible");
    chatPopup.classList.add("hidden");
    chatToggle.textContent = "Confused? Our Chatbot has got you covered!";
  } else {
    chatPopup.classList.remove("hidden");
    chatPopup.classList.add("visible");
    chatToggle.textContent = "Exit Chatbot";
  }
});
const chatWindow = document.getElementById("chat-window");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

function sendMessage() {
  const message = userInput.value.trim();
  if (!message) return;

  appendMessage("user", message);
  userInput.value = "";
  setTimeout(() => {
    const botReply = generateBotReply(message);
    appendMessage("bot", botReply);
  }, 500);
}

function appendMessage(sender, text) {
  const msg = document.createElement("div");
  msg.className = `message ${sender}`;
  msg.textContent = text;
  chatWindow.appendChild(msg);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function generateBotReply(userMsg) {
    if(None){
        return `You said: "${userMsg}"`;
    }
}