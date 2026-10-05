# Week 6 - Data-Driven Generative Poster (Streamlit version)
# Concept: instead of the USER choosing the poster's parameters,
# REAL-WORLD DATA (today's weather) chooses them.
#
# This builds directly on the Week 5 app.py:
# - blob(), make_palette(), draw_poster() are UNCHANGED
# - what's new is get_weather() + map_weather_to_params()

import random, math, datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
import streamlit as st
import requests

# ---------- Week 4-5 code: unchanged ----------

def blob(center=(0.5, 0.5), r=0.3, points=200, wobble=0.15):
    angles = np.linspace(0, 2 * math.pi, points, endpoint=False)
    radii = r * (1 + wobble * (np.random.rand(points) - 0.5))
    x = center[0] + radii * np.cos(angles)
    y = center[1] + radii * np.sin(angles)
    return x, y


def make_palette(k=6, mode="pastel", base_h=0.60):
    cols = []
    for _ in range(k):
        if mode == "pastel":
            h = random.random(); s = random.uniform(0.15, 0.35); v = random.uniform(0.9, 1.0)
        elif mode == "vivid":
            h = random.random(); s = random.uniform(0.8, 1.0); v = random.uniform(0.8, 1.0)
        elif mode == "mono":
            h = base_h; s = random.uniform(0.2, 0.6); v = random.uniform(0.5, 1.0)
        else:  # random
            h = random.random(); s = random.uniform(0.3, 1.0); v = random.uniform(0.5, 1.0)
        cols.append(tuple(hsv_to_rgb([h, s, v])))
    return cols


def draw_poster(n_layers=8, wobble=0.15, palette_mode="pastel", seed=0, label=""):
    random.seed(seed)
    np.random.seed(seed)
    fig, ax = plt.subplots(figsize=(6, 8))
    ax.axis("off")
    ax.set_facecolor((0.97, 0.97, 0.97))

    palette = make_palette(6, mode=palette_mode)
    for _ in range(n_layers):
        cx, cy = random.random(), random.random()
        rr = random.uniform(0.15, 0.45)
        x, y = blob((cx, cy), r=rr, wobble=wobble)
        color = random.choice(palette)
        alpha = random.uniform(0.3, 0.6)
        ax.fill(x, y, color=color, alpha=alpha, edgecolor=(0, 0, 0, 0))

    ax.text(0.05, 0.95, label or f"Data-Driven Poster • {palette_mode}",
            transform=ax.transAxes, fontsize=11, weight="bold")
    return fig


# ---------- NEW for Week 6: bring in real data ----------

# Open-Meteo: free, no API key needed (https://open-meteo.com)
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# A few cities students can switch between
CITIES = {
    "Seoul":  (37.5665, 126.9780),
    "Tokyo":  (35.6762, 139.6503),
    "New York": (40.7128, -74.0060),
    "London": (51.5074, -0.1278),
}


@st.cache_data(ttl=600)  # reuse the answer for 10 minutes, be kind to the API
def get_weather(city="Seoul"):
    """Fetch today's current weather. Returns a dict, or None if unreachable."""
    lat, lon = CITIES[city]
    try:
        resp = requests.get(
            WEATHER_URL,
            params={"latitude": lat, "longitude": lon, "current_weather": True},
            timeout=5,
        )
        resp.raise_for_status()
        return resp.json()["current_weather"]
    except Exception:
        return None  # network blocked, API down, etc.


def map_weather_to_params(weather):
    """This is the heart of 'data-driven art':
    turn real numbers into the poster's visual parameters."""
    temp = weather["temperature"]          # Celsius
    wind = weather["windspeed"]            # km/h
    code = weather["weathercode"]          # WMO weather code

    # Temperature -> wobble: hotter day, more chaotic/organic shapes
    wobble = np.clip(0.05 + (temp / 40) * 0.25, 0.05, 0.30)

    # Wind speed -> number of layers: windier day, busier composition
    n_layers = int(np.clip(5 + wind / 3, 5, 20))

    # Weather code -> palette mood
    # 0: clear, 1-3: cloudy, 45-48: fog, 51-67/80-82: rain, 71-77/85-86: snow
    if code == 0:
        palette_mode = "vivid"
    elif code in (1, 2, 3):
        palette_mode = "mono"
    elif code in (71, 73, 75, 77, 85, 86):
        palette_mode = "random"
    else:
        palette_mode = "pastel"

    # Seed by today's date -> same picture all day, new picture tomorrow
    seed = int(datetime.date.today().strftime("%Y%m%d"))

    return dict(n_layers=n_layers, wobble=round(float(wobble), 3),
                palette_mode=palette_mode, seed=seed)


# ---------- Streamlit UI ----------
st.set_page_config(page_title="Data-Driven Generative Poster", layout="centered")
st.title("Data-Driven Generative Poster")
st.caption("Arts and Advanced Big Data | When real-world data draws the picture")

city = st.sidebar.selectbox("City", list(CITIES.keys()))
use_live_data = st.sidebar.toggle("Use live weather data", value=True)

weather = get_weather(city) if use_live_data else None

if weather:
    params = map_weather_to_params(weather)
    st.sidebar.success(f"Live weather for {city}")
    st.sidebar.write(f"Temperature: {weather['temperature']} °C")
    st.sidebar.write(f"Wind speed: {weather['windspeed']} km/h")
    st.sidebar.write(f"Weather code: {weather['weathercode']}")
    label = f"{city} today • {weather['temperature']}°C"
else:
    if use_live_data:
        st.sidebar.warning("Could not reach the weather API. Using manual controls instead.")
    st.sidebar.header("Manual controls")
    params = dict(
        n_layers=st.sidebar.slider("Layers", 3, 20, 8),
        wobble=st.sidebar.slider("Wobble", 0.01, 0.30, 0.15),
        palette_mode=st.sidebar.selectbox("Palette mode", ["pastel", "vivid", "mono", "random"]),
        seed=st.sidebar.slider("Seed", 0, 9999, 0),
    )
    label = f"{city} • manual mode"

st.write(
    f"**Layers:** {params['n_layers']}  |  **Wobble:** {params['wobble']}  |  "
    f"**Palette:** {params['palette_mode']}  |  **Seed:** {params['seed']}"
)

fig = draw_poster(**params, label=label)
st.pyplot(fig)

st.caption(
    "Today's poster is generated from today's actual weather in the selected city. "
    "Come back tomorrow and it will look different, because the data changed."
)
