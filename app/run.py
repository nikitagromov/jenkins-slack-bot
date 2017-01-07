import asyncio
from local import DEBUG, TOKEN
from slack.client import subscribe


def handler(message, user):
    return 'Hi Hello, {username}'.format(username=user["user"]["name"])

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.set_debug(DEBUG)
    handlers = [handler]
    loop.run_until_complete(subscribe(TOKEN, handlers))
