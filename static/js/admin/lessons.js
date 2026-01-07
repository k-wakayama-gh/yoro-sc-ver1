// admin/lessons.js

// post: create lessons via spreadsheet GAS API
document.getElementById("add-lessons-all-btn").addEventListener("click", async function (event) {
    event.preventDefault();
    this.style.pointerEvents = "none";

    const api_url = document.getElementById("api-url").value;
    console.log("api_url:", api_url);

    // sending a request to GAS API
    const response_gas = await fetch(api_url, {
        method: "GET",
    });
    let result_gas = [];
    if (response_gas.ok) {
        result_gas = await response_gas.json();
        console.log("result of GAS API:", result_gas);
    } else {
        console.error("Error on fetching GAS API");
    };

    const token = loadAccessToken();

    // sending a request to python
    const response_python = await fetch("/json/admin/lessons/create", {
        method: "POST",
        headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
        body: JSON.stringify(result_gas),
    });
    if (response_python.ok) {
        const result_python = await response_python.json();
        console.log("response of python:", result_python);
    } else {
        console.error("Error on fetching python api");
    };

    // clear input after sending data
    document.getElementById("api-url").value = "";
    // reactivate button
    this.style.pointerEvents = "auto";
});





// on loading page: fetch and render lesson list
document.addEventListener("DOMContentLoaded", function () {
    //setDarkMode();
    fetchAndDisplayLessons();
});


// fetch, render lesson list data and attach event listeners
async function fetchAndDisplayLessons() {
    await renderLessons();
    attachEventListeners();
};


// attach event listeners to dynamically created elements
function attachEventListeners() {
    signUpLesson();
    cancelLessonOnSmallBtn();
    signUpCheck();
    signUpCancel();
    cancelCheck();
    CancelCancel();
};



// render lesson list
async function renderLessons() {
    const lessons = await fetchLessons();
    const myLessons = await fetchMyLessons();
    const lessonList = document.getElementById("lesson-list");

    // clear the previous lesson list
    lessonList.textContent = "";

    const cancelBtn = `<span class="lesson-cancel-btn-small">キャンセル</span>`;

    lessons.forEach(function (lesson) {
        let signUpBtn = "";
        if (document.getElementById("user-btn").classList.contains("is-loged-out")) {
            signUpBtn = "";
        } else if (myLessons.some(myLesson => myLesson.id == lesson.id)) {
            signUpBtn = `<button class="dummy-btn" style="position: relative;">申し込み済み${cancelBtn}</button>`;
        } else if (lesson.number == 1) {
            signUpBtn = `
                    <form class="children-signup-form hidden">
                        <input type="text" name="name" placeholder="お名前">
                        <button class="submit-signup-btn">申し込む</button>
                    </form>
                    <button class="lesson-sign-up-btn">申し込みをする</button>
                `;
        } else {
            signUpBtn = `<button class="lesson-sign-up-btn">申し込みをする</button>`;
        };

        // comment out here to accept more signups manually
        // if ([1,8,9,12].includes(lesson.number) && lesson.capacity_left <= 0 && !myLessons.some(myLesson => myLesson.id == lesson.id)) {
        //     signUpBtn = `<button class="dummy-btn-1" style="position: relative;">受付を締め切りました</button>`;
        // };

        let numberColor = "gray";
        if (lesson.number <= 1) {
            numberColor = "#a44d3a";
        } else if (lesson.number >= 100) {
            numberColor = "#dcbd24";
        } else {
            numberColor = "#4379a6";
        };

        let capacity_left = lesson.capacity;
        if (lesson.capacity_left != null) {
            capacity_left = lesson.capacity_left;
        };

        let capacity = "なし";
        if (lesson.capacity != null) {
            capacity = capacity_left + " / " + lesson.capacity + " 名";
        };
        const dayColor = {"日": "red", "月": "gray", "火": "orange", "水": "#4193f6", "木": "3f8d57", "金": "#f19937", "土": "blue"};
        const listItem = `
            <li class="lesson-list-li flex-column" style="border-color: ${numberColor};" data-lesson-id="${lesson.id}" data-lesson-number="${lesson.number}">
                <div class="flex-row-between lesson-number-etc">
                    <div class="lesson-number" style="background-color: ${numberColor};"><div>${lesson.number}</div></div>
                    <div class="lesson-name"><div class="flex-row">${lesson.title}</div></div>
                    <div class="lesson-day" style="background-color: ${dayColor[lesson.day]};">${lesson.day}</div>
                </div>

                <div class="flex-row lesson-img-etc">
                    <div class="lesson-teacher-etc flex-column">
                        <div class="lesson-img"><img src="/static/img/lessons/${lesson.teacher}.png"></div>
                        <div class="lesson-teacher"><span class="lesson-teacher-name">講師　</span>${lesson.teacher}</div>
                    </div>
                    
                    <div class="lesson-time-etc flex-column">
                        <div class="lesson-time">${lesson.time}</div>
                        <div class="lesson-fee">${lesson.price.toLocaleString()}円（全${lesson.lessons}回分）</div>
                        <div class="lesson-capacity">定員残り ${capacity}</div>
                        <!-- <div class="see-details"><a href="#">詳しく見る ＞</a></div> -->
                    </div>
                </div>

                <p class="lesson-description">${lesson.description}</p>

                ${signUpBtn}

                <div class="sign-up-check-message hidden">[確認]この教室に申し込みますか？</div>
                <div class="sign-up-check-div hidden">
                    <button class="lesson-sign-up-confirm-btn">はい</button>
                    <button class="lesson-sign-up-cancel-btn">いいえ</button>
                </div>

                <div class="cancel-check-message hidden">[確認]申し込みを取り消しますか？</div>
                <div class="cancel-check-div hidden">
                    <button class="lesson-cancel-confirm-btn">はい</button>
                    <button class="lesson-cancel-cancel-btn">いいえ</button>
                </div>
                
            </li>
        `;
        lessonList.insertAdjacentHTML("beforeend", listItem);
    });
    if (lessons.length !== 0) {
        // console.log("rendered lesson list");
        // const poster = `<li class="lesson-poster"><img src="/static/img/lessons/lesson-poster.png" style="width:100%; height: auto;"></li>`;
        document.querySelector("#lesson-list > :nth-child(1)").insertAdjacentHTML("afterend", poster);
    };
};




