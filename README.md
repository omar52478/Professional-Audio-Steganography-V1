# 🔊 Professional Audio Steganography Suite

![Application Screenshot](https://i.imgur.com/your-screenshot-url.png)
A comprehensive desktop application built with Python and CustomTkinter for hiding any type of data within audio files using the LSB (Least Significant Bit) steganography technique. The suite offers a modern, user-friendly interface with advanced features for enhanced security and performance.

---

## ✨ Key Features

* **Versatile Data Hiding:** Hide any file (images, documents, other audio files) or embed plain text directly.
* **🔒 Robust Encryption:** Secure your hidden data with a password. The application uses AES-128 encryption via the `cryptography` library with a key derived using PBDF2 for brute-force resistance.
* **📦 Efficient Compression:** Option to compress data using `zlib` before hiding, significantly increasing the payload capacity of the cover audio.
* **👁️ Advanced Preview System:**
    * **Waveform Visualization:** Displays the audio waveform for both cover and secret audio files (`.wav` & `.mp3`).
    * **Built-in Audio Player:** Play and stop audio files directly within the application.
    * **Image & Text Preview:** Instantly view images or text files before hiding or after extraction.
* **🖥️ Modern & Responsive GUI:** A sleek, modern interface built with `CustomTkinter` that is intuitive and easy to navigate.
* **⚙️ Multi-threaded Performance:** Long operations (hiding/extracting) run in separate threads to prevent the UI from freezing, with a real-time progress bar and log console.

---

## 🛠️ Technology Stack

* **Language:** Python 3.11+
* **GUI Framework:** CustomTkinter
* **Audio Processing:** pydub, simpleaudio, SciPy
* **Image Processing:** Pillow (PIL)
* **Waveform Plotting:** Matplotlib
* **Encryption:** cryptography
* **Compression:** zlib
* **External Tool:** FFmpeg (required for `.mp3` processing)

---

## 🚀 Setup and Installation

Follow these steps to get the application running on your local machine.

### 1. Prerequisites
* **Python 3.11+** installed.
* **FFmpeg:** This is crucial for `.mp3` support.
    * Download FFmpeg from [here](https://www.gyan.dev/ffmpeg/builds/).
    * Extract the folder (e.g., to `C:\ffmpeg`).
    * Add the `bin` subfolder (e.g., `C:\ffmpeg\bin`) to your system's PATH environment variables.

### 2. Clone the Repository
```bash
git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
cd your-repository-name