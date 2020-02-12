"""
SCL <scott@rerobots.net>
Copyright (c) 2020 rerobots, Inc.
"""
import aiohttp
from aiohttp import web


@web.middleware
async def cors_handler(request, handler):
    """Middleware to add CORS response headers
    """
    response = await handler(request)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@web.middleware
async def mistyversion_header(request, handler):
    """Add Misty-Command-Version header
    """
    response = await handler(request)
    response.headers['Misty-Command-Version'] = 'Current'
    return response


def generate_batterylevel():
    """Simulate battery level data

    Follows official API documentation
    (https://docs.mistyrobotics.com/misty-ii/rest-api/api-reference/#getbatterylevel)
    and observations in practice on real Misty robots.
    """
    return {
        'chargePercent': 1.0,
        'created': '2020-02-06T10:00:00.000Z',
        'current': 0.0,
        'isCharging': False,
        'sensorId': 'charge',
        'trained': False,
        'voltage': 8.3,
    }


async def battery(request):
    """GET /api/battery

    cf. https://docs.mistyrobotics.com/misty-ii/rest-api/api-reference/#getbatterylevel
    """
    return web.json_response({
        'status': 'Success',
        'result': generate_batterylevel(),
    })


async def device(request):
    """GET /api/device

    cf. https://docs.mistyrobotics.com/misty-ii/rest-api/api-reference/#getdeviceinformation
    """
    return web.json_response({
        'status': 'Success',
        'result': {
            'androidHardwareId': 'fake',
            'androidOSVersion': 'fake',
            'batteryLevel': generate_batterylevel(),
            'currentProfileName': 'fake',
            'ipAddress': '127.0.0.1',
            'networkConnectivity': 'InternetAccess',
            'occipitalDeviceInfo': None,
            'outputCapabilities': None,
            'sensorCapabilities': None,
            'sensoryServiceAppVersion': '0.0.0',
            'robotId': 'fake',
            'robotVersion': '0.0.0.0',
            'serialNumber': '0',
            'windowsOSVersion': '0.0.0.0',
        },
    })


async def get_system_updates(request):
    """GET /api/system/updates

    cf. https://docs.mistyrobotics.com/misty-ii/rest-api/api-reference/#getstoreupdateavailable
    """
    return web.json_response({
        'status': 'Success',
        'result': False,
    })


async def get_audio_list(request):
    """GET /api/audio/list

    cf. https://docs.mistyrobotics.com/misty-ii/rest-api/api-reference/#getaudiolist
    """
    return web.json_response({
        'status': 'Success',
        'result': [
            {
                'name': 'fake.wav',
                'systemAsset': True,
            },
        ],
    })


async def get_images_list(request):
    """GET /api/images/list

    cf. https://docs.mistyrobotics.com/misty-ii/rest-api/api-reference/#getimagelist
    """
    return web.json_response({
        'status': 'Success',
        'result': [
            {
                'name': 'fake.jpg',
                'systemAsset': True,
                'height': 272,
                'width': 400,
            },
        ],
    })


async def pubsub(request):
    """WebSocket via /pubsub
    """
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.CLOSED or msg.type == aiohttp.WSMsgType.ERROR:
            break
        else:
            if request.app['trace_unknown']:
                print('WebSocket rx:', msg.data)
    return ws


async def generic_options(request):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'DELETE,GET,OPTIONS,POST,PUT',
        'Access-Control-Allow-Headers': 'Content-Type,Accept,Access-Control-Allow-Origin',
    }
    return web.json_response(headers=headers, status=200)


async def default_route(request):
    print('{} {}'.format(request.method, request.path))
    qpairs = list(request.query.items())
    if qpairs:
        print('query pairs:', qpairs)
    if request.has_body:
        given = str(await request.read(), encoding='utf-8')
    else:
        given = ''
    if given:
        print('body:', given)
    return web.json_response(status=404)


def create_vm(trace_unknown=False):
    """Create Misty VM as aiohttp app.
    """
    app = web.Application(middlewares=[cors_handler, mistyversion_header])
    app.router.add_get(r'/api/device', device)
    app.router.add_get(r'/api/battery', battery)
    app.router.add_get(r'/api/system/updates', get_system_updates)
    app.router.add_get(r'/api/audio/list', get_audio_list)
    app.router.add_get(r'/api/images/list', get_images_list)
    app.router.add_get(r'/pubsub', pubsub)
    app.router.add_route('OPTIONS', r'/{path:.*}', generic_options)
    app['trace_unknown'] = trace_unknown
    if trace_unknown:
        app.router.add_route('*', '/{path:.*}', default_route)
    return app


def start_vm(addr=None, port=8888, trace_unknown=False):
    """Start VM

    addr: IP address to bind for listening; default is 127.0.0.1 (localhost).
    port: port number to bind
    trace_unknown: echo any requests of unknown method, path to stdout.
    """
    if addr is None:
        addr = '127.0.0.1'
    web.run_app(create_vm(trace_unknown=trace_unknown), host=addr, port=port)
    return 0
