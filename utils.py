"""
Utility functions and API integrations
"""
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from config import (
    OPENWEATHER_API_KEY, 
    SERPAPI_API_KEY,
    OPENWEATHER_FORECAST_URL,
    SERPAPI_BASE_URL,
    WEATHER_RAIN_THRESHOLD,
    WEATHER_TEMP_COMFORTABLE
)


# ============ Weather API ============

def fetch_weather_data(destination: str, start_date: str, end_date: str) -> Dict:
    """
    Fetch weather forecast from OpenWeatherMap
    """
    try:
        params = {
            "q": destination,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "cnt": 40  # 5 days forecast (8 readings per day)
        }
        
        response = requests.get(OPENWEATHER_FORECAST_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Check if we got valid data
        if "list" not in data or not data["list"]:
            return {"error": "No forecast data available", "forecasts": []}
        
        # Filter data for trip dates
        from datetime import datetime
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
        except:
            # If date parsing fails, use first 5 days of forecast
            start = datetime.now()
            end = start + timedelta(days=5)
        
        filtered_forecasts = []
        for item in data.get("list", []):
            forecast_time = datetime.fromtimestamp(item["dt"])
            if start <= forecast_time <= end + timedelta(days=1):  # Include end day fully
                filtered_forecasts.append({
                    "datetime": forecast_time.isoformat(),
                    "temp": item["main"]["temp"],
                    "feels_like": item["main"]["feels_like"],
                    "temp_min": item["main"]["temp_min"],
                    "temp_max": item["main"]["temp_max"],
                    "humidity": item["main"]["humidity"],
                    "weather": item["weather"][0]["main"],
                    "description": item["weather"][0]["description"],
                    "clouds": item["clouds"]["all"],
                    "wind_speed": item["wind"]["speed"],
                    "rain": item.get("rain", {}).get("3h", 0),
                    "pop": item.get("pop", 0) * 100  # Probability of precipitation
                })
        
        # If no forecasts in date range, use all available
        if not filtered_forecasts:
            for item in data.get("list", [])[:24]:  # Use first 3 days
                forecast_time = datetime.fromtimestamp(item["dt"])
                filtered_forecasts.append({
                    "datetime": forecast_time.isoformat(),
                    "temp": item["main"]["temp"],
                    "feels_like": item["main"]["feels_like"],
                    "temp_min": item["main"]["temp_min"],
                    "temp_max": item["main"]["temp_max"],
                    "humidity": item["main"]["humidity"],
                    "weather": item["weather"][0]["main"],
                    "description": item["weather"][0]["description"],
                    "clouds": item["clouds"]["all"],
                    "wind_speed": item["wind"]["speed"],
                    "rain": item.get("rain", {}).get("3h", 0),
                    "pop": item.get("pop", 0) * 100
                })
        
        return {
            "city": data["city"]["name"],
            "country": data["city"]["country"],
            "forecasts": filtered_forecasts,
            "timezone": data["city"]["timezone"]
        }
    except requests.exceptions.RequestException as e:
        print(f"Weather API Request Error: {e}")
        return {"error": f"API request failed: {str(e)}", "forecasts": []}
    except Exception as e:
        print(f"Weather Data Error: {e}")
        return {"error": str(e), "forecasts": []}


def calculate_weather_score(weather_data: Dict, holiday_type: str) -> float:
    """
    Calculate weather favorability score (0-100)
    """
    if not weather_data.get("forecasts"):
        return 50.0  # Neutral if no data
    
    scores = []
    for forecast in weather_data["forecasts"]:
        score = 100.0
        
        # Temperature comfort
        temp = forecast["temp"]
        if holiday_type == "Skiing":
            if temp < 0:
                score -= 0
            elif temp < 10:
                score -= 10
            else:
                score -= 30
        else:
            if WEATHER_TEMP_COMFORTABLE[0] <= temp <= WEATHER_TEMP_COMFORTABLE[1]:
                score -= 0
            elif temp < WEATHER_TEMP_COMFORTABLE[0]:
                score -= abs(temp - WEATHER_TEMP_COMFORTABLE[0]) * 2
            else:
                score -= abs(temp - WEATHER_TEMP_COMFORTABLE[1]) * 1.5
        
        # Rain/precipitation
        if forecast["pop"] > WEATHER_RAIN_THRESHOLD:
            score -= 30
        elif forecast["pop"] > 40:
            score -= 15
        
        # Weather conditions
        bad_weather = ["Thunderstorm", "Snow", "Extreme"]
        if forecast["weather"] in bad_weather and holiday_type not in ["Skiing"]:
            score -= 25
        
        # Wind
        if forecast["wind_speed"] > 15:
            score -= 10
        
        scores.append(max(0, score))
    
    return sum(scores) / len(scores) if scores else 50.0


# ============ Search APIs (SerpAPI) ============

def search_hotels(destination: str, check_in: str, check_out: str, num_people: str) -> List[Dict]:
    """
    Search hotels using SerpAPI Google Hotels
    """
    try:
        guests = parse_num_people(num_people)
        
        params = {
            "engine": "google_hotels",
            "q": f"{destination} hotels",
            "check_in_date": check_in,
            "check_out_date": check_out,
            "adults": guests,
            "currency": "INR",
            "gl": "in",
            "hl": "en",
            "api_key": SERPAPI_API_KEY
        }
        
        response = requests.get(SERPAPI_BASE_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Parse hotel results
        hotels = []
        properties = data.get("properties", [])
        
        for prop in properties[:15]:
            # Extract price
            price_per_night = None
            if prop.get("rate_per_night"):
                price_info = prop["rate_per_night"]
                if isinstance(price_info, dict):
                    price_per_night = price_info.get("lowest")
                elif isinstance(price_info, (int, float)):
                    price_per_night = price_info
            
            # If no price, try extracted price
            if not price_per_night and prop.get("total_rate"):
                total_rate = prop["total_rate"]
                if isinstance(total_rate, dict):
                    price_per_night = total_rate.get("lowest")
                elif isinstance(total_rate, (int, float)):
                    # Estimate per night from total
                    from datetime import datetime
                    days = (datetime.fromisoformat(check_out) - datetime.fromisoformat(check_in)).days
                    price_per_night = total_rate / days if days > 0 else total_rate
            
            # Default if still no price
            if not price_per_night:
                price_per_night = 3000
            
            hotel = {
                "name": prop.get("name", "Hotel"),
                "price_per_night": int(price_per_night),
                "rating": prop.get("overall_rating", 4.0),
                "link": prop.get("link", ""),
                "description": prop.get("description", "")[:200],
                "location": destination,
                "amenities": prop.get("amenities", [])
            }
            hotels.append(hotel)
        
        return hotels if hotels else generate_fallback_hotels(destination)
    except Exception as e:
        print(f"Hotel search error: {e}")
        return generate_fallback_hotels(destination)


def search_flights(departure_city: str, destination: str, 
                  outbound_date: str, return_date: str, num_people: str) -> List[Dict]:
    """
    Search flights using SerpAPI Google Flights
    """
    try:
        passengers = parse_num_people(num_people)
        
        params = {
            "engine": "google_flights",
            "departure_id": get_airport_code(departure_city),
            "arrival_id": get_airport_code(destination),
            "outbound_date": outbound_date,
            "return_date": return_date,
            "adults": passengers,
            "currency": "INR",
            "hl": "en",
            "gl": "in",
            "api_key": SERPAPI_API_KEY
        }
        
        response = requests.get(SERPAPI_BASE_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        flights = []
        best_flights = data.get("best_flights", [])
        other_flights = data.get("other_flights", [])
        all_flights = best_flights + other_flights
        
        for flight_data in all_flights[:10]:
            flights_info = flight_data.get("flights", [])
            if not flights_info:
                continue
            
            # Get first flight segment for airline info
            first_flight = flights_info[0]
            airline = first_flight.get("airline", "Unknown Airline")
            
            # Get total duration
            total_duration = flight_data.get("total_duration", 0)
            hours = total_duration // 60
            minutes = total_duration % 60
            duration_str = f"{hours}h {minutes}m" if hours else f"{minutes}m"
            
            # Get price
            price = flight_data.get("price", 15000)
            
            # Count stops
            layovers = flight_data.get("layovers", [])
            stops = "Non-stop" if not layovers else f"{len(layovers)} stop(s)"
            
            flight = {
                "airline": airline,
                "price_total": int(price),
                "price_per_person": int(price / passengers),
                "duration": duration_str,
                "stops": stops,
                "link": f"https://www.google.com/travel/flights",
                "outbound_date": outbound_date,
                "return_date": return_date,
                "passengers": passengers,
                "departure_airport": first_flight.get("departure_airport", {}).get("name", departure_city),
                "arrival_airport": first_flight.get("arrival_airport", {}).get("name", destination)
            }
            flights.append(flight)
        
        return flights if flights else generate_fallback_flights(departure_city, destination, passengers)
    except Exception as e:
        print(f"Flight search error: {e}")
        return generate_fallback_flights(departure_city, destination, 
                                        1 if num_people == "1" else 2)


def search_useful_links(destination: str, month: str) -> List[Dict]:
    """
    Search for travel guides and tips using SerpAPI
    """
    try:
        params = {
            "engine": "google",
            "q": f"travel guide {destination} tips {month}",
            "gl": "in",
            "hl": "en",
            "num": 5,
            "api_key": SERPAPI_API_KEY
        }
        
        response = requests.get(SERPAPI_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        links = []
        for result in data.get("organic_results", [])[:5]:
            links.append({
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", "")
            })
        
        return links
    except Exception as e:
        return []


# ============ Fallback Functions ============

def generate_fallback_hotels(destination: str) -> List[Dict]:
    """Generate fallback hotel data when API fails"""
    return [
        {
            "name": f"Hotel {i+1} in {destination}",
            "price_per_night": 2000 + (i * 500),
            "rating": 4.0 + (i * 0.2),
            "link": "",
            "description": f"Comfortable accommodation in {destination}",
            "location": destination,
            "amenities": ["WiFi", "Breakfast"]
        }
        for i in range(5)
    ]


def generate_fallback_flights(departure: str, destination: str, passengers: int) -> List[Dict]:
    """Generate fallback flight data when API fails"""
    # Estimate base price based on common routes
    route_key = f"{departure.lower()}-{destination.lower()}"
    
    # Common domestic routes pricing (per person)
    route_prices = {
        "mumbai-goa": 4000,
        "mumbai-delhi": 5000,
        "bangalore-chennai": 3500,
        "bengaluru-chennai": 3500,
        "delhi-mumbai": 5000,
        "delhi-bangalore": 6000,
        "chennai-bangalore": 3500,
        "hyderabad-bangalore": 3000,
        "pune-bangalore": 4000,
    }
    
    # Get base price or estimate
    base_price = route_prices.get(route_key, 5000)
    
    # If reverse route exists, use that
    reverse_key = f"{destination.lower()}-{departure.lower()}"
    if reverse_key in route_prices:
        base_price = route_prices[reverse_key]
    
    airlines = ["IndiGo", "Air India", "SpiceJet", "Vistara", "Go First"]
    
    return [
        {
            "airline": airlines[i % len(airlines)],
            "price_total": (base_price + (i * 1000)) * passengers,
            "price_per_person": base_price + (i * 1000),
            "duration": f"{2 + i}h 30m",
            "stops": "Non-stop" if i == 0 else f"{i} stop(s)",
            "link": "",
            "outbound_date": "",
            "return_date": "",
            "passengers": passengers,
            "departure_airport": departure,
            "arrival_airport": destination
        }
        for i in range(3)
    ]


def get_airport_code(city: str) -> str:
    """Map city names to airport codes for SerpAPI"""
    airport_codes = {
        "mumbai": "BOM",
        "delhi": "DEL",
        "bangalore": "BLR",
        "bengaluru": "BLR",
        "chennai": "MAA",
        "kolkata": "CCU",
        "hyderabad": "HYD",
        "pune": "PNQ",
        "ahmedabad": "AMD",
        "jaipur": "JAI",
        "goa": "GOI",
        "kochi": "COK",
        "cochin": "COK",
        "thiruvananthapuram": "TRV",
        "trivandrum": "TRV",
        "lucknow": "LKO",
        "chandigarh": "IXC",
        "indore": "IDR",
        "coimbatore": "CJB",
        "nagpur": "NAG",
        "srinagar": "SXR",
        "amritsar": "ATQ",
        "varanasi": "VNS",
        "bhubaneswar": "BBI",
        "patna": "PAT",
        "raipur": "RPR",
        "ranchi": "IXR",
        "bhopal": "BHO",
        "udaipur": "UDR",
        "guwahati": "GAU",
        "visakhapatnam": "VTZ",
        "vizag": "VTZ",
        "mangalore": "IXE",
        "madurai": "IXM",
        "manali": "KUU",  # Kullu-Manali
        "leh": "IXL",
        "port blair": "IXZ",
        "agra": "AGR"
    }
    
    city_lower = city.lower().strip()
    return airport_codes.get(city_lower, city_lower.upper()[:3])


# ============ Helper Functions ============

def parse_num_people(num_people: str) -> int:
    """Convert num_people string to actual number"""
    mapping = {
        "1": 1,
        "2": 2,
        "3": 3,
        "4-6": 5,    # Use middle of range
        "7-10": 8,   # Use middle of range
        "10+": 12    # Reasonable estimate
    }
    return mapping.get(num_people, 2)  # Default to 2


def format_currency(amount: float) -> str:
    """Format amount in INR"""
    return f"₹{amount:,.0f}"


def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime"""
    try:
        return datetime.fromisoformat(date_str)
    except:
        return datetime.strptime(date_str, "%Y-%m-%d")


def calculate_trip_duration(start_date: str, end_date: str) -> int:
    """Calculate number of days"""
    start = parse_date(start_date)
    end = parse_date(end_date)
    return (end - start).days + 1


def get_month_name(date_str: str) -> str:
    """Get month name from date"""
    date = parse_date(date_str)
    return date.strftime("%B")