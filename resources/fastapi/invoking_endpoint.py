import requests

response = requests.get(
"https://api.open-meteo.com/v1/forecast?latitude=40.4&longitude=-3.7&current_weather=true"
)

print(response.json())

