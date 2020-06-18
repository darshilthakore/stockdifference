import requests

def apicalls(url):
    headers = {'user-agent': 'Python script'}
    resp = requests.get(url, headers=headers).json()

    return resp