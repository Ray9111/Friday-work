async function sendMessage() {
    const inputField = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");
    const message = inputField.value;

    if (message.trim() === "") return;

    // 1. 顯示使用者的訊息
    chatBox.innerHTML += `<div class="message user-message" style="text-align: right; color: blue; margin: 5px;"><strong>我:</strong> ${message}</div>`;
    inputField.value = ""; // 清空輸入框

    // 2. 發送給 Flask 後端
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        // 3. 顯示 AI (或系統) 的回覆
        if (data.reply) {
            chatBox.innerHTML += `<div class="message bot-message" style="text-align: left; color: green; margin: 5px;"><strong>AI:</strong> ${data.reply}</div>`;
            // 自動捲動到底部
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    } catch (error) {
        console.error("Error:", error);
        chatBox.innerHTML += `<div style="color: red;">連線失敗，請檢查伺服器是否啟動</div>`;
    }
}

// 讓使用者按 Enter 也能發送
document.getElementById("user-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});