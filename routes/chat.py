from flask import Blueprint, request, jsonify
import g4f  # Для общения с GPT-4 через библиотеку g4f

# Создаем Blueprint для чата
chatbot_bp = Blueprint('chatbot', __name__)

# Обработчик сообщений для чата

def chat():
    user_message = request.json.get("message")  # Получаем сообщение от пользователя

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        # Получаем ответ от модели GPT через g4f
        response = g4f.ChatCompletion.create(
            model="gpt-4",  # Используем GPT-4
            messages=[{"role": "user", "content": user_message}]
        )

        # Логируем ответ для отладки
        print(f"Response: {response}")

        # Проверка, чтобы убедиться, что ответ содержит ожидаемую структуру
        if isinstance(response, dict) and 'choices' in response:
            ai_message = response['choices'][0]['message']['content']
        elif isinstance(response, str):
            ai_message = response  # Ответ - это строка
        else:
            return jsonify({"error": "Invalid response format"}), 500

        return jsonify({"response": ai_message})

    except Exception as e:
        print(f"Error: {str(e)}")  # Логируем ошибку
        return jsonify({"error": f"Error: {str(e)}"}), 500

    
chatbot_bp.add_url_rule('/chat', view_func=chat, methods=['POST'])