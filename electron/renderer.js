const { ipcRenderer } = require('electron');

const inputData = document.getElementById('inputData');
const addDataBtn = document.getElementById('addDataBtn');
const dataList = document.getElementById('dataList');

addDataBtn.addEventListener('click', () => {
    const data = inputData.value;
    ipcRenderer.send('add-data', data);
});

ipcRenderer.on('data-added', (event, data) => {
    const li = document.createElement('li');
    li.textContent = data;
    dataList.appendChild(li);
});
