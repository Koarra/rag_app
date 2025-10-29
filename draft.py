{
    // =====================
    // General Editor Settings
    // =====================
    "editor.fontFamily": "Fira Code, Menlo, Monaco, 'Courier New', monospace",
    "editor.fontLigatures": true,
    "editor.cursorBlinking": "smooth",
    "editor.lineNumbers": "relative",
    "editor.tabSize": 4,
    "editor.insertSpaces": true,
    "editor.renderWhitespace": "boundary",
    "editor.minimap.enabled": false,
    "workbench.colorTheme": "Default Dark+",
    "workbench.startupEditor": "newUntitledFile",
    "files.autoSave": "onFocusChange",

    // =====================
    // Vim Extension Settings
    // =====================
    "vim.enableNeovim": false,             // Set to true if you want to use Neovim as the engine
    "vim.useSystemClipboard": true,
    "vim.smartRelativeLine": true,
    "vim.hlsearch": true,
    "vim.incsearch": true,
    "vim.autoindent": true,
    "vim.sneak": true,
    "vim.leader": "<space>",

    // Enable colored status bar depending on Vim mode
    "vim.statusBarColorControl": true,
    "vim.statusBarColors": {
        "normal": "#005f5f",
        "insert": "#005f00",
        "visual": "#5f0000",
        "replace": "#5f005f",
        "commandline_in_progress": "#875f00"
    },

    // Optional: change cursor style depending on mode
    "vim.cursorStylePerMode": true,

    // Optional: mode-specific cursor shapes
    "vim.cursorStyle": "block",
    "vim.cursorStylePerMode.normal": "block",
    "vim.cursorStylePerMode.insert": "line",
    "vim.cursorStylePerMode.visual": "block-outline",

    // =====================
    // UI / Quality of Life
    // =====================
    "workbench.statusBar.visible": true,
    "workbench.activityBar.visible": true,
    "window.zoomLevel": 0,
    "terminal.integrated.fontSize": 14,
    "terminal.integrated.cursorBlinking": true
}
