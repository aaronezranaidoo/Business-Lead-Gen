import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import urllib.parse
import time

st.set_page_config(page_title="Smart SA Lead Scraper", layout="wide")
st.title("📡 Smart Business Lead Finder (SA)")
st.markdown("🔍 This app finds public business leads on **Google Search**, filtered by Facebook + YellowPages.")

provinces = [
    "Gauteng", "KwaZulu-Natal", "Western Cape", "Eastern Cape",
    "Free State", "Limpopo", "Mpumalanga", "North West", "Northern Cape"
]

industries = [
    "Plumber", "Mechanic", "Electrician", "Car Dealership", "Dentist",
    "Security Company", "Cleaning Services", "Towing", "Auto Parts", "IT Support"
]

province = st.selectbox("📍 Select Province", provinces)
industry = st.selectbox("🏢 Select Industry", industries)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# Helper: extract URLs from Google search results
def extract_google_links(query, max_results=20):
    search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num={max_results}"
    res = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    links = []

    for tag in soup.find_all("a", href=True):
        href = tag['href']
        match = re.search(r"https://[^&]+", href)
        if match:
            url = match.group(0)
            if "webcache" not in url and "google.com" not in url:
                links.append(url)

    return list(set(links))  # remove duplicates

# Parse lead info from URL text
def guess_name_from_url(url):
    parts = re.split(r"[/.%-]", url)
    keywords = [p for p in parts if p.lower() not in ['www', 'com', 'co', 'za', 'facebook', 'yellowpages']]
    return " ".join([w.capitalize() for w in keywords[:3]])

if st.button("🔎 Find Leads"):
    with st.spinner("Scouring the web like a digital ninja..."):

        yellow_query = f"site:yellowpages.co.za {industry} {province}"
        fb_query = f"site:facebook.com {industry} {province}"

        yellow_links = extract_google_links(yellow_query)
        fb_links = extract_google_links(fb_query)

        all_data = []

        for link in yellow_links:
            all_data.append({
                "Business": guess_name_from_url(link),
                "Source": "Yellow Pages",
                "Link": link
            })

        for link in fb_links:
            all_data.append({
                "Business": guess_name_from_url(link),
                "Source": "Facebook",
                "Link": link
            })

        if all_data:
            df = pd.DataFrame(all_data)
            st.success(f"✅ Found {len(df)} leads.")
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Download CSV", df.to_csv(index=False), file_name="leads.csv")
        else:
            st.warning("⚠️ No results found. Try a different province or industry.")

