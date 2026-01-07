// admin/settings.js

// フォーム送信時の処理
document.getElementById("period-form").addEventListener("submit", async function (event) {
    event.preventDefault();
  
    // フォームのデータを取得
    const year = document.getElementById("year").value;
    const season = document.getElementById("season").value;
    const start_time = document.getElementById("start_time").value;
    const end_time = document.getElementById("end_time").value;
  
    // PeriodRequestオブジェクトを作成
    const periodRequest = {
      year: parseInt(year),
      season: parseInt(season),
      start_time: convertToDateDict(start_time),
      end_time: convertToDateDict(end_time)
    };
  
    // トークンを取得して、Authorizationヘッダーに設定
    const token = loadAccessToken();
  
    if (!token) {
      alert("トークンが見つかりません。");
      return;
    }
  
    const response = await fetch("/admin/period", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
      },
      body: JSON.stringify(periodRequest)
    });
  
    if (response.ok) {
        const result = await response.json();
        document.getElementById("response-message").textContent = "期間情報が更新されました。";
        } else {
        const error = await response.json();
        document.getElementById("response-message").textContent = "エラー: " + error.detail;
        }
});

function convertToDateDict(dateTimeString) {
    const date = new Date(dateTimeString);
  
    return {
      year: date.getFullYear(),
      month: date.getMonth() + 1,
      day: date.getDate(),
      hour: date.getHours(),
      minute: date.getMinutes(),
      timezone: 9  // JST
    };
};



window.addEventListener("DOMContentLoaded", async () => {
    try {
        // APIから期間情報を取得
        const response = await fetch("/admin/period");
        if (!response.ok) {
            throw new Error("期間情報の取得に失敗しました");
        }
        const data = await response.json();

        // 年とシーズンをフォームに設定
        document.getElementById("year").value = data.year;
        document.getElementById("season").value = data.season;
        document.getElementById("start_time").value = data.start_time;
        document.getElementById("end_time").value = data.end_time;

        // // UTC日時をJSTに変換してdatetime-local形式で設定
        // document.getElementById("start_time").value = convertToJSTInput(data.start_time);
        // document.getElementById("end_time").value = convertToJSTInput(data.end_time);

    } catch (error) {
        console.error(error);
        document.getElementById("response-message").innerText = "期間情報の取得に失敗しました";
    }
});

// UTCの日時文字列をJSTのdatetime-local用形式（yyyy-MM-ddTHH:mm）に変換する関数
function convertToJSTInput(utcDateTime) {
    const date = new Date(utcDateTime);

    // UTC→JSTに変換（JSTはUTC+9）
    date.setHours(date.getHours() + 9);

    // JST日時をdatetime-local用のフォーマット（yyyy-MM-ddTHH:mm）に変換
    const yyyy = date.getFullYear();
    const mm = String(date.getMonth() + 1).padStart(2, '0');
    const dd = String(date.getDate()).padStart(2, '0');
    const hh = String(date.getHours()).padStart(2, '0');
    const min = String(date.getMinutes()).padStart(2, '0');

    return `${yyyy}-${mm}-${dd}T${hh}:${min}`;
}

function convertToInputDateTime(utcDateTime) {
    const date = new Date(utcDateTime);
    // datetime-local用のフォーマット (yyyy-MM-ddTHH:mm)
    return date.toISOString().slice(0, 16);
}

