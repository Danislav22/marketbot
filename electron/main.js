const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const sqlite3 = require('sqlite3').verbose();

let mainWindow;
let db;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            preload: path.join(__dirname, 'preload.js')
        }
    });

    mainWindow.loadFile('index.html');

    mainWindow.on('closed', function () {
        mainWindow = null;
    });
}

function createDB() {
    db = new sqlite3.Database('./data.db', (err) => {
        if (err) {
            console.error(err.message);
        }
        console.log('Connected to the data database.');
        db.run('CREATE TABLE IF NOT EXISTS data (data TEXT)');
    });
}

app.whenReady().then(() => {
    createWindow();
    createDB();
});

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') {
        db.close();
        app.quit();
    }
});

ipcMain.on('add-data', (event, data) => {
    db.run('INSERT INTO data(data) VALUES(?)', data, function(err) {
        if (err) {
            console.error(err.message);
            event.reply('data-added', 'Error adding data to database');
        } else {
            console.log("A row has been inserted with rowid ${this.lastID}");
            event.reply('data-added', data);
        }
    });
});