// todos.js


// function: get todo list data depending on user
async function fetchTodos() {
    const token = loadAccessToken();
    const response = await fetch("/my/todos/json", {
        method: "GET",
        headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
    });
    if (response.ok) {
        const todos = await response.json();
        console.log("success: fetched todo list");
        renderOnLogin();
        return todos;
    } else {
        // throw new Error(`HTTP error! Status: ${response.status}`);
        console.error("error: fetchTodos()");
        renderOnLogout();
        return []; // empty <=> length == 0
    };
};



// function: render and display todo list
async function displayTodos() {
    const todos = await fetchTodos();
    const todoList = document.getElementById("todo-list");
    // clear the previous todo list
    todoList.textContent = "";

    todos.forEach(function(todo) {
        const listItem = `
            <li>
                <strong>${todo.title}</strong>
                ${todo.content ? `<p class="todo-list-content">${todo.content}</p>` : ''}
                <p>Status: ${todo.is_done ? 'Done' : 'Pending'}</p>
                <section class="todo-action-section">
                    <!-- Pending状態変更ボタン -->
                    <button class="toggle-status-btn" data-todo-id="${ todo.id }" data-is-done="${ todo.is_done }">Toggle Status</button>
                    <!-- Editボタン -->
                    <button class="edit-btn" data-todo-id="${todo.id}">Edit</button>
                    <!-- Deleteボタン -->
                    <button class="delete-btn" data-todo-id="${todo.id}">Delete</button>
                    <!-- 確認用メッセージ -->
                    <div class="delete-form hidden" data-todo-id="${todo.id}">
                        <p>Are you sure you want to delete this ToDo?</p>
                        <button class="confirm-delete-btn">Confirm</button>
                        <button class="cancel-delete-btn">Cancel</button>
                    </div>
                    <!-- Editフォーム -->
                    <div class="edit-form hidden" data-todo-id="${todo.id}">
                        <input type="text" class="edit-title" placeholder="New Title" value="${todo.title}">
                        <textarea class="edit-content" placeholder="New Content" onclick="autoResize(this)" oninput="autoResize(this)">${todo.content}</textarea>
                        <button class="confirm-edit-btn">Save</button>
                        <button class="cancel-edit-btn">Cancel</button>
                    </div>
                </section>
            </li>
        `;
        todoList.insertAdjacentHTML("beforeend", listItem);
    });
    if (todos.length !== 0) {
        console.log("rendered todo list");
    };
};



// function: attach event listeners to dynamically created elements
function attachEventListeners() {
    toggleIsDoneEventListeners();
    patchTodoEventListeners();
    deleteTodoEventListeners();
};



// function: fetch and render todo list data and attach event listeners
async function fetchAndDisplayTodos() {
    await displayTodos();
    attachEventListeners();
};



// on loading page: fetch and render todo list
document.addEventListener("DOMContentLoaded", async function () {
    setDarkMode();
    await fetchAndDisplayTodos();
});



// function: patch: toggle is_done
async function toggleIsDone(todoId, sendingData) {
    await fetch(`/todos/is-done/${todoId}`, {
        method: "PATCH",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(sendingData)
    })
    .then(response => response.json())
    .then(data => {
        console.log("Success:", data);
    })
    .catch((error) => {
        console.error("Error:", error);
    });
};


// function: attach toggle is_done event listeners
function toggleIsDoneEventListeners() {
    document.querySelectorAll(".toggle-status-btn").forEach(function(button) {
        button.addEventListener("click", async function () {
            const todoId = this.dataset.todoId;
            const currentIsDone = this.dataset.isDone === "true" ? true : false; // small letter "true"

            const sendingData = {
                is_done: !currentIsDone
            };
            
            console.log("fetching data...");
            await toggleIsDone(todoId, sendingData);

            fetchAndDisplayTodos();
            console.log("success: rendered data.");
        });
    });
};



// function: patch a todo
async function patchTodo(todoId, sendingData) {
    await fetch(`/todos/${todoId}`, {
        method: "PATCH",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(sendingData)
    })
    .then(response => response.json())
    .then(data => {
        console.log("Success:", data);
    })
    .catch((error) => {
        console.error("Error:", error);
    });
};


// function: event listeners for "patchTodo" 
function patchTodoEventListeners() {
    document.querySelectorAll(".edit-btn").forEach(function(button) {
        button.addEventListener("click", function () {
            const todoId = this.dataset.todoId;
            const editForm = document.querySelector(`.edit-form[data-todo-id="${todoId}"]`);

            editForm.classList.toggle("hidden");
            
            // send patch request and refresh on click "Save" button
            editForm.querySelector(".confirm-edit-btn").addEventListener("click", async function () {
                const newTitle = editForm.querySelector(".edit-title").value;
                const newContent = editForm.querySelector(".edit-content").value;
                
                const sendingData = {};
                
                if (newTitle) {
                    sendingData.title = newTitle;
                }
                sendingData.content = newContent;
                
                console.log('fetching data...');
                await patchTodo(todoId, sendingData);
                
                fetchAndDisplayTodos();
                console.log('rendered data.');
            });

            // hide this edit form on click "Cancel" button
            editForm.querySelector(".cancel-edit-btn").addEventListener("click", function () {
                editForm.classList.add("hidden");
            });
        });
    });
};




