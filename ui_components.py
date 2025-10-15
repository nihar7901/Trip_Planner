"""
Streamlit UI Components for Trip Planner
"""
import streamlit as st
from datetime import datetime, timedelta
from utils import format_currency
import tempfile
from fpdf import FPDF


def apply_custom_css():
    """Apply custom CSS for attractive UI"""
    st.markdown("""
        <style>
        /* Main theme */
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
        }
        
        /* Title styling - IMPROVED CONTRAST */
        h1 {
            color: #ffffff !important;
            text-align: center;
            font-size: 3.5rem !important;
            font-weight: 800 !important;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.5) !important;
            margin-bottom: 1rem !important;
            background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        /* Subtitle styling */
        .subtitle {
            text-align: center;
            color: #ffffff !important;
            font-size: 1.3rem;
            font-weight: 600;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.4);
            margin-bottom: 2rem;
        }
        
        /* Center alignment for main content */
        .center-content {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            width: 100%;
        }
        
        /* Card styling */
        .stCard {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        /* Form container */
        [data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.95);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        
        /* Progress bar */
        .progress-container {
            background: rgba(255, 255, 255, 0.9);
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem auto;
            max-width: 900px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
            border-radius: 10px;
            font-weight: 600;
        }
        
        /* Weather card */
        .weather-card {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem auto;
            max-width: 800px;
            box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3);
        }
        
        /* Cost display */
        .cost-display {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            font-size: 1.5rem;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
            margin: 1rem auto;
            max-width: 600px;
        }
        
        /* Itinerary container - CENTER ALIGNED */
        .itinerary-container {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            line-height: 1.8;
            margin: 1rem auto;
            max-width: 900px;
        }
        
        /* Section headers in itinerary */
        .itinerary-container h2,
        .itinerary-container h3,
        .itinerary-container h4 {
            color: #667eea;
            margin-top: 1.5rem;
            margin-bottom: 0.8rem;
        }
        
        /* Lists in itinerary */
        .itinerary-container ul,
        .itinerary-container ol {
            margin-left: 1.5rem;
            margin-bottom: 1rem;
        }
        
        /* Icon styling */
        .icon-text {
            font-size: 1.2rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        /* Alert boxes */
        .stAlert {
            border-radius: 10px;
            border-left: 5px solid #667eea;
        }
        
        /* Center buttons container */
        .button-container {
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin: 2rem auto;
            max-width: 1000px;
        }
        </style>
    """, unsafe_allow_html=True)


def render_header():
    """Render application header"""
    st.markdown("""
        <h1>✈️ AI Travel Planner ✈️</h1>
    """, unsafe_allow_html=True)


def render_progress_tracker(state):
    """Render progress tracker"""
    steps = [
        ("Weather Check", "fetch_weather"),
        ("Search Hotels", "search_hotels"),
        ("Search Flights", "search_flights"),
        ("Budget Filter", "budget_filter"),
        ("Generate Plan", "generate_itinerary")
    ]
    
    completed_nodes = [log["node"] for log in state.get("node_logs", [])]
    
    st.markdown('<div class="progress-container">', unsafe_allow_html=True)
    cols = st.columns(len(steps))
    
    for i, (step_name, node_name) in enumerate(steps):
        with cols[i]:
            if node_name in completed_nodes:
                st.markdown(f"✅ **{step_name}**")
            else:
                st.markdown(f"⏳ {step_name}")
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_input_form():
    """Render the main input form"""
    with st.form("travel_form", clear_on_submit=False):
        st.markdown("### 📝 Plan Your Dream Trip")
        
        col1, col2 = st.columns(2)
        
        with col1:
            destination = st.text_input(
                "🌍 Destination", 
                placeholder="e.g., Goa, Manali, Kerala"
            )
            
            departure_city = st.text_input(
                "🛫 Departure City",
                value="Mumbai",
                placeholder="Where are you flying from?"
            )
            
            start_date = st.date_input(
                "📅 Start Date",
                value=datetime.now() + timedelta(days=30),
                min_value=datetime.now()
            )
            
            end_date = st.date_input(
                "📅 End Date",
                value=datetime.now() + timedelta(days=37),
                min_value=datetime.now() + timedelta(days=1)
            )
            
            num_people = st.selectbox(
                "👥 Number of People",
                ["1", "2", "3", "4-6", "7-10", "10+"]
            )
        
        with col2:
            holiday_type = st.selectbox(
                "🎯 Holiday Type",
                ["Any", "Beach", "Adventure", "City Break", "Skiing", 
                 "Party", "Backpacking", "Family", "Festival", "Romantic", "Cruise"]
            )
            
            budget_type = st.selectbox(
                "💰 Budget Type",
                ["Budget", "Mid-Range", "Luxury", "Backpacker", "Family"]
            )
            
            comments = st.text_area(
                "💭 Special Requests or Preferences",
                placeholder="Any specific requirements, dietary restrictions, accessibility needs, etc.",
                height=150
            )
        
        submit_btn = st.form_submit_button("🚀 Generate My Itinerary", use_container_width=True)
        
        if submit_btn:
            if not destination:
                st.error("Please enter a destination!")
                return None
            
            duration = (end_date - start_date).days + 1
            
            if duration < 1:
                st.error("End date must be after start date!")
                return None
            
            preferences = {
                "destination": destination,
                "departure_city": departure_city,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "duration": duration,
                "num_people": num_people,
                "holiday_type": holiday_type,
                "budget_type": budget_type,
                "comments": comments
            }
            
            return preferences
    
    return None