// get lessons
async function fetchLessons() {
    const token = loadAccessToken();
    const response = await fetch("/json/admin/lessons", {
        method: "GET",
        headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
    });
    if (response.ok) {
        const lessons = await response.json();
        console.log("success: fetchLessons()", lessons);
        // renderOnLogin();
        return lessons;
    } else {
        console.error("error: fetchLessons()");
        document.querySelector(".not-allowed").classList.remove("hidden");
        return []; // empty <=> length == 0
    };
};




// get my lessons
async function fetchMyLessons() {
    const token = loadAccessToken();
    const response = await fetch("/json/my/lessons", {
        method: "GET",
        headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
    });
    if (response.ok) {
        const myLessons = await response.json();
        console.log("success: fetchMyLessons()", myLessons);
        return myLessons;
    } else {
        console.error("error: fetchMyLessons()");
        return []; // empty <=> length == 0
    };
};



// sign up check
function signUpCheck() {
    document.querySelectorAll(".lesson-sign-up-btn").forEach(function (button) {
        button.addEventListener("click", function () {
            // console.log("clicked sign up btn");
            // console.log(this.nextElementSibling);
            // this.nextElementSibling.classList.toggle("hidden");
            // console.log(this.nextElementSibling.classList);
            this.parentNode.querySelector(".sign-up-check-div").classList.toggle("hidden");
            this.parentNode.querySelector(".sign-up-check-message").classList.toggle("hidden");
            this.classList.toggle("hidden");
        });
    });
};


function signUpCancel() {
    document.querySelectorAll(".lesson-sign-up-cancel-btn").forEach(function (button) {
        button.addEventListener("click", function () {
            this.parentNode.classList.toggle("hidden");
            this.parentNode.parentNode.querySelector(".lesson-sign-up-btn").classList.toggle("hidden");
            this.parentNode.parentNode.querySelector(".sign-up-check-message").classList.toggle("hidden");
        });
    });
};



