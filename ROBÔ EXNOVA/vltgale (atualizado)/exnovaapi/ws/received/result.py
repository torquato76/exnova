def result(api, message):
    if message["name"] == "result":
        api.result = message["msg"]["success"]