def render_weather_section(state):
    """Render weather information"""
    if not state.get("weather_analysis"):
        return
    
    score = state.get("weather_score", 0)
    
    # Color coding based on score
    if score >= 75:
        color = "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)"
        icon = "☀️"
    elif score >= 50:
        color = "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
        icon = "⛅"
    else:
        color = "linear-gradient(135deg, #868f96 0%, #596164 100%)"
        icon = "🌧️"
    
    st.markdown(f"""
        <div style='background: {color}; padding: 1.5rem; border-radius: 15px; 
                    color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2); margin: 1rem 0;'>
            <h3 style='margin: 0; color: white;'>{icon} Weather Forecast</h3>
            <p style='font-size: 1.8rem; font-weight: bold; margin: 0.5rem 0;'>
                Score: {score:.0f}/100
            </p>
            <p style='margin: 0;'>{state.get("weather_summary", "")}</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📊 Detailed Weather Analysis", expanded=False):
        st.markdown(state["weather_analysis"])


def render_alternate_destinations(state):
    """Render alternate destination suggestions"""
    alternates = state.get("alternate_destinations", [])
    
    if not alternates:
        return
    
    st.warning("⚠️ Weather conditions are not ideal. Consider these alternatives:")
    
    cols = st.columns(len(alternates))
    for i, alt in enumerate(alternates):
        with cols[i]:
            st.markdown(f"""
                <div style='background: rgba(255,255,255,0.9); padding: 1rem; 
                            border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
                    <h4 style='color: #667eea;'>{alt['name']}</h4>
                    <p style='font-size: 0.9rem;'>{alt['reason']}</p>
                    <p style='color: #888; font-size: 0.8rem;'>📍 {alt['distance']}</p>
                </div>
            """, unsafe_allow_html=True)


def render_selected_options(state):
    """Render top 3 hotels and flights for user selection"""
    selected_hotels = state.get("selected_hotels", [])
    selected_flights = state.get("selected_flights", [])
    chosen_hotel = state.get("chosen_hotel", {})
    chosen_flight = state.get("chosen_flight", {})
    
    if not selected_hotels or not selected_flights:
        return
    
    st.markdown("### 🏨 Top 3 Hotel Options")
    
    # Display hotels in 3 columns
    hotel_cols = st.columns(3)
    for i, hotel in enumerate(selected_hotels[:3]):
        with hotel_cols[i]:
            is_chosen = (hotel.get("name") == chosen_hotel.get("name"))
            border_color = "#667eea" if is_chosen else "#ddd"
            badge = "✅ Selected" if is_chosen else f"Option {i+1}"
            
            # Get hotel name and truncate if too long
            hotel_name = hotel.get('name', f'Hotel Option {i+1}')
            if len(hotel_name) > 50:
                hotel_name = hotel_name[:47] + "..."
            
            st.markdown(f"""
                <div style='background: white; padding: 1.5rem; border-radius: 10px; 
                            border: 3px solid {border_color};
                            box-shadow: 0 4px 15px rgba(0,0,0,0.1); height: 100%;'>
                    <span style='background: {border_color}; color: white; padding: 0.3rem 0.6rem; 
                                 border-radius: 5px; font-size: 0.8rem; font-weight: bold;'>{badge}</span>
                    <h4 style='color: #667eea; margin-top: 0.5rem; min-height: 60px;'>{hotel_name}</h4>
                    <p style='margin: 0.5rem 0;'><strong>💰 Price:</strong> {format_currency(hotel.get('price_per_night', 0))}/night</p>
                    <p style='margin: 0.5rem 0;'><strong>📊 Total:</strong> {format_currency(hotel.get('price_per_night', 0) * state['preferences'].get('duration', 1))}</p>
                    <p style='margin: 0.5rem 0;'><strong>⭐ Rating:</strong> {'⭐' * int(hotel.get('rating', 4))}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Button to select this hotel
            if not is_chosen:
                if st.button(f"Choose Hotel {i+1}", key=f"hotel_{i}", use_container_width=True):
                    st.session_state.state["chosen_hotel"] = hotel
                    # Recalculate cost
                    duration = state['preferences'].get('duration', 7)
                    hotel_cost = hotel.get('price_per_night', 0) * duration
                    flight_cost = chosen_flight.get('price_total', 0)
                    st.session_state.state["total_cost"] = hotel_cost + flight_cost
                    st.rerun()
    
    st.markdown("---")
    st.markdown("### ✈️ Top 3 Flight Options")
    
    # Display flights in 3 columns
    flight_cols = st.columns(3)
    for i, flight in enumerate(selected_flights[:3]):
        with flight_cols[i]:
            is_chosen = (flight.get("airline") == chosen_flight.get("airline"))
            border_color = "#667eea" if is_chosen else "#ddd"
            badge = "✅ Selected" if is_chosen else f"Option {i+1}"
            
            # Get airline name
            airline_name = flight.get('airline', f'Flight Option {i+1}')
            if len(airline_name) > 40:
                airline_name = airline_name[:37] + "..."
            
            st.markdown(f"""
                <div style='background: white; padding: 1.5rem; border-radius: 10px; 
                            border: 3px solid {border_color};
                            box-shadow: 0 4px 15px rgba(0,0,0,0.1); height: 100%;'>
                    <span style='background: {border_color}; color: white; padding: 0.3rem 0.6rem; 
                                 border-radius: 5px; font-size: 0.8rem; font-weight: bold;'>{badge}</span>
                    <h4 style='color: #667eea; margin-top: 0.5rem; min-height: 60px;'>{airline_name}</h4>
                    <p style='margin: 0.5rem 0;'><strong>💰 Price:</strong> {format_currency(flight.get('price_total', 0))}</p>
                    <p style='margin: 0.5rem 0;'><strong>⏱️ Duration:</strong> {flight.get('duration', 'N/A')}</p>
                    <p style='margin: 0.5rem 0;'><strong>🛫 Type:</strong> {flight.get('stops', 'N/A')}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Button to select this flight
            if not is_chosen:
                if st.button(f"Choose Flight {i+1}", key=f"flight_{i}", use_container_width=True):
                    st.session_state.state["chosen_flight"] = flight
                    # Recalculate cost
                    duration = state['preferences'].get('duration', 7)
                    hotel_cost = chosen_hotel.get('price_per_night', 0) * duration
                    flight_cost = flight.get('price_total', 0)
                    st.session_state.state["total_cost"] = hotel_cost + flight_cost
                    st.rerun()
    
    # Total cost display
    total = state.get("total_cost", 0)
    st.markdown(f"""
        <div class='cost-display'>
            💰 Total Estimated Cost: {format_currency(total)}
            <p style='font-size: 0.9rem; margin-top: 0.5rem;'>
                (Hotel: {format_currency(chosen_hotel.get('price_per_night', 0) * state['preferences'].get('duration', 1))} + 
                Flight: {format_currency(chosen_flight.get('price_total', 0))})
            </p>
        </div>
    """, unsafe_allow_html=True)


def render_itinerary(state):
    """Render the generated itinerary"""
    itinerary = state.get("itinerary", "")
    
    if not itinerary:
        return
    
    st.markdown("<div class='center-content'>", unsafe_allow_html=True)
    st.markdown("### 📋 Your Personalized Itinerary")
    
    # Clean and format itinerary
    import re
    
    # Remove excessive symbols and clean text
    clean_itinerary = itinerary.replace("*", "").replace("---", "")
    clean_itinerary = re.sub(r'\*\*', '', clean_itinerary)
    
    # Convert markdown-style headers to HTML
    lines = clean_itinerary.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            formatted_lines.append("<br>")
            continue
            
        # Main headers (all caps or starts with ###)
        if line.isupper() and len(line) > 5:
            formatted_lines.append(f"<h3 style='color: #667eea; margin-top: 1.5rem;'>{line.title()}</h3>")
        # Sub headers (Day X:, HOTEL:, etc.)
        elif line.startswith(('Day ', 'DAY ', 'Hotel:', 'HOTEL:', 'Flight:', 'FLIGHT:', 'Accommodation:', 'ACCOMMODATION:')):
            formatted_lines.append(f"<h4 style='color: #764ba2; margin-top: 1rem;'>{line}</h4>")
        # Bullet points
        elif line.startswith(('-', '•', '*')):
            formatted_lines.append(f"<li>{line[1:].strip()}</li>")
        # Numbered lists
        elif re.match(r'^\d+\.', line):
            formatted_lines.append(f"<li>{line.split('.', 1)[1].strip()}</li>")
        # Regular text
        else:
            formatted_lines.append(f"<p>{line}</p>")
    
    formatted_itinerary = '\n'.join(formatted_lines)
    
    st.markdown(f"""
        <div class='itinerary-container'>
            {formatted_itinerary}
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_additional_features(state):
    """Render buttons for additional features"""
    st.markdown("<div class='center-content'>", unsafe_allow_html=True)
    st.markdown("### 🎁 Enhance Your Plan")
    
    st.markdown("<div class='button-container'>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    features = {}
    
    with col1:
        if st.button("🎯 Activities", use_container_width=True):
            features["activity"] = True
    
    with col2:
        if st.button("🔗 Travel Guides", use_container_width=True):
            features["links"] = True
    
    with col3:
        if st.button("🎒 Packing List", use_container_width=True):
            features["packing"] = True
    
    with col4:
        if st.button("🍽️ Food & Culture", use_container_width=True):
            features["food"] = True
    
    # Export button separately
    if st.button("📄 Export as PDF", use_container_width=True):
        features["export"] = True
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    return features


def render_feature_results(state):
    """Render additional feature results in expanders"""
    if state.get("activity_suggestions"):
        with st.expander("🎯 Activity Suggestions", expanded=True):
            st.markdown(state["activity_suggestions"])
    
    if state.get("useful_links"):
        with st.expander("🔗 Useful Travel Links", expanded=True):
            for link in state["useful_links"]:
                st.markdown(f"**[{link['title']}]({link['link']})**")
                if link.get("snippet"):
                    st.caption(link["snippet"])
                st.markdown("---")
    
    if state.get("packing_list"):
        with st.expander("🎒 Packing List", expanded=True):
            st.markdown(state["packing_list"])
    
    if state.get("food_culture_info"):
        with st.expander("🍽️ Food & Culture Guide", expanded=True):
            st.markdown(state["food_culture_info"])


def render_chat_interface(state):
#     """Render chat interface"""
#     st.markdown("### 💬 Ask About Your Itinerary")
    
#     # Display chat history
#     for chat in state.get("chat_history", []):
#         with st.chat_message("user"):
#             st.markdown(chat["question"])
#         with st.chat_message("assistant"):
#             st.markdown(chat["response"])
    
#     return st.chat_input("Ask me anything about your trip...")
    return None  # Temporarily disable chat interface


def export_to_pdf(state):
    """Export itinerary to PDF"""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Travel Itinerary", ln=True, align='C')
        pdf.ln(5)
        
        # Content
        pdf.set_font("Arial", size=10)
        itinerary_text = state.get("itinerary", "")
        
        for line in itinerary_text.split("\n"):
            line = line.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 5, line)
        
        # Create temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(temp_file.name)
        return temp_file.name
    except Exception as e:
        st.error(f"PDF generation failed: {str(e)}")
        return None


def render_feedback_buttons():
    """Render feedback buttons"""
    st.markdown("<div class='center-content'>", unsafe_allow_html=True)
    st.markdown("### 📢 What's Next?")
    
    st.markdown("<div class='button-container'>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    feedback = None
    
    with col1:
        if st.button("✅ Accept Plan", use_container_width=True):
            feedback = "accept"
    
    with col2:
        if st.button("🏨 Change Hotels", use_container_width=True):
            feedback = "modify_hotels"
    
    with col3:
        if st.button("📅 Change Dates", use_container_width=True):
            feedback = "modify_dates"
    
    with col4:
        if st.button("🌍 New Destination", use_container_width=True):
            feedback = "change_destination"
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    return feedback