// signup.js


function autoInputUsername (input) {
    const email = input.value;
    document.getElementById("username-input").value = email;
};



// sign up form
document.getElementById("sign-up-check-btn").addEventListener("click", async function () {

    // set a stand alone form data
    const formData = new FormData(document.getElementById("sign-up-form"));

    const last_name = formData.get("last_name");
    const first_name = formData.get("first_name");
    const last_name_furigana = formData.get("last_name_furigana");
    const first_name_furigana = formData.get("first_name_furigana");
    const tel = formData.get("tel");
    const postal_code = formData.get("postal_code");
    const address = formData.get("address");
    const email = formData.get("email");

    const username = formData.get("username");
    const plain_password = formData.get("password");

    const signUpInfomation = `
    <ul id="sign-up-check" class="grid-1-2" style="text-align: start; font-size: medium;">
        <li>お名前</li>
        <li>${last_name}　${first_name}</li>
        <li>ふりがな</li>
        <li>${last_name_furigana}　${first_name_furigana}</li>
        <li>電話番号</li>
        <li>${tel}</li>
        <li>郵便番号</li>
        <li>${postal_code}</li>
        <li>住所</li>
        <li>${address}</li>
        <li>メールアドレス</li>
        <li>${email}</li>
        <li>ユーザー名</li>
        <li>${username}</li>
        <li>パスワード</li>
        <li>${plain_password}</li>
    </ul>
    `;

    document.getElementById("sign-up-check-div").textContent = "";
    document.getElementById("sign-up-check-div").insertAdjacentHTML("beforeend", signUpInfomation);

    document.getElementById("sign-up-form").classList.add("hidden");
    document.getElementById("sign-up-check-div").classList.remove("hidden");
    document.getElementById("sign-up-btn").classList.remove("hidden");
    document.getElementById("sign-up-cancel-btn").classList.remove("hidden");
});


    

document.getElementById("sign-up-btn").addEventListener("click", async function () {
    // event.preventDefault(); // prevent the default form sending
    document.getElementById("sign-up-btn").style.pointerEvents = "none"; // prevent double submit
    document.getElementById("sign-up-btn").textContent = "処理中...";

    // フォーム内で:invalidスタイルが適用されている要素の数を取得
    let invalidElementsCount = document.querySelectorAll("form:invalid").length;
    if (invalidElementsCount != 0) {
        document.getElementById("sign-up-btn").textContent = "以上の内容で登録する";
        document.getElementById("sign-up-btn").style.pointerEvents = "auto"; // reactivate sign up btn
        alert("登録に失敗しました。入力内容に不備があります。");
        throw new Error("内容に不備があります。");
    };

    // set a stand alone form data
    const formData = new FormData(document.getElementById("sign-up-form"));

    const last_name = formData.get("last_name");
    const first_name = formData.get("first_name");
    const last_name_furigana = formData.get("last_name_furigana");
    const first_name_furigana = formData.get("first_name_furigana");
    const tel = formData.get("tel");
    const postal_code = formData.get("postal_code");
    const address = formData.get("address");
    const email = formData.get("email");

    const username = formData.get("username");
    const plain_password = formData.get("password");
    
    const body = {
        username: username,
        plain_password: plain_password,
        last_name: last_name,
        first_name: first_name,
        last_name_furigana: last_name_furigana,
        first_name_furigana: first_name_furigana,
        tel: tel,
        postal_code: postal_code,
        address: address,
        email: email,
    };

    // send a post request to the endpoint
    const response = await fetch("/users/signup", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(body),
    });
    if (response.ok) {
        const result = await response.json();
        console.log("success: create a new account", result);
        // location.reload();
        await login(username, plain_password);
        location.href="/signupcomplete";
    } else if (response.status === 406) {
        console.error("error: create a new account");
        document.getElementById("sign-up-btn").textContent = "以上の内容で登録する";
        document.getElementById("sign-up-btn").style.pointerEvents = "auto"; // reactivate sign up btn
        alert("登録に失敗しました。このユーザー名はすでに使用されています。");
    } else {
        console.error("error: create a new account");
        document.getElementById("sign-up-btn").textContent = "以上の内容で登録する";
        document.getElementById("sign-up-btn").style.pointerEvents = "auto"; // reactivate sign up btn
        alert("登録に失敗しました。");
    };
});



async function login (username, password) {
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
    } else {
        alert("ログインに失敗しました");
    };
};



document.getElementById("sign-up-cancel-btn").addEventListener("click", function () {
    document.getElementById("sign-up-form").classList.remove("hidden");
    document.getElementById("sign-up-check-div").classList.add("hidden");
    document.getElementById("sign-up-btn").classList.add("hidden");
    document.getElementById("sign-up-cancel-btn").classList.add("hidden");
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




// logout
document.getElementById("logout-btn").addEventListener("click", function (event) {
    event.preventDefault();
    localStorage.removeItem("accessToken");
    localStorage.removeItem("username");
    console.log("success: logout");
    alert("ログアウトしました。");
    location.reload();
});





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


