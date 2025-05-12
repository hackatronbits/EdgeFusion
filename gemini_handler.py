import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure the API key from the environment variable
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize the model and chat instance
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat(history=[])

# Function to get response from Gemini model
def get_gemini_response(prompt):
    try:
        # Send the message to Gemini API and get the response
        response = chat.send_message(prompt, stream=False)
        
        # Check if the response contains text and return it
        if response.text:
            return response.text
        else:
            return "No response text received from Gemini."

    except Exception as e:
        # Log the error and provide a more detailed message
        error_message = f"Error while calling Gemini API: {str(e)}"
        print(error_message)  # Optional: you can log this to a file instead of print
        return error_message
