import streamlit as st
import requests
import os

if not os.path.exists("data"):
    os.makedirs("data")


API_URL = "http://localhost:8000"

st.title("📚 AI-Powered RAG System")

st.sidebar.header("Upload Documents")
uploaded_file = st.sidebar.file_uploader("Upload a text or PDF file", type=["txt", "pdf"])

if uploaded_file:
    with open(f"data/{uploaded_file.name}", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    response = requests.post(f"{API_URL}/upload/", files={"file": uploaded_file.getvalue()})
    st.sidebar.success(response.json()["message"])

st.header("Ask a Question")
query = st.text_input("Enter your question:")

if st.button("Get Answer"):
    if query:
        response = requests.get(f"{API_URL}/ask/", params={"query": query})
        st.write("### Answer")
        st.write(response.json()["answer"])
        st.write("#### Retrieved Context")
        st.write(response.json()["context"])

        # Feedback section
        st.write("#### Was this answer helpful?")
        feedback = st.radio("Feedback:", ("like", "neutral", "dislike"), key="feedback_radio")

        if st.button("Submit Feedback", key="submit_feedback"):
            feedback_payload = {
                "question": query,
                "answer": result["answer"],
                "feedback": feedback
            }

            try:
                fb_response = requests.post(f"{API_URL}/feedback/", json=feedback_payload)
                st.success(" Feedback submitted successfully.")
            except Exception as e:
                st.error(" Error while submitting feedback.")
                st.write("Exception:", str(e))
                
    else:
        st.warning("Please enter a question.")


