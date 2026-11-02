"""Streamlit demo.  Run from project root:  streamlit run app/streamlit_app.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import streamlit as st
from app.agent import TrendPilotAgent
from app.tools import file_saver

st.set_page_config(page_title="TrendPilot", page_icon="🚀")
st.title("🚀 TrendPilot: Local AI Agent for Viral Content")
topic = st.text_area("Topic", "I built a YOLOv8 helmet detection project")
platform = st.selectbox("Platform", ["LinkedIn", "Instagram", "YouTube Shorts", "TikTok", "X/Twitter", "Facebook"])
tone = st.selectbox("Tone", ["Professional and exciting", "Motivational", "Funny", "Short and catchy", "Meme style", "Inspirational"])
output_type = st.selectbox("Output type", ["Post", "Reel Script", "Post + Reel Script", "Full plan"])

if st.button("Generate"):
    logs = []
    with st.spinner("Agent is working..."):
        try:
            st.session_state["res"] = TrendPilotAgent(logger=logs.append).run(topic, platform, tone, output_type)
            st.session_state["logs"] = logs
        except RuntimeError as e:
            st.error(str(e))

res = st.session_state.get("res")
if res:
    with st.expander("Agent plan & tool calls", expanded=True):
        st.code("\n".join(st.session_state["logs"]))
    st.subheader(res.get("title", ""))
    st.markdown(f"**Content idea:** {res['content_idea']}")
    st.markdown(f"**Hook:** {res['hook']}")
    if res.get("caption"):
        st.markdown("**Caption**"); st.write(res["caption"])
    if res.get("hashtags"):
        st.markdown(" ".join(res["hashtags"]))
    if res.get("reel_script"):
        st.markdown("**Reel script**"); st.text(res["reel_script"])
    st.markdown(f"**Thumbnail text:** {res.get('thumbnail')}")
    st.info(f"Review ({res['review']['score']}/10): {res['review']['comments']}")
    st.success(f"Auto-saved to: {res['saved_file']}")
    if st.button("Save result as JSON too"):
        st.success(f"Saved: {file_saver(res, 'json')}")
