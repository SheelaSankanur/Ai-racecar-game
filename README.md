# AI Race Car Simulation

A hand-controlled racing game built with Python, OpenCV, MediaPipe, and Tkinter. Move your hand in front of the webcam to steer the car, avoid falling obstacles, and score points while driving on the road.

## Features

- Hand tracking with the latest MediaPipe Hand Landmarker API.
- Webcam-based control using the index finger position.
- Tkinter game window with road graphics and score display.
- Random falling obstacles.
- Collision detection and game over screen.
- Restart support using the `R` key.

## Preview

![AI Race Car Simulation](Screenshot-2026-06-07-090132.jpg)

## Requirements

- Python 3.10 or newer
- OpenCV
- MediaPipe
- Pillow
- Webcam

## Installation

1. Clone or download this project.
2. Open the project folder in VS Code or your editor.
3. Install the required packages:

```bash
pip install opencv-python mediapipe pillow
```

## MediaPipe Model

This project uses the latest MediaPipe Hand Landmarker API, so the model file `hand_landmarker.task` must be available in the same folder as the Python file. If it is not present, the program will download it automatically from the official MediaPipe model URL.

## How to Run

Run the Python file:

```bash
python Airacecar.py
```

## Controls

- Move your hand left or right in front of the webcam to control the car.
- Press `R` to restart after game over.
- Close the window to exit the game.

## Gameplay

- The car stays on the road and follows your hand movement.
- Obstacles fall from the top of the road.
- If the car touches an obstacle, the game ends.
- Your score increases over time while you survive.

## Folder Structure

```bash
Ai racecar/
│
├── Airacecar.py
├── Screenshot-2026-06-07-090132.jpg
├── hand_landmarker.task
└── README.md
```

## Troubleshooting

### MediaPipe error
If you get an error like `module 'mediapipe' has no attribute 'solutions'`, make sure you are using the latest version of the code because this project uses the new Tasks API instead of `mp.solutions` [web:16][web:27].

### Webcam not opening
- Check if your camera is being used by another app.
- Try changing `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)`.

### Model file not downloading
Make sure you have an internet connection the first time you run the game.

## Future Improvements

- Add better car and obstacle images.
- Add sound effects.
- Add increasing difficulty with faster obstacles.
- Add high score saving.

## License

This project is for learning and personal use.
