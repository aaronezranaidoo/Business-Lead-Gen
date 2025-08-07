import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

st.set_page_config(page_title="YellowPages SA Scraper", layout="wide")
st.title("📞 YellowPages South Africa Business Lead Scraper")

provinces = {
    "Gauteng": "gauteng",
    "KwaZulu-Natal": "kwazulu-natal",
    "Western Cape": "western-cape",
    "Eastern Cape": "eastern-cape",
    "Free State": "free-state",
    "Limpopo": "limpopo",
    "Mpumalanga": "mpumalanga",
    "North West": "north-west",
    "Northern Cape": "northern-cape"
}

industries = [
    "Plumber", "Mechanic", "Electrician", "Car Dealership", "Dentist",
    "Security Company", "Cleaning Services", "Towing", "Auto Parts", "IT Support"
]

province = st.selectbox("📍 Select Province", list(provinces.keys()))
industry = st.selectbox("🏢 Select Industry", industries)
num_pages = st.slider("Number of pages to scrape", min_value=1, max_value=5, value=2)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def scrape_yellowpages(province_slug, industry, pages=1):
    results = []
    base_url = f"https://www.yellowpages.co.za/search/{province_slug}/{industry.lower().replace(' ', '-')}"
    
    for page in range(1, pages + 1):
        url = f"{base_url}?page={page}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        listings = soup.find_all("div", class_="yp-listing")
        if not listings:
            break  # no more results

        for listing in listings:
            name = listing.find("h3", class_="yp-listing-title")
            phone = listing.find("span", class_="phone")
            address = listing.find("div", class_="yp-listing-address")
            link_tag = listing.find("a", href=True)

            results.append({
                "Business Name": name.text.strip() if name else "",
                "Phone": phone.text.strip() if phone else "",
                "Address": address.text.strip() if address else "",
                "URL": "https://www.yellowpages.co.za" + link_tag['href'] if link_tag else ""
            })
        time.sleep(random.uniform(1.5, 3))

    return results

if st.button("🔎 Scrape YellowPages"):
    with st.spinner(f"Scraping {num_pages} pages of {industry} in {province}..."):
        data = scrape_yellowpages(provinces[province], industry, pages=num_pages)
        if data:
            df = pd.DataFrame(data)
            st.success(f"Found {len(df)} business listings.")
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Download CSV", df.to_csv(index=False), file_name=f"{industry}_{province}_yellowpages.csv")
        else:
            st.warning("No results found, try changing the selections or number of pages.")



