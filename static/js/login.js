// login.js


// on loading page: fetch username
document.addEventListener("DOMContentLoaded", function () {
    displayUsername();
});


async function displayUsername() {
    const myUsername = await fetchMyUsername();
    if (myUsername.length != 0) {
        // const shortName = myUsername.slice(0, 6);
        // document.getElementById("user-btn").textContent = shortName;
        // console.log("short name: ", shortName);
        document.getElementById("user-btn").textContent = "ログイン済";
        document.getElementById("user-btn").style.color = "lightblue";
    } else {
        document.getElementById("user-btn").style.color = "lightgoldenrodyellow";
    };
};


// fetch my username and confirm login
async function fetchMyUsername() {
    const token = loadAccessToken();
    const response = await fetch("/my/username", {
        method: "GET",
        headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
    });
    if (response.ok) {
        const result = await response.json();
        console.log("success: fetchMyUsername()", result);
        renderOnLogin();
        document.getElementById("user-btn").classList.remove("is-loged-out");
        return result;
    } else {
        console.error("error: fetchMyUsername()");
        renderOnLogout();
        return []; // empty <=> length == 0
    };
};



// login form
document.getElementById("login-form").addEventListener('submit', async function (event) {
    event.preventDefault();
    document.getElementById("login-btn").style.pointerEvents = "none"; // prevent double submit
    document.getElementById("login-btn").textContent = "ログイン中...";
    document.getElementById("login-failed-message").classList.add("hidden");
    const loginForm = document.getElementById("login-form");
    
    const formData = new FormData(loginForm);
    const username = formData.get("username");
    const password = formData.get("password");

    // ログインはjsonでなくform dataを送信する
    const response = await fetch("/token", {
        method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body: `username=${username}&password=${password}`,
    });

    if (response.ok) {
        const { access_token } = await response.json(); // { access_token } <=> response.access_token
        localStorage.setItem("accessToken", access_token);
        localStorage.setItem("username", username);

        console.log("success: login");
        location.reload();
    } else {
        // alert("ログインに失敗しました。もう一度やり直してください。");
        document.getElementById("login-failed-message").classList.remove("hidden");
        // reactivate submit button
        document.getElementById("login-btn").style.pointerEvents = "auto";
        document.getElementById("login-btn").textContent = "ログインする";
    };
});



// logout
document.getElementById("logout-btn").addEventListener("click", function (event) {
    event.preventDefault();
    localStorage.removeItem("accessToken");
    localStorage.removeItem("username");
    console.log("success: logout");
    alert("ログアウトしました。");
    location.reload();
});




// load access token from local storage
function loadAccessToken() {
    try {
        const token = localStorage.getItem("accessToken");
        return token;
    } catch (error) {
        console.error("Failed to load access token", error);
    };
};






// switch rendering depending on login status: logout
function renderOnLogout () {
    document.querySelectorAll(".on-login").forEach(function (x) {
        x.classList.add("hidden");
    });
    document.querySelectorAll(".on-logout").forEach(function (x) {
        x.classList.remove("hidden");
    });
};



// switch rendering depending on login status: login
function renderOnLogin () {
    document.querySelectorAll(".on-login").forEach(function (x) {
        x.classList.remove("hidden");
    });
    document.querySelectorAll(".on-logout").forEach(function (x) {
        x.classList.add("hidden");
    });
};


