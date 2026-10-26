
const searchInput = document.getElementById("labSearch");
const labCards = document.querySelectorAll(".lab-card[data-name]");
const noResults = document.getElementById("noResults");

if (searchInput) {
    searchInput.addEventListener("input", () => {
        const query = searchInput.value.toLowerCase().trim();
        let visibleCount = 0;

        labCards.forEach((card) => {
            const matches = card.dataset.name.includes(query);
            card.style.display = matches ? "" : "none";
            if (matches) visibleCount++;
        });

        if (noResults) {
            noResults.hidden = visibleCount !== 0;
        }
    });
}