// function: delete a todo
async function deleteTodo(todoId) {
    await fetch(`/todos/${todoId}`, {
        method: "DELETE"
    })
    .then(response => response.json())
    .then(data => {
        console.log("Success:", data);
    })
    .catch((error) => {
        console.error("Error:", error);
    });
};



// function: event listeners for "deleteTodo"
function deleteTodoEventListeners() {
    document.querySelectorAll(".delete-btn").forEach(function(button) {
        button.addEventListener("click", function () {
            const todoId = this.dataset.todoId;
            const deleteForm = document.querySelector(`.delete-form[data-todo-id="${todoId}"]`);

            deleteForm.classList.toggle("hidden");
            
            // send delete request and refresh on click "Confirm" button
            deleteForm.querySelector(".confirm-delete-btn").addEventListener("click", async function () {
                
                console.log('fetching data...');
                await deleteTodo(todoId);

                fetchAndDisplayTodos();
                console.log('rendered data.');
            });

            // hide this confirmation message on click "Cancel" button
            deleteForm.querySelector(".cancel-delete-btn").addEventListener("click", () => {
                deleteForm.classList.add("hidden");
            });
        });
    });
};




// create: add todo from
document.getElementById("add-todo-form").addEventListener("submit", async function (event) {
    event.preventDefault(); // prevent default form submit
    document.querySelector("#add-todo-form-btn").style.pointerEvents = "none"; // prevent double submit

    // フォームのデータを取得
    const formData = new FormData(document.getElementById("add-todo-form"));
    
    const sendingData = {
        title: formData.get("title"),
        content: formData.get("content")
    };

    // エンドポイントにPOSTリクエストを送信
    const token = loadAccessToken();
    await fetch("/my/todos", {
        method: "POST",
        headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
        body: JSON.stringify(sendingData)
    })
    .then(response => response.json())
    .then(data => {
        console.log("Success:", data);
        fetchAndDisplayTodos();
    })
    .catch((error) => {
        console.error("Error:", error);
    });

    // clear form after sending data
    document.querySelector("#title").value = "";
    document.querySelector("#content").value = "";
    // reactivate submit button
    document.querySelector("#add-todo-form-btn").style.pointerEvents = "auto";
});




// login form
document.getElementById('login-form').addEventListener('submit', async function (event) {
    event.preventDefault();
    document.getElementById("login-btn").style.pointerEvents = "none"; // prevent double submit
    const loginForm = document.getElementById('login-form');
    
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
        const { access_token } = await response.json(); // { access_token } <=> response.access_token
        localStorage.setItem('accessToken', access_token);
        localStorage.setItem("username", username);
        
        location.reload();
        // alert('ログイン成功');
        console.log('success: login');
    } else {
        alert("error: login");
    };
    // reactivate submit button
    document.getElementById("login-btn").style.pointerEvents = "auto";
});


// logout
document.getElementById("logout-btn").addEventListener("click", async function (event) {
    event.preventDefault();
    localStorage.removeItem("accessToken");
    localStorage.removeItem("username");
    console.log("success: logout");
    alert("success: logout");
    location.reload();
});


// textareaの高さを自動調整
function autoResize(textarea) {
    // 高さを設定してからスクロールの有無をチェック
    textarea.style.height = 'auto';
    textarea.style.height = (textarea.scrollHeight) + 'px';
};



// load access token from local storage
function loadAccessToken() {
    try {
        const token = localStorage.getItem("accessToken");
        return token;
    } catch (error) {
        console.error("Failed to load access token:", error);
    };
};



// 使用しない
async function getUserData() {
    const token = loadAccessToken();
    const response = await fetch("/my/username", {
        method: "GET",
        headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
    });
    if (response.ok) {
        const user = await response.json();
        localStorage.setItem("username", user);
        console.log("user: " + user);
        return user;
    } else {
        // throw new Error(`HTTP error! Status: ${response.status}`);
        console.error("getUserData", error);
    };
};



// sign up form
document.getElementById("sign-up-form").addEventListener("submit", async function (event) {
    event.preventDefault(); // prevent the default form sending
    document.getElementById("sign-up-btn").style.pointerEvents = "none"; // prevent double submit
    const signUpForm = document.getElementById("sign-up-form");

    // get the form data and define the sending data
    const formData = new FormData(signUpForm);
    
    const sendingData = {
        username: formData.get("username"),
        plain_password: formData.get("password")
    };
    
    // send a post request to the endpoint
    await fetch("/users", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(sendingData)
    })
    .then(response => response.json())
    .then(data => {
        console.log("success: create a new account", data);
        location.reload();
    })
    .catch((error) => {
        console.error("error: create a new account", error);
    });
    // reactivate submit button
    document.getElementById("sign-up-btn").style.pointerEvents = "auto";
});



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


// function isDarkMode() {
//     const isDarkMode = localStorage.getItem("isDarkMode");
//     return isDarkMode;
// };


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


