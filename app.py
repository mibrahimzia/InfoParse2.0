import streamlit as st
import requests
from bs4 import BeautifulSoup

st.title("🌐 URL Content Scraper + Query Tool")

# Input URL
url = st.text_input("Enter a URL to scrape:")

if url:
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract text content
            text = soup.get_text(separator="\n", strip=True)

            # Display preview
            st.subheader("📄 Extracted Content (preview)")
            st.text_area("Content", text[:3000], height=250)

            # Save content in session state for reuse
            st.session_state["scraped_text"] = text

            # --- 🔎 Query Feature ---
            st.subheader("🔎 Query the Content")
            query = st.text_input("Enter a keyword or phrase to search:")
            if query:
                results = [line for line in text.split("\n") if query.lower() in line.lower()]
                if results:
                    st.write("### Results:")
                    for r in results[:10]:  # show top 10 matches
                        st.write("- " + r.strip())
                else:
                    st.warning("No matches found.")

        else:
            st.error(f"Failed to fetch the page. Status code: {response.status_code}")

    except Exception as e:
        st.error(f"Error fetching the URL: {str(e)}")
