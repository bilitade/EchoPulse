import streamlit as st
import requests

st.set_page_config(
    page_title="EchoPulse",
    page_icon="⭐",
    layout="centered"
)

st.markdown("""
<style>
.main { max-width: 700px; }

.review-card {
    background: white;
    padding: 2rem;
    border-radius: 18px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

h1 { text-align: center; }

.stButton button {
    width: 100%;
    height: 3rem;
    border-radius: 12px;
    font-weight: 600;
}

textarea {
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

st.title("⭐ EchoPulse")
st.caption("How was your experience?")

rating = st.radio(
    "Rate your experience",
    [1, 2, 3, 4, 5],
    horizontal=True
)

review = st.text_area(
    "Leave a review",
    placeholder="Tell us what you liked, what could be improved, or anything you'd like us to know...",
    height=150
)

submit = st.button("Submit Review")

if submit:
    if not review.strip():
        st.warning("Please write a review.")
    else:
        payload = {
            "rating": rating,
            "review": review
        }

        try:
            response = requests.post(
                "https://bilitade2022.app.n8n.cloud/webhook-test/echopulse-agent",
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                st.success("Thank you for your feedback!")
            else:
                st.error(f"Webhook error: {response.status_code}")

        except Exception as e:
            st.error(f"Request failed: {e}")