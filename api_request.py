import requests

def call_api():
    url = "https://api.example.com/your/endpoint"
    response = requests.get(url)

    if response.status_code == 200:
        print("GET request was successful.")
        print("Response data:", response.json())
    else:
        print(f"GET request failed with status code {response.status_code}.")

if __name__ == "__main__":
    call_api()
