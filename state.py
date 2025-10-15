"""
State management for Trip Planner
"""
from typing import TypedDict, Annotated, Literal
from datetime import datetime


class GraphState(TypedDict):
    """Complete state schema for the trip planning workflow"""
    
    # ============ User Input ============
    preferences: dict  # {
        # destination, departure_city, start_date, end_date, 
        # duration, num_people, holiday_type, budget_type, comments
    # }
    
    # ============ Weather Data ============
    weather_raw: dict  # Raw OpenWeatherMap API response
    weather_analysis: str  # LLM analysis of weather conditions
    weather_favorable: bool  # True if weather is good
    weather_score: float  # 0-100 score
    weather_summary: str  # Brief summary for UI
    
    # ============ Alternate Destinations ============
    alternate_destinations: list[dict]  # [{name, reason, distance}]
    alternate_selected: bool  # If user selected alternate
    
    # ============ Search Results ============
    hotel_results: list[dict]  # Raw hotel search results
    flight_results: list[dict]  # Raw flight search results
    
    # ============ Filtered & Ranked ============
    budget_approved_hotels: list[dict]  # Hotels within budget
    budget_approved_flights: list[dict]  # Flights within budget
    ranked_hotels: list[dict]  # Top 5 hotels
    ranked_flights: list[dict]  # Top 3 flights
    
    # ============ Selected Options ============
    selected_hotels: list[dict]  # Top 3 hotels for user to choose
    selected_flights: list[dict]  # Top 3 flights for user to choose
    chosen_hotel: dict  # Final user choice (default: first one)
    chosen_flight: dict  # Final user choice (default: first one)
    total_cost: float  # Total trip cost in INR
    
    # ============ Itinerary ============
    itinerary: str  # Full text itinerary
    day_wise_plan: list[dict]  # [{day, date, activities, meals, notes}]
    
    # ============ Additional Info ============
    activity_suggestions: str  # Detailed activity suggestions
    packing_list: str  # What to pack
    food_culture_info: str  # Food and culture guide
    useful_links: list[dict]  # [{title, link}]
    
    # ============ User Interaction ============
    user_feedback: str  # "accept", "modify_hotels", "modify_dates", "change_destination"
    replan_reason: str  # Why replanning is needed
    modification_request: str  # User's modification request
    
    # ============ Chat ============
    chat_history: Annotated[list[dict], "List of {question, response} pairs"]
    user_question: str  # Current question
    chat_response: str  # Current response
    
    # ============ Monitoring & Logs ============
    current_node: str  # Current executing node
    node_logs: list[dict]  # [{node, timestamp, status, duration}]
    errors: list[str]  # Any errors encountered
    warnings: list[str]  # Any warnings
    
    # ============ Control Flow ============
    workflow_status: Literal["in_progress", "completed", "failed", "waiting_user"]
    next_action: str  # Next node to execute


def create_initial_state() -> GraphState:
    """Create initial empty state"""
    return {
        "preferences": {},
        "weather_raw": {},
        "weather_analysis": "",
        "weather_favorable": False,
        "weather_score": 0.0,
        "weather_summary": "",
        "alternate_destinations": [],
        "alternate_selected": False,
        "hotel_results": [],
        "flight_results": [],
        "budget_approved_hotels": [],
        "budget_approved_flights": [],
        "ranked_hotels": [],
        "ranked_flights": [],
        "selected_hotels": [],
        "selected_flights": [],
        "chosen_hotel": {},
        "chosen_flight": {},
        "total_cost": 0.0,
        "itinerary": "",
        "day_wise_plan": [],
        "activity_suggestions": "",
        "packing_list": "",
        "food_culture_info": "",
        "useful_links": [],
        "user_feedback": "",
        "replan_reason": "",
        "modification_request": "",
        "chat_history": [],
        "user_question": "",
        "chat_response": "",
        "current_node": "",
        "node_logs": [],
        "errors": [],
        "warnings": [],
        "workflow_status": "in_progress",
        "next_action": ""
    }


def log_node_execution(state: GraphState, node_name: str, status: str, duration: float = 0.0) -> GraphState:
    """Helper to log node execution"""
    log_entry = {
        "node": node_name,
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "duration": duration
    }
    state["node_logs"].append(log_entry)
    state["current_node"] = node_name
    return state