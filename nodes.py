"""
LangGraph Nodes for Trip Planning Workflow
"""
import json
import time
from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from state import GraphState, log_node_execution
from utils import (
    fetch_weather_data, calculate_weather_score, search_hotels, 
    search_flights, search_useful_links, format_currency
)
from config import (
    GOOGLE_API_KEY, LLM_MODEL, LLM_TEMPERATURE, 
    BUDGET_RANGES, WEATHER_FAVORABLE_THRESHOLD, HOLIDAY_PREFERENCES
)

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    api_key=GOOGLE_API_KEY, 
    model=LLM_MODEL,
    temperature=LLM_TEMPERATURE
)


# ============ Node 1: Fetch Weather ============

def fetch_weather_node(state: GraphState) -> Dict:
    """Fetch weather forecast for trip dates"""
    start_time = time.time()
    
    try:
        prefs = state["preferences"]
        destination = prefs["destination"]
        start_date = prefs["start_date"]
        end_date = prefs["end_date"]
        
        weather_data = fetch_weather_data(destination, start_date, end_date)
        
        if weather_data.get("error"):
            return {
                "weather_raw": {},
                "errors": state.get("errors", []) + [f"Weather API error: {weather_data['error']}"],
                "node_logs": state.get("node_logs", [])
            }
        
        duration = time.time() - start_time
        state = log_node_execution(state, "fetch_weather", "success", duration)
        
        return {
            "weather_raw": weather_data,
            "node_logs": state["node_logs"]
        }
    except Exception as e:
        return {
            "weather_raw": {},
            "errors": state.get("errors", []) + [f"Fetch weather failed: {str(e)}"],
            "node_logs": state.get("node_logs", [])
        }


# ============ Node 2: Analyze Weather ============

def analyze_weather_node(state: GraphState) -> Dict:
    """Analyze weather data and generate score"""
    start_time = time.time()
    
    try:
        weather_data = state["weather_raw"]
        prefs = state["preferences"]
        holiday_type = prefs.get("holiday_type", "Any")
        
        if not weather_data.get("forecasts"):
            return {
                "weather_analysis": "Weather data unavailable",
                "weather_score": 50.0,
                "weather_favorable": True,
                "weather_summary": "Unable to fetch weather, proceeding with planning"
            }
        
        # Calculate score
        score = calculate_weather_score(weather_data, holiday_type)
        
        # LLM analysis
        prompt = f"""
        Analyze this weather forecast for a {holiday_type} trip to {weather_data.get('city')}:
        
        Weather Data:
        {json.dumps(weather_data['forecasts'][:10], indent=2)}
        
        Provide:
        1. A brief weather summary (2-3 sentences)
        2. Key concerns or highlights
        3. Recommendations for travelers
        
        Weather Score: {score:.1f}/100
        
        Keep it concise and practical.
        """
        
        try:
            analysis = llm.invoke(prompt).content.strip()
        except:
            analysis = f"Weather score: {score:.1f}/100. Check detailed forecast."
        
        # Determine if favorable
        favorable = score >= WEATHER_FAVORABLE_THRESHOLD
        
        # Create summary
        avg_temp = sum(f["temp"] for f in weather_data["forecasts"]) / len(weather_data["forecasts"])
        summary = f"Score: {score:.0f}/100 | Avg Temp: {avg_temp:.1f}°C"
        
        duration = time.time() - start_time
        state = log_node_execution(state, "analyze_weather", "success", duration)
        
        return {
            "weather_analysis": analysis,
            "weather_score": score,
            "weather_favorable": favorable,
            "weather_summary": summary,
            "node_logs": state["node_logs"]
        }
    except Exception as e:
        return {
            "weather_analysis": "Analysis failed",
            "weather_score": 50.0,
            "weather_favorable": True,
            "weather_summary": "Proceeding with default",
            "errors": state.get("errors", []) + [f"Weather analysis failed: {str(e)}"]
        }


