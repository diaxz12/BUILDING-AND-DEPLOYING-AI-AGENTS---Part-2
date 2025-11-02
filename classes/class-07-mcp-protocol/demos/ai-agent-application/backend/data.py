"""Shared sample data used by the travel planner demo."""

SAMPLE_LISTINGS = {
    "paris": [
        {"name": "Left Bank Loft", "price": 180, "address": "5 Rue du Sabot", "distance_city_center_km": 1.2},
        {"name": "Montmartre Artist Studio", "price": 140, "address": "12 Rue Gabrielle", "distance_city_center_km": 2.4},
    ],
    "tokyo": [
        {"name": "Shinjuku Skyline Apartment", "price": 210, "address": "1-2-3 Nishishinjuku", "distance_city_center_km": 0.9},
        {"name": "Asakusa Riverside Flat", "price": 120, "address": "8-4-1 Asakusa", "distance_city_center_km": 3.1},
    ],
    "lisbon": [
        {"name": "Alfama View Loft", "price": 110, "address": "Rua de São Tomé 28", "distance_city_center_km": 0.8},
        {"name": "LX Factory Studio", "price": 130, "address": "Rua Rodrigues de Faria 103", "distance_city_center_km": 3.5},
    ],
}

SAMPLE_ATTRACTIONS = {
    "paris": [
        {"name": "Louvre Museum", "neighborhood": "1st arrondissement", "open": "09:00-18:00", "tip": "Book timed tickets online."},
        {"name": "Eiffel Tower", "neighborhood": "7th arrondissement", "open": "09:30-23:45", "tip": "Sunset slots give great views."},
    ],
    "tokyo": [
        {"name": "Senso-ji Temple", "neighborhood": "Asakusa", "open": "Always open", "tip": "Arrive before 9 AM to beat crowds."},
        {"name": "TeamLab Planets", "neighborhood": "Toyosu", "open": "09:00-21:00", "tip": "Wear shorts—part of the exhibit is ankle deep in water."},
    ],
    "lisbon": [
        {"name": "Belém Tower", "neighborhood": "Belém", "open": "10:00-18:30", "tip": "Combine with a visit to the Discoveries Monument."},
        {"name": "Tram 28 Ride", "neighborhood": "Graca to Baixa", "open": "06:00-22:30", "tip": "Start early to secure a seat."},
    ],
}
