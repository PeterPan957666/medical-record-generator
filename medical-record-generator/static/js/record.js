document.addEventListener('DOMContentLoaded', () => {
    const btnDoctor = document.getElementById('btnDoctor');
    const btnPatient = document.getElementById('btnPatient');
    const outputContent = document.getElementById('outputContent');
    const editBtn = document.getElementById('editBtn');
    const signBtn = document.getElementById('signBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const backBtn = document.getElementById('backBtn');

    let editedContent = '';
    let editing = false;

    const DOCTOR = typeof DOCTOR_RECORD !== 'undefined' ? DOCTOR_RECORD : '';
    const PATIENT = typeof PATIENT_RECORD !== 'undefined' ? PATIENT_RECORD : '';

    function setMode(mode) {
        if (mode === 'doctor') {
            btnDoctor.classList.add('doctor');btnDoctor.classList.remove('patient');
            btnPatient.classList.add('patient');btnPatient.classList.remove('doctor');
            outputContent.textContent = DOCTOR || '没有病历，请返回首页生成。';
        } else {
            btnPatient.classList.add('doctor');btnPatient.classList.remove('patient');
            btnDoctor.classList.add('patient');btnDoctor.classList.remove('doctor');
            outputContent.textContent = PATIENT || '没有病历，请返回首页生成。';
        }
    }
    setMode('doctor');

    btnDoctor.addEventListener('click', () => setMode('doctor'));
    btnPatient.addEventListener('click', () => setMode('patient'));

    // 修改/保存病历
    editBtn.addEventListener('click', () => {
        if (!editing) {
            editing = true;
            outputContent.contentEditable = true;
            outputContent.focus();
            editBtn.textContent = '保存病历';
            editBtn.classList.add('saved'); // 保存中状态（蓝色）
        } else {
            editing = false;
            outputContent.contentEditable = false;
            editedContent = outputContent.innerText;
            editBtn.textContent = '修改病历';
            editBtn.classList.remove('saved'); // 恢复橙色
            alert('病历已保存，可下载时将包含修改内容。');
        }
    });

    backBtn.addEventListener('click', () => window.location.href = '/');

    signBtn.addEventListener('click', () => {
        const name = prompt('请输入医生姓名：', '张三');
        if (name && name.trim()) {
            const notice = document.createElement('div');
            notice.classList.add('sign-notice');
            notice.textContent = `✅ 本病历已由主治医师【${name.trim()}】审核确认`;
            const card = document.querySelector('.output-card');
            if (card) card.parentNode.insertBefore(notice, card);
            downloadBtn.disabled = false;
            downloadBtn.classList.remove('disabled');
            downloadBtn.classList.add('enabled');
        }
    });

    downloadBtn.addEventListener('click', () => {
        if (downloadBtn.disabled) return;
        const content = editedContent || outputContent.innerText;
        const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;a.download = '病历.txt';a.click();
        URL.revokeObjectURL(url);
    });
});
