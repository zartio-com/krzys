import discord
from discord.ext import commands

from llama_api import ChatInstance, LlamaAPI


async def append_to_message_or_reply(message: discord.Message, content: str, view: discord.ui.View):
    if len(message.content) + len(content) <= 2000:
        await message.edit(content=message.content + content, view=view)
        return

    await message.edit(content=message.content, view=None)
    await message.reply(content, view=view)


class PingReplyActions(discord.ui.View):
    def __init__(self, chat_instance: ChatInstance):
        self.chat_instance = chat_instance
        super().__init__()

    @discord.ui.button(label="Kontynuuj", style=discord.ButtonStyle.primary, custom_id="ping_reply_continue")
    async def continue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        response: discord.InteractionResponse = interaction.response
        await response.defer(ephemeral=True)

        llm_response = await LlamaAPI.get_response(self.chat_instance)
        if llm_response == '':
            await append_to_message_or_reply(
                interaction.message,
                '\nNie mam nic do dodania',
                PingReplyActions(self.chat_instance))
            return
        await append_to_message_or_reply(interaction.message, llm_response, PingReplyActions(self.chat_instance))

    @discord.ui.button(label="Dopytaj", style=discord.ButtonStyle.blurple, custom_id="ping_reply_ask_more")
    async def ask_more(self, interaction: discord.Interaction, button: discord.ui.Button):
        response: discord.InteractionResponse = interaction.response
        await response.send_modal(AskMoreModal(self.chat_instance))


class AskMoreModal(discord.ui.Modal, title="Kontynuacja czatu"):
    question = discord.ui.TextInput(label="Pytanie", style=discord.TextStyle.paragraph)

    def __init__(self, chat_instance: ChatInstance):
        super().__init__(timeout=None)

        self.chat_instance = chat_instance

    async def on_submit(self, interaction: discord.Interaction) -> None:
        response: discord.InteractionResponse = interaction.response
        await response.defer(ephemeral=True)

        self.chat_instance.user_input(self.question.value)
        llm_response = await LlamaAPI.get_response(self.chat_instance)
        if llm_response == '':
            llm_response = 'Nie mam odpowiedzi na to pytanie :('

        new_content = f'\n{interaction.user.display_name}: {self.question.value}\nKrzyś: {llm_response}'
        await append_to_message_or_reply(interaction.message, new_content, PingReplyActions(self.chat_instance))


class PingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.chat_instances = {}
        self.bot = bot

    @commands.Cog.listener('on_message')
    async def on_message(self, message: discord.Message):
        if self.bot.user not in message.mentions:
            return

        if message.author.id == self.bot.user.id:
            return

        message_content = message.content.replace(f'<@{self.bot.user.id}>', '').strip()
        chat = ChatInstance(message.author.id,
                            channel_context=message.channel,
                            user_context=message.author,
                            instruction='ping_krzys', parameters='ping_krzys')
        chat.user_input(message_content)

        llm_response = await LlamaAPI.get_response(chat)
        if llm_response == '':
            llm_response = 'Nie mam odpowiedzi na to pytanie :('
        await message.reply(llm_response, view=PingReplyActions(chat))


async def setup(bot: commands.Bot):
    await bot.add_cog(PingCog(bot))
