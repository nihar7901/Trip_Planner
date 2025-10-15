"""
Configuration file for Trip Planner
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY")

# Model Configuration
LLM_MODEL = "gemini-2.5-flash"
LLM_TEMPERATURE = 0.7

# Budget Ranges (in INR per night for hotels, total for flights)
BUDGET_RANGES = {
    "Backpacker": {
        "hotel_per_night": (500, 1500),
        "flight_total": (3000, 8000),
    },
    "Budget": {
        "hotel_per_night": (1500, 4000),
        "flight_total": (8000, 15000),
    },
    "Mid-Range": {
        "hotel_per_night": (4000, 10000),
        "flight_total": (15000, 35000),
    },
    "Luxury": {
        "hotel_per_night": (10000, 50000),
        "flight_total": (35000, 150000),
    },
    "Family": {
        "hotel_per_night": (3000, 12000),
        "flight_total": (10000, 40000),
    }
}

# Weather Thresholds
WEATHER_FAVORABLE_THRESHOLD = 65  # Score out of 100
WEATHER_RAIN_THRESHOLD = 60  # Rain probability %
WEATHER_TEMP_COMFORTABLE = (15, 35)  # Celsius

# API Endpoints
OPENWEATHER_FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"
SERPAPI_BASE_URL = "https://serpapi.com/search"

# UI Configuration
STREAMLIT_PAGE_TITLE = "AI Travel Planner"
STREAMLIT_LAYOUT = "wide"
STREAMLIT_ICON = "✈️"

# Holiday Types and their characteristics
HOLIDAY_PREFERENCES = {
    "Beach": {"activities": ["swimming", "sunbathing", "water sports"], "weather_pref": "sunny"},
    "Adventure": {"activities": ["hiking", "trekking", "climbing"], "weather_pref": "clear"},
    "City Break": {"activities": ["sightseeing", "museums", "shopping"], "weather_pref": "any"},
    "Skiing": {"activities": ["skiing", "snowboarding"], "weather_pref": "cold"},
    "Party": {"activities": ["nightlife", "clubs", "bars"], "weather_pref": "any"},
    "Backpacking": {"activities": ["exploring", "local culture"], "weather_pref": "any"},
    "Family": {"activities": ["theme parks", "family attractions"], "weather_pref": "pleasant"},
    "Festival": {"activities": ["events", "concerts", "festivals"], "weather_pref": "any"},
    "Romantic": {"activities": ["fine dining", "scenic views"], "weather_pref": "pleasant"},
    "Cruise": {"activities": ["sailing", "onboard activities"], "weather_pref": "calm"},
    "Any": {"activities": ["general tourism"], "weather_pref": "any"}
}

