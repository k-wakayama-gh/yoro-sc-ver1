// todos_jinja.js


// create: add todo from
document.getElementById("add-todo-form").addEventListener("submit", function(event) {
    event.preventDefault(); // フォームのデフォルトの送信を停止

    // フォームのデータを取得
    const formData = new FormData(document.getElementById("add-todo-form"));
    
    const sendingData = {
        title: formData.get("title"),
        content: formData.get("content")
    };

    // エンドポイントにPOSTリクエストを送信
    fetch("/todos", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(sendingData)
    })
    .then(response => response.json())
    .then(data => {
        console.log("Success:", data);
        location.reload();
    })
    .catch((error) => {
        console.error("Error:", error);
    });
});





// patch: ToDoリスト内のToggle Statusボタンをクリックした時の処理
document.querySelectorAll(".toggle-status-btn").forEach(button => {
    button.addEventListener("click", async function(event) {
        const todoId = this.dataset.todoId; // ボタンに紐付けられたToDoのIDを取得
        const currentIsDone = this.dataset.isDone === "True" ? true : false; // 現在のis_doneの状態を取得
        
        // 送信するデータは現在の状態の反転
        const sendingData = {
            is_done: !currentIsDone
        };

        // エンドポイントにPATCHリクエストを送信する
        await fetch(`/todos/is-done/${todoId}`, {
            method: "PATCH",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(sendingData)
        })
        .then(response => response.json())
        .then(data => {
            console.log("Success:", data);
            document.location.reload();
        })
        .catch((error) => {
            console.error("Error:", error);
        });
    });
});





// patch: ToDoリスト内のEditボタンをクリックした時の処理
document.querySelectorAll(".edit-btn").forEach(button => {
    button.addEventListener("click", function(event) {
        const todoId = this.dataset.todoId; // Editボタンに紐付けられたToDoのIDを取得
        
        // 編集用のフォームを表示する
        const editForm = document.querySelector(`.edit-form[data-todo-id="${todoId}"]`);
        editForm.classList.toggle("hidden");

        // 編集用フォーム内のSaveボタンがクリックされた時の処理
        editForm.querySelector(".confirm-edit-btn").addEventListener("click", function() {
            const newTitle = editForm.querySelector(".edit-title").value;
            const newContent = editForm.querySelector(".edit-content").value;

            // 送信するデータを格納するオブジェクト
            const sendingData = {};

            // 新しいデータが存在すればオブジェクトに追加 => contentはNone/Nullでもいい
            if (newTitle) {
                sendingData.title = newTitle;
            }
            // if (newContent) {
            //     sendingData.content = newContent;
            // }
            sendingData.content = newContent;

            // エンドポイントにPATCHリクエストを送信する
            fetch(`/todos/${todoId}`, {
                method: "PATCH",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(sendingData)
            })
            .then(response => response.json())
            .then(data => {
                console.log("Success:", data);
                document.location.reload();
            })
            .catch((error) => {
                console.error("Error:", error);
            });
        });

        // 編集用フォーム内のCancelボタンがクリックされた時の処理
        editForm.querySelector(".cancel-edit-btn").addEventListener("click", function() {
            // 編集用フォームを非表示にする
            editForm.classList.add("hidden");
        });
    });
});




// delete: ToDoリスト内の削除ボタンをクリックした時の処理
document.querySelectorAll(".delete-btn").forEach(button => {
    button.addEventListener("click", function(event) {
        const todoId = this.dataset.todoId; // 削除ボタンに紐付けられたToDoのIDを取得

        // 確認用ポップアップを表示
        const confirmationPopup = document.querySelector(`.confirmation-popup[data-todo-id="${todoId}"]`);
        confirmationPopup.classList.toggle("hidden");

        // 確認用ポップアップ内のConfirmボタンがクリックされた時の処理
        confirmationPopup.querySelector(".confirm-delete-btn").addEventListener("click", function() {
            // FastAPIのエンドポイントにDELETEリクエストを送信してToDoを削除
            fetch(`/todos/${todoId}`, {
                method: "DELETE"
            })
            .then(response => response.json())
            .then(data => {
                console.log("Success:", data);
                document.location.reload();
            })
            .catch((error) => {
                console.error("Error:", error);
            });
        });

        // 確認用メッセージのCancelボタンがクリックされた時の処理
        confirmationPopup.querySelector(".cancel-delete-btn").addEventListener("click", function() {
            // 確認用メッセージを隠す
            confirmationPopup.classList.add("hidden");
        });
    });
});




// ログインフォーム
const loginForm = document.getElementById('login-form');
loginForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    
    const formData = new FormData(loginForm);
    const username = formData.get('username');
    const password = formData.get('password');

    // ログインはjsonでなくform dataを送信する
    const response = await fetch('/token', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: `username=${username}&password=${password}`,
    });

    if (response.ok) {
        const { access_token } = await response.json();
        // トークンをlocalStorageに保存
        localStorage.setItem('accessToken', access_token);
        alert('ログイン成功');
        // console.log('ログイン成功');
    } else {
        alert('ログイン失敗');
    }
});


// ログアウト
const logoutBtn = document.getElementById('logout-btn');
logoutBtn.addEventListener('click', async (event) => {
    event.preventDefault();
    localStorage.removeItem('accessToken');
    }
);


// textareaの高さを自動調整
function autoResize(textarea) {
    // 高さを設定してからスクロールの有無をチェック
    textarea.style.height = 'auto';
    textarea.style.height = (textarea.scrollHeight) + 'px';
}

