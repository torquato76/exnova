
def training_balance_reset(api, message):
    if message["name"] == "training-balance-reset":
        api.training_balance_reset_request = message["msg"]["isSuccessful"]