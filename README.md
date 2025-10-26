# Streaming-Application

**Streaming-Application** is a Python-based video streaming player. It is built using **socket programming** for real-time communication and **Qt5** for a responsive graphical user interface (GUI).

## Features

* Real-time video streaming between server and client.
* Clean and interactive GUI powered by PyQt5.
* Modular design with separate server and client components.

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/yuvalhoshea1-afk/Streaming-Application.git
cd Streaming-Application
```

2. **Install Python dependencies:**
   All required Python packages are listed in `requirements.txt`. Install them using:

```bash
pip install -r requirements.txt
```

## Usage

* Run the **server** first to start streaming:

```bash
python server/server.py
```

* Then run the **client** to connect and play the stream:

```bash
python client/main.py
```

## Server Notes

* Make sure to keep the required folders (`server/videos/`, etc.) in place.
* Avoid uploading large database files or cache files directly to GitHub; use `.gitignore` or Git LFS if needed.

## Client Notes

* Ensure any required folders (e.g., `client/assets/`) are present.
* The client connects to the server to receive and play the video stream.
* Avoid uploading large local files directly to GitHub; use `.gitignore` or Git LFS if needed.

## Requirements

* Python 3.x
* PyQt5
* Any other dependencies are included in `requirements.txt`.
