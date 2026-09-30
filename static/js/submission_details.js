
/* ========================================
   CODEARENA — SUBMISSION DETAILS
   ======================================== */

document.addEventListener("DOMContentLoaded", () => {

    // TEST CASE PROGRESS BAR

    const progressBar = document.querySelector(".progress-fill");

    if (progressBar) {
        const rawProgress = Number(progressBar.dataset.progress);

        // Keep the percentage between 0 and 100.
        const percentage = Number.isFinite(rawProgress)
            ? Math.min(100, Math.max(0, rawProgress))
            : 0;

        // Start at zero and animate to the actual result.
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                progressBar.style.width = `${percentage}%`;
            });
        });

        progressBar.setAttribute("role", "progressbar");
        progressBar.setAttribute("aria-label", "Test cases passed");
        progressBar.setAttribute("aria-valuemin", "0");
        progressBar.setAttribute("aria-valuemax", "100");
        progressBar.setAttribute("aria-valuenow", String(percentage));
    }


    // COPY SUBMITTED CODE

    const copyButton = document.getElementById("copy-code");
    const submittedCode = document.getElementById("submitted-code");

    if (copyButton && submittedCode) {

        const originalButtonText = copyButton.textContent.trim();

        copyButton.addEventListener("click", async () => {

            const code = submittedCode.textContent;

            if (!code) {
                copyButton.textContent = "No code to copy";
                return;
            }

            try {
                // Works on localhost and secure HTTPS websites.
                if (navigator.clipboard && window.isSecureContext) {
                    await navigator.clipboard.writeText(code);
                } else {
                    // Fallback for browsers without Clipboard API.
                    const temporaryTextarea =
                        document.createElement("textarea");

                    temporaryTextarea.value = code;
                    temporaryTextarea.style.position = "fixed";
                    temporaryTextarea.style.opacity = "0";

                    document.body.appendChild(temporaryTextarea);

                    temporaryTextarea.select();

                    const copied = document.execCommand("copy");

                    temporaryTextarea.remove();

                    if (!copied) {
                        throw new Error("Copy command failed");
                    }
                }

                copyButton.textContent = "✓ Copied!";
                copyButton.classList.add("copied");

            } catch (error) {

                console.error("Unable to copy code:", error);

                copyButton.textContent = "Copy failed";
                copyButton.classList.remove("copied");

            }

            // Restore the button after two seconds.
            setTimeout(() => {
                copyButton.textContent = originalButtonText;
                copyButton.classList.remove("copied");
            }, 2000);

        });
    }

});