# ============ Node 3: Suggest Alternates ============

def suggest_alternates_node(state: GraphState) -> Dict:
    """Suggest alternate destinations if weather is unfavorable"""
    start_time = time.time()
    
    try:
        prefs = state["preferences"]
        destination = prefs["destination"]
        holiday_type = prefs.get("holiday_type", "Any")
        
        prompt = f"""
        The weather forecast for {destination} is unfavorable (score: {state['weather_score']:.1f}/100).
        
        Suggest 3 alternate destinations in India that:
        1. Are similar in vibe to {destination}
        2. Are suitable for a {holiday_type} holiday
        3. Typically have better weather during the same period
        4. Are within reasonable travel distance
        
        Return ONLY a JSON array like this:
        [
            {{"name": "Destination1", "reason": "Why it's better", "distance": "~500 km"}},
            {{"name": "Destination2", "reason": "Why it's better", "distance": "~300 km"}},
            {{"name": "Destination3", "reason": "Why it's better", "distance": "~400 km"}}
        ]
        """
        
        result = llm.invoke(prompt).content.strip()
        
        # Parse JSON
        import re
        json_match = re.search(r'\[.*\]', result, re.DOTALL)
        if json_match:
            alternates = json.loads(json_match.group())
        else:
            alternates = []
        
        duration = time.time() - start_time
        state = log_node_execution(state, "suggest_alternates", "success", duration)
        
        return {
            "alternate_destinations": alternates,
            "node_logs": state["node_logs"]
        }
    except Exception as e:
        return {
            "alternate_destinations": [],
            "warnings": state.get("warnings", []) + [f"Could not suggest alternates: {str(e)}"]
        }


# ============ Node 4: Search Hotels ============

def search_hotels_node(state: GraphState) -> Dict:
    """Search for hotels"""
    start_time = time.time()
    
    try:
        prefs = state["preferences"]
        destination = prefs["destination"]
        start_date = prefs["start_date"]
        end_date = prefs["end_date"]
        num_people = prefs.get("num_people", "2")
        
        hotels = search_hotels(destination, start_date, end_date, num_people)
        
        duration = time.time() - start_time
        state = log_node_execution(state, "search_hotels", "success", duration)
        
        return {
            "hotel_results": hotels,
            "node_logs": state["node_logs"]
        }
    except Exception as e:
        return {
            "hotel_results": [],
            "errors": state.get("errors", []) + [f"Hotel search failed: {str(e)}"]
        }


# ============ Node 5: Search Flights ============

def search_flights_node(state: GraphState) -> Dict:
    """Search for flights"""
    start_time = time.time()
    
    try:
        prefs = state["preferences"]
        departure_city = prefs.get("departure_city", "Delhi")
        destination = prefs["destination"]
        start_date = prefs["start_date"]
        end_date = prefs["end_date"]
        num_people = prefs.get("num_people", "2")
        
        flights = search_flights(departure_city, destination, start_date, end_date, num_people)
        
        duration = time.time() - start_time
        state = log_node_execution(state, "search_flights", "success", duration)
        
        return {
            "flight_results": flights,
            "node_logs": state["node_logs"]
        }
    except Exception as e:
        return {
            "flight_results": [],
            "errors": state.get("errors", []) + [f"Flight search failed: {str(e)}"]
        }


# ============ Node 6: Budget Filter ============

