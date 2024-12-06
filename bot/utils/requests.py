import requests

FAST_API_URL = "http://84.201.145.135:8000/"
headers = {
    'accept': 'application/json',
}


async def is_newbie(tg_id: str) -> bool:
    response = requests.get(f"{FAST_API_URL}users/is_newbie/{tg_id}", headers=headers)
    answer = response.json()
    return answer["is_newbie"]
