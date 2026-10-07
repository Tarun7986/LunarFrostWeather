
import time
import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


session = requests.Session()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/forecast', methods=['POST'])
def get_weather():

    start = time.time()

    request_data = request.get_json(silent=True) or {}
    city = request_data.get("city")

    if not isinstance(city, str) or not city.strip():
        return jsonify({"error": "City is required"}), 400


    # --------------------------------
    # CITY → LATITUDE / LONGITUDE
    # --------------------------------

    cities = {
        "delhi": (28.6139, 77.2090),
        "new delhi": (28.6139, 77.2090),
        "agra": (27.1767, 78.0081),
        "mumbai": (19.0760, 72.8777),
        "bangalore": (12.9716, 77.5946),
        "bengaluru": (12.9716, 77.5946),
        "kolkata": (22.5726, 88.3639),
        "chennai": (13.0827, 80.2707),
        "hyderabad": (17.3850, 78.4867),
        "jaipur": (26.9124, 75.7873),
        "lucknow": (26.8467, 80.9462),
        "kanpur": (26.4499, 80.3319),
        "pune": (18.5204, 73.8567),
        "ahmedabad": (23.0225, 72.5714),
        "ghaziabad": (28.6692, 77.4538),
        "noida": (28.5355, 77.3910)
    }

    city_key = city.strip().lower()

    if city_key in cities:

        latitude, longitude = cities[city_key]

        print("CITY LOOKUP:", time.time() - start, "seconds")

    else:

        # --------------------------------
        # FALLBACK GEOCODING
        # --------------------------------

        url = "https://nominatim.openstreetmap.org/search"

        params = {
            "q": city,
            "format": "json",
            "limit": 1
        }

        headers = {
            "User-Agent": "lunar-frost-weather-app/1.0"
        }

        try:

            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=5
            )

            response.raise_for_status()

            data = response.json()

            if not data:
                return jsonify({
                    "error": f"City not found: {city}"
                }), 404

            latitude = float(data[0]["lat"])
            longitude = float(data[0]["lon"])

            print("CITY LOOKUP:", time.time() - start, "seconds")

        except requests.exceptions.RequestException as err:

            return jsonify({
                "error": f"Geocoding error: {err}"
            }), 500


    # --------------------------------
    # LATITUDE / LONGITUDE → WEATHER
    # --------------------------------

    # WEATHER API

    try:

        # API 1 — Open-Meteo
        weather_url = "https://api.open-meteo.com/v1/forecast"

        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,weather_code",
            "timezone": "auto"
        }

        weather_response = requests.get(
            weather_url,
            params=weather_params,
            timeout=5,
            proxies={
                "http": None,
                "https": None
            }
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()

        temperature = weather_data["current"].get("temperature_2m")
        weather_code = weather_data["current"].get("weather_code")

        weather_descriptions = {
            0: "clear sky",
            1: "mainly clear",
            2: "partly cloudy",
            3: "overcast",
            45: "fog",
            48: "depositing rime fog",
            51: "light drizzle",
            53: "moderate drizzle",
            55: "dense drizzle",
            56: "light freezing drizzle",
            57: "dense freezing drizzle",
            61: "slight rain",
            63: "moderate rain",
            65: "heavy rain",
            66: "light freezing rain",
            67: "heavy freezing rain",
            71: "slight snow fall",
            73: "moderate snow fall",
            75: "heavy snow fall",
            77: "snow grains",
            80: "slight rain showers",
            81: "moderate rain showers",
            82: "violent rain showers",
            85: "slight snow showers",
            86: "heavy snow showers",
            95: "thunderstorm",
            96: "thunderstorm with slight hail",
            99: "thunderstorm with heavy hail"
        }

        if temperature is None or weather_code is None:
            raise requests.exceptions.RequestException(
                "Temperature or weather code not found"
            )

        description = weather_descriptions.get(
            weather_code,
            "unknown weather condition"
        )

        return jsonify({
            "city": city,
            "temperature": temperature,
            "weather_code": weather_code,
            "description": description
        })

    except (
        requests.exceptions.RequestException,
        KeyError,
        TypeError,
        ValueError
    ) as err:

        print("Open-Meteo failed:", err)

        # API 2 — wttr.in
        try:

            fallback_url = f"https://wttr.in/{latitude},{longitude}"

            fallback_response = requests.get(
                fallback_url,
                params={"format": "j1"},
                headers={
                    "User-Agent": "lunar-frost-weather-app/1.0"
                },
                timeout=2
            )

            fallback_response.raise_for_status()

            fallback_data = fallback_response.json()

            temperature = float(
                fallback_data["current_condition"][0]["temp_C"]
            )

            description = (
                fallback_data["current_condition"][0]
                ["weatherDesc"][0]["value"]
            )

            return jsonify({
                "city": city,
                "temperature": temperature,
                "weather_code": 0,
                "description": description
            })

        except (
            requests.exceptions.RequestException,
            KeyError,
            TypeError,
            ValueError
        ) as err2:

            print("wttr.in failed:", err2)

            # API 3 — WeatherAPI
            try:

                weatherapi_url = (
                    "https://api.weatherapi.com/v1/current.json"
                )

                weatherapi_params = {
                    "key": os.getenv("WEATHERAPI_KEY"),
                    "q": f"{latitude},{longitude}",
                    "aqi": "no"
                }

                weatherapi_response = requests.get(
                    weatherapi_url,
                    params=weatherapi_params,
                    timeout=2
                )

                weatherapi_response.raise_for_status()

                weatherapi_data = weatherapi_response.json()

                temperature = weatherapi_data["current"]["temp_c"]

                description = (
                    weatherapi_data["current"]
                    ["condition"]["text"]
                )

                return jsonify({
                    "city": city,
                    "temperature": temperature,
                    "weather_code": 0,
                    "description": description
                })

            except (
                requests.exceptions.RequestException,
                KeyError,
                TypeError,
                ValueError
            ) as err3:

                print("WeatherAPI failed:", err3)

                return jsonify({
                    "error": "Weather services are currently unavailable."
                }), 503


if __name__ == '__main__':
    app.run(debug=True)
