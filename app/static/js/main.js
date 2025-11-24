document.addEventListener("DOMContentLoaded", () => {
    setupTabs();
    loadHighlights();
    setupSearch();
    setupAnimeBrowse();
});

function setupTabs() {
    const buttons = document.querySelectorAll(".tab-button");
    const tabs = document.querySelectorAll(".tab-content");

    buttons.forEach(btn => {
        btn.addEventListener("click", () => {
            buttons.forEach(b => b.classList.remove("active"));
            tabs.forEach(t => t.classList.remove("active"));

            btn.classList.add("active");
            const target = btn.getAttribute("data-tab");
            document.getElementById("tab-" + target).classList.add("active");
        });
    });
}

function loadHighlights() {
    fetch("/api/highlights")
        .then(r => r.json())
        .then(data => {
            const container = document.getElementById("highlights-container");
            container.innerHTML = "";

            ["real", "rumor", "fake"].forEach(label => {
                if (!data[label]) return;
                const col = document.createElement("div");
                col.className = "highlight-column";
                col.innerHTML = `<h3>${label.toUpperCase()}</h3>`;
                data[label].forEach(item => {
                    const card = document.createElement("div");
                    card.className = "news-card";
                    card.innerHTML = `<h4>${item.title}</h4><p>${item.text}</p>`;
                    col.appendChild(card);
                });
                container.appendChild(col);
            });
        })
        .catch(err => console.error(err));
}

function setupSearch() {
    const input = document.getElementById("search-input");
    const btn = document.getElementById("search-button");
    const resultDiv = document.getElementById("search-result");

    btn.addEventListener("click", () => {
        const query = input.value.trim();
        if (!query) return;

        resultDiv.innerHTML = "<p>Analyzing...</p>";

        fetch("/api/search", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({query})
        })
            .then(r => r.json())
            .then(data => {
                if (data.error) {
                    resultDiv.innerHTML = `<p class="error">${data.error}</p>`;
                    return;
                }
                const pred = data.prediction;
                const label = pred.label.toUpperCase();
                const conf = (pred.confidence * 100).toFixed(1);

                let html = `<div class="prediction-card">
                    <h3>Prediction: <span class="label-${pred.label}">${label}</span> (${conf}%)</h3>
                    <h4>Similar news from dataset</h4>
                </div>`;

                html += `<ul class="similar-list">`;
                data.similar_news.forEach(item => {
                    html += `<li><strong>[${item.label}]</strong> ${item.title}</li>`;
                });
                html += `</ul>`;

                resultDiv.innerHTML = html;
            })
            .catch(err => {
                console.error(err);
                resultDiv.innerHTML = "<p class='error'>Error calling API.</p>";
            });
    });
}

function setupAnimeBrowse() {
    const input = document.getElementById("anime-input");
    const btn = document.getElementById("anime-button");
    const resultDiv = document.getElementById("anime-result");

    btn.addEventListener("click", () => {
        const name = input.value.trim();
        if (!name) return;
        resultDiv.innerHTML = "<p>Loading...</p>";

        fetch("/api/anime/" + encodeURIComponent(name))
            .then(r => r.json())
            .then(data => {
                const counts = data.counts || {};
                let html = `<h3>Results for "${data.anime}"</h3>`;
                html += `<p>Counts: real=${counts.real || 0}, rumor=${counts.rumor || 0}, fake=${counts.fake || 0}</p>`;
                html += `<ul class="anime-list">`;
                data.items.forEach(item => {
                    html += `<li><strong>[${item.label}]</strong> ${item.title}</li>`;
                });
                html += `</ul>`;
                resultDiv.innerHTML = html;
            })
            .catch(err => {
                console.error(err);
                resultDiv.innerHTML = "<p class='error'>Error calling API.</p>";
            });
    });
}
