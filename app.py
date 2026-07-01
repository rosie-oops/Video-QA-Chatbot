import logging

import streamlit as st

from ingest import process_video
from retrieval import ask_question

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("app.log", mode="a", encoding="utf-8"),
        logging.StreamHandler(),  # keep printing to the terminal too
    ],
)

st.set_page_config(page_title="Video QA Chatbot", page_icon="🎥", layout="wide")

st.title("🎥 Video QA Chatbot")
st.markdown("Ask questions from any YouTube video.")

video_url = st.text_input("YouTube URL")

col1, col2 = st.columns(2)
with col1:
    process_clicked = st.button("▶ Process Video", use_container_width=True)

if process_clicked:
    with st.spinner("Processing video... (this can take a while on first run)"):
        try:
            result = process_video(video_url)
            st.session_state["video_id"] = result["video_id"]
            st.session_state["video_title"] = result["video_title"]
            st.success(
                f"Processed \"{result['video_title']}\" "
                f"({result['num_chunks']} chunks indexed)"
            )
        except Exception as exc:
            st.session_state.pop("video_id", None)
            st.error(f"Processing failed: {exc}")

if st.session_state.get("video_id"):
    st.info(f"Current video: **{st.session_state.get('video_title')}**")

question = st.text_input("Ask a question")
ask_clicked = st.button("💬 Ask", use_container_width=True)

if ask_clicked:
    if not st.session_state.get("video_id"):
        st.warning("Please process a video first.")
    elif not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Generating answer..."):
            try:
                answer = ask_question(question, video_id=st.session_state["video_id"])
                st.subheader("Answer")
                st.success(answer)
            except Exception as exc:
                st.error(f"Failed to answer: {exc}")