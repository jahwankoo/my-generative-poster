# Week 6 - Your Data, Your Poster (Streamlit version)
# Concept: every ROW of a CSV file becomes one shape on the poster.
#   - one numeric column  -> shape size
#   - one column          -> shape color (category or number)
#   - one numeric column  -> how wobbly each shape is
#
# Builds on the Week 5 app.py: blob() and make_palette() are reused unchanged.

import io, math, random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
import streamlit as st

MAX_ROWS = 200  # keep the web app fast


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


# ---------- NEW for Week 6: data in, poster out ----------

def normalize(series):
    """Scale a numeric column to 0..1 (0.5 everywhere if the column is constant)."""
    lo, hi = series.min(), series.max()
    if hi == lo:
        return pd.Series(0.5, index=series.index)
    return (series - lo) / (hi - lo)


def draw_data_poster(df, size_col, color_col, wobble_col, palette_mode, seed, title):
    random.seed(seed)
    np.random.seed(seed)
    fig, ax = plt.subplots(figsize=(6, 8))
    ax.axis("off")
    ax.set_facecolor((0.97, 0.97, 0.97))

    # 1) size: bigger value -> bigger blob
    sizes = 0.08 + 0.30 * normalize(df[size_col])

    # 2) wobble: bigger value -> more irregular blob (or a fixed value)
    if wobble_col == "(none)":
        wobbles = pd.Series(0.15, index=df.index)
    else:
        wobbles = 0.02 + 0.28 * normalize(df[wobble_col])

    # 3) color: categories get palette colors, numbers get a hue gradient
    if pd.api.types.is_numeric_dtype(df[color_col]):
        t = normalize(df[color_col])
        colors = [hsv_to_rgb([0.65 - 0.65 * v, 0.6, 0.95]) for v in t]  # blue -> red
    else:
        cats = list(df[color_col].astype(str).unique())
        palette = make_palette(max(len(cats), 1), mode=palette_mode)
        lookup = dict(zip(cats, palette))
        colors = [lookup[str(c)] for c in df[color_col]]

    # 4) place and draw one blob per row
    for i in range(len(df)):
        cx, cy = random.random(), random.random()
        x, y = blob((cx, cy), r=float(sizes.iloc[i]), wobble=float(wobbles.iloc[i]))
        ax.fill(x, y, color=colors[i], alpha=0.5, edgecolor=(0, 0, 0, 0))

    ax.text(0.05, 0.95, title, transform=ax.transAxes, fontsize=12, weight="bold")
    return fig


def load_sample():
    return pd.read_csv(io.StringIO(
        "day,steps,sleep_hours,mood\n"
        "1,8200,7.5,happy\n2,4100,6.0,tired\n3,10500,8.0,happy\n4,6700,6.5,calm\n"
        "5,3000,5.0,stressed\n6,12000,7.0,happy\n7,9100,7.5,calm\n8,2500,5.5,stressed\n"
        "9,7300,6.8,calm\n10,11200,8.2,happy\n11,5200,6.2,tired\n12,6100,7.1,calm\n"
    ))


# ---------- Streamlit UI ----------
st.set_page_config(page_title="Your Data, Your Poster", layout="centered")
st.title("Your Data, Your Poster")
st.caption("Arts and Advanced Big Data | Every row of your data becomes a shape")

st.sidebar.header("1. Your data")
uploaded = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
    except Exception:
        st.error("That file could not be read as a CSV. Please check the file and try again.")
        st.stop()
else:
    st.sidebar.info("No file uploaded yet, showing a sample (daily steps, sleep, mood).")
    df = load_sample()

df = df.dropna().head(MAX_ROWS)
numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]

if len(df) == 0 or len(numeric_cols) == 0:
    st.error("The data needs at least one row and one numeric column.")
    st.stop()

with st.expander(f"Preview of your data ({len(df)} rows)"):
    st.dataframe(df.head(10))

st.sidebar.header("2. Map data to art")
size_col = st.sidebar.selectbox("Size of each shape", numeric_cols)
color_col = st.sidebar.selectbox("Color of each shape", list(df.columns), index=len(df.columns) - 1)
wobble_col = st.sidebar.selectbox("Wobble of each shape", ["(none)"] + numeric_cols)

st.sidebar.header("3. Style")
palette_mode = st.sidebar.selectbox("Palette mode (for categories)", ["pastel", "vivid", "mono", "random"])
seed = st.sidebar.slider("Seed (layout)", 0, 9999, 0)
title = st.sidebar.text_input("Poster title", "My Data Poster")

fig = draw_data_poster(df, size_col, color_col, wobble_col, palette_mode, seed, title)
st.pyplot(fig)

buf = io.BytesIO()
fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
st.download_button("Download poster as PNG", buf.getvalue(), file_name="my_data_poster.png", mime="image/png")
