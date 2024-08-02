import openai
import requests
from dotenv import load_dotenv
import os
import base64
import streamlit as st

# Load environment variables from .env file
load_dotenv()


# Function to decode Base64 encoded keys
def decode_key(encoded_key):
    decoded_bytes = base64.b64decode(encoded_key.encode('utf-8'))
    return decoded_bytes.decode('utf-8')


# Access API keys from environment variables and decode them
encoded_openai_api_key = os.getenv('ENCODED_OPENAI_API_KEY')
encoded_weather_api_key = os.getenv('ENCODED_WEATHER_API_KEY')
encoded_chatbot_assistant_key = os.getenv('ENCODED_CHATBOT_ASSISTANT_KEY')

# Debug prints to check if environment variables are loaded correctly
print(f"ENCODED_OPENAI_API_KEY: {encoded_openai_api_key}")
print(f"ENCODED_WEATHER_API_KEY: {encoded_weather_api_key}")
print(f"ENCODED_CHATBOT_ASSISTANT_KEY: {encoded_chatbot_assistant_key}")

if not encoded_openai_api_key or not encoded_weather_api_key or not encoded_chatbot_assistant_key:
    raise ValueError("One or more environment variables are missing or not loaded correctly.")

openai.api_key = decode_key(encoded_openai_api_key)
weather_api_key = decode_key(encoded_weather_api_key)
chatbot_assistant_key = decode_key(encoded_chatbot_assistant_key)


# Function to get detailed weather information
def get_weather_details(location, unit='c'):
    weather_api_url = f'http://api.weatherapi.com/v1/forecast.json?key={weather_api_key}&q={location}&days=1&alerts=yes'

    response = requests.get(weather_api_url)
    weather_data = response.json()

    # Extract current weather details
    current = weather_data['current']
    forecast = weather_data['forecast']['forecastday'][0]
    alerts = weather_data.get('alerts', {'alert': []})

    if unit == 'c':
        temperature = current['temp_c']
        unit_symbol = '°C'
    else:
        temperature = current['temp_f']
        unit_symbol = '°F'

    weather_description = current['condition']['text']
    rain_forecast = forecast['day']['daily_chance_of_rain']
    storm_forecast = forecast['day'].get('daily_chance_of_storm', 0)

    # Extract alerts
    alert_messages = [alert['headline'] for alert in alerts['alert']]

    weather_info = {
        "temperature": temperature,
        "unit_symbol": unit_symbol,
        "description": weather_description,
        "rain_forecast": rain_forecast,
        "storm_forecast": storm_forecast,
        "alerts": alert_messages
    }

    return weather_info


# Example OpenAI prompt to create a friendly response
def create_chatbot_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )
    return response.choices[0].message['content']


# Function to get weather icon based on description
def get_weather_icon(description):
    description = description.lower()
    if "rain" in description:
        return "🌧️"
    elif "cloud" in description:
        return "☁️"
    elif "sun" in description or "clear" in description:
        return "☀️"
    elif "snow" in description:
        return "❄️"
    elif "storm" in description or "thunder" in description:
        return "⛈️"
    else:
        return "🌡️"


# Streamlit App
def main():
    st.title("Weather Update App")

    location = st.text_input("Enter the location (e.g., Lahore, Pakistan):")
    unit = st.selectbox("Select the unit:", ["Celsius (C)", "Fahrenheit (F)"])

    unit = 'c' if unit.startswith('C') else 'f'

    if location:
        weather_info = get_weather_details(location, unit)
        icon = get_weather_icon(weather_info["description"])

        st.write(
            f"The current temperature in {location} is {weather_info['temperature']}{weather_info['unit_symbol']} with {weather_info['description']}.")
        st.write(f"Chance of rain: {weather_info['rain_forecast']}%")
        st.write(f"Chance of storm: {weather_info['storm_forecast']}%")
        st.write(icon)

        if weather_info['alerts']:
            st.write("Alerts:")
            for alert in weather_info['alerts']:
                st.write(f"- {alert}")
        else:
            st.write("No severe weather alerts.")


if __name__ == "__main__":
    main()
