import requests

word = "encapsulation"
url = f"https://freedictionaryapi.com/api/v1/entries/en/{word}"
resp = requests.get(url, timeout=5)
print(resp.status_code, resp.text)