def budget_filter_node(state: GraphState) -> Dict:
    """Filter hotels and flights by budget"""
    start_time = time.time()
    
    try:
        prefs = state["preferences"]
        budget_type = prefs.get("budget_type", "Mid-Range")
        duration = prefs.get("duration", 7)
        
        budget_range = BUDGET_RANGES.get(budget_type, BUDGET_RANGES["Mid-Range"])
        
        # Filter hotels
        hotel_min, hotel_max = budget_range["hotel_per_night"]
        approved_hotels = [
            h for h in state["hotel_results"]
            if hotel_min <= h.get("price_per_night", 0) <= hotel_max
        ]
        
        # Filter flights
        flight_min, flight_max = budget_range["flight_total"]
        approved_flights = [
            f for f in state["flight_results"]
            if flight_min <= f.get("price_total", 0) <= flight_max
        ]
        
        # If too few results, relax constraints
        if len(approved_hotels) < 3:
            approved_hotels = sorted(state["hotel_results"], 
                                   key=lambda x: x.get("price_per_night", 0))[:10]
        
        if len(approved_flights) < 2:
            approved_flights = sorted(state["flight_results"], 
                                    key=lambda x: x.get("price_total", 0))[:5]
        
        duration = time.time() - start_time
        state = log_node_execution(state, "budget_filter", "success", duration)
        
        return {
            "budget_approved_hotels": approved_hotels,
            "budget_approved_flights": approved_flights,
            "node_logs": state["node_logs"]
        }
    except Exception as e:
        return {
            "budget_approved_hotels": state.get("hotel_results", [])[:10],
            "budget_approved_flights": state.get("flight_results", [])[:5],
            "warnings": state.get("warnings", []) + [f"Budget filter issue: {str(e)}"]
        }


# ============ Node 7: Preference Ranking ============

def preference_ranking_node(state: GraphState) -> Dict:
    """Rank hotels and flights by preferences"""
    start_time = time.time()
    
    try:
        prefs = state["preferences"]
        holiday_type = prefs.get("holiday_type", "Any")
        
        hotels = state["budget_approved_hotels"][:15]
        flights = state["budget_approved_flights"][:8]
        
        # LLM-based ranking
        prompt = f"""
        Rank these options for a {holiday_type} trip:
        
        HOTELS:
        {json.dumps([{"name": h["name"], "price": h["price_per_night"], "rating": h.get("rating", 4.0)} for h in hotels], indent=2)}
        
        FLIGHTS:
        {json.dumps([{"airline": f["airline"], "price": f["price_total"], "duration": f.get("duration", "N/A")} for f in flights], indent=2)}
        
        Return ONLY a JSON object:
        {{
            "top_hotels": [0, 2, 1, 4, 3],  // indices of top 5 hotels in order
            "top_flights": [1, 0, 2]  // indices of top 3 flights in order
        }}
        
        Consider: value for money, ratings, suitability for {holiday_type}.
        """
        
        result = llm.invoke(prompt).content.strip()
        
        # Parse JSON
        import re
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            rankings = json.loads(json_match.group())
            
            top_hotel_indices = rankings.get("top_hotels", list(range(5)))[:5]
            top_flight_indices = rankings.get("top_flights", list(range(3)))[:3]
            
            ranked_hotels = [hotels[i] for i in top_hotel_indices if i < len(hotels)]
            ranked_flights = [flights[i] for i in top_flight_indices if i < len(flights)]
        else:
            # Fallback: sort by price and rating
            ranked_hotels = sorted(hotels, key=lambda x: (-x.get("rating", 4.0), x.get("price_per_night", 0)))[:5]
            ranked_flights = sorted(flights, key=lambda x: x.get("price_total", 0))[:3]
        
        # Select best options
        selected_hotels = ranked_hotels[:3] if len(ranked_hotels) >= 3 else ranked_hotels
        selected_flights = ranked_flights[:3] if len(ranked_flights) >= 3 else ranked_flights
        
        # Default choices (user can change these in UI)
        chosen_hotel = selected_hotels[0] if selected_hotels else {}
        chosen_flight = selected_flights[0] if selected_flights else {}
        
        # Calculate total cost (using default choices)
        duration_days = prefs.get("duration", 7)
        hotel_cost = chosen_hotel.get("price_per_night", 0) * duration_days
        flight_cost = chosen_flight.get("price_total", 0)
        total_cost = hotel_cost + flight_cost
        
        duration = time.time() - start_time
        state = log_node_execution(state, "preference_ranking", "success", duration)
        
        return {
            "ranked_hotels": ranked_hotels,
            "ranked_flights": ranked_flights,
            "selected_hotels": selected_hotels,
            "selected_flights": selected_flights,
            "chosen_hotel": chosen_hotel,
            "chosen_flight": chosen_flight,
            "total_cost": total_cost,
            "node_logs": state["node_logs"]
        }
    except Exception as e:
        # Fallback selection
        hotels = state["budget_approved_hotels"]
        flights = state["budget_approved_flights"]
        
        return {
            "ranked_hotels": hotels[:5],
            "ranked_flights": flights[:3],
            "selected_hotels": hotels[:3],
            "selected_flights": flights[:3],
            "chosen_hotel": hotels[0] if hotels else {},
            "chosen_flight": flights[0] if flights else {},
            "total_cost": 0.0,
            "warnings": state.get("warnings", []) + [f"Ranking failed: {str(e)}"]
        }


