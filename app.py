from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Define the URL of your Rasa server
RASA_SERVER_URL = "http://localhost:5005/chat"

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json["message"]
 
    # Send the user message to the Rasa server
    rasa_response = requests.post(RASA_SERVER_URL, json={"message": user_message})

    if rasa_response.status_code == 200:
        rasa_data = rasa_response.json()
        chatbot_response = ""
        for message in rasa_data:
            if "text" in message:
                chatbot_response += message["text"] + "\n"

        return jsonify({"response": chatbot_response})
    else:
        return jsonify({"response": "Chatbot encountered an error."}), 500

if __name__ == '__main__':
    app.run(debug=True)
