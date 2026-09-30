
document.addEventListener("DOMContentLoaded", function () {

    // SEARCH AND FILTERS

    const searchInput = document.getElementById("submission-search");
    const statusFilter = document.getElementById("status-filter");
    const resetButton = document.getElementById("reset-filters");

    const submissionRows = Array.from(
        document.querySelectorAll(".submission-row")
    );

    const noResults = document.getElementById("no-results");
    const emptyMessage = document.getElementById("empty-message");


    function filterSubmissions() {

        if (!searchInput || !statusFilter) {
            return;
        }

        const searchText = searchInput.value.trim().toLowerCase();
        const selectedStatus = statusFilter.value;

        let visibleCount = 0;

        submissionRows.forEach(function (row) {

            const problemTitle = (
                row.dataset.title || ""
            ).toLowerCase();

            const submissionStatus = row.dataset.status || "";

            const matchesSearch = problemTitle.includes(searchText);

            const matchesStatus =
                selectedStatus === "all" ||
                submissionStatus === selectedStatus;

            const shouldShow = matchesSearch && matchesStatus;

            row.hidden = !shouldShow;

            if (shouldShow) {
                visibleCount++;
            }

        });


        // Display the empty state when there are no matches

        if (noResults) {
            noResults.hidden = visibleCount > 0;
        }

        if (emptyMessage && submissionRows.length > 0) {
            emptyMessage.textContent =
                "Try a different search or reset your filters.";
        }

    }


    // CONNECT SEARCH AND STATUS FILTER

    if (searchInput) {
        searchInput.addEventListener("input", filterSubmissions);
    }

    if (statusFilter) {
        statusFilter.addEventListener("change", filterSubmissions);
    }


    // RESET BUTTON

    if (resetButton) {

        resetButton.addEventListener("click", function () {

            if (searchInput) {
                searchInput.value = "";
            }

            if (statusFilter) {
                statusFilter.value = "all";
            }

            filterSubmissions();

            if (searchInput) {
                searchInput.focus();
            }

        });

    }


    // ANIMATED TEST-CASE PROGRESS BARS

    const progressBars = document.querySelectorAll(".tests-fill");

    progressBars.forEach(function (bar) {

        const progress = Number(bar.dataset.progress);

        const safeProgress = Number.isFinite(progress)
            ? Math.max(0, Math.min(100, progress))
            : 0;

        bar.style.width = safeProgress + "%";

    });


    // MOBILE SIDEBAR

    const menuToggle = document.getElementById("menu-toggle");
    const sidebar = document.getElementById("sidebar");

    if (menuToggle && sidebar) {

        menuToggle.addEventListener("click", function () {

            const isOpen = sidebar.classList.toggle("open");

            menuToggle.setAttribute(
                "aria-expanded",
                String(isOpen)
            );

        });


        // Close sidebar after clicking a navigation link

        const sidebarLinks = sidebar.querySelectorAll("a");

        sidebarLinks.forEach(function (link) {

            link.addEventListener("click", function () {

                sidebar.classList.remove("open");

                menuToggle.setAttribute(
                    "aria-expanded",
                    "false"
                );

            });

        });


        // Close sidebar when clicking outside it on mobile

        document.addEventListener("click", function (event) {

            const clickedInsideSidebar =
                sidebar.contains(event.target);

            const clickedMenuButton =
                menuToggle.contains(event.target);

            if (
                sidebar.classList.contains("open") &&
                !clickedInsideSidebar &&
                !clickedMenuButton
            ) {

                sidebar.classList.remove("open");

                menuToggle.setAttribute(
                    "aria-expanded",
                    "false"
                );

            }

        });

    }


    // INITIALIZE FILTERS

    filterSubmissions();

});