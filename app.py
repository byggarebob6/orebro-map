import streamlit as st
import pandas as pd
import sqlite3
import folium
from streamlit_folium import st_folium
import os

# Connect to the database
conn = sqlite3.connect("locations.db")
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    lat REAL,
    lon REAL,
    category TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    location TEXT
)
""")
conn.commit()


# Load locations
def load_locations():
    cursor.execute("SELECT name, lat, lon, category FROM locations")
    return pd.DataFrame(cursor.fetchall(), columns=["name", "lat", "lon", "category"])


# Add new location
def add_location(name, lat, lon, category):
    cursor.execute("INSERT INTO locations (name, lat, lon, category) VALUES (?, ?, ?, ?)",
                   (name, lat, lon, category))
    conn.commit()


df = load_locations()

# --- Sidebar: User Input ---
st.sidebar.title("Add a Location")
name = st.sidebar.text_input("Location Name")
lat = st.sidebar.number_input("Latitude", min_value=59.0, max_value=60.0)
lon = st.sidebar.number_input("Longitude", min_value=15.0, max_value=16.0)
category = st.sidebar.selectbox("Category", ["Historical", "Cultural", "Nature", "Food", "Shopping", "Bikes"])

if st.sidebar.button("Add Location"):
    add_location(name, lat, lon, category)
    st.sidebar.success(f"Added {name}!")

# --- Sidebar: Image Upload ---
st.sidebar.title("Upload a Picture")
uploaded_file = st.sidebar.file_uploader("Choose an image...", type=["jpg", "png"])
location_ref = st.sidebar.text_input("Reference Location")

if uploaded_file is not None and location_ref:
    # Save the image
    os.makedirs("pics", exist_ok=True)
    file_path = f"pics/{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Save reference in the database
    cursor.execute("INSERT INTO images (filename, location) VALUES (?, ?)", (uploaded_file.name, location_ref))
    conn.commit()

    st.sidebar.success(f"Uploaded {uploaded_file.name} for {location_ref}!")

# --- Page Navigation ---
selected_page = st.sidebar.radio("Choose a page:", ["Map", "Pics"])

# --- Map Page ---
if selected_page == "Map":
    st.title("Explore Örebro 🏰")
    st.write("Discover special locations in the city!")

    # Map Display
    st.subheader("Map of Örebro Locations")
    map = folium.Map(location=[59.2753, 15.2134], zoom_start=12)

    for _, row in df.iterrows():
        folium.Marker(
            [row["lat"], row["lon"]],
            popup=row["name"],
            tooltip=row["name"],
            icon=folium.Icon(color="blue"),
        ).add_to(map)

    st_folium(map, width=700, height=500)
    st.subheader("Filtered Locations")
    st.table(df)

# --- Pics Page ---
if selected_page == "Pics":
    st.title("User Uploaded Images 📸")

    cursor.execute("SELECT filename, location FROM images")
    images = cursor.fetchall()

    if images:
        for filename, location in images:
            image_path = f"pics/{filename}"
            st.image(image_path, caption=f"{location}", width=500)
    else:
        st.write("No images uploaded yet.")


