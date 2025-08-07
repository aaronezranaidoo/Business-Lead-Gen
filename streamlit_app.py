import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.title("Free Business Contact Finder 🇿🇦")

st.markdown("""
Search for emails and phone numbers of businesses in any industry and city in South Africa — using publicly available data.
""")

industry = st.text_input("Enter industry or business type (e.g. panel beaters, plumbers, textile suppliers):")
location = st.text_input("Enter location (e.g. Cape Town, Durban, Johannesburg):")
search_btn = st.button("Search")

def search_cylex(industry, location):
    url = f"https://www.cylex.net.za/{location.lower()}/{industry.lower().replace(' ', '-')}.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    
    data = []
    for listing in soup.select('.entry'):
        name = listing.select_one('.company').text.strip() if listing.select_one('.company') else ""
        phone = listing.select_one('.phone').text.strip() if listing.select_one('.phone') else ""
        email = listing.select_one('.email').text.strip() if listing.select_one('.email') else ""
        data.append({"Business Name": name, "Phone": phone, "Email": email})
    return data

if search_btn and industry and location:
    st.info(f"Searching for {industry} in {location}...")
    results = search_cylex(industry, location)

    if results:
        df = pd.DataFrame(results)
        st.success(f"Found {len(df)} businesses.")
        st.dataframe(df)
        st.download_button("Download CSV", data=df.to_csv(index=False), file_name="business_contacts.csv")
    else:
        st.warning("No results found. Try different keywords or city.")