// sign up to a lesson
function signUpLesson() {
    document.querySelectorAll(".lesson-sign-up-confirm-btn").forEach(function (button) {
        button.addEventListener("click", async function () {
            const token = loadAccessToken();
            const lessonId = this.parentNode.parentNode.dataset.lessonId;
            // const lessonId = this.parentNode.dataset.lessonId;
            // const lessonNumber = this.parentNode.dataset.lessonNumber;

            this.textContent = "処理中...";

            const body = {};

            console.log("fetching data...");

            const response = await fetch(`/lessons/${lessonId}`, {
                method: "POST",
                headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
                body: JSON.stringify(body),
            });

            if (response.ok) {
                const result = await response.json();
                fetchAndDisplayLessons();
                console.log("success: signed up to a lesson", result);
            } else {
                console.error("error: signUpLesson()");
                alert("エラーが発生しました。もう一度やり直してください。")
            };
        });
    });
};



// sign up to a children lesson
// function signupChildrenLesson() {
//     document.querySelector(".children-lesson-sign-up-btn").addEventListener("click", )
// };



// cancel check
function cancelCheck() {
    document.querySelectorAll(".lesson-cancel-btn-small").forEach(function (button) {
        button.addEventListener("click", function () {
            this.parentNode.parentNode.querySelector(".cancel-check-div").classList.toggle("hidden");
            this.parentNode.parentNode.querySelector(".cancel-check-message").classList.toggle("hidden");
            this.parentNode.classList.toggle("hidden");
        });
    });
};


function CancelCancel() {
    document.querySelectorAll(".lesson-cancel-cancel-btn").forEach(function (button) {
        button.addEventListener("click", function () {
            this.parentNode.parentNode.querySelector(".dummy-btn").classList.toggle("hidden");
            this.parentNode.parentNode.querySelector(".cancel-check-div").classList.toggle("hidden");
            this.parentNode.parentNode.querySelector(".cancel-check-message").classList.toggle("hidden");
        });
    });
};



// cancel a lesson
function cancelLessonOnSmallBtn() {
    document.querySelectorAll(".lesson-cancel-confirm-btn").forEach(function (button) {
        button.addEventListener("click", async function () {
            const token = loadAccessToken();
            const lessonId = this.parentNode.parentNode.dataset.lessonId;

            // this.parentNode.textContent = "処理中...";
            this.textContent = "";

            const body = {};

            console.log("fetching data...");

            const response = await fetch(`/my/lessons/${lessonId}`, {
                method: "DELETE",
                headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
                body: JSON.stringify(body),
            });

            if (response.ok) {
                const result = await response.json();
                fetchAndDisplayLessons();
                console.log("success: cancel a lesson", result);
            } else {
                console.error("error: cancelLesson()");
            };
        });
    });
};



// refresh capacity left
document.getElementById("refresh-capacity").addEventListener("click", async function (event) {
    event.preventDefault();
    this.style.pointerEvents = "none";

    const token = loadAccessToken();

    const response = await fetch("/lessons/refresh/capacity", {
        method: "GET",
        headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
    });
    if (response.ok) {
        const result = await response.json();
        console.log("refreshed capacity left:", result);
        fetchAndDisplayLessons();
    } else {
        console.error("Error refreshing capacity left");
    };
    this.style.pointerEvents = "auto";
});




// create: add lesson from
document.getElementById("add-lesson-form").addEventListener("submit", async function (event) {
    event.preventDefault(); // prevent default form submit
    document.getElementById("add-lesson-btn").style.pointerEvents = "none"; // prevent double submit

    // フォームのデータを取得
    const formData = new FormData(document.getElementById("add-lesson-form"));
    
    const sendingData = {
        year: formData.get("year"),
        season: formData.get("season"),
        number: formData.get("number"),
        title: formData.get("title"),
        teacher: formData.get("teacher"),
        day: formData.get("day"),
        time: formData.get("time"),
        price: formData.get("price"),
        description: formData.get("description"),
        capacity: formData.get("capacity"),
        lessons: formData.get("lessons"),
    };

    // エンドポイントにPOSTリクエストを送信
    const token = loadAccessToken();

    const response = await fetch("/lessons", {
        method: "POST",
        headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
        body: JSON.stringify(sendingData),
    });

    if (response.ok) {
        const result = await response.json();
        console.log("Success:", result);
        fetchAndDisplayLessons();
    } else {
        console.error("Error on add lesson form");
    };

    // clear form after sending data
    document.querySelectorAll("#add-lesson-form > input").forEach(function (x) {
        x.value = "";
    });
    // reactivate submit button
    document.querySelector("#add-lesson-btn").style.pointerEvents = "auto";
});
