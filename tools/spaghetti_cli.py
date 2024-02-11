#!/usr/bin/env python3
from typing import Dict, Iterable, List
import cmd2
import sys
import requests


empty_parser = cmd2.Cmd2ArgumentParser()

login_parser = cmd2.Cmd2ArgumentParser()
login_parser.add_argument("username", help="Spaghetti account username")
login_parser.add_argument("password", help="Spaghetti account password")


class SpaghettiCLI(cmd2.Cmd):
    base_url: str = "http://127.0.0.1:8080"
    token: str = None

    @cmd2.with_argparser(login_parser)
    def do_login(self, args):
        """
        Login to the spaghetti API
        """
        response = requests.post(
            f"{self.base_url}/api/login",
            json={
                "username": args.username,
                "password": args.password,
            }
        )
        body = response.json()
        print(response.status_code, body)

        if response.status_code == 200:
            self.token = body["token"]

    @cmd2.with_argparser(empty_parser)
    def do_status(self, args):
        """
        Get status
        """
        response = requests.get(
            f"{self.base_url}/api/status",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        body = response.json()
        print(response.status_code, body)


if __name__ == '__main__':
    app = SpaghettiCLI()
    sys.exit(app.cmdloop())
