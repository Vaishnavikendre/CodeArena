
/* ==========================================
   CODEARENA — MAIN JAVASCRIPT
   ========================================== */

document.addEventListener("DOMContentLoaded", function () {

    /* ======================================
       SOLVE PROBLEM — ELEMENTS
       ====================================== */

    const runButton = document.getElementById("run-button");
    const submitButton = document.getElementById("submit-button");

    const output = document.getElementById("output");
    const outputStatus = document.querySelector(".output-status");
    const codeEditor = document.getElementById("code-editor");
    const language = document.getElementById("language");

    // Clear Custom Input button
    const clearInputButton = document.getElementById("clear-input");
    const customInput = document.getElementById("custom-input");

    if (clearInputButton && customInput) {
        clearInputButton.addEventListener("click", function () {
            customInput.value = "";
            customInput.focus();
        });
    }

    
const starterCode = {
    python: `def solve(arr):
    # Write your solution here
    pass`,

    java: `import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        // Write your solution here

        sc.close();
    }
}`
};

// Save drafts separately for each problem.
const problemId = submitButton.dataset.problemId;
const storageKey = `codearena-drafts-${problemId}`;

// Load previously saved code, if available.
let storedCode = {};

try {
    storedCode = JSON.parse(localStorage.getItem(storageKey)) || {};
} catch (error) {
    storedCode = {};
}

let previousLanguage = language.value;

const savedCode = {
    python: storedCode.python ?? (
        previousLanguage === "python"
            ? codeEditor.value
            : starterCode.python
    ),

    java: storedCode.java ?? (
        previousLanguage === "java"
            ? codeEditor.value
            : starterCode.java
    )
};

// Restore the saved code for the currently selected language.
codeEditor.value = savedCode[previousLanguage];

// Automatically save changes while typing.
codeEditor.addEventListener("input", function () {
    savedCode[language.value] = codeEditor.value;
    localStorage.setItem(storageKey, JSON.stringify(savedCode));
});

// Save and restore code when switching languages
language.addEventListener("change", function () {
    const newLanguage = language.value;

    savedCode[previousLanguage] = codeEditor.value;
    localStorage.setItem(storageKey, JSON.stringify(savedCode));

    codeEditor.value =
        savedCode[newLanguage] ?? starterCode[newLanguage] ?? "";

    previousLanguage = newLanguage;
});


/* MONACO EDITOR */

let monacoEditorInstance = null;
const monacoContainer = document.getElementById("monaco-editor");


if (monacoContainer && typeof require !== "undefined") {
    require.config({
        paths: {
            vs: "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.52.2/min/vs"
        }
    });

    require(["vs/editor/editor.main"], function () {
        monacoEditorInstance = monaco.editor.create(monacoContainer, {
            value: codeEditor.value,
            language: language.value,
            theme: "vs-dark",
            automaticLayout: true,
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: "on",
            scrollBeyondLastLine: false
        });

        // Send Monaco changes to the original textarea
        monacoEditor.onDidChangeModelContent(function () {
            codeEditor.value = monacoEditor.getValue();
            codeEditor.dispatchEvent(new Event("input"));
        });

        // Restore the correct code when switching languages
        language.addEventListener("change", function () {
            monaco.editor.setModelLanguage(
                monacoEditor.getModel(),
                language.value
            );
            monacoEditor.setValue(codeEditor.value);
        });

        // Show Monaco and hide the original textarea
        monacoContainer.style.display = "block";
        codeEditor.style.display = "none";
        monacoEditor.layout();
    });
}

// Reset Code button
const resetCodeButton = document.getElementById("reset-code");

if (resetCodeButton) {
    resetCodeButton.addEventListener("click", function () {
        const shouldReset = confirm(
            "Reset your current code? Your changes in this language will be lost."
        );

        if (!shouldReset) {
            return;
        }

        const currentLanguage = language.value;
        const originalCode = starterCode[currentLanguage] || "";

        // Update Monaco
        if (monacoEditorInstance) {
            monacoEditorInstance.setValue(originalCode);
        }
        // Update textarea
        codeEditor.value = originalCode;

        // Update saved draft
        savedCode[currentLanguage] = originalCode;
        localStorage.setItem(
            storageKey,
            JSON.stringify(savedCode)
        );
    });
}

    let isProcessing = false;


    /* ======================================
       HELPER FUNCTIONS
       ====================================== */

    function showOutput(message, type = "normal") {

        if (!output) return;

        output.textContent = message;

        output.style.color = {
            success: "#a8ddb1",
            error: "#f0aaa2",
            warning: "#efd09b",
            normal: "#e1e8da"
        }[type] || "#e1e8da";
    }


    function setProcessing(processing, action = "") {

        isProcessing = processing;

        if (runButton) {
            runButton.disabled = processing;

            runButton.textContent =
                processing && action === "run"
                    ? "Running..."
                    : "▶ Run Code";
        }

        if (submitButton) {
            submitButton.disabled = processing;

            submitButton.textContent =
                processing && action === "submit"
                    ? "Judging..."
                    : "Submit Solution ↗";
        }

        if (language) {
            language.disabled = processing;
        }
    }


    function validateCode() {

        if (!codeEditor || !language) {
            return false;
        }

        if (!codeEditor.value.trim()) {
            showOutput(
                "Please write some Python code before running or submitting.",
                "warning"
            );

            codeEditor.focus();

            return false;
        }

        return true;
    }


    async function readResponse(response) {

        let result;

        try {
            result = await response.json();
        } catch (error) {
            throw new Error(
                "The server returned an invalid response. Check your Flask terminal."
            );
        }

        if (!response.ok) {
            throw new Error(
                result.error ||
                result.message ||
                `Server error (${response.status}).`
            );
        }

        return result;
    }


    /* ======================================
       RUN CODE
       ====================================== */

    if (runButton && submitButton && output && codeEditor && language) {

        runButton.addEventListener("click", async function () {

            if (outputStatus) {
                outputStatus.textContent = "● Running...";
            }

            if (isProcessing || !validateCode()) {
                return;
            }

            const code = codeEditor.value;

            setProcessing(true, "run");

            showOutput(
                "Running your Python code...\nPlease wait.",
                "normal"
            );

            try {

                const response = await fetch("/run-code", {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        code,
                        language: language.value,
                        custom_input: document.getElementById("custom-input").value
                    })
                });

                const result = await readResponse(response);

                if (result.success) {

                    if (outputStatus) {
                        outputStatus.textContent = "● Execution Successful";
                        outputStatus.style.color = "#9fcf9f";
                    }


                    const programOutput =
                        result.output !== undefined &&
                        result.output !== null &&
                        String(result.output).length > 0
                            ? String(result.output)
                            : "Your code executed successfully, but produced no output.";

                    showOutput(
                        "✓ Execution completed\n\n" + programOutput,
                        "success"
                    );

                } else {

                    if (outputStatus) {
                        outputStatus.textContent = "● Execution Failed";
                        outputStatus.style.color = "#d98f8f";
                    }

                    showOutput(
                        "✕ Execution failed\n\n" +
                        (result.error || "An unknown error occurred."),
                        "error"
                    );
                }

            } catch (error) {

                showOutput(
                    "✕ Unable to run your code\n\n" +
                    error.message +
                    "\n\nMake sure your Flask server is running.",
                    "error"
                );

                console.error("Run Code error:", error);

            } finally {

                setProcessing(false);

            }

        });


        /* ==================================
           SUBMIT SOLUTION
           ================================== */

        submitButton.addEventListener("click", async function () {

            if (isProcessing || !validateCode()) {
                return;
            }

            const code = codeEditor.value;
            const problemId = submitButton.dataset.problemId;

            if (!problemId) {

                showOutput(
                    "Problem ID is missing. Refresh the page and try again.",
                    "error"
                );

                return;
            }

            setProcessing(true, "submit");

            if (outputStatus) {
                outputStatus.textContent = "● Judging...";
                outputStatus.style.color = "#e7c891";
            }

            showOutput(
                "Judging your solution...\nRunning the test cases.",
                "normal"
            );

            try {

                const response = await fetch("/submit", {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        code: code,
                        problem_id: problemId,
                        language: language.value
                    })
                });

                const result = await readResponse(response);

                const passed = result.passed ?? 0;
                const total = result.total ?? 0;

                const testSummary =
                    "\n\nTests Passed: " +
                    passed +
                    " / " +
                    total;

                if (result.status === "Accepted") {

                    if (outputStatus) {
                        outputStatus.textContent = "● Accepted";
                        outputStatus.style.color = "#9fcf9f";
                    }

                    showOutput(
                        "✓ Accepted!\n\n" +
                        "Your solution passed all the test cases." +
                        testSummary +
                        "\n\nYou can view this attempt in My Submissions.",
                        "success"
                    );

                } else if (result.status === "Wrong Answer") {

                    if (outputStatus) {
                        outputStatus.textContent = "● Wrong Answer";
                        outputStatus.style.color = "#d98f8f";
                    }

                    showOutput(
                        "✕ Wrong Answer\n\n" +
                        "Your code ran, but some test cases did not pass." +
                        testSummary +
                        "\n\nReview your logic and try again.",
                        "error"
                    );

                } else if (result.status === "Time Limit Exceeded") {

                    if (outputStatus) {
                        outputStatus.textContent = "● Time Limit Exceeded";
                        outputStatus.style.color = "#e7c891";
                    }

                    showOutput(
                        "⚠ Time Limit Exceeded\n\n" +
                        "Your solution took too long to execute." +
                        testSummary +
                        "\n\nTry a more efficient approach.",
                        "warning"
                    );

                } else if (result.status === "Runtime Error") {

                    if (outputStatus) {
                        outputStatus.textContent = "● Runtime Error";
                        outputStatus.style.color = "#d98f8f";
                    }

                    showOutput(
                        "✕ Runtime Error\n\n" +
                        (result.error || "Your code encountered an error.") +
                        testSummary,
                        "error"
                    );

                } else {

                    if (outputStatus) {
                        outputStatus.textContent =
                            "● " + (result.status || "Submission Error");

                        outputStatus.style.color = "#e7c891";
                    }

                    showOutput(
                        "⚠ " +
                        (result.status || "Submission Error") +
                        "\n\n" +
                        (result.error || "Please review your code and try again.") +
                        testSummary,
                        "warning"
                    );

                }

            } catch (error) {

                showOutput(
                    "✕ Unable to submit your solution\n\n" +
                    error.message +
                    "\n\nCheck that your Flask server is running.",
                    "error"
                );

                console.error("Submission error:", error);

            } finally {

                setProcessing(false);

            }

        });

    }


    /* ======================================
       DASHBOARD SEARCH AND FILTERS
       ====================================== */

    const problemSearch = document.getElementById("problem-search");
    const difficultyFilter = document.getElementById("difficulty-filter");
    const topicFilter = document.getElementById("topic-filter");
    const statusFilter = document.getElementById("status-filter");

    const resetFiltersButton =
        document.getElementById("reset-filters");


    function filterProblems() {

        if (
            !problemSearch ||
            !difficultyFilter ||
            !topicFilter ||
            !statusFilter
        ) {
            return;
        }

        const searchText =
            problemSearch.value.trim().toLowerCase();

        const difficulty = difficultyFilter.value;
        const topic = topicFilter.value;
        const status = statusFilter.value;

        const cards =
            document.querySelectorAll(".problem-card");

        cards.forEach(function (card) {

            const title =
                (card.dataset.title || "").toLowerCase();

            const cardDifficulty =
                card.dataset.difficulty || "";

            const cardTopic =
                card.dataset.topic || "";

            const isSolved =
                card.dataset.solved === "true";


            const matchesSearch =
                title.includes(searchText);

            const matchesDifficulty =
                difficulty === "all" ||
                cardDifficulty === difficulty;

            const matchesTopic =
                topic === "all" ||
                cardTopic === topic;

            const matchesStatus =
                status === "all" ||
                (status === "solved" && isSolved) ||
                (status === "unsolved" && !isSolved);


            card.style.display =
                matchesSearch &&
                matchesDifficulty &&
                matchesTopic &&
                matchesStatus
                    ? ""
                    : "none";

        });

    }


    if (
        problemSearch &&
        difficultyFilter &&
        topicFilter &&
        statusFilter
    ) {

        problemSearch.addEventListener(
            "input",
            filterProblems
        );

        difficultyFilter.addEventListener(
            "change",
            filterProblems
        );

        topicFilter.addEventListener(
            "change",
            filterProblems
        );

        statusFilter.addEventListener(
            "change",
            filterProblems
        );

    }


    /* ======================================
       RESET DASHBOARD FILTERS
       ====================================== */

    if (resetFiltersButton) {

        resetFiltersButton.addEventListener(
            "click",
            function () {

                if (
                    !problemSearch ||
                    !difficultyFilter ||
                    !topicFilter ||
                    !statusFilter
                ) {
                    return;
                }

                problemSearch.value = "";
                difficultyFilter.value = "all";
                topicFilter.value = "all";
                statusFilter.value = "all";

                filterProblems();

            }
        );

    }

});