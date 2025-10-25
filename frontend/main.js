const topic = document.getElementById("concepts");
const moreButton = document.getElementById("more");

let allData = [];
let visibleCount = 15; 
async function fetchDataAndSort() {
  try {
    const response = await fetch("YOUR_API_ENDPOINT");
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    console.log(data);
    allData = data; // store globally
    return data;
  } catch (error) {
    console.error("Error fetching data:", error);
    return null;
  }
}

const displayConcepts = (data, limit = data.length) => {
  topic.innerHTML = ""; // clear old content
  data.slice(0, limit).forEach((indiv, index) => {
    const { name, internal_relevance_score, relevance_score, is_archived } = indiv;
    if (is_archived) return;

    const btn = document.createElement("button");
    btn.className = "jersey-10-title concept-btn"; // use class instead of id

    if (internal_relevance_score >= 66) {
      btn.style.backgroundColor = "#FF7900";
      btn.textContent = `${name}: Relevance: ${relevance_score} Trending 🔥`;
    } else if (internal_relevance_score >= 33) {
      btn.style.backgroundColor = "#9dc183";
      btn.textContent = `${name}: Relevance: ${relevance_score} Good 😊`;
    } else {
      btn.style.color = "#000000";
      btn.style.backgroundColor = "#90d5ff";
      btn.textContent = `${name}: Relevance: ${relevance_score} Not relavent 😐`;
    }

btn.addEventListener("click", () => {
  window.location.href = `info.html?name=${encodeURIComponent(name)}`;
});

    topic.appendChild(btn);
  });

  moreButton.style.display = data.length > limit ? "block" : "none";
};

(async () => {
  const newData = await fetchDataAndSort();
  if (newData) {
    displayConcepts(newData, visibleCount);
  }
})();

moreButton.addEventListener("click", () => {
  visibleCount += 15;
  displayConcepts(allData, visibleCount);
});