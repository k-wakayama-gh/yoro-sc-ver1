// base.js


// textareaの高さを自動調整
function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = (textarea.scrollHeight) + 'px';
};


document.getElementById("user-btn").addEventListener("click", function () {
    if (this.textContent == "ログイン済") {
        document.getElementById("logout-btn").classList.toggle("hidden");
    };
});


document.getElementById("menu-btn").addEventListener("click", function () {
    document.getElementById("nav-mobile-content").classList.toggle("hidden");
});


