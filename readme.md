Installation & requirements
---------------------------
Tested with Python 3.10

This bot does require running api backend of https://github.com/oobabooga/text-generation-webui

Be sure to set environment variables in .env file.
COMFYUI_HOST is currently not used - stable diffusion support coming soon.

Installation steps:
1. `python -m venv venv`
2. `./venv/Scripts/activate`
3. `python -m pip install -r requirements.txt`
4. `python ./main.py`

## Current capabilities
You can ping this bot with `@botname` and it will respond to your message.

## Modifying the bot
In _data there are "parameters" and "instructions" directories.
You can edit the _data/instructions/ping_krzys.txt file to change the bot personality.
Parameters are passed through api to text-generation-webui backend. More on parameters here:
https://github.com/oobabooga/text-generation-webui/wiki/03-%E2%80%90-Parameters-Tab

## Polish language support
For the bot to be capable of speaking (somewhat good) polish,
you need to download fine-tuned model from https://huggingface.co/TheBloke/Trurl-2-7B-GPTQ

There is also 13B model available at:
https://huggingface.co/TheBloke/Trurl-2-13B-GPTQ