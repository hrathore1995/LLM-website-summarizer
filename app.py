import streamlit as st
from summarizer import Website, summarize_text

st.title("Website Summarizer")
st.write("### This is a website summarizer by Harshwardhan")
st.markdown("Enter a URL and get a short summary!")

# User input for URL
url = st.text_input("Enter the website URL", "")

# User choice for JavaScript-rendered pages
use_selenium = st.checkbox("Use Selenium for JavaScript-heavy pages?")

if st.button("Summarize"):
    if url:
        st.info("Fetching website content...")
        website = Website(url, use_selenium=use_selenium)
        st.success("Website content fetched!")

        st.info("Generating summary...")
        summary = summarize_text(website.text, website.title)
        st.markdown("### Summary:")
        st.write(summary)
    else:
        st.error("Please enter a valid URL.")
