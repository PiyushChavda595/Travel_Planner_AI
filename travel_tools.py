import json
import requests
import streamlit as st


# -------- Load JSON utilities -------- #

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


# -------- Flights -------- #

def search_flights(source, destination):
    flights = load_json("dataset/flights.json")

    matches = [
        f for f in flights
        if f["from"].lower() == source.lower()
        and f["to"].lower() == destination.lower()
    ]

    return matches


# -------- Hotels -------- #

def search_hotels(city):
    hotels = load_json("dataset/hotels.json")

    return [
        h for h in hotels
        if h["city"].lower() == city.lower()
    ]


# -------- Places -------- #

def suggest_places(city):
    places = load_json("dataset/places.json")

    return [
        p for p in places
        if p["city"].lower() == city.lower()
    ]


# -------- Coordinates -------- #

def get_city_coords(city):
    coords = load_json("dataset/city_coords.json")
    return coords.get(city)


# -------- Live Weather -------- #
# Needs OpenWeather API KEY in st.secrets["OPENWEATHER_KEY"]

def get_weather(city):

    api_key = st.secrets["OPENWEATHER_KEY"]

    url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"q={city}&appid={api_key}&units=metric"
    )

    r = requests.get(url)

    if r.status_code != 200:
        return None

    data = r.json()

    return {
        "temp": data["main"]["temp"],
        "desc": data["weather"][0]["description"].title()
    }
