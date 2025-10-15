# 🌍 AI Travel Planner

An intelligent trip planning system powered by **Gemini 2.5 Flash**, **LangGraph**, and **Streamlit**. This application autonomously plans, evaluates, and optimizes travel options based on real-time weather data, budget constraints, and user preferences.

## ✨ Features

### Core Functionality
- 🤖 **AI-Powered Itinerary Generation** - Personalized day-wise travel plans
- 🌤️ **Real-Time Weather Analysis** - Smart decision-making based on weather forecasts
- 🏨 **Hotel Search & Filtering** - Budget-appropriate accommodations
- ✈️ **Flight Search** - Round-trip flight options with pricing
- 💰 **Budget Management** - INR-based filtering and cost estimation
- 🔄 **Alternate Destinations** - Suggestions when weather is unfavorable

### Additional Features
- 🎯 **Activity Recommendations** - Unique local experiences
- 🎒 **Smart Packing Lists** - Weather and activity-based suggestions
- 🍽️ **Food & Culture Guide** - Local cuisine and etiquette tips
- 🔗 **Travel Resources** - Curated links to guides and tips
- 💬 **Interactive Chat** - Ask questions about your itinerary
- 📄 **PDF Export** - Download your complete travel plan

### Intelligent Workflow
- **LangGraph Orchestration** - Sequential decision-making with conditional routing
- **Weather-Based Routing** - Automatic alternate suggestions for bad weather
- **Budget Filtering** - Smart filtering based on Indian budget ranges
- **Preference Ranking** - AI-powered ranking of options
- **Replanning Capability** - Modify hotels, dates, or destinations dynamically

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI                         │
├─────────────────────────────────────────────────────────┤
│                    LangGraph Workflow                   │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐       │
│  │Weather│→│Decision│→│Search│→│Filter│→│Itinerary│     │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘       │
├─────────────────────────────────────────────────────────┤
│              External APIs                              │
│  • OpenWeatherMap  • SerpAPI  • Gemini                  │
└─────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
trip-planner/
├── app.py                  # Main Streamlit application
├── config.py              # Configuration and constants
├── state.py               # State management schema
├── nodes.py               # LangGraph nodes
├── utils.py               # API calls and helpers
├── ui_components.py       # Streamlit UI components
├── requirements.txt       # Dependencies
├── .env                   # API keys (create this)
└── README.md             # This file
```

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone <repo-url>
cd trip-planner
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up API Keys

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
SERPAPI_API_KEY=your_serpapi_key_here
```

#### Get Your API Keys:

1. **Google Gemini API Key**
   - Visit: https://makersuite.google.com/app/apikey
   - Sign in with Google account
   - Create a new API key
   - Copy and paste into `.env`

2. **OpenWeatherMap API Key**
   - Visit: https://openweathermap.org/api
   - Sign up for free account
   - Go to API keys section
   - Copy your API key

3. **SerpAPI Key**
   - Visit: https://serpapi.com/
   - Sign up for free account (100 searches/month)
   - Find your API key in dashboard
   - Copy and paste into `.env`

### 4. Run the Application
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### Planning a Trip

1. **Fill the Form**
   - Enter destination (e.g., "Goa", "Manali")
   - Select departure city
   - Choose travel dates
   - Specify number of people
   - Pick holiday type (Beach, Adventure, etc.)
   - Select budget type (Budget, Mid-Range, Luxury)
   - Add any special requests

2. **Generate Itinerary**
   - Click "Generate My Itinerary"
   - Watch the progress tracker
   - Review weather analysis
   - Check selected hotel and flight options
   - Read the detailed day-wise itinerary

3. **Enhance Your Plan**
   - Click "Activities" for unique local experiences
   - Get "Travel Guides" for additional resources
   - Generate a "Packing List" based on weather
   - Explore "Food & Culture" information
   - "Export PDF" to download your itinerary

4. **Chat & Modify**
   - Ask questions in the chat interface
   - Use feedback buttons to:
     - Accept the plan
     - Change hotels
     - Modify dates
     - Pick a new destination

## 🎨 UI Features

### Visual Design
- **Gradient backgrounds** with glassmorphism effects
- **Color-coded weather cards** (green = good, yellow = ok, gray = poor)
- **Interactive buttons** with hover effects
- **Responsive layout** for different screen sizes
- **Smooth animations** and transitions

### User Experience
- **Progress tracking** shows workflow execution
- **Real-time updates** as data is fetched
- **Collapsible sections** for additional information
- **Chat history** preserved during session
- **Error handling** with user-friendly messages

## 🔧 Configuration

### Budget Ranges (INR)

Edit in `config.py`:

```python
BUDGET_RANGES = {
    "Backpacker": {
        "hotel_per_night": (500, 1500),
        "flight_total": (3000, 8000),
    },
    "Budget": {
        "hotel_per_night": (1500, 4000),
        "flight_total": (8000, 15000),
    },
    # ... customize as needed
}
```

### Weather Thresholds

```python
WEATHER_FAVORABLE_THRESHOLD = 65  # Score out of 100
WEATHER_RAIN_THRESHOLD = 60       # Rain probability %
```

## 🧪 Testing

### Test the Workflow

1. **Test Weather Decision**
   - Try destinations with different weather patterns
   - Verify alternate suggestions appear when weather is poor

2. **Test Budget Filtering**
   - Use different budget types
   - Check if results match expected price ranges

3. **Test Replanning**
   - Click "Change Hotels" button
   - Verify new hotels are suggested

4. **Test Chat**
   - Ask specific questions about itinerary
   - Check if responses are contextual

## 🐛 Troubleshooting

### Common Issues

1. **API Key Errors**
   ```
   Solution: Check .env file exists and keys are correct
   ```

2. **No Results Found**
   ```
   Solution: Try popular destinations like "Goa" or "Delhi"
   SerpAPI has rate limits (100 searches/month on free tier)
   ```

3. **Weather Data Unavailable**
   ```
   Solution: System will continue with neutral weather assumption
   Check OpenWeatherMap API key is valid
   ```

4. **PDF Export Fails**
   ```
   Solution: Some special characters may not export
   The itinerary is still viewable in the app
   ```

## 📊 Technology Stack

- **Frontend**: Streamlit 1.29.0
- **LLM**: Google Gemini 2.5 Flash
- **Workflow**: LangGraph 0.0.26
- **APIs**: 
  - OpenWeatherMap (Weather forecasts)
  - SerpAPI (Hotel & flight search via Google Hotels/Flights)
- **PDF Generation**: FPDF 1.7.2

## 🎯 Project Goals

This project demonstrates:
- ✅ Autonomous multi-step decision-making
- ✅ Real-time API integration
- ✅ Conditional workflow routing
- ✅ State management across complex workflows
- ✅ User interaction and feedback loops
- ✅ Professional UI/UX design

## 🚀 Future Enhancements

- [ ] Add LangSmith integration for monitoring
- [ ] Implement multi-destination trips
- [ ] Add Google Maps integration
- [ ] Voice input/output support
- [ ] User preference memory (embeddings)
- [ ] Social sharing features
- [ ] Mobile-responsive improvements
- [ ] Multi-language support


Built with ❤️ using LangChain, LangGraph & Streamlit

