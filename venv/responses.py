from random import choice, randint

def get_respose(user_input: str) -> str:
    lowered: str = user_input.lower()

    if lowered == '':
        return 'Well, you\'re awfully silent ( ._. )""'
    elif 'hello' in lowered:
        return 'Hello there!'