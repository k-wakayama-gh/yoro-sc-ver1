// my/childrensignup.js


document.querySelectorAll("#select-number-of-children > span").forEach(function (x) {
    x.addEventListener("click", function () {
        const number = x.dataset.number;
        document.getElementById("counter").textContent = number;
        resetNumberButton();
        x.classList.add("selected");
        console.log(number);
        const children = document.querySelectorAll(".each-child");
        children.forEach(function (y) {
            y.classList.add("hidden");
        });
        const targetElements = Array.prototype.slice.call(children, 0, number);
        targetElements.forEach(function (y) {
            y.classList.remove("hidden");
        });
    });
});


function resetNumberButton() {
    document.querySelectorAll("#select-number-of-children > span").forEach(function (x) {
        x.classList.remove("selected");
    });
};



// children signup form
document.getElementById("signup-check-btn").addEventListener("click", async function () {

    document.getElementById("signup-check-div").textContent = "";

    const number = document.getElementById("counter").textContent;

    const children = document.querySelectorAll(".each-child > form");
    const targetElements = Array.prototype.slice.call(children, 0, number);

    let eachNumber = 1;

    targetElements.forEach(function (x) {

        // set a stand alone form data
        console.log(x);
        const formData = new FormData(x);
    
        const last_name = formData.get("last_name");
        const first_name = formData.get("first_name");
        const last_name_furigana = formData.get("last_name_furigana");
        const first_name_furigana = formData.get("first_name_furigana");
    
        const signUpInfomation = `
        <p class="numbering">${eachNumber}</p>
        <ul class="grid-1-2" style="text-align: start; font-size: medium;">
            <li>氏名</li>
            <li>${last_name}　${first_name}</li>
            <li>ふりがな</li>
            <li>${last_name_furigana}　${first_name_furigana}</li>
        </ul>
        <div class="space"></div>
        `;
        document.getElementById("signup-check-div").insertAdjacentHTML("beforeend", signUpInfomation);

        eachNumber += 1;
    });

    document.getElementById("children-signup-form").classList.add("hidden");
    document.getElementById("signup-check-div").classList.remove("hidden");
    document.getElementById("signup-btn").classList.remove("hidden");
    document.getElementById("signup-cancel-btn").classList.remove("hidden");
});


    

document.getElementById("signup-btn").addEventListener("click", async function () {
    document.getElementById("signup-btn").style.pointerEvents = "none"; // prevent double submit
    document.getElementById("signup-btn").textContent = "処理中...";

    const number = document.getElementById("counter").textContent;

    const ignoreNumber = (5 - number);

    for (let i=number + 1; i <= 5; i++) {
        const selector = `#children-name-div:nthchild(${i}) input`;
        document.querySelectorAll(selector).forEach(function (x) {
            x.value = "";
        });
    };

    // フォーム内で:invalidスタイルが適用されている要素の数を取得
    let invalidElementsCount = document.querySelectorAll(".each-child > form:invalid").length - ignoreNumber;
    if (invalidElementsCount != 0) {
        document.getElementById("signup-btn").textContent = "以上の内容で登録する";
        document.getElementById("signup-btn").style.pointerEvents = "auto"; // reactivate sign up btn
        alert("登録に失敗しました。入力内容に不備があります。");
        throw new Error("内容に不備があります。");
    };

    let body = [];

    const children = document.querySelectorAll(".each-child > form");
    const targetElements = Array.prototype.slice.call(children, 0, number);

    targetElements.forEach(function (x) {

        // set a stand alone form data
        const formData = new FormData(x);
    
        const last_name = formData.get("last_name");
        const first_name = formData.get("first_name");
        const last_name_furigana = formData.get("last_name_furigana");
        const first_name_furigana = formData.get("first_name_furigana");
    
        const child = {
            child_last_name: last_name,
            child_first_name: first_name,
            child_last_name_furigana: last_name_furigana,
            child_first_name_furigana: first_name_furigana,
        };

        body.push(child);
    });

    // send a post request to the endpoint
    const token = loadAccessToken();
    const response = await fetch("/my/children", {
        method: "POST",
        headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
        body: JSON.stringify(body),
    });
    if (response.ok) {
        const result = await response.json();
        console.log("success: create a new account", result);
        location.href="/my/userdetails";
    } else {
        console.error("error: create a new account");
        document.getElementById("signup-btn").textContent = "以上の内容で登録する";
        document.getElementById("signup-btn").style.pointerEvents = "auto"; // reactivate sign up btn
        alert("登録に失敗しました。");
    };
});




document.getElementById("signup-cancel-btn").addEventListener("click", function () {
    document.getElementById("children-signup-form").classList.remove("hidden");
    document.getElementById("signup-check-div").classList.add("hidden");
    document.getElementById("signup-btn").classList.add("hidden");
    document.getElementById("signup-cancel-btn").classList.add("hidden");
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


