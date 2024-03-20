import json


def is_valid(data):
    try:
        json.loads(data)
        return True
    except json.JSONDecodeError:
        return False


def getObject(_string):
    return json.loads(_string)


