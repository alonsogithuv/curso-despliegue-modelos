import requests

url = "http://127.0.0.1:8000"

r = requests.get(f"{url}/")
print(r.json())

paciente = {
  "sbp": 160,
  "Tabaco": 12,
  "ldl": 5.73,
  "Adiposidad": 23.11,
  "Familia": "Presente",
  "Tipo": 49,
  "Obesidad": 25.3,
  "Alcohol": 97.2,
  "Edad": 52
}

r = requests.post(f"{url}/predecir", json=paciente)
print(r.json())

