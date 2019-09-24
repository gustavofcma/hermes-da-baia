import re
import discord
from discord import Webhook, RequestsWebhookAdapter
import telegram
from decouple import config
from baia_users import users, from_discord

TOKEN = config('DISCORD_TOKEN')
TLG = config('TELEGRAM_TOKEN')
WEBHOOK_ID =config('WEBHOOK_ID')
WEBHOOK_TOKEN = config('WEBHOOK_TOKEN')
GROUP_ID = config('BAIA_ID')
GUILD_ID = config('GUILD_ID', default=0, cast=int)
CHANNEL_ID = config('CHANNEL_ID', default=0, cast=int)

webhook = Webhook.partial(WEBHOOK_ID, WEBHOOK_TOKEN, adapter=RequestsWebhookAdapter())
bot = telegram.Bot(token=TLG)
print(bot.getMe())
client = discord.Client()


def resolve_mentions(mensagem):
    for item in from_discord.keys():
        mensagem = re.sub(f'<@{item}>', users[from_discord[item]]['telegram']['user'], mensagem)

    return mensagem


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.guild.id != GUILD_ID or message.channel.id != CHANNEL_ID:
        return

    autor = users[from_discord[message.author.id]]['nome']

    mensagem_composta = f'*{autor}*:\n'
    mensagem_composta += resolve_mentions(message.content)
    bot.sendMessage(GROUP_ID, mensagem_composta, parse_mode='Markdown')


@client.event
async def on_ready():
    print(f'Logged in as {client.user.name} ({client.user.id})')
    print('------')

client.run(TOKEN)
