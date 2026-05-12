import os
import cv2
import time
import sqlite3
import traceback
import numpy as np
from concurrent.futures import ThreadPoolExecutor

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

# =========================================================
# Sovereign Video/Camera Studio - Vishwakarma Edition
# =========================================================

APP_NAME = "Sovereign Video/Camera Studio"
OUTPUT_DIR = "/sdcard/Sovereign_AI/"
DB_FILE = "history.db"
INSTRUCTIONS_FILE = "INSTRUCTIONS.md"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================================================
# SQLite Permanent Memory
# =========================================================

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    event TEXT,
    details TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS preferences (
    key TEXT PRIMARY KEY,
    value TEXT
)
""")

conn.commit()


def log_event(event, details=""):
    cursor.execute(
        "INSERT INTO history(timestamp, event, details) VALUES(datetime('now'), ?, ?)",
        (event, details)
    )
    conn.commit()


def check_memory():
    try:
        if os.path.exists(INSTRUCTIONS_FILE):
            with open(INSTRUCTIONS_FILE, "r", encoding="utf-8") as f:
                instructions = f.read()
                print("[MEMORY LOADED]")
                print(instructions[:500])
                log_event("MEMORY_LOADED", "Instructions restored")
        else:
            log_event("MEMORY_MISSING", "INSTRUCTIONS.md missing")
    except Exception as e:
        log_event("MEMORY_ERROR", str(e))


# =========================================================
# Self-Healing Logger
# =========================================================

def self_heal(error):
    try:
        err = traceback.format_exc()
        log_event("ERROR", err)

        print("\n[SELF-HEAL SYSTEM]")
        print("Detected Error:", error)

        suggestions = [
            "Check camera permissions.",
            "Verify OpenCV installation.",
            "Ensure Android storage permission granted.",
            "Reduce processing resolution to 240p.",
            "Restart camera stream.",
        ]

        for s in suggestions:
            print("Fix Suggestion:", s)

    except Exception as heal_error:
        print("Self-heal failed:", heal_error)


# =========================================================
# Cartoon Filter Engine
# =========================================================

def cartoonize_frame(frame):
    try:
        # Downscale for mobile speed
        frame = cv2.resize(frame, (640, 360), interpolation=cv2.INTER_CUBIC)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)

        edges = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            9,
            9
        )

        color = cv2.bilateralFilter(frame, 9, 250, 250)

        cartoon = cv2.bitwise_and(color, color, mask=edges)

        return cartoon

    except Exception as e:
        self_heal(e)
        return frame


# =========================================================
# Video Processor
# =========================================================

class VideoProcessor:

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)

    def process_frame(self, frame):
        future = self.executor.submit(cartoonize_frame, frame)
        return future.result()

    def save_frame(self, frame):
        try:
            filename = os.path.join(
                OUTPUT_DIR,
                f"frame_{int(time.time())}.jpg"
            )

            cv2.imwrite(filename, frame)

            log_event("FRAME_SAVED", filename)

            return filename

        except Exception as e:
            self_heal(e)
            return None


# =========================================================
# Kivy UI
# =========================================================

class SovereignUI(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        check_memory()

        self.processor = VideoProcessor()

        self.image = Image(size_hint=(1, 0.75))
        self.add_widget(self.image)

        controls = BoxLayout(size_hint=(1, 0.1))

        self.capture_btn = Button(text="Save Frame")
        self.capture_btn.bind(on_press=self.save_current_frame)

        self.history_btn = Button(text="View History")
        self.history_btn.bind(on_press=self.show_history)

        controls.add_widget(self.capture_btn)
        controls.add_widget(self.history_btn)

        self.add_widget(controls)

        self.status = Label(
            text="Sovereign System Active",
            size_hint=(1, 0.05)
        )

        self.add_widget(self.status)

        self.history_view = TextInput(
            readonly=True,
            multiline=True,
            size_hint=(1, 0.1)
        )

        scroll = ScrollView(size_hint=(1, 0.2))
        scroll.add_widget(self.history_view)

        self.add_widget(scroll)

        self.capture = cv2.VideoCapture(0)

        Clock.schedule_interval(self.update, 1.0 / 24.0)

        self.current_frame = None

        log_event("SYSTEM_START", "Application booted")

    def update(self, dt):
        try:
            ret, frame = self.capture.read()

            if ret:
                processed = self.processor.process_frame(frame)

                self.current_frame = processed

                buf = cv2.flip(processed, 0).tobytes()

                texture = Texture.create(
                    size=(processed.shape[1], processed.shape[0]),
                    colorfmt='bgr'
                )

                texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')

                self.image.texture = texture

                self.status.text = "Live Camera Cartoon Filter Running"

        except Exception as e:
            self_heal(e)

    def save_current_frame(self, instance):
        try:
            if self.current_frame is not None:
                path = self.processor.save_frame(self.current_frame)

                self.status.text = f"Saved: {path}"

        except Exception as e:
            self_heal(e)

    def show_history(self, instance):
        try:
            cursor.execute(
                "SELECT timestamp, event, details FROM history ORDER BY id DESC LIMIT 50"
            )

            rows = cursor.fetchall()

            history_text = ""

            for row in rows:
                history_text += f"{row[0]} | {row[1]} | {row[2]}\n"

            self.history_view.text = history_text

        except Exception as e:
            self_heal(e)


# =========================================================
# Main App
# =========================================================

class SovereignApp(App):

    def build(self):
        return SovereignUI()

    def on_stop(self):
        log_event("SYSTEM_STOP", "Application closed")


if __name__ == "__main__":
    SovereignApp().run()
