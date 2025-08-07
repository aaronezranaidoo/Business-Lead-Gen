import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import urllib.parse
import time

st.set_page_config(page_title="SA Business Leads Finder", layout="wide")
st.title("📞 Free Business Lead Finder (South Africa)")
st.markdown("Get public contact info from Yellow Pages and Facebook in your chosen city and field.")

cities = [
    "Johannesburg", "Cape Town", "Durban", "Pretoria", "Port Elizabeth",
    "East London", "Bloemfontein", "Polokwane", "Nelspruit", "Kimberley"
]

industries = [
    "Plumber", "Mechanic", "Electrician", "Construction", "IT Services",
    "Car Dealership", "Dentist", "Accountant", "Security", "Cleaning Services"
]

city = st.selectbox("📍 Choose a city", cities)
industry = st.selectbox("🏢 Choose an industry", industries)

# --- Yellow Pages Scraper ---
def scrape_yellow_pages(city, industry):
    results = []
    search_term = f"{industry} {city}".replace(" ", "+")
    url = f"https://www.yellowpages.co.za/search?query={search_term}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    listings = soup.find_all('div', class_='yp-listing')

    for listing in listings:
        name = listing.find('a', class_='yp-listing-name')
        phone = listing.find('a', class_='yp-call')
        email_tag = listing.find('a', href=re.compile(r'mailto:'))

        results.append({
            'Business': name.text.strip() if name else "N/A",
            'Phone': phone.text.strip() if phone else "N/A",
            'Email': email_tag['href'].replace("mailto:", "") if email_tag else "N/A",
            'Facebook Page': '—'
        })

    return results

# --- Facebook Page Finder ---
def find_facebook_pages(industry, city, max_results=10):
    query = f"{industry} {city} site:facebook.com"
    search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)
        fb_pages = []

        for link in links:
            href = link["href"]
            if "facebook.com" in href and "/pages" not in href and "webcache" not in href:
                match = re.search(r"https://www\.facebook\.com/[^&]+", href)
                if match:
                    fb_url = match.group(0)
                    if fb_url not in fb_pages:
                        fb_pages.append(fb_url)
            if len(fb_pages) >= max_results:
                break

        return fb_pages
    except:
        return []

# --- Combine and Display ---
if st.button("🔎 Search"):
    with st.spinner("Gathering leads..."):

        yellow_data = scrape_yellow_pages(city, industry)
        fb_pages = find_facebook_pages(industry, city)

        # Attach Facebook pages to first few entries
        for i in range(min(len(fb_pages), len(yellow_data))):
            yellow_data[i]['Facebook Page'] = fb_pages[i]

        df = pd.DataFrame(yellow_data)

        if df.empty:
            st.warning("No leads found. Try another city or field.")
        else:
            st.success(f"Found {len(df)} business leads.")
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Download as CSV", df.to_csv(index=False), file_name=f"{industry}_{city}_leads.csv")
