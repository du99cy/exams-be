
from fastapi.encoders import jsonable_encoder


def responseModel(*, data=None, message='success', status_code=200):
    return jsonable_encoder({
        "data": data,
        "status_code": status_code,
        "message": message
    })
