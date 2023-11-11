import json
import os
from abc import ABC, abstractmethod

import discord
import requests


class ChatInstance:
    def __init__(self, chat_id,
                 channel_context: discord.abc.GuildChannel = None,
                 user_context: discord.Member = None,
                 instruction: str = '', parameters: str = '', template: str = 'llama2_chat'):
        self.chat_id = chat_id
        self.channel_context = channel_context
        self.user_context = user_context

        if instruction != '':
            with open(f'_data/instructions/{instruction}.txt', 'r', encoding='utf-8') as file:
                self.instructions = file.read()
        else:
            self.instructions = ''

        if parameters != '':
            with open(f'_data/parameters/{instruction}.json', 'r', encoding='utf-8') as file:
                self.parameters = json.loads(file.read())
        else:
            self.parameters = {}

        with open(f'_data/templates/{template}.json', 'r', encoding='utf-8') as file:
            self.template_data = json.loads(file.read())

        self.chat_history = []

    def user_input(self, user_input: str):
        self.chat_history.append([user_input.strip(), ''])

    def bot_response(self, bot_response: str):
        self.chat_history[-1][1] += bot_response


class LlamaPostProcessor(ABC):
    @abstractmethod
    async def process(self, chat: ChatInstance, last_response: str) -> str:
        pass


class LlamaOptions:
    def __init__(self, begin_response_with: str = '', response_finished: bool = True):
        self.begin_response_with = begin_response_with
        self.response_finished = response_finished


class LlamaAPI:
    _POST_PROCESSORS: list[type[LlamaPostProcessor]] = []

    @staticmethod
    def build_prompt(chat: ChatInstance, options: LlamaOptions) -> str:
        prompt = chat.template_data['context'].format(instructions=chat.instructions)

        if options.begin_response_with != '':
            chat.chat_history[-1][1] += options.begin_response_with

        is_first = True
        for chat_turn in chat.chat_history:
            if not is_first:
                prompt += chat.template_data['user_bot_finish_turn']
            is_first = False

            prompt += chat.template_data['user_template'].format(chat_turn[0])
            if chat_turn[1] != '' and options.response_finished:
                prompt += chat.template_data['bot_template'].format(chat_turn[1])
            elif chat_turn[1] != '':
                prompt += chat_turn[1]

        return prompt

    @staticmethod
    def register_post_processor(post_processor: type[LlamaPostProcessor]):
        LlamaAPI._POST_PROCESSORS.append(post_processor)

    @staticmethod
    async def get_response(chat: ChatInstance, options: LlamaOptions = None) -> str:
        if options is None:
            options = LlamaOptions()

        # Default request values
        request = {
            'prompt': LlamaAPI.build_prompt(chat, options),
            'max_new_tokens': 250,
            'auto_max_new_tokens': False,
            'max_tokens_second': 0,
            'do_sample': True,
            'temperature': 0.7,
            'top_p': 0.1,
            'typical_p': 1,
            'epsilon_cutoff': 0,  # In units of 1e-4
            'eta_cutoff': 0,  # In units of 1e-4
            'tfs': 1,
            'top_a': 0,
            'repetition_penalty': 1.18,
            'presence_penalty': 0,
            'frequency_penalty': 0,
            'repetition_penalty_range': 0,
            'top_k': 40,
            'min_length': 0,
            'no_repeat_ngram_size': 0,
            'num_beams': 1,
            'penalty_alpha': 0,
            'length_penalty': 1,
            'early_stopping': False,
            'mirostat_mode': 0,
            'mirostat_tau': 5,
            'mirostat_eta': 0.1,
            'grammar_string': '',
            'guidance_scale': 1,
            'negative_prompt': '',

            'seed': 1894984548,
            'add_bos_token': True,
            'truncation_length': 2048,
            'ban_eos_token': False,
            'custom_token_bans': '',
            'skip_special_tokens': True,
            'stopping_strings': []
        }

        request = dict(list(request.items()) + list(chat.parameters.items()))
        response = requests.post('{}/api/v1/generate'.format(os.getenv('LLAMA_HOST')), json=request)

        if response.status_code == 200:
            result = response.json()['results'][0]['text']
            if options.begin_response_with != '':
                result = options.begin_response_with + result
            for post_processor in LlamaAPI._POST_PROCESSORS:
                result = await post_processor().process(chat, result)
            chat.bot_response(result)
            return result