# ============ Node 8: Generate Itinerary ============

def generate_itinerary_node(state: GraphState) -> Dict:
    """Generate complete day-wise itinerary"""
    start_time = time.time()
    
    try:
        prefs = state["preferences"]
        hotel = state["chosen_hotel"]
        flight = state["chosen_flight"]
        weather = state["weather_analysis"]
        
        prompt = f"""
        Create a detailed day-wise travel itinerary:
        
        TRIP DETAILS:
        - Destination: {prefs["destination"]}
        - Duration: {prefs["duration"]} days
        - Dates: {prefs["start_date"]} to {prefs["end_date"]}
        - Holiday Type: {prefs.get("holiday_type", "Any")}
        - Number of People: {prefs.get("num_people", "2")}
        - Budget: {prefs.get("budget_type", "Mid-Range")}
        - Comments: {prefs.get("comments", "None")}
        
        SELECTED HOTEL:
        - Name: {hotel.get("name", "TBD")}
        - Price: {format_currency(hotel.get("price_per_night", 0))} per night
        - Total: {format_currency(hotel.get("price_per_night", 0) * prefs["duration"])}
        
        SELECTED FLIGHT:
        - Airline: {flight.get("airline", "TBD")}
        - Price: {format_currency(flight.get("price_total", 0))} (round trip)
        
        WEATHER FORECAST:
        {weather}
        
        TOTAL ESTIMATED COST: {format_currency(state["total_cost"])}
        
        Create a comprehensive itinerary with:
        1. Day 0 (Arrival): Travel details, check-in, evening activities
        2. Days 1-{prefs["duration"]-1}: Morning, afternoon, evening activities for each day
        3. Last Day (Departure): Check-out, last activities, return flight
        
        For each day include:
        - Specific activities and attractions
        - Meal recommendations (breakfast, lunch, dinner spots)
        - Estimated time for each activity
        - Travel tips and local insights
        - Downtime/rest periods
        
        Make it detailed, practical, and exciting! Format in clear sections.
        """
        
        itinerary = llm.invoke(prompt).content.strip()
        
        duration = time.time() - start_time
        state = log_node_execution(state, "generate_itinerary", "success", duration)
        
        return {
            "itinerary": itinerary,
            "workflow_status": "completed",
            "node_logs": state["node_logs"]
        }
    except Exception as e:
        return {
            "itinerary": "Failed to generate itinerary. Please try again.",
            "errors": state.get("errors", []) + [f"Itinerary generation failed: {str(e)}"],
            "workflow_status": "failed"
        }


# ============ Additional Feature Nodes ============

def activity_suggestions_node(state: GraphState) -> Dict:
    """Generate activity suggestions"""
    try:
        prefs = state["preferences"]
        prompt = f"""
        Suggest unique local activities for a {prefs.get("holiday_type", "general")} trip to {prefs["destination"]}:
        
        Duration: {prefs["duration"]} days
        Itinerary: {state["itinerary"][:500]}...
        
        Provide 8-10 specific activity suggestions with:
        - Activity name
        - Brief description
        - Estimated cost in INR
        - Best time to do it
        
        Focus on experiences beyond typical tourist spots.
        """
        
        result = llm.invoke(prompt).content.strip()
        return {"activity_suggestions": result}
    except Exception as e:
        return {"activity_suggestions": "", "warnings": state.get("warnings", []) + [str(e)]}


