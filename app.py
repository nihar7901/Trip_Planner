"""
AI Travel Planner - Main Application
"""
import streamlit as st
from langgraph.graph import StateGraph, END
from state import GraphState, create_initial_state
from nodes import (
    fetch_weather_node,
    analyze_weather_node,
    suggest_alternates_node,
    search_hotels_node,
    search_flights_node,
    budget_filter_node,
    preference_ranking_node,
    generate_itinerary_node,
    activity_suggestions_node,
    packing_list_node,
    food_culture_node,
    fetch_useful_links_node,
    chat_node
)
from ui_components import (
    apply_custom_css,
    render_header,
    render_progress_tracker,
    render_input_form,
    render_weather_section,
    render_alternate_destinations,
    render_selected_options,
    render_itinerary,
    render_additional_features,
    render_feature_results,
    render_chat_interface,
    render_feedback_buttons,
    export_to_pdf
)
from config import STREAMLIT_PAGE_TITLE, STREAMLIT_LAYOUT, STREAMLIT_ICON

# ============ LangGraph Workflow Setup ============

def route_after_weather_decision(state: GraphState) -> str:
    """Route based on weather favorability"""
    if state["weather_favorable"]:
        return "search_hotels"
    else:
        return "suggest_alternates"


def route_after_alternates(state: GraphState) -> str:
    """Route based on user selection of alternates"""
    # For now, continue to hotel search regardless
    # In a full implementation, you'd wait for user input here
    return "search_hotels"


def build_workflow() -> StateGraph:
    """Build the LangGraph workflow"""
    workflow = StateGraph(GraphState)
    
    # Add all nodes
    workflow.add_node("fetch_weather", fetch_weather_node)
    workflow.add_node("analyze_weather", analyze_weather_node)
    workflow.add_node("suggest_alternates", suggest_alternates_node)
    workflow.add_node("search_hotels", search_hotels_node)
    workflow.add_node("search_flights", search_flights_node)
    workflow.add_node("budget_filter", budget_filter_node)
    workflow.add_node("preference_ranking", preference_ranking_node)
    workflow.add_node("generate_itinerary", generate_itinerary_node)
    
    # Set entry point
    workflow.set_entry_point("fetch_weather")
    
    # Define edges
    workflow.add_edge("fetch_weather", "analyze_weather")
    
    # Conditional routing after weather analysis
    workflow.add_conditional_edges(
        "analyze_weather",
        route_after_weather_decision,
        {
            "search_hotels": "search_hotels",
            "suggest_alternates": "suggest_alternates"
        }
    )
    
    # From alternates back to hotel search
    workflow.add_edge("suggest_alternates", "search_hotels")
    
    # Sequential flow for search and filtering
    workflow.add_edge("search_hotels", "search_flights")
    workflow.add_edge("search_flights", "budget_filter")
    workflow.add_edge("budget_filter", "preference_ranking")
    workflow.add_edge("preference_ranking", "generate_itinerary")
    workflow.add_edge("generate_itinerary", END)
    
    return workflow.compile()


# ============ Initialize App ============

st.set_page_config(
    page_title=STREAMLIT_PAGE_TITLE,
    page_icon=STREAMLIT_ICON,
    layout=STREAMLIT_LAYOUT
)

# Apply custom CSS
apply_custom_css()

# Initialize session state
if "state" not in st.session_state:
    st.session_state.state = create_initial_state()
    st.session_state.graph = build_workflow()
    st.session_state.workflow_running = False

# ============ Main App Layout ============

# Header
render_header()

# Input Form (always visible at top)
preferences = render_input_form()

