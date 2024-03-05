#!/usr/bin/env python3
import cmd2
import sys
import requests


status_parser = cmd2.Cmd2ArgumentParser()
invites_parser = cmd2.Cmd2ArgumentParser()
create_invite_parser = cmd2.Cmd2ArgumentParser()
list_friends_parser = cmd2.Cmd2ArgumentParser()
list_transactions_parser = cmd2.Cmd2ArgumentParser()

income_parser = cmd2.Cmd2ArgumentParser()
income_parser.add_argument("amount", type=int, nargs="?", default=10, help="Amount to grant")

set_url_parser = cmd2.Cmd2ArgumentParser()
set_url_parser.add_argument("url", help="e.g. https://spaghetti.miramontes.dev")

login_parser = cmd2.Cmd2ArgumentParser()
login_parser.add_argument("username", help="Spaghetti account username")
login_parser.add_argument("password", help="Spaghetti account password")

register_parser = cmd2.Cmd2ArgumentParser()
register_parser.add_argument("username", help="Spaghetti account username")
register_parser.add_argument("password", help="Spaghetti account password")
register_parser.add_argument("invite_code", help="Invite code")

check_invite_parser = cmd2.Cmd2ArgumentParser()
check_invite_parser.add_argument("invite_code", help="Invite code to check")

delete_invite_parser = cmd2.Cmd2ArgumentParser()
delete_invite_parser.add_argument("invite_code", help="Invite code to delete")

add_friend_parser = cmd2.Cmd2ArgumentParser()
add_friend_parser.add_argument("name", help="Username to add as a friend")

delete_friend_parser = cmd2.Cmd2ArgumentParser()
delete_friend_parser.add_argument("name", help="Username to remove as a friend")

transfer_parser = cmd2.Cmd2ArgumentParser()
transfer_parser.add_argument("user", help="User to transfer to")
transfer_parser.add_argument("amount", help="Amount to transfer")
transfer_parser.add_argument("comment", nargs="?", default="", help="Transaction comment")

lookup_user_parser = cmd2.Cmd2ArgumentParser()
lookup_user_parser.add_argument("name", help="Username to look up")


class SpaghettiCLI(cmd2.Cmd):
    base_url: str = "https://spaghetti.miramontes.dev"
    id: str = None
    token: str = None

    @cmd2.with_argparser(set_url_parser)
    def do_set_url(self, args):
        """
        Set API server url
        """
        self.base_url = args.url.rstrip("/")

    @cmd2.with_argparser(status_parser)
    def do_status(self, args):
        """
        Get account status
        """
        response = requests.get(
            f"{self.base_url}/api/status",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        body = response.json()
        print(response.status_code, body)

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
        print(response.status_code, response.text)
        if response.status_code == 200:
            body = response.json()
            self.token = body["token"]
            self.id = body["user"]["id"]


    @cmd2.with_argparser(register_parser)
    def do_register(self, args):
        """
        Register a new spaghetti account
        """
        response = requests.post(
            f"{self.base_url}/api/register",
            json={
                "username": args.username,
                "password": args.password,
                "invite_code": args.invite_code,
            }
        )
        body = response.json()
        print(response.status_code, body)

        if response.status_code == 200:
            self.token = body["token"]

    @cmd2.with_argparser(income_parser)
    def do_income(self, args):
        """
        Add income to all users
        """
        response = requests.post(
            f"{self.base_url}/admin/balance/grant-all",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"amount": args.amount},
        )
        body = response.json()
        print(response.status_code, body)

    @cmd2.with_argparser(invites_parser)
    def do_invites(self, args):
        """
        List invite codes
        """
        response = requests.get(
            f"{self.base_url}/api/invites",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        body = response.json()
        print(response.status_code, body)

        for invite in body["invites"]:
            code = invite["code"]
            print(f"{self.base_url}/register?code={code}")

    @cmd2.with_argparser(check_invite_parser)
    def do_check_invite(self, args):
        """
        Check an invite code
        """
        response = requests.get(
            f"{self.base_url}/api/invite?code={args.invite_code}",
        )
        body = response.json()
        print(response.status_code, body)

    @cmd2.with_argparser(create_invite_parser)
    def do_invite(self, args):
        """
        Create invite code
        """
        response = requests.post(
            f"{self.base_url}/api/invite",
            headers={"Authorization": f"Bearer {self.token}"},
            json={}
        )
        body = response.json()
        print(response.status_code, body)
        code = body["code"]
        print(f"{self.base_url}/register?code={code}")

    @cmd2.with_argparser(delete_invite_parser)
    def do_delete_invite(self, args):
        """
        Delete invite code
        """
        response = requests.delete(
            f"{self.base_url}/api/invite?code={args.invite_code}",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        body = response.json()
        print(response.status_code, body)

    @cmd2.with_argparser(add_friend_parser)
    def do_add_friend(self, args):
        """
        Delete invite code
        """
        response = requests.post(
            f"{self.base_url}/api/friend",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"name": args.name},
        )
        body = response.json()
        print(response.status_code, body)

    @cmd2.with_argparser(list_friends_parser)
    def do_list_friends(self, args):
        """
        Get account status
        """
        response = requests.get(
            f"{self.base_url}/api/friends",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        body = response.json()
        print(response.status_code, body)

    @cmd2.with_argparser(delete_friend_parser)
    def do_remove_friend(self, args):
        """
        Remove friend
        """
        response = requests.delete(
            f"{self.base_url}/api/friend?name={args.name}",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        body = response.json()
        print(response.status_code, body)

    @cmd2.with_argparser(transfer_parser)
    def do_transfer(self, args):
        """
        Transfer spaghetti to another user
        """
        response = requests.post(
            f"{self.base_url}/api/transfer",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "source": self.id,
                "destination": args.user,
                "amount": args.amount,
                "comment": args.comment,
            }
        )
        body = response.json()
        print(response.status_code, body)

    @cmd2.with_argparser(lookup_user_parser)
    def do_lookup_user(self, args):
        """
        Look up a user by name
        """
        response = requests.get(
            f"{self.base_url}/api/user?name={args.name}",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        body = response.json()
        print(response.status_code, body)

    @cmd2.with_argparser(list_transactions_parser)
    def do_list_transactions(self, args):
        """
        List transactions
        """
        response = requests.get(
            f"{self.base_url}/api/transactions",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        body = response.json()
        print(response.status_code, body)


if __name__ == '__main__':
    app = SpaghettiCLI()
    sys.exit(app.cmdloop())
