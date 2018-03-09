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

friends1 = []
friends1_dict = {}


async def fetch(session, url):
    async with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()


async def first_search(deep: int, start_id):
    friends1.append(Friend(start_id, 0, None))
    friends1_dict[start_id] = Friend(start_id, 0, None)

    async with aiohttp.ClientSession() as session:
        url = 'https://api.vk.com/method/friends.get?user_id={}&v=5.73'
        for i in friends1:
            if (i.deep >= deep):  # Не искать друзей, для друзей большей глубины
                return
            json_str = await fetch(session, url.format(i.user_id))
            dic = json.loads(json_str)
            try:
                res = dic['response']['items']

                for user_id in res:
                    friend = Friend(user_id, i.deep + 1, i)
                    friends1.append(friend)
                    if user_id not in friends1_dict:
                        friends1_dict[user_id] = friend
                print('\ruser 1 friends count: '+str(len(friends1)), end = "")
            except KeyError as e:
                pass
                # print(json_str)


async def second_search(deep: int, start_id):
    friends2 = [Friend(start_id, 0, None)]
    friends2_dict = {}
    friends2_dict[start_id] = Friend(start_id, 0, None)

    async with aiohttp.ClientSession() as session:
        url = 'https://api.vk.com/method/friends.get?user_id={}&v=5.73'
        for i in friends2:
            if (i.deep >= deep):  # Не искать друзей, для друзей большей глубины
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
                print('\ruser 2 friends count: ' + str(len(friends2)), end="")
            except KeyError as e:
                pass
                # print(json_str)


async def get_names(friends_chain: []):
    result = [''] * len(friends_chain)
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
        print("->".join(result))


def get_friend_chain(start_friend, end_friend):
    res = [start_friend.user_id]
    fr = start_friend
    while fr.parent_friend is not None:
        res.append(fr.parent_friend.user_id)
        fr = fr.parent_friend
    res.reverse()
    fr = end_friend
    while fr.parent_friend is not None:
        res.append(fr.parent_friend.user_id)
        fr = fr.parent_friend
    return res


def print_friends(first_id, first_deep, second_id, second_deep):


    loop = asyncio.get_event_loop()

    start = time.time()
    loop.run_until_complete(first_search(first_deep, first_id))
    finish = time.time() - start

    print()
    print(finish)

    start = time.time()
    loop.run_until_complete(second_search(second_deep, second_id))
    finish = time.time() - start

    print()
    print(finish)

    for (start, end) in result:
        loop.run_until_complete(get_names(get_friend_chain(start, end)))

    loop.close()


if __name__ == "__main__":

    #https://api.vk.com/method/users.get?user_ids=dm&v=5.73
    first_id = 53360669
    first_deep = 2

    second_id = 634666
    second_deep = 2

    print_friends(first_id, first_deep, second_id, second_deep)
