# import sympy as smp
# import numpy as np

def get_response(user_input: str) -> str:
    lowered: str = user_input.lower()

    if lowered == '':
        return 'Well, you\'re awfully silent ( ._. )""'
    elif 'hello' in lowered:
        return 'Hello there!'
    elif 'add' in lowered[:3]:
        return add(*lowered[4:].split())

def add(*arr):
    result = 0
    for i in arr:
        if i.isdigit():
            result += int(i)
    return result