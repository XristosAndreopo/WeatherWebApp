WeatherWebApp
=============

A modern Django application delivering rich weather insights with:

*   **Dashboard**: Daily forecast cards and rotating weather‑inspired quotes
    
*   **Interactive Map**: Search any location, draggable marker, daily/hourly forecasts
    
*   **Find by Location**: Ad‑hoc city search with day‑slider and hourly chart
    
*   **Favorites**: Save and view your favorite locations with two‑day snapshots
    
*   **User Settings**: Default city/country, units (°C/°F), and visual themes
    

🚀 Features
-----------

*   **5‑Day Forecast** via OpenWeatherMap API
    
*   **Hourly Chart** for next 24 hrs powered by Chart.js
    
*   **Interactive Leaflet Map** with geolocation, click & drag support
    
*   **User Authentication** (login/logout/profile)
    
*   **Persistent Preferences** stored per user (default city, units, theme)
    
*   **Multiple Themes**: Light, Light‑Dark, Dracula, Sepia, High‑Contrast
    
*   **Responsive UI** built on Bootstrap 5
    

🛠 Tech Stack
-------------

*   **Backend**: Python 3.10+, Django 5.2
    
*   **Frontend**: Bootstrap 5, Leaflet.js, Chart.js, vanilla ES modules
    
*   **Data**: OpenWeatherMap API
    
*   **Database**: SQLite (dev), switchable to PostgreSQL
    
*   **Testing**: Django TestCase & RequestFactory
    
*   **Env Management**: python‑dotenv
    

📋 Prerequisites
----------------

*   Python 3.10+
    
*   Git
    
*   OpenWeatherMap API key (free at [https://openweathermap.org/api](https://openweathermap.org/api))
    

⚙️ Installation
---------------

1.  **Clone the repository**  
    ```bash
    git clone https://github.com/XristosAndreopo/WeatherWebApp.gitcd WeatherWebApp

2.  **Create & activate a virtual environment**  
    ```bash
    python -m venv .venv
    # macOS/Linux
    source .venv/bin/activate
    # Windows(PowerShell)
    .venv\\Scripts\\activate
    
3.  **Install dependencies**  
    ```bash
    pip install -r requirements.txt

4.  **Create a .env file in the project root (next to manage.py):** 
    DJANGO_SECRET_KEY=your-django-secret-key</br>
    DJANGO_DEBUG=True</br>
    DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost</br>
    OPENWEATHER_API_KEY=your-openweathermap-key</br>


🗄️ Database Setup
---------------

1. **Set up the database**
    ```bash
     cd weatherapp
     python manage.py makemigrations
     python manage.py migrate

2. **Create Superuser**
     ```bash
     python manage.py createsuperuser


🚧 Running the Development Server
---------------
1. **Run locally**
    ```bash
    cd weatherapp
    python manage.py runserver

Visit http://127.0.0.1:8000/ in your browser.


📂 Project Structure
--------------------


```text
WeatherWebApp/
├── config/
│   ├── settings.py           # Project settings & .env loading
│   ├── urls.py               # Root URL configuration
│   └── context_processors.py # Inject default_city & default_country
├── weather/
│   ├── migrations/
│   ├── models.py             # FavoriteLocation & Preference
│   ├── views.py              # Class-based & function views
│   ├── services.py           # OpenWeatherMap client wrapper
│   ├── utils.py              # Forecast parsing & preferences helper
│   ├── constants.py          # Icon mapping & API URL constants
│   ├── forms.py              # Location search form
│   ├── urls.py               # App URL patterns
│   └── templates/weather/    # App-specific templates
├── static/
│   ├── css/                  # theme.css
│   ├── js/                   # dashboard.js, map.js, find.js, theme.js
│   └── img/weather_icons/    # Local weather icons
├── templates/
│   └── base.html             # Global base template
├── tests/
│   └── test_context_processors.py
├── .env.example              # Example environment file
├── requirements.txt          # Python dependencies
├── manage.py
└── README.md
```
🤝 Contributing
---------------
```text
1.  Fork the repo
    
2.  git checkout -b feature/YourFeature
    
3.  git commit -m "Add feature XYZ"
    
4.  Push and open a Pull Request.
```    

_Please include tests and update documentation for new functionality._


📄 License
----------

This project is licensed under the MIT License.


📬 Contact
----------

**Christos Andreopoulos**

*   Email: xristos.andreopo@gmail.com
    
*   GitHub: [https://github.com/XristosAndreopo](https://github.com/XristosAndreopo)
    
*   LinkedIn: [https://www.linkedin.com/in/christos-andreopoulos-3b6302372/](https://www.linkedin.com/in/christos-andreopoulos-3b6302372/)
