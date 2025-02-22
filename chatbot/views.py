from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import chatbot_response

@csrf_exempt
def chatbot_view(request):
    if request.method == 'POST':
        try:
            user_query = request.POST.get('query', '')
            city = request.POST.get('city', '')
            
            if not user_query:
                return JsonResponse({
                    'response': "Please ask me a question about plants!"
                })
                
            bot_reply = chatbot_response(user_query, city)
            return JsonResponse({'response': bot_reply})
            
        except Exception as e:
            print(f"View error: {str(e)}")
            return JsonResponse({
                'response': "I apologize, but I'm having trouble processing your request. Please try again."
            }, status=500)
            
    return JsonResponse({
        'response': "Please use POST method to communicate with the chatbot."
    }, status=405)