def packing_list_node(state: GraphState) -> Dict:
    """Generate packing list"""
    try:
        prefs = state["preferences"]
        weather = state["weather_summary"]
        
        prompt = f"""
        Create a comprehensive packing list for:
        - Destination: {prefs["destination"]}
        - Duration: {prefs["duration"]} days
        - Holiday Type: {prefs.get("holiday_type", "Any")}
        - Weather: {weather}
        
        Organize in categories:
        1. Clothing
        2. Toiletries & Personal Care
        3. Electronics & Gadgets
        4. Documents & Money
        5. Health & Safety
        6. Activity-Specific Items
        7. Miscellaneous
        
        Be specific and practical.
        """
        
        result = llm.invoke(prompt).content.strip()
        return {"packing_list": result}
    except Exception as e:
        return {"packing_list": "", "warnings": state.get("warnings", []) + [str(e)]}


def food_culture_node(state: GraphState) -> Dict:
    """Generate food and culture guide"""
    try:
        prefs = state["preferences"]
        prompt = f"""
        Provide a food and culture guide for {prefs["destination"]}:
        
        Budget: {prefs.get("budget_type", "Mid-Range")}
        
        Include:
        1. MUST-TRY LOCAL DISHES (5-7 dishes with descriptions)
        2. RECOMMENDED RESTAURANTS (budget-appropriate)
        3. STREET FOOD GUIDE (safe options)
        4. CULTURAL ETIQUETTE (dos and don'ts)
        5. LOCAL CUSTOMS (greetings, tipping, dress code)
        6. IMPORTANT PHRASES (if different language)
        
        Be practical and respectful.
        """
        
        result = llm.invoke(prompt).content.strip()
        return {"food_culture_info": result}
    except Exception as e:
        return {"food_culture_info": "", "warnings": state.get("warnings", []) + [str(e)]}


def fetch_useful_links_node(state: GraphState) -> Dict:
    """Fetch useful travel links"""
    try:
        prefs = state["preferences"]
        destination = prefs["destination"]
        month = prefs.get("start_date", "")[:7]  # Get year-month
        
        links = search_useful_links(destination, month)
        return {"useful_links": links}
    except Exception as e:
        return {"useful_links": [], "warnings": state.get("warnings", []) + [str(e)]}


def chat_node(state: GraphState) -> Dict:
    """Handle chat queries about itinerary"""
    try:
        prompt = f"""
        Context:
        Preferences: {json.dumps(state['preferences'], indent=2)}
        Itinerary: {state['itinerary'][:1000]}
        Selected Hotels: {json.dumps([h.get('name', 'N/A') for h in state.get('selected_hotels', [])], indent=2)}
        Selected Flights: {json.dumps([f.get('airline', 'N/A') for f in state.get('selected_flights', [])], indent=2)}
        Chosen Hotel: {state.get('chosen_hotel', {}).get('name', 'N/A')}
        Chosen Flight: {state.get('chosen_flight', {}).get('airline', 'N/A')}
        Total Cost: {format_currency(state.get('total_cost', 0))}
        
        User Question: {state['user_question']}
        
        Provide a helpful, concise response. Keep it conversational and under 150 words.
        """
        
        response = llm.invoke(prompt).content.strip()
        
        chat_entry = {
            "question": state['user_question'],
            "response": response
        }
        
        chat_history = state.get('chat_history', []) + [chat_entry]
        
        return {
            "chat_response": response,
            "chat_history": chat_history
        }
    except Exception as e:
        return {
            "chat_response": "Sorry, I couldn't process your question.",
            "warnings": state.get("warnings", []) + [str(e)]
        }