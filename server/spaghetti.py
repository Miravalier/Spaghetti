#!/usr/bin/env python3.7

import sys
from flask import Flask
from flask_restful import reqparse, Resource, Api

app = Flask(__name__)
api = Api(app)


def log(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)


def idtoken(token):
    log("Received token {}".format(token))
    # TODO actually authenticate the token
    if True:
        return True
    else:
        abort(403, message="Failed to authenticate with the server.")
        raise ValueError("Invalid idtoken")


class AuthenticatedParser(reqparse.RequestParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument('idtoken', type=idtoken, help='Invalid Google OAuth2 idtoken', required=True)


class AuthStatus(Resource):
    def put(self):
        parser = AuthenticatedParser()
        args = parser.parse_args()
        return {"status": "authenticated"}


class Status(Resource):
    def get(self):
        return {"status": "online"}


api.add_resource(AuthStatus, '/authstatus')
api.add_resource(Status, '/status')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3033, debug=True)
