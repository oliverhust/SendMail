#!/usr/bin/python
# -*- coding: utf-8 -*-


from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


def run():
    authorizer = DummyAuthorizer()
    authorizer.add_user("user", "12345", r"D:\tmp", perm="elradfmw")
    authorizer.add_anonymous(r"D:\tmp")
    handler = FTPHandler
    handler.authorizer = authorizer
    server = FTPServer(("127.0.0.1", 5555), handler)
    server.serve_forever()


if __name__ == '__main__':
    run()
