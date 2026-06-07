import tkinter as tk
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PIL import Image, ImageTk
import numpy as np
import time
import urllib.request
import os
import random

MODEL_PATH = "hand_landmarker.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

if not os.path.exists(MODEL_PATH):
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

class RaceCarGame:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Race Car Simulation")
        self.root.geometry("900x720")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=900, height=720, highlightthickness=0)
        self.canvas.pack()

        self.cap = cv2.VideoCapture(0)

        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

        self.road_left = 225
        self.road_right = 675
        self.road_center = (self.road_left + self.road_right) // 2

        self.car_width = 90
        self.car_height = 140
        self.car_y = 540
        self.car_x = self.road_center - self.car_width // 2

        self.car_img = self.create_car_sprite()

        self.finger_x = self.road_center
        self.score = 0
        self.last_score_time = time.time()
        self.line_y = 0

        self.obstacles = []
        self.spawn_timer = 0
        self.game_over = False

        self.root.bind("r", self.restart_game)
        self.root.bind("R", self.restart_game)

        self.update_frame()

    def create_car_sprite(self):
        car = np.zeros((140, 90, 4), dtype=np.uint8)
        cv2.rectangle(car, (20, 30), (70, 120), (0, 0, 255, 255), -1)
        cv2.rectangle(car, (28, 20), (62, 45), (255, 0, 0, 255), -1)
        cv2.rectangle(car, (32, 5), (58, 35), (255, 255, 255, 255), -1)
        cv2.circle(car, (18, 35), 10, (50, 50, 50, 255), -1)
        cv2.circle(car, (72, 35), 10, (50, 50, 50, 255), -1)
        cv2.circle(car, (18, 110), 10, (50, 50, 50, 255), -1)
        cv2.circle(car, (72, 110), 10, (50, 50, 50, 255), -1)
        return car

    def create_obstacle(self):
        width = random.randint(45, 70)
        height = random.randint(60, 90)
        x = random.randint(self.road_left + 20, self.road_right - width - 20)
        y = -height
        speed = random.randint(8, 13)
        return {"x": x, "y": y, "w": width, "h": height, "speed": speed}

    def overlay_image(self, background, overlay, x, y):
        h, w = overlay.shape[:2]
        if x >= background.shape[1] or y >= background.shape[0]:
            return background

        x1 = max(x, 0)
        y1 = max(y, 0)
        x2 = min(x + w, background.shape[1])
        y2 = min(y + h, background.shape[0])

        overlay_x1 = x1 - x
        overlay_y1 = y1 - y
        overlay_x2 = overlay_x1 + (x2 - x1)
        overlay_y2 = overlay_y1 + (y2 - y1)

        alpha = overlay[overlay_y1:overlay_y2, overlay_x1:overlay_x2, 3] / 255.0
        for c in range(3):
            background[y1:y2, x1:x2, c] = (
                alpha * overlay[overlay_y1:overlay_y2, overlay_x1:overlay_x2, c] +
                (1 - alpha) * background[y1:y2, x1:x2, c]
            )
        return background

    def detect_hand(self, frame_bgr):
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self.detector.detect(mp_image)

        if result.hand_landmarks:
            index_tip = result.hand_landmarks[0][8]
            self.finger_x = int(index_tip.x * 900)

    def draw_road(self, frame):
        frame[:] = (0, 120, 0)
        cv2.rectangle(frame, (self.road_left, 0), (self.road_right, 720), (160, 160, 160), -1)

        self.line_y += 10
        if self.line_y > 90:
            self.line_y = 0

        for y in range(-60, 720, 90):
            yy = y + self.line_y
            cv2.rectangle(frame, (442, yy), (458, yy + 35), (255, 255, 255), -1)

        cv2.putText(frame, f"Score: {self.score}", (50, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 3)

    def move_car(self):
        target_x = self.finger_x - self.car_width // 2
        target_x = max(self.road_left + 10, min(target_x, self.road_right - self.car_width - 10))
        self.car_x += int((target_x - self.car_x) * 0.2)

    def update_score(self):
        now = time.time()
        if now - self.last_score_time > 0.1 and not self.game_over:
            self.score += 1
            self.last_score_time = now

    def rect_collision(self, a, b):
        return not (
            a["x"] + a["w"] < b["x"] or
            a["x"] > b["x"] + b["w"] or
            a["y"] + a["h"] < b["y"] or
            a["y"] > b["y"] + b["h"]
        )

    def update_obstacles(self):
        if not self.game_over:
            self.spawn_timer += 1
            if self.spawn_timer > 30:
                self.obstacles.append(self.create_obstacle())
                self.spawn_timer = 0

        for obs in self.obstacles:
            obs["y"] += obs["speed"]

        self.obstacles = [o for o in self.obstacles if o["y"] < 720]

    def check_collision(self):
        car_box = {
            "x": self.car_x,
            "y": self.car_y,
            "w": self.car_width,
            "h": self.car_height
        }
        for obs in self.obstacles:
            if self.rect_collision(car_box, obs):
                self.game_over = True
                return

    def restart_game(self, event=None):
        self.score = 0
        self.last_score_time = time.time()
        self.obstacles = []
        self.spawn_timer = 0
        self.game_over = False
        self.car_x = self.road_center - self.car_width // 2
        self.finger_x = self.road_center

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (900, 720))

            self.detect_hand(frame)
            self.draw_road(frame)

            if not self.game_over:
                self.move_car()
                self.update_score()
                self.update_obstacles()
                self.check_collision()

            for obs in self.obstacles:
                cv2.rectangle(frame, (obs["x"], obs["y"]), (obs["x"] + obs["w"], obs["y"] + obs["h"]), (0, 0, 255), -1)

            car_resized = cv2.resize(self.car_img, (self.car_width, self.car_height))
            frame = self.overlay_image(frame, car_resized, self.car_x, self.car_y)

            if self.game_over:
                cv2.rectangle(frame, (180, 250), (720, 420), (0, 0, 0), -1)
                cv2.putText(frame, "GAME OVER", (260, 330),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 0, 255), 4)
                cv2.putText(frame, "Press R to Restart", (245, 385),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)

            self.canvas.imgtk = imgtk
            self.canvas.create_image(0, 0, anchor="nw", image=imgtk)

        self.root.after(15, self.update_frame)

    def on_close(self):
        if self.cap.isOpened():
            self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RaceCarGame(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()