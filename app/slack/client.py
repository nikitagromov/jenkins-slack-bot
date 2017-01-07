
"""Slack Bot that prints on the console."""
import asyncio
import json
import sys

import aiohttp


async def subscribe(token, handlers):
    channel = asyncio.Queue()

    asyncio.ensure_future(bot(token, channel))

    while True:
        data = await channel.get()
        message = data['message']
        send_func = data['send']

        if message.get('type') == 'message':
            user = await api_call('users.info', token,
                                  {'user': message.get('user')})
            if user['user']['is_bot'] and user['user']['name'] == 'jenkins':
                send_func(json.dumps({'type': 'message',
                                      'channel': message['channel'],
                                      'text': 'Hi I am Jenkins Bot'}))
                continue

            for handler in handlers:
                print("handler {0}: {1}".format(user["user"]["name"],
                                                message["text"]))
                response = {'type': 'message', 'channel': message['channel']}
                response.update({'text': handler(data['message'], user)})
                send_func(json.dumps(response))
        else:
            print(message, file=sys.stderr)


async def api_call(method, token, data=None):
    """Slack API call."""
    with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        form = aiohttp.FormData(data or {})
        form.add_field('token', token)
        async with session.post('https://slack.com/api/{0}'.format(method),
                                data=form) as response:
            assert 200 == response.status, ('{0} with {1} failed.'
                                            .format(method, data))
            return await response.json()


async def bot(token, channel):
    """Create a bot that joins Slack."""
    rtm = await api_call("rtm.start", token=token)
    assert rtm['ok'], "Error connecting to RTM."

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        async with session.ws_connect(rtm["url"]) as ws:
            async for msg in ws:
                assert msg.tp == aiohttp.MsgType.text
                message = json.loads(msg.data)
                await channel.put({'message': message, 'send': ws.send_str})
