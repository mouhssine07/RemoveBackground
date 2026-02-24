"""
Background Remover - Streamlit App
Run: streamlit run app.py

Dependencies:
    pip install streamlit rembg pillow onnxruntime
"""

import io
import zipfile
import streamlit as st
from PIL import Image
from rembg import remove, new_session

st.set_page_config(page_title="BG Remover", page_icon="✂️", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #0a0a0f; color: #e8e8f0; }
header[data-testid="stHeader"] { background: transparent; }
.hero { text-align: center; padding: 3rem 0 1.5rem; }
.hero h1 {
    font-family: 'Syne', sans-serif; font-size: 3.2rem; font-weight: 800;
    background: linear-gradient(135deg, #e8e8f0 30%, #7c6fcd 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0; letter-spacing: -1px;
}
.hero p { color: #888; font-size: 1.05rem; margin-top: 0.5rem; font-weight: 300; }
[data-testid="stFileUploader"] {
    background: #13131c; border: 1.5px dashed #2e2e45;
    border-radius: 16px; padding: 1rem;
}
label { color: #aaa !important; font-size: 0.85rem !important; }
[data-testid="stSelectbox"] > div > div {
    background: #13131c !important; border: 1px solid #2e2e45 !important;
    color: #e8e8f0 !important; border-radius: 10px !important;
}
.stButton > button {
    width: 100%; background: linear-gradient(135deg, #7c6fcd, #5b4fcf);
    color: white; border: none; border-radius: 12px; padding: 0.75rem 2rem;
    font-family: 'Syne', sans-serif; font-size: 1rem; font-weight: 700;
    cursor: pointer; margin-top: 0.5rem;
}
.stButton > button:hover { opacity: 0.88; }
[data-testid="stDownloadButton"] > button {
    width: 100%; background: #13131c; color: #e8e8f0;
    border: 1.5px solid #2e2e45; border-radius: 12px; padding: 0.65rem 2rem;
    font-size: 0.95rem; margin-top: 0.25rem;
}
[data-testid="stDownloadButton"] > button:hover { border-color: #7c6fcd; }
[data-testid="stImage"] img { border-radius: 14px; border: 1px solid #2e2e45; }
hr { border-color: #1e1e2e; }
[data-testid="stAlert"] {
    background: #13131c !important; border: 1px solid #2e2e45 !important;
    border-radius: 12px !important; color: #aaa !important;
}
.checker-wrap {
    background-image:
        linear-gradient(45deg, #1e1e2e 25%, transparent 25%),
        linear-gradient(-45deg, #1e1e2e 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, #1e1e2e 75%),
        linear-gradient(-45deg, transparent 75%, #1e1e2e 75%);
    background-size: 20px 20px;
    background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
    background-color: #13131c; border-radius: 14px; padding: 8px; border: 1px solid #2e2e45;
}
.badge {
    display: inline-block; background: #1e1e30; color: #7c6fcd;
    font-size: 0.75rem; padding: 3px 10px; border-radius: 20px;
    border: 1px solid #2e2e45; margin-bottom: 1rem; font-weight: 500;
}
</style>
""", unsafe_allow_html=True)


# ── rembg loader ──────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_rembg_session(model_name: str):
    return new_session(model_name)


def to_png_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG", compress_level=1)
    return buf.getvalue()


def apply_bg_color(img: Image.Image, color=None) -> Image.Image:
    """Composite the RGBA image onto a solid color background if a color is given."""
    if not color:
        return img
    bg = Image.new("RGBA", img.size, color)
    bg.paste(img, mask=img.split()[3])  # use alpha as mask
    return bg.convert("RGB")


def build_zip(items: list) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in items:
            z.writestr(name, data)
    return buf.getvalue()


# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>✂️ BG Remover</h1>
    <p>Remove backgrounds instantly — lossless PNG, no watermarks, free forever.</p>
</div>
""", unsafe_allow_html=True)

col_model, col_tip = st.columns([2, 3])
with col_model:
    model_choice = st.selectbox(
        "AI Model",
        options=["u2net", "u2netp", "u2net_human_seg", "isnet-general-use", "silueta"],
        format_func=lambda x: {
            "u2net":             "U2Net — General (best quality)",
            "u2netp":            "U2Net-P — Lightweight (faster)",
            "u2net_human_seg":   "U2Net Human — Portraits",
            "isnet-general-use": "ISNet — High quality alt",
            "silueta":           "Silueta — Humans, fast",
        }[x],
        index=0,
    )
with col_tip:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 First run downloads the model (~170 MB). Subsequent runs are instant.", icon=None)

st.markdown("---")

uploaded_files = st.file_uploader(
    "Drop images here or click to browse",
    type=["jpg", "jpeg", "png", "webp", "bmp", "tiff"],
    accept_multiple_files=True,
    label_visibility="collapsed",
)

if uploaded_files:
    st.markdown(f'<div class="badge">📂 {len(uploaded_files)} file(s) selected</div>', unsafe_allow_html=True)

    if st.button("🚀 Remove Background", use_container_width=True):

        with st.spinner(f"Loading {model_choice} model..."):
            session = load_rembg_session(model_choice)

        results = []
        for uploaded_file in uploaded_files:
            with st.spinner(f"Processing **{uploaded_file.name}**..."):
                img = Image.open(uploaded_file).convert("RGBA")
                try:
                    result_img = remove(img, session=session)
                    out_name = uploaded_file.name.rsplit(".", 1)[0] + "_noBg.png"
                    results.append((out_name, img, result_img))
                except Exception as e:
                    st.error(f"❌ Failed on {uploaded_file.name}: {e}")

        if results:
            st.session_state["results"] = results

if "results" in st.session_state and st.session_state["results"]:
    results = st.session_state["results"]
    st.success(f"✅ {len(results)} image(s) processed.")
    st.markdown("---")

    for idx, (out_name, original, result_img) in enumerate(results):
        st.markdown(f"**{out_name}**")
        c1, c2 = st.columns(2)
        with c1:
            st.caption("Original")
            st.image(original, use_container_width=True)

        # Color background controls per image
        col_check, col_pick = st.columns([1, 1])
        with col_check:
            use_color = st.checkbox("🎨 Color background", value=False, key=f"use_color_{idx}")
        with col_pick:
            picked_color = st.color_picker("Pick color", "#FFFFFF", key=f"color_{idx}", disabled=not use_color) if use_color else None

        # Apply color or keep transparent
        display_img = apply_bg_color(result_img, picked_color) if picked_color else result_img
        download_bytes = to_png_bytes(display_img)

        with c2:
            st.caption("Background Removed")
            st.markdown('<div class="checker-wrap">', unsafe_allow_html=True)
            st.image(display_img, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.download_button(f"⬇️ Download {out_name}", download_bytes, out_name, "image/png", key=f"dl_{idx}")
        st.markdown("---")

    if len(results) > 1:
        all_bytes = [(n, to_png_bytes(apply_bg_color(r, None) if not st.session_state.get(f"use_color_{i}") else apply_bg_color(r, st.session_state.get(f"color_{i}", "#FFFFFF")))) for i, (n, _, r) in enumerate(results)]
        st.download_button(
            "📦 Download All as ZIP",
            build_zip(all_bytes),
            "removed_backgrounds.zip", "application/zip"
        )
else:
    st.markdown('<div style="text-align:center;color:#444;padding:2rem 0;">Supports JPG · PNG · WEBP · BMP · TIFF &nbsp;|&nbsp; Batch upload supported</div>', unsafe_allow_html=True)

st.markdown('<div style="text-align:center;color:#333;font-size:.8rem;padding:2rem 0 1rem;">Powered by rembg · U2Net · Runs 100% locally · No data stored</div>', unsafe_allow_html=True)