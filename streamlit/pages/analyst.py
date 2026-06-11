import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

N8N_ANALYST_URL = os.getenv("N8N_ANALYST_WEBHOOK_URL", "")

st.set_page_config(page_title="Feedback Analyst", layout="centered")

st.title("Feedback Analyst")
st.caption("Ask questions about stored customer reviews.")

if not N8N_ANALYST_URL:
    st.warning("Set `N8N_ANALYST_WEBHOOK_URL` in `.env`.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("What are the top issues this week?"):
    if not N8N_ANALYST_URL:
        st.error("Analyst webhook URL is not configured.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        history = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[:-1]
        ]

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        N8N_ANALYST_URL,
                        json={"question": prompt, "history": history},
                        timeout=120,
                    )
                    if response.status_code == 200:
                        data = response.json()
                        answer = (
                            data.get("answer")
                            or data.get("output")
                            or data.get("text")
                            or str(data)
                        )
                        st.markdown(answer)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": answer}
                        )
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"Request failed: {e}")
