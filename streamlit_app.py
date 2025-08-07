import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import urllib.parse

st.set_page_config(page_title="SA Business Lead Scraper", layout="wide")
st.title("📡 SA Business Lead Scraper via Google Search")
st.markdown("Select province and industry to scrape Google business leads.")

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
num_results = st.slider("Number of results to scrape", min_value=10, max_value=50, step=10, value=20)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def scrape_google_search(query, num_results=20):
    results = []
    for start in range(0, num_results, 10):
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&start={start}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # Google results container div class: 'tF2Cxc'
        for g in soup.find_all('div', class_='tF2Cxc'):
            title_tag = g.find('h3')
            link_tag = g.find('a')
            snippet_tag = g.find('span', class_='aCOpRe')

            if title_tag and link_tag:
                title = title_tag.text
                link = link_tag['href']
                snippet = snippet_tag.text if snippet_tag else ""
                results.append({
                    "Business Name": title,
                    "URL": link,
                    "Snippet": snippet
                })

        time.sleep(random.uniform(2, 4))  # polite delay between requests

    return results

if st.button("🔎 Scrape Leads"):
    search_query = f"{province} {industry}"
    with st.spinner(f"Scraping Google for '{search_query}'..."):
        leads = scrape_google_search(search_query, num_results=num_results)
        if leads:
            df = pd.DataFrame(leads)
            st.success(f"Found {len(df)} leads.")
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Download CSV", df.to_csv(index=False), file_name=f"{industry}_{province}_leads.csv")
        else:
            st.warning("No leads found. Try changing your selections or increasing results.")


