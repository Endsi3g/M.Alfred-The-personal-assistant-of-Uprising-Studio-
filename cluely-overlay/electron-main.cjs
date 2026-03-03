const { app, BrowserWindow, globalShortcut, ipcMain } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 600,
        height: 800,
        transparent: true,
        frame: false,
        alwaysOnTop: true,
        skipTaskbar: true,
        resizable: false,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.cjs')
        }
    });

    // Enable Stealth/Undetectability
    // On Windows this uses SetWindowDisplayAffinity(WDA_EXCLUDEFROMCAPTURE)
    // On macOS it uses setContentProtection(true)
    mainWindow.setContentProtection(true);

    // Load React App
    if (isDev) {
        mainWindow.loadURL('http://localhost:5173');
        // mainWindow.webContents.openDevTools({ mode: 'detach' });
    } else {
        mainWindow.loadFile(path.join(__dirname, 'dist', 'index.html'));
    }

    // Prevent moving if we want it fixed, or allow drag region via CSS app-region: drag

    // Register Global Shortcuts
    // Assist Mode trigger
    globalShortcut.register('CommandOrControl+Enter', () => {
        mainWindow.webContents.send('trigger-assist');
    });

    // Hide/Show Toggle
    globalShortcut.register('CommandOrControl+\\', () => {
        if (mainWindow.isVisible()) {
            mainWindow.hide();
        } else {
            mainWindow.showInactive();
        }
    });
}

app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('will-quit', () => {
    globalShortcut.unregisterAll();
});

// IPC communication for commands from UI to Electron
ipcMain.on('hide-window', () => {
    if (mainWindow) mainWindow.hide();
});

ipcMain.on('close-app', () => {
    app.quit();
});

ipcMain.on('set-stealth', (event, enabled) => {
    if (mainWindow) mainWindow.setContentProtection(enabled);
});
