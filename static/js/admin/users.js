// admin/users.js

// request to change password
document.getElementById("patch-user-info-btn").addEventListener("click", async function (event) {
    event.preventDefault;
    this.style.pointerEvents = "none";

    document.getElementById("success-change-password-p").classList.add("hidden");
    document.getElementById("fail-change-password-p").classList.add("hidden");
    document.getElementById("form-error-p").classList.add("hidden");

    let invalidElementsCount = document.querySelectorAll("#patch-user-info-form:invalid").length;
    if (invalidElementsCount != 0) {
        this.style.pointerEvents = "auto";
        // alert("パスワードの変更に失敗しました。パスワードは４文字以上必要です。一部の記号は使用できません。");
        document.getElementById("form-error-p").classList.remove("hidden");
        throw new Error("error on form");
    };

    const username = document.getElementById("username-input").value;
    const new_password = document.getElementById("new-password-input").value;
    // console.log(username);
    const sending_data = {
        "plain_password": new_password,
    };
    const token = loadAccessToken();
    const response = await fetch(`/admin/users/${username}`, {
        method: "PATCH",
        headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
        body: JSON.stringify(sending_data),
    });
    if (response.ok) {
        const result = await response.json();
        console.log("chnaged password:", result);
        document.getElementById("success-change-password-p").classList.remove("hidden");
    } else {
        console.error("Error on changing password");
        document.getElementById("fail-change-password-p").classList.remove("hidden");
    };

    document.getElementById("username-input").value = "";
    document.getElementById("new-password-input").value = "";
    this.style.pointerEvents = "auto";
});




// on loading page: fetch and render users
document.addEventListener("DOMContentLoaded", function () {
    displayUsers();
});



async function displayUsers () {
    const users = await fetchUsers();
    // console.log(users);
    // const dummy_data = [];
    const table_section = document.getElementById("user-list-section");
    table_section.textContent = "";
    
    const table_content = `
        <table id="user-list-table">
            <h2>ユーザー一覧</h2>
            <thead>
                <tr>
                    <th>id</th>
                    <th>ユーザー名</th>
                    <th>氏名</th>
                    <th>ふりがな</th>
                    <th>電話番号</th>
                    <th>申込数<th>
                </tr>
            </thead>
            <tbody id="user-list-table-body">
            </tbody>
        </table>
        <div class="space"></div>
    `;
    table_section.insertAdjacentHTML("beforeend", table_content);

    users.forEach(function (user) {
        const table_body_content = `
            <tr>
                <td>${user.id}</td>
                <td>${user.username}</td>
                <td>${user.name}</td>
                <td>${user.furigana}</td>
                <td>${user.tel}</td>
                <td>${user.lessons}</td>
            </tr>
        `;
        const table_body = document.getElementById("user-list-table-body");
        table_body.insertAdjacentHTML("beforeend", table_body_content);
    });
};



async function fetchUsers () {
    const token = loadAccessToken();
    const response = await fetch("/json/admin/users-full", {
        method: "GET",
        headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
    });
    if (response.ok) {
        const result = await response.json();
        return result;
    } else {
        console.error("error: fetchUsers()");
        return [];
    };
};

