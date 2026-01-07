// my/userdetails/edit.js

document.addEventListener("DOMContentLoaded", function () {
    renderEditForm();
});

// 編集フォームを表示する
async function renderEditForm() {
    const userDetails = await fetchMyUserDetails();

    // フォームの各フィールドに初期値を設定
    document.getElementById("last_name").value = userDetails.last_name || "";
    document.getElementById("first_name").value = userDetails.first_name || "";
    document.getElementById("last_name_furigana").value = userDetails.last_name_furigana || "";
    document.getElementById("first_name_furigana").value = userDetails.first_name_furigana || "";
    document.getElementById("tel").value = userDetails.tel || "";
    document.getElementById("postal_code").value = userDetails.postal_code || "";
    document.getElementById("address").value = userDetails.address || "";
    document.getElementById("email").value = userDetails.email || "";
}

// ユーザー情報を取得する
async function fetchMyUserDetails() {
    const token = loadAccessToken();
    const response = await fetch("/json/my/userdetails", {
        method: "GET",
        headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
    });
    if (response.ok) {
        return await response.json();
    } else {
        console.error("error: fetchMyUserDetails()");
        return {};
    }
}

// 編集内容を送信する
document.getElementById("save-btn").addEventListener("click", async function () {
    const userDetails = new FormData(document.getElementById("user-details-edit-form"));
    const token = loadAccessToken();
    const data = {};
    userDetails.forEach((value, key) => {
        if (value != "") {
            data[key] = value;
        }
    });

    const response = await fetch("/my/userdetails", {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify(data)
    });

    if (response.ok) {
        document.getElementById("status-message").textContent = "変更が保存されました。";
        document.getElementById("status-message").classList.remove("hidden");
        console.log("success: patched my userdetails");
    } else {
        document.getElementById("status-message").textContent = "エラーが発生しました。";
        document.getElementById("status-message").classList.remove("hidden");
    }
});

