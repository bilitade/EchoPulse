import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

N8N_INGEST_URL = os.getenv("N8N_INGEST_WEBHOOK_URL", "")

st.set_page_config(page_title="Submit Review", layout="centered")

st.title("Submit Review")
st.caption("How was your experience?")

if not N8N_INGEST_URL:
    st.warning("Set `N8N_INGEST_WEBHOOK_URL` in `.env`.")

rating = st.radio("Rating", [1, 2, 3, 4, 5], horizontal=True)

review = st.text_area(
    "Your review",
    placeholder="What went well? What could be improved?",
    height=150,
)

if st.button("Submit"):
    if not review.strip():
        st.warning("Please write a review.")
    elif not N8N_INGEST_URL:
        st.error("Ingest webhook URL is not configured.")
    else:
        try:
            response = requests.post(
                N8N_INGEST_URL,
                json={"rating": rating, "review": review},
                timeout=60,
            )
            if response.status_code == 200:
                data = response.json()
                labels = data.get("labels", {})
                st.success(data.get("message", "Thank you for your feedback."))
                if labels:
                    st.info(
                        f"**{labels.get('category')}** · "
                        f"{labels.get('severity')} severity · "
                        f"{labels.get('sentiment')}"
                    )
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")
