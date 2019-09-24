from discord import Webhook, RequestsWebhookAdapter, Embed
import telepot.aio
from telepot.aio.loop import MessageLoop
from decouple import config
import asyncio
from baia_users import users, from_telegram, from_telegram_usernames

TELEGRAM_TOKEN = config('TELEGRAM_TOKEN')
WEBHOOK_ID = config('TEST_WEBHOOK_ID')
WEBHOOK_TOKEN = config('TEST_WEBHOOK_TOKEN')
GROUP_ID = config('GROUP_ID', default=0, cast=int)

discord_webhook = Webhook.partial(WEBHOOK_ID, WEBHOOK_TOKEN, adapter=RequestsWebhookAdapter())


async def resolve_mentions(mensagem):
    mentions = sorted([item for item in mensagem['entities'] if
                       item['type'] in ('mention', 'text_mention')], key=lambda i: i['offset'])
    gap = 0
    if 'entities' in mensagem.keys():
        for item in mensagem['entities']:
            if item['type'] == 'mention':
                metade_1 = mensagem["text"][:item["offset"]+gap]
                metade_2 = mensagem["text"][item["offset"]+gap+item["length"]:]
                baia_user = from_telegram_usernames[mensagem["text"][item["offset"]+gap:item["offset"]+gap+item["length"]]]
                mention = f'<@{users[baia_user]["discord"]["id"]}>'
                mensagem['text'] = f'{metade_1}{mention}{metade_2}'
                gap = len(mention) - item['length']
            elif item['type'] == 'text_mention':
                metade_1 = mensagem["text"][:item["offset"] + gap]
                metade_2 = mensagem["text"][item["offset"] + gap + item["length"]:]
                baia_user = from_telegram[item['user']['id']]
                mention = f'<@{users[baia_user]["discord"]["id"]}>'
                mensagem['text'] = f'{metade_1}{mention}{metade_2}'
                gap = len(mention) - item['length']
    return mensagem


async def handle(msg):
    print(msg)

    chat_id = msg['chat']['id']
    autor = msg['from']

    if chat_id != GROUP_ID or autor['is_bot']:
        return

    if 'text' not in msg.keys():
        sorry = f'Parece que o {autor["first_name"]} mandou algo lá no Telegram.\n'
        sorry += 'Infelizmente ainda não sei ler as figura.'
        discord_webhook.send(sorry)
        return

    msg = await resolve_mentions(msg)
    full_msg = msg['text']

    embed = Embed(description=full_msg)
    embed.set_author(name=f'{autor["first_name"]} {autor["last_name"]}')

    discord_webhook.send(embed=embed)

telegram_bot = telepot.aio.Bot(TELEGRAM_TOKEN)
loop = asyncio.get_event_loop()

loop.create_task(MessageLoop(telegram_bot, handle).run_forever())
print('Listening...')

loop.run_forever()
