async function calculate() {
    // 1. 抓取輸入框的值
    const elec = document.getElementById('elec').value;
    const transport = document.getElementById('transport').value;

    // 2. 準備要傳給後端的資料
    const payload = {
        electricity: elec,
        transport: transport
    };

    // 3. 使用 fetch 呼叫後端 API
    try {
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.success) {
            // 4. 更新畫面顯示結果
            document.getElementById('result-area').style.display = 'block';
            document.getElementById('score').innerText = data.total;
            document.getElementById('advice').innerText = data.advice;
        } else {
            alert('計算錯誤：' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('連線失敗');
    }
}