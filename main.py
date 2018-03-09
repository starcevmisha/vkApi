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

result = []

friends1_id = []
friends1 = []
friends1_dict = {}



async def fetch(session, url):
    async with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()

async def first_search(deep:int, start_id:int):
    friends1.append(Friend(start_id, 0, None))
    friends1_id.append(start_id)
    friends1_dict[start_id] = Friend(start_id, 0, None)

    async with aiohttp.ClientSession() as session:
        url = 'https://api.vk.com/method/friends.get?user_id={}&v=5.73'
        for i in friends1:
            if (i.deep >= deep):## Не искать друзей, для друзей большей глубины
                return
            json_str = await fetch(session, url.format(i.user_id))
            dic = json.loads(json_str)
            try:
                res = dic['response']['items']

                for user_id in res:
                    friend = Friend(user_id, i.deep + 1, i)
                    friends1.append(friend)
                    friends1_id.append(user_id)
                    if not user_id in friends1_dict:
                        friends1_dict[user_id] = friend
                print(len(friends1))
            except KeyError as e:
                print(json_str)

async def second_search(deep:int, start_id:int):
    friends2 = [Friend(start_id, 0, None)]
    friends2_id = [start_id]
    friends2_dict = {}
    friends2_dict[start_id] = Friend(start_id, 0, None)

    async with aiohttp.ClientSession() as session:
        url = 'https://api.vk.com/method/friends.get?user_id={}&v=5.73'
        for i in friends2:
            if (i.deep >= deep):## Не искать друзей, для друзей большей глубины
                return
            json_str = await fetch(session, url.format(i.user_id))
            dic = json.loads(json_str)
            try:
                res = dic['response']['items']
                for user_id in res:
                    friend = Friend(user_id, i.deep + 1, i)
                    if user_id in friends1_dict:
                        result.append((friends1_dict[user_id], friend))
                    else:
                        friends2.append(friend)
                print(len(friends2))
            except KeyError as e:
                pass
                # print(json_str)

async def get_names(friends_chain:[]):
    result=[""]*len(friends_chain)
    async with aiohttp.ClientSession() as session:
        url = 'https://api.vk.com/method/users.get?user_ids={}&v=5.73'
        for i in range(len(friends_chain)):
            json_str = await fetch(session, url.format(friends_chain[i]))
            dic = json.loads(json_str)
            try:
                name = dic['response'][0]['first_name']
                soname = dic['response'][0]['last_name']
                result[i] = "{} {}({})".format(name, soname, friends_chain[i])
            except KeyError as e:
                pass
                # print(json_str)
        print(("->").join(result))


def get_friend_chain(start_friend, end_friend):
    res = [start_friend.user_id]
    fr = start_friend
    while not fr.parent_friend is None:
        res.append(fr.parent_friend.user_id)
        fr = fr.parent_friend
    res.reverse()
    fr = end_friend
    while not fr.parent_friend is None:
        res.append(fr.parent_friend.user_id)
        fr = fr.parent_friend
    return res

start = time.time()
loop = asyncio.get_event_loop()
loop.run_until_complete(first_search(2, 53360669))
finish = time.time() - start
print(finish)
print(len(friends1))
print(len(friends1_dict))

second_id = 161573138
start = time.time()
loop.run_until_complete(second_search(2,second_id))
finish = time.time() - start
print(finish)

tasks = []
for (start, end) in result:
    loop.run_until_complete(get_names(get_friend_chain(start, end)))

loop.close()


