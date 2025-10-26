// --- URL Params ---
const params = new URLSearchParams(window.location.search);
const conceptId = params.get("id");
const topicName = params.get("name");

const memory = [];
const recommenders = document.getElementById("similar");

// --- Back Button ---
document.getElementById("back-btn").addEventListener("click", () => {
  window.location.href = "index.html";
});

// --- Fetch Functions ---
async function fetchConceptData(topicId) {
  try {
    const res = await fetch(`https://fetch-supabase-topic-full-xvt4z5lyxa-uc.a.run.app?topic_id=${topicId}`);
    if (!res.ok) throw new Error("Network error");
    return await res.json();
  } catch (err) {
    console.error("Error fetching concept data:", err);
    return null;
  }
}

async function fetchExerciseData(topicId) {
  try {
    const res = await fetch(`https://fetch-supabase-exercise-full-xvt4z5lyxa-uc.a.run.app?topic_id=${topicId}`, {
      method: "GET",
      headers: { "Content-Type": "application/json" }
    });
    if (!res.ok) throw new Error("Network error");
    return await res.json();
  } catch (err) {
    console.error("Error fetching exercise data:", err);
    return null;
  }
}

async function fetchSimilarTopics(topicId, num_recs = 3) {
  try {
    const res = await fetch(`https://fetch-recommendations-xvt4z5lyxa-uc.a.run.app?topic_id=${topicId}&num_recs=${num_recs}`, {
      method: "GET",
      headers: { "Content-Type": "application/json" }
    });
    if (!res.ok) throw new Error("Network error");
    return await res.json();
  } catch (err) {
    console.error("Error fetching recommendations:", err);
    return null;
  }
}

// --- Render Functions ---
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

function renderQuiz(questions) {
  if (!Array.isArray(questions) || questions.length === 0) {
    document.getElementById("quiz").style.display = "none";
    return;
  }

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
      const label = document.createElement("label");
      label.innerHTML = `<input type="radio" name="answer${index}" value="${i}"> ${opt}`;
      block.appendChild(label);
      block.appendChild(document.createElement("br"));
    });

    form.insertBefore(block, submitBtn);
  });

  submitBtn.addEventListener("click", () => {
    let score = 0;
    questions.forEach((q, index) => {
      const selected = document.querySelector(`input[name="answer${index}"]:checked`);
      if (selected && Number(selected.value) === q.answer) {
        score++;
      }
    });

    feedback.textContent = `You scored ${score} out of ${questions.length}`;
    feedback.style.fontWeight = "bold";
    feedback.style.marginTop = "10px";
    feedback.style.color = score === questions.length ? "green" : score >= questions.length / 2 ? "orange" : "red";
  });
}

function renderRecData(rec) {
  if (!Array.isArray(rec) || rec.length === 0) {
    recommenders.innerHTML = "<p>No similar topics found.</p>";
    return;
  }

  recommenders.innerHTML = "<h3>Similar Topics:</h3>";

  rec.forEach(({ id, name, similarity }) => {
    const similar = Math.round(similarity * 100);
    const link = document.createElement("a");
    link.href = `info.html?id=${encodeURIComponent(id)}&name=${encodeURIComponent(name)}`;
    link.className = "recommend-link";
    link.textContent = `${name} ${similar}% Similarity`;

    const wrapper = document.createElement("p");
    wrapper.appendChild(link);
    recommenders.appendChild(wrapper);
  });
}

// --- Main Flow ---
(async () => {
  if (!conceptId) {
    document.body.innerHTML = "<p>Missing concept ID in URL.</p>";
    return;
  }

  const conceptData = await fetchConceptData(conceptId);
  if (conceptData) renderConceptDetails(conceptData);

  const exerciseData = await fetchExerciseData(conceptId);
  if (Array.isArray(exerciseData) && exerciseData.length > 0) {
    renderQuiz(exerciseData);
  } else {
    document.getElementById("quiz").style.display = "none";
  }

  const recData = await fetchSimilarTopics(conceptId);
  renderRecData(recData);
})();

// --- Chatbot Toggle ---
const chatToggle = document.getElementById("chat-toggle");
const chatPopup = document.getElementById("chat-popup");

chatToggle.addEventListener("click", () => {
  const isVisible = chatPopup.classList.contains("visible");

  if (isVisible) {
    chatPopup.classList.remove("visible");
    chatPopup.classList.add("hidden");
    chatToggle.textContent = "Confused? Grasp has got you covered!";
  } else {
    chatPopup.classList.remove("hidden");
    chatPopup.classList.add("visible");
    chatToggle.textContent = "Exit Grasp";
  }
});

// --- Chatbot Messaging ---
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

  const spinner = document.getElementById("loading-indicator");
  spinner.style.display = "block"; 

  try {
    const botReply = await generateBotReply(message, memory, topicName);
    appendMessage("bot", botReply.slice(10));
  } catch (err) {
    appendMessage("bot", "Sorry, something went wrong.");
  } finally {
    spinner.style.display = "none"; 
  }
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