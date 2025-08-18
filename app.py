#app.py
import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Web Scraper App", layout="wide")

st.title("🌐 Simple Web Scraper")
st.write("Enter a URL below to scrape its visible text content.")

# Input box
url = st.text_input("Website URL", "https://example.com")

if st.button("Scrape Website"):
    if not url.startswith("http"):
        st.error("Please enter a valid URL (starting with http or https).")
    else:
        try:
            # Fetch page
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                # Extract visible text
                for script in soup(["script", "style"]):
                    script.extract()
                text = " ".join(soup.stripped_strings)

                # Display results
                st.subheader("🔍 Extracted Text")
                st.text_area("Content", text, height=300)

                # Show preview summary (first 500 chars)
                st.subheader("📑 Summary Preview")
                st.write(text[:500] + "..." if len(text) > 500 else text)
            else:
                st.error(f"Failed to retrieve page (Status code: {response.status_code})")
        except Exception as e:
            st.error(f"Error: {e}")

