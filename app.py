import streamlit as st
import cloudscraper
from bs4 import BeautifulSoup

st.title("🌐 URL Content Scraper + Query Tool (Cloudflare Bypass)")

url = st.text_input("Enter a URL to scrape:")

if url:
    try:
        # Use cloudscraper instead of requests
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url, timeout=15)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract text content
            text = soup.get_text(separator="\n", strip=True)

            st.subheader("📄 Extracted Content (preview)")
            st.text_area("Content", text[:3000], height=250)

            st.session_state["scraped_text"] = text

            # Search/query feature
            st.subheader("🔎 Query the Content")
            query = st.text_input("Enter a keyword or phrase to search:")
            if query:
                results = [line for line in text.split("\n") if query.lower() in line.lower()]
                if results:
                    st.write("### Results:")
                    for r in results[:10]:
                        st.write("- " + r.strip())
                else:
                    st.warning("No matches found.")

        else:
            st.error(f"Failed to fetch the page. Status code: {response.status_code}")

    except Exception as e:
        st.error(f"Error fetching the URL: {str(e)}")
