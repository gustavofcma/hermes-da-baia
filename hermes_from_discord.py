import re
import discord
from discord import Webhook, RequestsWebhookAdapter
import telegram
from decouple import config
from baia_users import users, from_discord

TOKEN = config('DISCORD_TOKEN')
TLG = config('TELEGRAM_TOKEN')
WEBHOOK_ID =config('TEST_WEBHOOK_ID')
WEBHOOK_TOKEN = config('TEST_WEBHOOK_TOKEN')
GROUP_ID = config('GROUP_ID')
GUILD_ID = config('GUILD_ID', default=0, cast=int)
CHANNEL_ID = config('CHANNEL_ID', default=0, cast=int)

webhook = Webhook.partial(WEBHOOK_ID, WEBHOOK_TOKEN, adapter=RequestsWebhookAdapter())
# bot = telepot.Bot(TLG)
bot = telegram.Bot(token=TLG)
print(bot.getMe())
# print(bot.getUpdates())

# webhook.send(bot.getUpdates())

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

    print(message)

    '''if message.guild.id != GUILD_ID or message.channel.id != CHANNEL_ID:
        return

    if message.content.startswith('.'):
        user_ = message.guild.get_member(310936477817241610)
        print(user_.avatar_url)
        await message.delete()
        return
'''
    autor = users[from_discord[message.author.id]]['nome']

    teste_user = telegram.User(id=71836992, first_name='Gustavo', is_bot=False)
    teste = telegram.MessageEntity(offset=0, length=5, type='text_mention', user=teste_user)

    mensagem_composta = f'*{autor}*:\n'
    mensagem_composta += resolve_mentions(message.content)
    print(mensagem_composta)
    bot.sendMessage(GROUP_ID, mensagem_composta, parse_mode='Markdown')

    if message.content.startswith('!hello'):
        msg = f'Fala {message.author.mention}, seu arrombado!'
        await message.channel.send(msg)
        await message.channel.send(message.content)
        autor = users[from_discord[message.author.id]]['nome']
        mensagem_composta = f'*{autor}*:\n'
        mensagem_composta += message.content
        bot.sendMessage(GROUP_ID, mensagem_composta, parse_mode='Markdown')
        print(f'Message sent on {message.guild}/{message.channel} as reply to {message.author}')
        print(message.guild.id, message.channel.id)


@client.event
async def on_ready():
    print(f'Logged in as {client.user.name} ({client.user.id})')
    print('------')

client.run(TOKEN)
