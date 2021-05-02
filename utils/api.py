import asyncio
import re
import requests


async def get_amazing_fact():
    loop = asyncio.get_event_loop()
    req = loop.run_in_executor(None, requests.get, 'https://www.mentalfloss.com/api/facts')
    res = await req

    if res.status_code != 200:
        return []

    data = res.json()

    data = list(map(lambda fact: {
        'content': re.sub(r"<[^>]*>", "*", fact['fact']),
        'url': fact['fullStoryUrl'] or '',
        'image_url': fact['primaryImage'],
        'image_credit': fact['imageCredit']
    }, data))

    return data


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_amazing_fact())
    loop.close()
