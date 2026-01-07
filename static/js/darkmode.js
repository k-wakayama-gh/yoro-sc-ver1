// darkmode.js


// function: set dark mode adaptively
function setDarkMode() {
    const isDarkMode = localStorage.getItem("isDarkMode");

    if (isDarkMode === "true") {
        document.body.classList.add("dark-mode");
        console.log("success: set dark mode");
    } else if (isDarkMode === "false") {
        // pass
        console.log("success: set light mode");
    } else {
        adaptiveDarkMode();
    };
};


// lemma: function for setDarkMode()
function adaptiveDarkMode() {
    const isDarkMode = window.matchMedia("(prefers-color-scheme:dark)").matches;

    if (isDarkMode === true) {
        document.body.classList.add("dark-mode");
        localStorage.setItem("isDarkMode", true);
        console.log("success: saved dark mode");
    } else if (isDarkMode === false) {
        localStorage.setItem("isDarkMode", false);
        console.log("success: saved light mode");
    };
};


// switch dark mode and light mode
function toggleDarkMode() {
    const isDarkMode = document.body.classList.contains("dark-mode");

    if (isDarkMode) {
        document.body.classList.remove("dark-mode");
        localStorage.setItem("isDarkMode", false);
    } else if (!isDarkMode) {
        document.body.classList.add("dark-mode");
        localStorage.setItem("isDarkMode", true);
    };
};


// event listener to toggleDarkMode()
document.getElementById("toggle-dark-mode-btn").addEventListener("click", function () {
    toggleDarkMode();
});