# Handle form submission
if preferences:
    # Reset state and start new planning
    st.session_state.state = create_initial_state()
    st.session_state.state["preferences"] = preferences
    st.session_state.workflow_running = True
    
    # Run the workflow
    with st.spinner("🔮 Planning your perfect trip..."):
        try:
            result = st.session_state.graph.invoke(st.session_state.state)
            st.session_state.state.update(result)
            st.session_state.workflow_running = False
            
            if result.get("itinerary"):
                st.success("✨ Your itinerary is ready!")
                st.balloons()
            else:
                st.error("❌ Failed to generate itinerary. Please try again.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.session_state.workflow_running = False

# ============ Display Results ============

state = st.session_state.state

# Show progress tracker if workflow is running or completed
if state.get("node_logs") or st.session_state.workflow_running:
    render_progress_tracker(state)

# Display weather information
if state.get("weather_analysis"):
    st.markdown("---")
    render_weather_section(state)
    
    # Show alternates if weather is bad
    if not state.get("weather_favorable") and state.get("alternate_destinations"):
        render_alternate_destinations(state)

# Display selected options and itinerary
if state.get("itinerary"):
    st.markdown("---")
    
    # Selected hotel and flight options (centered)
    render_selected_options(state)
    
    st.markdown("---")
    
    # Main itinerary (centered)
    render_itinerary(state)
    
    st.markdown("---")
    
    # Additional features buttons (centered)
    feature_actions = render_additional_features(state)
        
    # Handle feature button clicks
    if feature_actions.get("activity"):
        with st.spinner("Fetching activity suggestions..."):
            result = activity_suggestions_node(state)
            st.session_state.state.update(result)
            st.rerun()
    
    if feature_actions.get("links"):
        with st.spinner("Fetching travel guides..."):
            result = fetch_useful_links_node(state)
            st.session_state.state.update(result)
            st.rerun()
    
    if feature_actions.get("packing"):
        with st.spinner("Generating packing list..."):
            result = packing_list_node(state)
            st.session_state.state.update(result)
            st.rerun()
    
    if feature_actions.get("food"):
        with st.spinner("Fetching food & culture info..."):
            result = food_culture_node(state)
            st.session_state.state.update(result)
            st.rerun()
    
    if feature_actions.get("export"):
        pdf_path = export_to_pdf(state)
        if pdf_path:
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "📥 Download PDF",
                    f,
                    file_name="travel_itinerary.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    
    # Display feature results
    render_feature_results(state)
    
    st.markdown("---")
    
    # Feedback buttons (centered)
    feedback = render_feedback_buttons()
    
    if feedback:
        if feedback == "accept":
            st.success("🎉 Great! Have an amazing trip!")
            st.balloons()
        elif feedback == "modify_hotels":
            st.info("🔄 Searching for different hotels...")
            with st.spinner("Finding alternatives..."):
                # Re-run hotel search and ranking
                result1 = search_hotels_node(state)
                st.session_state.state.update(result1)
                result2 = budget_filter_node(st.session_state.state)
                st.session_state.state.update(result2)
                result3 = preference_ranking_node(st.session_state.state)
                st.session_state.state.update(result3)
                result4 = generate_itinerary_node(st.session_state.state)
                st.session_state.state.update(result4)
                st.rerun()
        elif feedback == "modify_dates":
            st.info("📅 Please modify dates in the form above and regenerate.")
        elif feedback == "change_destination":
            st.info("🌍 Please enter a new destination in the form above.")
    
    # CHAT INTERFACE - COMMENTED OUT
    # with col_chat:
    #     # Chat interface
    #     user_input = render_chat_interface(state)
    #     
    #     if user_input:
    #         st.session_state.state["user_question"] = user_input
    #         with st.spinner("Thinking..."):
    #             result = chat_node(st.session_state.state)
    #             st.session_state.state.update(result)
    #             st.rerun()

# ============ Sidebar - Info & Stats ============

with st.sidebar:
    st.markdown("### 📊 Trip Summary")
    
    if state.get("preferences"):
        prefs = state["preferences"]
        st.markdown(f"""
        **Destination:** {prefs.get('destination', 'N/A')}  
        **Duration:** {prefs.get('duration', 0)} days  
        **Type:** {prefs.get('holiday_type', 'N/A')}  
        **Budget:** {prefs.get('budget_type', 'N/A')}  
        **People:** {prefs.get('num_people', 'N/A')}
        """)
        
        if state.get("total_cost"):
            from utils import format_currency
            st.markdown(f"**Total Cost:** {format_currency(state['total_cost'])}")
        
        # Show chosen hotel and flight
        if state.get("chosen_hotel"):
            st.markdown("---")
            st.markdown("**✅ Chosen Hotel:**")
            st.markdown(f"_{state['chosen_hotel'].get('name', 'N/A')[:30]}_")
        
        if state.get("chosen_flight"):
            st.markdown("**✅ Chosen Flight:**")
            st.markdown(f"_{state['chosen_flight'].get('airline', 'N/A')}_")
    
    st.markdown("---")
    
    st.markdown("### ℹ️ About")
    st.markdown("""
    This AI Travel Planner uses:
    - 🤖 **Gemini 2.5 Flash** for intelligent planning
    - 🌤️ **OpenWeather API** for weather forecasts
    - 🔍 **SerpAPI** for hotel & flight search
    - 🗺️ **LangGraph** for workflow orchestration
    
    Features:
    - ✅ Real-time weather analysis
    - ✅ Budget-based filtering
    - ✅ Personalized recommendations
    - ✅ Interactive chat assistant
    - ✅ Alternate destination suggestions
    """)
    
    # Debug info (optional, can be removed)
    if st.checkbox("Show Debug Info"):
        st.markdown("### 🐛 Debug")
        st.json({
            "nodes_executed": len(state.get("node_logs", [])),
            "errors": len(state.get("errors", [])),
            "warnings": len(state.get("warnings", [])),
            "workflow_status": state.get("workflow_status", "unknown")
        })
        
        if state.get("errors"):
            st.error("Errors:")
            for error in state["errors"]:
                st.text(error)
        
        if state.get("warnings"):
            st.warning("Warnings:")
            for warning in state["warnings"]:
                st.text(warning)

# ============ Footer ============

st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: Black; padding: 2rem;'>
        <p style='font-size: 1.2rem; font-weight: 600;'>Hope you got the information you needed! ✨</p>
    </div>
""", unsafe_allow_html=True)