
from exnovaapi.http.resource import Resource
from exnovaapi.http.register import Register


class Getprofile(Resource):

    url = "/".join((Register.url, "getregdata"))

    def _get(self):

        return self.send_http_request("GET")

    def __call__(self):
        return self._get()
