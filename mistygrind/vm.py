"""
SCL <scott@rerobots.net>
Copyright (c) 2020 rerobots, Inc.
"""
from aiohttp import web


def start_vm():
    app = web.Application()
    web.run_app(app, host='127.0.0.1', port=8888)
    return 0
