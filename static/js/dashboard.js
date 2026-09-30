
document.addEventListener("DOMContentLoaded", function () {

    // Get dashboard elements
    const search = document.getElementById("problem-search");
    const difficulty = document.getElementById("difficulty-filter");
    const topic = document.getElementById("topic-filter");
    const status = document.getElementById("status-filter");
    const reset = document.getElementById("reset-filters");

    const cards = document.querySelectorAll(".problem-card");
    const noResults = document.getElementById("no-results");


    // SEARCH AND FILTERS

    function filterProblems() {

        if (!search || !difficulty || !topic || !status) {
            return;
        }

        const query = search.value.trim().toLowerCase();
        let visibleCount = 0;

        cards.forEach(function (card) {

            const title = (
                card.dataset.title ||
                card.querySelector("h3")?.textContent ||
                ""
            ).toLowerCase().trim();

            const matchesSearch = title.includes(query);

            const matchesDifficulty =
                difficulty.value === "all" ||
                card.dataset.difficulty === difficulty.value;

            const matchesTopic =
                topic.value === "all" ||
                card.dataset.topic === topic.value;

            const isSolved = card.dataset.solved === "true";

            const matchesStatus =
                status.value === "all" ||
                (status.value === "solved" && isSolved) ||
                (status.value === "unsolved" && !isSolved);

            const shouldShow =
                matchesSearch &&
                matchesDifficulty &&
                matchesTopic &&
                matchesStatus;

            card.style.display = shouldShow ? "" : "none";

            if (shouldShow) {
                visibleCount++;
            }

        });

        // Show a message when no problems match
        if (noResults) {
            noResults.hidden = visibleCount !== 0;
        }

    }


    // CONNECT FILTERS

    if (search && difficulty && topic && status) {

        search.addEventListener("input", filterProblems);

        difficulty.addEventListener("change", filterProblems);

        topic.addEventListener("change", filterProblems);

        status.addEventListener("change", filterProblems);

        filterProblems();

    }


    // RESET FILTERS

    if (reset) {

        reset.addEventListener("click", function () {

            if (!search || !difficulty || !topic || !status) {
                return;
            }

            search.value = "";
            difficulty.value = "all";
            topic.value = "all";
            status.value = "all";

            filterProblems();

            search.focus();

        });

    }


    // CODING PROGRESS BAR

    const progressFill = document.querySelector(".progress-fill");

    if (progressFill) {

        const progress = Number(progressFill.dataset.progress);

        const safeProgress = Number.isFinite(progress)
            ? Math.min(100, Math.max(0, progress))
            : 0;

        progressFill.style.width = safeProgress + "%";

    }


    // MOBILE SIDEBAR

    const menuToggle = document.getElementById("menu-toggle");
    const sidebar = document.getElementById("sidebar");

    if (menuToggle && sidebar) {

        menuToggle.setAttribute("aria-expanded", "false");

        menuToggle.addEventListener("click", function () {

            const isOpen = sidebar.classList.toggle("open");

            menuToggle.setAttribute(
                "aria-expanded",
                String(isOpen)
            );

        });

        // Close sidebar after selecting a navigation link
        sidebar.querySelectorAll("a").forEach(function (link) {

            link.addEventListener("click", function () {

                sidebar.classList.remove("open");

                menuToggle.setAttribute("aria-expanded", "false");

            });

        });

    }

});