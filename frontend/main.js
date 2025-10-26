const topic = document.getElementById("concepts");
const moreButton = document.getElementById("more");

let allData = [];
const limit = 15;
let offset = 0; // start at 0

async function fetchDataAndSort(limit, offset) {
  try {
    const res = await fetch(
      `https://fetch-supabase-topics-xvt4z5lyxa-uc.a.run.app?limit=${limit}&offset=${offset}`,
      {
        method: "GET",
        headers: { "Content-Type": "application/json" }
      }
    );
    if (!res.ok) throw new Error("Network error");
    const data = await res.json();
    allData.push(...data); // append properly
        // 👇 Decide whether to show/hide the More button
    if (data.length < limit) {
      // fewer than limit means no more data
      moreButton.style.display = "none";
    } else {
      moreButton.style.display = "block";
    }
    console.log(data)
    return data;
  } catch (err) {
    console.error("Error fetching topics:", err);
    return null;
  }
}

const displayConcepts = (data) => {
  data.forEach((indiv) => {
    const { id, name, internal_relevance_score, relevance_score, date_added } = indiv;

    const btn = document.createElement("button");
    btn.className = "jersey-10-title concept-btn multi-line-button";
    const date = date_added ? date_added.slice(0, 10) : "";

    if (internal_relevance_score >= 1) {
      btn.style.borderColor = "#ffa657ff";
      btn.innerHTML = `${name}:<br> Trending 🔥 ${date}`;
    } else if (internal_relevance_score >= 0) {
      btn.style.borderColor = "#9dc183";
      btn.style.backgroundColor = "#eafbe3ff"
      btn.innerHTML = `${name}:<br> Relevant 😊 ${date}`;
    } else {
      btn.style.borderColor = "#90d5ff";
      btn.style.backgroundColor = "#F0F8FF"
      btn.innerHTML = `${name}:<br> Not relevant 😐 ${date}`;
    }

    btn.addEventListener("click", () => {
      window.location.href = `info.html?id=${encodeURIComponent(id)}&name=${encodeURIComponent(name)}`;
    });

    topic.appendChild(btn);
  });
};

// --- Initial load ---
(async () => {
  const newData = await fetchDataAndSort(limit, offset);
  if (newData) {
    displayConcepts(newData);
  }
})();

// --- Load more ---
moreButton.addEventListener("click", async () => {
  offset += limit;
  const moreData = await fetchDataAndSort(limit, offset);
  if (moreData) {
    displayConcepts(moreData);
  }
});