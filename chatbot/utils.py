import requests
import google.generativeai as genai
from django.conf import settings

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

def get_weather(city):
    """Fetch real-time weather data for a given city with error handling."""
    if not city or city.strip() == "":
        return "Weather information not available (no city provided)"
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={settings.OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=5)  # Add timeout
        
        if response.status_code == 200:
            data = response.json()
            weather_info = (
                f"Current weather in {city}: "
                f"{data['weather'][0]['description']}, "
                f"Temperature: {data['main']['temp']}°C"
            )
            return weather_info
        else:
            return f"Weather information not available for {city}"
            
    except requests.exceptions.RequestException as e:
        print(f"Weather API error: {str(e)}")
        return "Weather information temporarily unavailable"

def chatbot_response(user_query, city):
    """Generate chatbot response with error handling."""
    try:
        # Get weather info with error handling
        weather_info = get_weather(city) if city else "No weather information available"
        
        # Create the prompt with weather info
        system_prompt = """You are a specialized plant care assistant. Only provide responses related to plants, gardening, 
        and plant care. If the query is not about plants, politely inform the user that you can only help with plant-related questions.
        Format your response in a clear, structured way."""

        full_query = f"{system_prompt}User Question: {user_query}Weather Context: {weather_info}"
        
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(full_query)
            
            if response and response.text:
                return format_response(response.text)
            else:
                return format_response("I apologize, but I couldn't generate a response. Please try asking your question again.")
                
        except Exception as e:
            print(f"Gemini API error: {str(e)}")
            return format_response("I'm having trouble processing your request. Please try again in a moment.")
            
    except Exception as e:
        print(f"General error: {str(e)}")
        return format_response("I apologize for the inconvenience. I'm having trouble processing your request.")

def is_plant_related(query):
    """Check if the query is related to plants."""
    plant_keywords = [
        # General plant terms
        'plant', 'garden', 'flower', 'tree', 'seed', 'soil', 'water', 'grow',
        'leaf', 'root', 'prune', 'fertilizer', 'pest', 'sunlight',
        
        # Agricultural terms
        'crop', 'farm', 'field', 'harvest', 'cultivation', 'agriculture',
        'irrigation', 'planting', 'sowing', 'yield',
        
        # Specific crops
        'paddy', 'rice', 'wheat', 'corn', 'maize', 'vegetable',
        'fruit', 'herb', 'grain', 'pulse',
        
        # Farming practices
        'organic', 'fertilize', 'mulch', 'compost', 'tillage',
        'preparation', 'nursery', 'transplant', 'spacing',
        
        # Plant health
        'disease', 'nutrient', 'deficiency', 'growth', 'weed',
        'pesticide', 'herbicide', 'fungicide', 'botanical', 'flora'
    ]
    
    query_words = query.lower().split()
    return any(keyword in query_words or keyword in query.lower() for keyword in plant_keywords)

def format_response(response):
    """Format the response in a clear, structured, and formal way with proper headings."""
    
    sections = response.split('**')
    formatted_output = []
    
    for i, section in enumerate(sections):
        if i == 0:  # Skip empty first split
            continue
            
        if i % 2 == 1:  # Section headers
            header = section.strip().upper()
            formatted_output.append(f"{header} ")  # Clearly marked headings
        else:  # Section content
            lines = section.strip()
            for line in lines:
                line = line.strip()
                if line:
                    if line.startswith('*'):
                        formatted_output.append(f"- {line[1:].strip()}")  # Bullet points
                    elif line[0].isdigit() and line[1] == '.':
                        formatted_output.append(f"{line}")  # Numbered points
                    else:
                        formatted_output.append(line)  # General text
    
    return "\n".join(formatted_output)
