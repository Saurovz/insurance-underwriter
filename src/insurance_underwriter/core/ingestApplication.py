import json

def get_user_info(name="Tim", age=30, sex="male"):
    user_data = {
        "name": name,
        "age": age,
        "sex": sex
    }
    return json.dumps(user_data)