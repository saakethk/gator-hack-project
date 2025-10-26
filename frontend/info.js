// --- Grab topic_id from URL ---
const params = new URLSearchParams(window.location.search);
const conceptId = params.get("id"); // URL should be info.html?id=123
const topicName = params.get("name");

const memory = [];
let exerciseDataArray = [];

// --- Back button ---
document.getElementById("back-btn").addEventListener("click", () => {
  window.location.href = "main.html";
});

// --- Fetch concept data ---
async function fetchConceptData(topicId) {
  try {
    const res1 = await fetch(
      `https://fetch-supabase-topic-full-xvt4z5lyxa-uc.a.run.app?topic_id=${topicId}`
    );
    if (!res1.ok) throw new Error("Network error");
    const data = await res1.json(); // parse JSON
    return data;
  } catch (err) {
    console.error("Error fetching concept data:", err);
    return null;
  }
}

async function fetchExerciseData(topicId){
  try {
    const res2 = await fetch(`https://fetch-supabase-exercise-full-xvt4z5lyxa-uc.a.run.app?topic_id=${encodeURIComponent(topicId)}`,
      { 
        method: "GET",
       headers: {"Content-Type": "application/json"}
      }
    );
    if (!res2.ok) throw new Error("Network error");
    const exerciseData = await res2.json();
    exerciseDataArray = exerciseData;
    return exerciseData;
  } catch (err) {
    console.error("Error fetching concept data:", err);
    return null;
  }
}

// --- Render concept details ---
function renderConceptDetails(data) {
  document.querySelector("h1.jersey-10-title").textContent = data.name || conceptId;
  document.getElementById("summary").textContent = data.summary || "No summary available.";

  document.getElementById("pros-list").innerHTML = Array.isArray(data.pros)
    ? data.pros.map(item => `<li>${item}</li>`).join("")
    : "";

  document.getElementById("cons-list").innerHTML = Array.isArray(data.cons)
    ? data.cons.map(item => `<li>${item}</li>`).join("")
    : "";
}

// --- Render quiz ---
function renderQuiz(questions) {
  const form = document.getElementById("mcq-form");
  const submitBtn = document.getElementById("submit-answer");
  const feedback = document.getElementById("feedback");

  questions.forEach((q, index) => {
    const block = document.createElement("div");
    block.className = "question-block";

    const p = document.createElement("p");
    p.textContent = q.question;
    block.appendChild(p);

    q.answer_choices.forEach((opt, i) => {
      const letter = String.fromCharCode(65 + i);
      const label = document.createElement("label");
      label.innerHTML = `<input type="radio" name="answer${index}" value="${i}"> ${opt}`;
      block.appendChild(label);
      block.appendChild(document.createElement("br"));
      i = i+1
    });

    form.insertBefore(block, submitBtn);
  });
 
  submitBtn.addEventListener("click", () => {
    let score = 0;
    questions.forEach((q, index) => {
      const selected = document.querySelector(`input[name="answer${index}"]:checked`);
      if (Number(selected.value) === q.answer){
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
  if (!conceptId) return;
  const conceptData = await fetchConceptData(conceptId);
  renderConceptDetails(conceptData);
  const data = await fetchExerciseData(conceptId)
  console.log(data)
  if (data.length > 0) {
    renderQuiz(data);
  } else {
    document.getElementById("quiz").style.display = "none";
  }
})();

// --- Chatbot toggle ---
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

// --- Chatbot messaging ---
const chatWindow = document.getElementById("chat-window");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

async function sendMessage() {
  const message = userInput.value.trim();
  if (!message) return;

  appendMessage("user", message);
  userInput.value = "";

  setTimeout(async () => {
    const botReply = await generateBotReply(message, memory, topicName);
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

async function generateBotReply(userMsg, memoryArray, topic) {
  try {
    const res = await fetch(
      `https://chat-request-xvt4z5lyxa-uc.a.run.app/?query=${encodeURIComponent(userMsg)}&history=${encodeURIComponent(JSON.stringify(memoryArray))}&topic=${encodeURIComponent(topic)}`,
      {
        method: "GET",
        headers: { "Content-Type": "application/json" }
      }
    );

    if (!res.ok) throw new Error("Network error");

    const data = await res.text();
    const reply = data || "No reply received.";

    memoryArray.push({ role: "user", content: userMsg });
    memoryArray.push({ role: "bot", content: reply });

    return reply;
  } catch (err) {
    console.error("Error fetching chatbot response:", err);
    return "Sorry, something went wrong.";
  }
}