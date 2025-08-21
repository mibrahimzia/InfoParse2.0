import streamlit as st
import requests
import json
import csv
import io
import time
from urllib.parse import urlparse
import pandas as pd
from backend.ai_interpreter import pattern_based_interpreter
from backend.crawler import crawl_website
from backend.ai_enhancer import ai_enhancer

# Configure Streamlit page
st.set_page_config(
    page_title="WebToAPI Converter Pro",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* ... (keep existing styles) ... */
    .nl-output {
        background-color: #f8f9fa;
        border-left: 4px solid #4b6cb7;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .tab-content {
        padding: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def validate_url(url: str) -> bool:
    """Perform basic URL validation"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def convert_to_format(data, format_type):
    """Convert data to selected format"""
    # ... (keep existing implementation) ...

def main():
    st.markdown('<div class="header"><h1>🌐 WebToAPI Converter Pro</h1><p>Extract data from single pages or entire websites</p></div>', 
                unsafe_allow_html=True)
    
    # Extraction type selection
    extraction_type = st.radio(
        "Extraction Type:",
        ["Single Page", "Whole Website"],
        horizontal=True
    )
    
    # URL input
    url = st.text_input("Enter Website URL:", placeholder="https://example.com")
    
    # Query input
    query = st.text_area("What would you like to extract?", 
                        placeholder="e.g. 'All product names, prices and images' or 'Information about faculty members'",
                        height=100)
    
    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        col1, col2 = st.columns(2)
        with col1:
            output_format = st.selectbox("Output Format", ["JSON", "CSV"])
        with col2:
            if extraction_type == "Whole Website":
                max_pages = st.slider("Max Pages to Crawl", 5, 100, 20)
                max_depth = st.slider("Max Depth", 1, 5, 2)
    
    # Action button
    if st.button("✨ Extract Data", use_container_width=True, type="primary"):
        if not url or not query:
            st.error("Please provide both a URL and extraction instructions")
        else:
            if not validate_url(url):
                st.error("Please enter a valid URL (including http:// or https://)")
            else:
                with st.spinner("🔍 Processing your request..."):
                    try:
                        # Parse the query
                        extraction_plan = pattern_based_interpreter(query)
                        
                        # Perform extraction
                        if extraction_type == "Single Page":
                            # Single page extraction (existing logic)
                            headers = {
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                                "Accept-Language": "en-US,en;q=0.9",
                            }
                            
                            response = requests.get(url, headers=headers, timeout=30)
                            response.raise_for_status()
                            
                            # Extract data
                            from backend.scraper import extract_data
                            results = extract_data(url, extraction_plan)
                            
                        else:
                            # Whole website crawling
                            results = crawl_website(
                                url, query, 
                                max_pages=max_pages, 
                                max_depth=max_depth
                            )
                        
                        # Store results
                        st.session_state.extracted_data = results
                        st.session_state.output_format = output_format
                        st.session_state.query = query
                        st.experimental_rerun()
                        
                    except Exception as e:
                        st.error(f"Extraction failed: {str(e)}")
    
    # Results section
    if "extracted_data" in st.session_state:
        st.markdown("""
        <div class="success-box">
            <h3>✅ Extraction Complete!</h3>
            <p>Your data has been successfully extracted:</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate natural language output
        nl_output = ai_enhancer.generate_natural_summary(
            st.session_state.extracted_data, 
            st.session_state.query
        )
        
        # Display natural language output
        st.markdown("### Natural Language Summary")
        st.markdown(f'<div class="nl-output">{nl_output}</div>', unsafe_allow_html=True)
        
        # Tabbed interface for different outputs
        tab1, tab2 = st.tabs(["Structured Data", "Raw Output"])
        
        with tab1:
            st.markdown("### Structured Data Preview")
            
            if extraction_type == "Single Page":
                # Display single page data
                if st.session_state.output_format == "JSON":
                    st.json(st.session_state.extracted_data)
                else:
                    formatted_data, mime_type, file_ext = convert_to_format(
                        st.session_state.extracted_data, 
                        st.session_state.output_format
                    )
                    st.text(formatted_data)
            else:
                # Display website crawl results
                st.info(f"Extracted data from {len(st.session_state.extracted_data)} pages")
                
                # Show summary of crawled data
                df_data = []
                for page in st.session_state.extracted_data:
                    df_data.append({
                        "URL": page.get("url", "N/A"),
                        "Depth": page.get("depth", 0),
                        "Title": page.get("content", {}).get("article", {}).get("title", "N/A"),
                        "Images": len(page.get("content", {}).get("images", [])),
                        "Tables": len(page.get("content", {}).get("tables", [])),
                    })
                
                if df_data:
                    df = pd.DataFrame(df_data)
                    st.dataframe(df)
                
                # Show detailed data for the first few pages
                with st.expander("View Detailed Data for First 3 Pages"):
                    for i, page in enumerate(st.session_state.extracted_data[:3]):
                        st.markdown(f"**Page {i+1}: {page.get('url')}**")
                        st.json(page)
        
        with tab2:
            st.markdown("### Raw Output")
            
            # Convert data to selected format
            formatted_data, mime_type, file_ext = convert_to_format(
                st.session_state.extracted_data, 
                st.session_state.output_format
            )
            
            if st.session_state.output_format == "JSON":
                st.json(st.session_state.extracted_data)
            else:
                st.text(formatted_data)
            
            # Download button
            st.download_button(
                label=f"📥 Download as {st.session_state.output_format}",
                data=formatted_data,
                file_name=f"extracted_data.{file_ext}",
                mime=mime_type
            )
        
        # Question answering section
        st.markdown("---")
        st.markdown("### Ask Questions About the Data")
        
        question = st.text_input("Ask a question about the extracted content:")
        if question:
            answer = ai_enhancer.answer_question(st.session_state.extracted_data, question)
            st.info(f"**Answer:** {answer}")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem; color: #666;">
        <p>Built with ❤️ using Python, Streamlit, and Hugging Face Transformers</p>
        <p>
            <a href="https://github.com/yourusername/webtapi" target="_blank">GitHub</a> | 
            <a href="https://huggingface.co/spaces" target="_blank">Hugging Face</a> | 
            AGPL-3.0 License
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()