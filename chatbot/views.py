from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import google.generativeai as genai

# Configure logging
logger = logging.getLogger(__name__)

# Set your Gemini API Key
API_KEY = "AIzaSyCcsCxuyWsgL8aaUGCUQC9GQfB9MTPGWHY"

# Configure the Generative AI client
genai.configure(api_key=API_KEY)

# Define a system prompt to format responses
SYSTEM_PROMPT = """You are a helpful Plant Care Assistant. Format your responses in a clear, structured way:

1. Use bullet points for lists
2. Use bold for important terms
3. Separate paragraphs clearly
4. Keep responses concise and focused
5. Use markdown formatting:
   - **bold** for emphasis
   - • for bullet points
   - Add line breaks between sections

Always maintain a friendly, professional tone."""

@csrf_exempt
def chatbot_response(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')

        if not user_message:
            return JsonResponse({'error': 'No message provided'}, status=400)

        try:
            # Create the model
            model = genai.GenerativeModel("gemini-pro")

            # Combine system prompt with user message
            formatted_prompt = f"{SYSTEM_PROMPT}\n\nUser Question: {user_message}"

            # Generate content
            response = model.generate_content(formatted_prompt)

            # Format the response with markdown
            ai_message = response.text.replace('•', '&bull;')  # Convert bullets to HTML entities
            
            logger.info(f"Generated response for: {user_message}")
            return JsonResponse({'response': ai_message})

        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return JsonResponse({
                'response': "I apologize, but I'm having trouble processing your request right now. Please try again."
            }, status=200)  # Return 200 to show error in chat instead of failing

    return JsonResponse({'error': 'Invalid request method'}, status=400)
