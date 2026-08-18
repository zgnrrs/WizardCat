# 🐈‍⬛ Wizard Cat

> ✨ A magical pixel-art Pomodoro timer designed to make focused work and study sessions a little more fun.

[⬇️ Download for Windows](../../releases/latest)

---

## ✨ About

**Wizard Cat** is a lightweight Windows desktop application built with **Python and PySide6**.

It combines the Pomodoro technique with a cozy pixel-art aesthetic, an animated wizard cat, and a magical purple-themed interface.

The goal is simple: make focused work and study sessions feel a little less boring. 🪄

---

## ✨ Features

- 🍅 Pomodoro focus timer
- ☕ Short and long breaks
- 🐈‍⬛ Animated wizard cat
- ✨ Magical pixel-art inspired interface
- ⚙️ Customizable focus and break durations
- 🔄 Countdown and count-up timer modes
- 🔢 Pomodoro session counter
- 🔔 Desktop notifications
- 💾 Persistent user settings
- ⌨️ Keyboard shortcuts
- 🖥️ Frameless desktop widget
- 🪄 Draggable window

---

## 💻 Download

You don't need Python or any additional dependencies to use Wizard Cat.

### 🪟 Windows

Download the latest version:

### [⬇️ Download Wizard Cat](../../releases/latest)

Download `WizardCat.exe`, run it, and start focusing. 🪄

> **Note:** Windows may display a security warning because the application is not digitally signed. If you downloaded the executable from this repository's Releases page, make sure the file is `WizardCat.exe`.

---

## 🎯 How It Works

Wizard Cat follows the Pomodoro technique:

1. 🧙‍♂️ Start a focus session.
2. 📚 Work until the timer reaches zero.
3. ☕ Take a short break.
4. 🔁 Repeat the cycle.
5. 🌙 After a set number of sessions, take a longer break.

The number and duration of sessions can be customized from the settings menu.

---

## ⚙️ Settings

Wizard Cat allows you to customize:

| Setting | Description |
|---|---|
| Focus Duration | Length of a focus session |
| Short Break | Duration of a short break |
| Long Break | Duration of a long break |
| Sessions Before Long Break | Number of focus sessions before a long break |
| Timer Mode | Countdown or count-up |
| Automatic Breaks | Automatically start breaks |
| Automatic Focus | Automatically start the next focus session |

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|---|---|
| `Space` | Start / Pause timer |
| `R` | Reset timer |

---

## 🛠️ Built With

- 🐍 **Python**
- 🖥️ **PySide6 / Qt**
- 📦 **PyInstaller**
- 🎨 **Pixel Art**
- 🎞️ **GIF Animation**

---

## 📁 Project Structure

```text
WizardCat/
│
├── assets/
│   └── cat/
│       └── wizard_cat.gif
│
├── fonts/
│   └── PressStart2P-Regular.ttf
│
├── icon.ico
├── main.py
├── README.md
├── requirements.txt
└── .gitignore
