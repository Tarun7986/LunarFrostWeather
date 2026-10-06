// =========================
// CLOCK
// =========================

function updateClock() {

    const now = new Date();

    let hours = now.getHours();
    let minutes = now.getMinutes();
    let seconds = now.getSeconds();

    hours = String(hours).padStart(2, "0");
    minutes = String(minutes).padStart(2, "0");
    seconds = String(seconds).padStart(2, "0");

    document.getElementById("time").textContent =
        `${hours}:${minutes}:${seconds}`;

    const date = now.toLocaleDateString(
        "en-IN",
        {
            weekday: "long",
            day: "numeric",
            month: "long",
            year: "numeric"
        }
    );

    document.getElementById("date").textContent = date;
}


// =========================
// TIME OF DAY
// =========================

function updateTimeTheme() {

    const hour = new Date().getHours();

    document.body.classList.remove(
        "morning",
        "afternoon",
        "evening",
        "night"
    );

    if (hour >= 5 && hour < 12) {

        document.body.classList.add("morning");

        document.getElementById("timePeriod").textContent =
            "Good Morning";

    }

    else if (hour >= 12 && hour < 17) {

        document.body.classList.add("afternoon");

        document.getElementById("timePeriod").textContent =
            "Afternoon";

    }

    else if (hour >= 17 && hour < 21) {

        document.body.classList.add("evening");

        document.getElementById("timePeriod").textContent =
            "Evening";

    }

    else {

        document.body.classList.add("night");

        document.getElementById("timePeriod").textContent =
            "Night";

    }
}


// =========================
// WEATHER SEARCH
// =========================

async function getWeather() {

    const cityInput =
        document.getElementById("cityInput");

    const city =
        cityInput.value.trim();

    if (!city) {

        document.getElementById("weatherResult").innerHTML = `
            <div class="condition">
                Please enter a city.
            </div>
        `;

        return;
    }

    try {

        const response = await fetch(
            "/forecast",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    city: city
                })
            }
        );

        const data = await response.json();

        if (data.error) {

            document.getElementById("weatherResult").innerHTML = `
                <div class="condition">
                    ${data.error}
                </div>
            `;

            return;
        }

        let condition = "";

        if (data.weather_code === 0) {
            condition = "Clear sky";
        }

        else if (data.weather_code === 1) {
            condition = "Mainly clear";
        }

        else if (data.weather_code === 2) {
            condition = "Partly cloudy";
        }

        else if (data.weather_code === 3) {
            condition = "Overcast";
        }

        else if (
            data.weather_code === 45 ||
            data.weather_code === 48
        ) {
            condition = "Fog";
        }

        else if (
            data.weather_code >= 51 &&
            data.weather_code <= 57
        ) {
            condition = "Drizzle";
        }

        else if (
            data.weather_code >= 61 &&
            data.weather_code <= 67
        ) {
            condition = "Rain";
        }

        else if (
            data.weather_code >= 71 &&
            data.weather_code <= 77
        ) {
            condition = "Snow";
        }

        else if (
            data.weather_code >= 80 &&
            data.weather_code <= 82
        ) {
            condition = "Rain showers";
        }

        else if (
            data.weather_code >= 85 &&
            data.weather_code <= 86
        ) {
            condition = "Snow showers";
        }

        else if (
            data.weather_code >= 95 &&
            data.weather_code <= 99
        ) {
            condition = "Thunderstorm";
        }

        else {
            condition = "Unknown weather";
        }

        document.getElementById("weatherResult").innerHTML = `

            <div class="temperature">
                ${data.temperature}°C
            </div>

            <div class="city-name">
                ${data.city}
            </div>

            <div class="condition">
                ${condition}
            </div>

        `;

    }

    catch (error) {

        document.getElementById("weatherResult").innerHTML = `
            <div class="condition">
                Unable to connect to the weather server.
            </div>
        `;

        console.error(error);
    }
}


// =========================
// SEARCH BUTTON
// =========================

document
    .getElementById("searchButton")
    .addEventListener("click", getWeather);


// =========================
// ENTER KEY
// =========================

document
    .getElementById("cityInput")
    .addEventListener("keydown", function(event) {

        if (event.key === "Enter") {
            getWeather();
        }

    });


// =========================
// START
// =========================

updateClock();
updateTimeTheme();


// Update clock every second
setInterval(updateClock, 1000);


// Update theme every minute
setInterval(updateTimeTheme, 60000);