# Mindful — AI-Based Fatigue Detection and Wellness Care System

A polished, responsive web application prototype for real-time fatigue awareness and personalized wellness care.

## Run locally

This is a dependency-free frontend. From the repository root:

```bash
python3 -m http.server 4173 --bind 0.0.0.0
```

Then open `http://localhost:4173`.

## Included

- Overview dashboard with fatigue score, screen time, break adherence, blink rate, trend charts, activity, and wellness streak.
- Live monitor view with optional webcam access using `getUserMedia`, local privacy messaging, and simulated signal cards.
- Personalized breathing intervention modal with a 60-second animated reset.
- Insights, history, and settings screens.
- Responsive layout for desktop and mobile.
- No backend or external data is required for the demo; the UI is ready to connect to OpenCV/MediaPipe and LightGBM services.
