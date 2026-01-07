// admin/lessonmember.js


// on loading page: fetch and render lessons and their users (members)
document.addEventListener("DOMContentLoaded", function () {
    console.log("loaded page");
    displayLessonMember();
});



async function displayLessonMember () {
    // console.log("called: displayLessonMember()");
    const data = await fetchLessonMember();
    console.log(data);
    const dummy_data = [];
    const table_section = document.getElementById("lesson-member-section");
    table_section.textContent = "";
    // data = [{"lesson_id": "int", "lesson_title": "string", "users": ["..."]}, {"lesson_id": "int", "lesson_title": "string", "users": ["..."]}, ...]
    // data.foreach lesson => lesson["lesson_id"], lesson["lesson_title"], lesson["users"]
    // lesson["users"].foreach user => user.last_name, ...
    
    data.forEach(function (lesson) {
        console.log("first for activated");
        if (lesson.lesson_number == 1) {
            const table_body_class = `table-body-${lesson.lesson_number}`;
            const table_body_selector = `.${table_body_class}`;
            const table_content = `
                <table class="lesson-member-table" data-lesson-number="${lesson.lesson_number}">
                    <h2>${lesson.lesson_number}：${lesson.lesson_title}</h2>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>氏名</th>
                            <th>ふりがな</th>
                            <th>保護者</th>
                            <th>電話番号</th>
                            <th>郵便番号</th>
                            <th>住所</th>
                        </tr>
                    </thead>
                    <tbody class=${table_body_class}>
                    </tbody>
                </table>
                <div class="space"></div>
            `;
            table_section.insertAdjacentHTML("beforeend", table_content);
            let index = 1;
            lesson["users"].forEach(function (user) {
                const table_body_content = `
                    <tr>
                        <td>${index}</td>
                        <td>${user.child_last_name}　${user.child_first_name}</td>
                        <td>${user.child_last_name_furigana}　${user.child_first_name_furigana}</td>
                        <td>${user.parent_name}</td>
                        <td>${user.parent_tel}</td>
                        <td>${user.parent_postal_code}</td>
                        <td>${user.parent_address}</td>
                    </tr>
                `;
                const table_body = document.querySelector(table_body_selector);
                table_body.insertAdjacentHTML("beforeend", table_body_content);
                index ++;
            });
        } else if (lesson["lesson_number"] != 1) {
            const table_body_class = `table-body-${lesson["lesson_number"]}`;
            const table_body_selector = `.${table_body_class}`;
            const table_content = `
                <table class="lesson-member-table" data-lesson-number="${lesson["lesson_number"]}">
                    <h2>${lesson["lesson_number"]}：${lesson["lesson_title"]}</h2>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>氏名</th>
                            <th>ふりがな</th>
                            <th>電話番号</th>
                            <th>郵便番号</th>
                            <th>住所</th>
                        </tr>
                    </thead>
                    <tbody class="${table_body_class}">
                    </tbody>
                </table>
                <div class="space"></div>
            `;
            table_section.insertAdjacentHTML("beforeend", table_content);
    
            let index = 1;
            lesson["users"].forEach(function (user) {
                const table_body_content = `
                    <tr>
                        <td>${index}</td>
                        <td>${user.last_name}　${user.first_name}</td>
                        <td>${user.last_name_furigana}　${user.first_name_furigana}</td>
                        <td>${user.tel}</td>
                        <td>${user.postal_code}</td>
                        <td>${user.address}</td>
                    </tr>
                `;
                const table_body = document.querySelector(table_body_selector);
                table_body.insertAdjacentHTML("beforeend", table_body_content);
                index ++;
            });
        };
    });
};





async function fetchLessonMember () {
    const token = loadAccessToken();
    const response = await fetch("/json/admin/lessons/users", {
        method: "GET",
        headers: {"Content-Type": "application/json", "Authorization": "Bearer " + token},
    });
    if (response.ok) {
        const result = await response.json();
        return result;
    } else {
        console.error("error: fetchLessonMember()");
        return []
    };
};


