import streamlit as st
import requests

API_URL = "https://your-api-service.onrender.com/fetch"  # replace with your deployed backend URL

st.title("Reusable API - Web Content Fetcher")
st.write("Enter a URL to fetch and interact with its content using our reusable API.")

url = st.text_input("Enter a URL:")

if st.button("Fetch Content"):
    if url:
        try:
            response = requests.get(API_URL, params={"url": url}, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    st.success("Content fetched successfully!")
                    st.text_area("Website Content", data.get("content", ""), height=400)
                else:
                    st.error(f"Error: {data}")
            else:
                st.error(f"Failed with status code {response.status_code}")
        except Exception as e:
            st.error(f"Exception: {e}")
    else:
        st.warning("Please enter a URL.")
