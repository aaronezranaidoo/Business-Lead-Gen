import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# === UI SETUP ===
st.title("🔍 Free SA Business Contact Finder")
st.markdown("Search for public contact info by industry and location.")

# Province and industry dropdowns
cities = [
    "Johannesburg", "Cape Town", "Durban", "Pretoria", "Port Elizabeth",
    "East London", "Bloemfontein", "Polokwane", "Nelspruit", "Kimberley"
]

industries = [
    "Plumber", "Mechanic", "Electrician", "Construction", "IT Services",
    "Car Dealership", "Dentist", "Accountant", "Security", "Cleaning Services"
]

city = st.selectbox("📍 Choose a city", cities)
category = st.selectbox("🏢 Choose an industry", industries)

# === Scraper Function ===
def get_contacts(city, category):
    query = f"{category} in {city}"
    url = f"https://www.cylex.net.za/search?q={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    cards = soup.find_all("div", class_="col-sm-12 search-item")

    results = []
    for card in cards:
        name = card.find("a", class_="business-name")
        phone = card.find("span", class_="contact-phone")
        email = card.find("a", class_="contact-email")

        results.append({
            "Business": name.text.strip() if name else "N/A",
            "Phone": phone.text.strip() if phone else "N/A",
            "Email": email['href'].replace("mailto:", "") if email else "N/A"
        })

    return results

# === Action Button ===
if st.button("🔎 Search"):
    with st.spinner("Searching..."):
        data = get_contacts(city, category)
        if data:
            df = pd.DataFrame(data)
            st.success(f"Found {len(df)} results.")
            st.dataframe(df)
            st.download_button("📥 Download CSV", df.to_csv(index=False), file_name="contacts.csv")
        else:
            st.warning("No results found. Try a different city or industry.")

