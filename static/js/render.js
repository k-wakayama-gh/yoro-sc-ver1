// render.js


// switch rendering depending on login status: logout
function renderOnLogout () {
    document.querySelectorAll(".on-login").forEach(function(x) {
        x.classList.add("hidden");
    });
    document.querySelectorAll(".on-logout").forEach(function(x) {
        x.classList.remove("hidden");
    });
};



// switch rendering depending on login status: login
function renderOnLogin () {
    document.querySelectorAll(".on-login").forEach(function(x) {
        x.classList.remove("hidden");
    });
    document.querySelectorAll(".on-logout").forEach(function(x) {
        x.classList.add("hidden");
    });
};

