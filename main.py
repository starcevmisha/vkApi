import asyncio
import json
import time

import aiohttp
import async_timeout


class Friend:
    def __init__(self, user_id, deep, parent_friend):
        self.user_id = user_id
        self.deep = deep
        self.parent_friend = parent_friend


friends_id = [53360669]
friends = [Friend(53360669, 0, None)]
last_deep_dict = {}



async def fetch(session, url):
    async with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()


async def main(deep):
    async with aiohttp.ClientSession() as session:
        url = 'https://api.vk.com/method/friends.get?user_id={}&v=5.73'
        for i in friends:
            if (i.deep >= deep):## Не искать друзей, для друзей большей глубины
                return
            json_str = await fetch(session, url.format(i.user_id))
            dic = json.loads(json_str)
            try:
                res = dic['response']['items']

                for user_id in res:
                    friend = Friend(user_id, i.deep + 1, i)
                    friends.append(friend)
                    friends_id.append(user_id)
                    if i.deep+1 == deep:
                        last_deep_dict[user_id] = friend

                print(len(friends))
            except KeyError as e:
                print(json_str)


start = time.time()
loop = asyncio.get_event_loop()
loop.run_until_complete(main(2))
loop.close()
finish = time.time() - start
print(finish)
print(len(friends))
print(len(last_deep_dict))
