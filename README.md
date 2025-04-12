# Lunar Brightness Adjuster

A Python script that automatically adjusts external display brightness using the [Lunar CLI](https://lunar.fyi/#cli) based on ambient light levels captured from a webcam.

## Features

*   Measures ambient brightness (average luminance) using a webcam.
*   Adjusts display brightness within a configured minimum and maximum range based on the measured brightness.
*   The brightness adjustment range is customizable via the `config.json` file.

## Requirements

*   Python 3
*   OpenCV (`opencv-python`)
*   NumPy (`numpy`)
*   [Lunar CLI](https://lunar.fyi/#cli) installed and available in your system's PATH.
*   macOS (Camera access permission is required).

## Setup

1.  **Clone or Download the Repository:**
    ```bash
    # Clone the repository if needed
    # git clone <repository_url>
    # cd lunar-support
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python3 -m venv venv
    ```

3.  **Install Dependencies:**
    ```bash
    venv/bin/pip install opencv-python numpy
    ```

4.  **Grant Camera Access:**
    *   Go to macOS "System Settings" > "Privacy & Security" > "Camera".
    *   Allow camera access for the application you are using to run the script (e.g., Terminal, VS Code).

## Configuration

1.  Create a `config.json` file in the project root if it doesn't already exist.
2.  Set the minimum (`min_brightness`) and maximum (`max_brightness`) brightness levels (between 0 and 100) in the following format:

    ```json
    {
      "min_brightness": 35,
      "max_brightness": 80
    }
    ```
    *   `min_brightness`: The lower limit for display brightness when the environment is darkest.
    *   `max_brightness`: The upper limit for display brightness when the environment is brightest.

## Usage

Run the script using the following command:

```bash
venv/bin/python adjust_brightness.py
```

The script will activate the webcam, measure the brightness, and adjust the display brightness accordingly using the Lunar CLI.