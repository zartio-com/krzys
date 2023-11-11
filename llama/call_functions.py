import random
from urllib import request

import discord
from bs4 import BeautifulSoup

from llama_api import LlamaPostProcessor, ChatInstance, LlamaAPI, LlamaOptions


async def get_weather(chat: ChatInstance, city):
    # city = args['city']
    url = f'https://www.google.com/search?q={city}+pogoda'
    req = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = request.urlopen(req).read()
    soup = BeautifulSoup(html, 'html.parser')
    result = soup.find("div", {"class": "BNeawe iBp4i AP7Wnd"}).text
    conditions = soup.find('div', attrs={'class': 'BNeawe tAd8D AP7Wnd'}).text.replace('\n', ', ')

    return f'SYSTEM: Current weather in {city}: {result} ({conditions})'


async def get_user_status(chat: ChatInstance, user_id):
    member = chat.channel_context.guild.get_member(int(user_id))
    if member is None:
        return "User not found"

    for activity in member.activities:
        if activity.type == discord.ActivityType.playing:
            return f'User is playing {activity.name}'
        if activity.type == discord.ActivityType.listening:
            return f'User is listening to {activity.title} by {activity.artist} on Spotify'

    random_activities = [
        'masturbating', 'having gay sex', 'watching gay porn',
        'slicing his wrists', 'urinating in the church'
    ]

    selected = random.choice(random_activities)
    return f'User is {selected}'


class CallFunctionsPostProcessor(LlamaPostProcessor):
    _AVAILABLE_FUNCTIONS = {
        'get_weather': get_weather,
        'get_user_status': get_user_status
    }

    async def process(self, chat: ChatInstance, last_response: str) -> str:
        last_response = last_response.strip()

        if '::' not in last_response:
            return last_response

        func = last_response.split('::')
        command = func[0]
        args = func[1].replace('<', '').replace('>', '')

        if command not in self._AVAILABLE_FUNCTIONS:
            return last_response

        result = await self._AVAILABLE_FUNCTIONS[command](chat, args)

        chat.bot_response(last_response)
        chat.user_input(result)

        return await LlamaAPI.get_response(chat, LlamaOptions(response_finished=False))
