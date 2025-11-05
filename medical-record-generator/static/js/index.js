// index.js - 简化版：只做文本输入 + 生成触发
document.addEventListener('DOMContentLoaded', () => {
    const genBtn = document.getElementById('genBtn');
    const doctorInput = document.getElementById('doctorInput');
    const micHint = document.getElementById('micHint'); // 可能不存在，但不影响

    genBtn.addEventListener('click', async () => {
        const input = doctorInput.value.trim();
        if (!input) {
            alert('请输入病历信息');
            return;
        }
        genBtn.disabled = true;
        genBtn.textContent = '生成中...';

        try {
            const resp = await fetch('/generate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ doctor_input: input })
            });
            if (!resp.ok) {
                const err = await resp.json().catch(()=>({error:'服务器错误'}));
                alert('生成失败：' + (err.error || '未知错误'));
                genBtn.disabled = false;
                genBtn.textContent = '生成病历';
                return;
            }
            const data = await resp.json();
            if (data.redirect) {
                window.location.href = data.redirect;
            } else {
                alert('未知响应，请查看后台');
            }
        } catch (e) {
            console.error(e);
            alert('网络或服务器错误，请检查后端服务是否启动。');
        } finally {
            genBtn.disabled = false;
            genBtn.textContent = '生成病历';
        }
    });
});
