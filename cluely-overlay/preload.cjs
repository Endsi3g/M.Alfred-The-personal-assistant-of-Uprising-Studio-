const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    hideWindow: () => ipcRenderer.send('hide-window'),
    closeApp: () => ipcRenderer.send('close-app'),
    setStealth: (enabled) => ipcRenderer.send('set-stealth', enabled),
    onAssistTriggered: (callback) => ipcRenderer.on('trigger-assist', callback)
});
