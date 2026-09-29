# Week 5 - Interactive Generative Poster (Streamlit version)
# Concepts: from Colab notebook to web app
# Change from Colab: ipywidgets `interact` -> Streamlit sidebar widgets

import random, math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
import streamlit as st


# Blob shape
def blob(center=(0.5, 0.5), r=0.3, points=200, wobble=0.15):
    angles = np.linspace(0, 2 * math.pi, points, endpoint=False)
    radii = r * (1 + wobble * (np.random.rand(points) - 0.5))
    x = center[0] + radii * np.cos(angles)
    y = center[1] + radii * np.sin(angles)
    return x, y


# Simple palette generator (HSV pastel/vivid/mono)
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


# Main drawing function: returns a figure instead of calling plt.show()
def draw_poster(n_layers=8, wobble=0.15, palette_mode="pastel", seed=0):
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

    ax.text(0.05, 0.95, f"Interactive Poster • {palette_mode}",
            transform=ax.transAxes, fontsize=12, weight="bold")
    return fig


# ---------- Streamlit UI ----------
st.set_page_config(page_title="Interactive Generative Poster", layout="centered")
st.title("Interactive Generative Poster")
st.caption("Arts and Advanced Big Data | From Colab to the Web")

st.sidebar.header("Controls")
n_layers = st.sidebar.slider("Layers", min_value=3, max_value=20, value=8, step=1)
wobble = st.sidebar.slider("Wobble", min_value=0.01, max_value=0.30, value=0.15, step=0.01)
palette_mode = st.sidebar.selectbox("Palette mode", ["pastel", "vivid", "mono", "random"])
seed = st.sidebar.slider("Seed", min_value=0, max_value=9999, value=0, step=1)

fig = draw_poster(n_layers, wobble, palette_mode, seed)
st.pyplot(fig)
