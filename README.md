# Mindful — AI-Based Fatigue Detection and Wellness Care System

A polished, responsive web application prototype for real-time fatigue awareness and personalized wellness care.

## Run locally

This is a dependency-free frontend. From the repository root:

```bash
python3 -m http.server 4173 --bind 0.0.0.0
```

Then open `http://localhost:4173`.

## Enable the real AI pipeline

Install the computer-vision and model dependencies before starting the server:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python3 server.py --port 4173
```

With these dependencies installed, the browser captures webcam frames and sends them to `/api/frame`. The backend uses MediaPipe Face Mesh to extract eye landmarks, calculates an Eye Aspect Ratio blink signal and head-posture deviation, and sends those features through the LightGBM inference model. Without the packages, the application remains usable with its server-side baseline scorer.

## Included

- Overview dashboard with fatigue score, screen time, break adherence, blink rate, trend charts, activity, and wellness streak.
- Live monitor view with optional webcam access using `getUserMedia`, local privacy messaging, and simulated signal cards.
- Personalized breathing intervention modal with a 60-second animated reset.
- Insights, history, and settings screens.
- Responsive layout for desktop and mobile.
- No backend or external data is required for the demo; the UI is ready to connect to OpenCV/MediaPipe and LightGBM services.
