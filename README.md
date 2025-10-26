# Streaming-Application

Streaming-Application is a Python video streaming player. It uses **socket programming** for real-time communication and **Qt5** for a responsive graphical interface.

## Features

* Stream video between server and client in real-time.
* User-friendly GUI built with PyQt5.
* Modular design with separate server and client components.

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/yuvalhoshea1-afk/Streaming-Application.git
cd Streaming-Application
```

2. **Install Python dependencies:**
   All required packages are listed in `requirements.txt`. Install them using:

```bash
pip install -r requirements.txt
```

## Configuration

* Before running, adjust the `.env` files in both the server and client directories to set the correct `IP` and `PORT` values for your network environment.
* To add more videos, place them in the `server/videos/` folder following the same naming and format as the existing videos.

## Running

* Start the server first:

```bash
python server/server.py
```

* Then start the client to connect and play the stream:

```bash
python client/main.py
```

## Server Notes

* Keep the required folders (`server/videos/`, etc.) in place.

## Client Notes

* The client connects to the server to receive and play the stream.

## Requirements

* Python 3.x
* PyQt5
* Other dependencies are listed in `requirements.txt`.
