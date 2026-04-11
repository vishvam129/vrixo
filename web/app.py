"""Vrixo Streamlit web UI.

Implements Features #36-43: Streamlit app with sidebar navigation,
file upload, before/after comparison, and connected AI pipelines.

Run: streamlit run web/app.py
"""

from __future__ import annotations

import io
import tempfile
from collections.abc import Callable
from pathlib import Path

import streamlit as st
from PIL import Image

from ai.models.background_removal import remove_background
from ai.models.face_enhance import enhance_faces
from ai.models.object_remove import remove_object
from ai.models.restoration import restore_photo
from ai.models.upscaler import upscale_image
from web.auth import current_user, login_form, signup_form
from web.quota import decrement_quota, get_remaining_quota
from web.watermark import apply_watermark

# ---------- Page config ----------
st.set_page_config(
    page_title="Vrixo — AI Photo Magic",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Session state init ----------
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "processed_image" not in st.session_state:
    st.session_state.processed_image = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None


# ---------- Helpers ----------
def _run_ai_pipeline(
    input_image: Image.Image,
    ai_fn: Callable[[Path, Path], object],
) -> Image.Image:
    """Save input to a temp file, run the AI function, return the result image.

    Uses context-managed temp files so resources are always released.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir)
        temp_in = temp_dir / "input.png"
        temp_out = temp_dir / "output.png"
        input_image.save(temp_in)
        ai_fn(temp_in, temp_out)
        return Image.open(temp_out).copy()


def show_before_after(original: Image.Image, processed: Image.Image) -> None:
    """#38: Side-by-side before/after comparison."""
    col1, col2 = st.columns(2)
    with col1:
        st.caption("Before")
        st.image(original, use_container_width=True)
    with col2:
        st.caption("After")
        st.image(processed, use_container_width=True)


def download_button_for_image(image: Image.Image, filename: str = "result.png") -> None:
    """#43: Download button for processed images."""
    buf = io.BytesIO()
    user = current_user()
    if user is None or user.get("tier") == "free":
        image = apply_watermark(image)
    image.save(buf, format="PNG")
    st.download_button(
        label="⬇️ Download result",
        data=buf.getvalue(),
        file_name=filename,
        mime="image/png",
    )


def has_quota() -> bool:
    """Return True if the user can perform another operation today."""
    email = st.session_state.user_email
    if email is None:
        st.info("ℹ️ Please sign in to use this feature (free tier: 5/day).")
        return False
    if get_remaining_quota(email) <= 0:
        st.error("⛔ Daily quota reached. Upgrade to Pro for unlimited access.")
        return False
    return True


def require_upload() -> bool:
    """Return True if a photo has been uploaded, else show a warning."""
    if st.session_state.uploaded_image is None:
        st.warning("👆 Please upload a photo first.")
        return False
    return True


# ---------- Sidebar navigation (#36) ----------
with st.sidebar:
    st.title("✨ Vrixo")
    st.caption("AI photo magic")
    st.divider()

    # Auth UI
    if st.session_state.user_email:
        st.success(f"Signed in: {st.session_state.user_email}")
        remaining = get_remaining_quota(st.session_state.user_email)
        st.caption(f"Free tier: {remaining}/5 remaining today")
        if st.button("Log out"):
            st.session_state.user_email = None
            st.rerun()
    else:
        auth_mode = st.radio("Account", ["Sign in", "Sign up"], horizontal=True)
        if auth_mode == "Sign in":
            login_form()
        else:
            signup_form()

    st.divider()
    st.markdown("### Features")
    feature = st.radio(
        "Select a feature",
        [
            "🖼️ Upload photo",
            "✂️ Remove background",
            "🔍 Upscale (HD)",
            "😊 Face enhance",
            "🕰️ Restore old photo",
            "🧽 Remove object",
        ],
        label_visibility="collapsed",
    )


# ---------- Main area ----------
st.title("✨ Vrixo — AI Photo Magic")

if feature == "🖼️ Upload photo":
    st.subheader("Upload a photo")
    st.markdown("Supported formats: **JPG, PNG, WebP** • Maximum size: **10 MB**")

    uploaded = st.file_uploader(  # #37
        "Drop or click to upload",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=False,
    )
    if uploaded is not None:
        if uploaded.size > 10 * 1024 * 1024:
            st.error("❌ File too large. Maximum upload size is 10 MB.")
        else:
            image = Image.open(uploaded)
            st.session_state.uploaded_image = image
            st.success(f"✓ Uploaded: {uploaded.name} ({image.size[0]}x{image.size[1]})")
            st.image(image, caption="Preview", use_container_width=True)
    elif st.session_state.uploaded_image is not None:
        st.image(st.session_state.uploaded_image, caption="Current image", use_container_width=True)


elif feature == "✂️ Remove background":
    st.subheader("Remove background")
    if require_upload():
        st.image(st.session_state.uploaded_image, caption="Original", width=400)
        clicked = st.button("✂️ Remove background", type="primary")
        if clicked and has_quota():
            with st.spinner("⚙️ Removing background..."):  # #42
                result = _run_ai_pipeline(
                    st.session_state.uploaded_image,
                    lambda i, o: remove_background(i, o),
                )
                st.session_state.processed_image = result
                decrement_quota(st.session_state.user_email)
            st.success("✓ Background removed!")
            show_before_after(st.session_state.uploaded_image, result)
            download_button_for_image(result, "vrixo-no-bg.png")


elif feature == "🔍 Upscale (HD)":
    st.subheader("Upscale to HD / 4K")
    if require_upload():
        scale = st.radio("Upscale factor", [2, 4, 8], horizontal=True, index=1)
        face_opt = st.checkbox("Face-optimized enhancement", value=False)
        clicked = st.button("🔍 Upscale", type="primary")
        if clicked and has_quota():
            with st.spinner(f"⚙️ Upscaling {scale}x..."):
                result = _run_ai_pipeline(
                    st.session_state.uploaded_image,
                    lambda i, o: upscale_image(i, o, scale=scale, face_optimized=face_opt),
                )
                st.session_state.processed_image = result
                decrement_quota(st.session_state.user_email)
            st.success(f"✓ Upscaled {scale}x!")
            show_before_after(st.session_state.uploaded_image, result)
            download_button_for_image(result, f"vrixo-{scale}x.png")


elif feature == "😊 Face enhance":
    st.subheader("Enhance faces")
    if require_upload():
        clicked = st.button("😊 Enhance faces", type="primary")
        if clicked and has_quota():
            with st.spinner("⚙️ Enhancing faces..."):
                face_count_box: list[int] = []

                def _enhance(i: Path, o: Path) -> None:
                    _, count = enhance_faces(i, o)
                    face_count_box.append(count)

                result = _run_ai_pipeline(st.session_state.uploaded_image, _enhance)
                st.session_state.processed_image = result
                decrement_quota(st.session_state.user_email)
            if face_count_box and face_count_box[0] == 0:
                st.warning("⚠️ No faces detected — image saved unchanged.")
            else:
                count = face_count_box[0] if face_count_box else 0
                st.success(f"✓ Enhanced {count} face(s)!")
            show_before_after(st.session_state.uploaded_image, result)
            download_button_for_image(result, "vrixo-enhanced.png")


elif feature == "🕰️ Restore old photo":
    st.subheader("Restore old photo")
    if require_upload():
        col1, col2 = st.columns(2)
        with col1:
            colorize = st.checkbox("Colorize (if B&W)", value=True)
        with col2:
            repair = st.checkbox("Repair scratches", value=True)
        clicked = st.button("🕰️ Restore", type="primary")
        if clicked and has_quota():
            with st.spinner("⚙️ Restoring photo..."):
                result = _run_ai_pipeline(
                    st.session_state.uploaded_image,
                    lambda i, o: restore_photo(i, o, colorize=colorize, repair_scratches=repair),
                )
                st.session_state.processed_image = result
                decrement_quota(st.session_state.user_email)
            st.success("✓ Photo restored!")
            show_before_after(st.session_state.uploaded_image, result)
            download_button_for_image(result, "vrixo-restored.png")


elif feature == "🧽 Remove object":
    st.subheader("Remove unwanted objects")
    if require_upload():
        st.info("🤖 Auto-detect mode: Vrixo will find and remove the most prominent object.")
        clicked = st.button("🧽 Remove auto-detected object", type="primary")
        if clicked and has_quota():
            with st.spinner("⚙️ Removing object..."):
                result = _run_ai_pipeline(
                    st.session_state.uploaded_image,
                    lambda i, o: remove_object(i, o, auto=True),
                )
                st.session_state.processed_image = result
                decrement_quota(st.session_state.user_email)
            st.success("✓ Object removed!")
            show_before_after(st.session_state.uploaded_image, result)
            download_button_for_image(result, "vrixo-clean.png")


# ---------- Footer ----------
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #888; font-size: 0.9em;'>
    Vrixo — AI photo magic • <a href="/terms">Terms</a> • <a href="/privacy">Privacy</a>
    </div>
    """,
    unsafe_allow_html=True,
)
