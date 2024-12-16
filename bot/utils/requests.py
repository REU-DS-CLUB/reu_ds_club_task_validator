import requests
from typing import NamedTuple


class User(NamedTuple):
    tg_id: str
    username: str
    auth_timestamp: str
    assignments: list


class Task(NamedTuple):
    task_name: str
    task_status: str
    task_description: str
    task_type: str
    task_data: str
    requirements: str
    task_data_admin: str
    check_solution_file: str
    task_id: int


class Assignments(NamedTuple):
    task_id: int
    tg_id: str
    mark: int
    status: str
    error_message: str
    assignment_file: str
    timestamp: str


FAST_API_URL = "http://app:8000"
headers = {
    'accept': 'application/json',
}


async def is_newbie(tg_id: str) -> bool:
    response = requests.get(f"{FAST_API_URL}/users/is_newbie/{tg_id}", headers=headers)
    answer = response.json()
    return answer["is_newbie"]


async def add_user(tg_id: str, username: str):
    data = {
        "tg_id": tg_id,
        "username": username
    }
    response = requests.post(f"{FAST_API_URL}/users/add_user", json=data)
    return response.status_code


async def get_tasks():
    response = requests.get(f"{FAST_API_URL}/tasks/get_tasks", headers=headers)
    answer = response.json()
    return [Task(**ans) for ans in answer]


async def get_task(task_id: int):
    response = requests.get(f"{FAST_API_URL}/tasks/get_task/{task_id}", headers=headers)
    return response


async def submit_assignment(task_id: int, tg_id: str, assignment_file: str) -> int:
    data = {
      "task_id": task_id,
      "tg_id": tg_id,
      "assignment_file": assignment_file
    }

    response = requests.post(f"{FAST_API_URL}/assignments/submit_assignment", json=data)
    return response.status_code


async def get_assignments(task_id: int, tg_id: str):
    response = requests.get(f"{FAST_API_URL}/assignments/get_assignments/{task_id}/{tg_id}", headers=headers)
    return response


async def get_results(tg_id: str):
    response = requests.get(f"{FAST_API_URL}/assignments/get_results/{tg_id}", headers=headers)
    return response
