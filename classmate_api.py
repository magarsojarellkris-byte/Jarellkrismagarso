import requests

score = input("Enter your score: ")

url = "https://janinepagmanoja.onrender.com/grade"
params = {"score": score}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    print("Score:", data["score"])
    print("Remark:", data["remark"])
else:
    print("Request failed.")
    print("Status Code:", response.status_code)
    print(response.text)