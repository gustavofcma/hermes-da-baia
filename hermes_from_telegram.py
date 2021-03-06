from discord import Webhook, RequestsWebhookAdapter, Embed
import telepot.aio
from telepot.aio.loop import MessageLoop
from decouple import config
import asyncio
from baia_users import users, from_telegram, from_telegram_usernames

TELEGRAM_TOKEN = config('TELEGRAM_TOKEN')
WEBHOOK_ID = config('WEBHOOK_ID')
WEBHOOK_TOKEN = config('WEBHOOK_TOKEN')
GROUP_ID = config('BAIA_ID', default=0, cast=int)

discord_webhook = {}
for i in range(len(users)):
    discord_webhook[f'{i:02d}'] = Webhook.partial(config(f'{i:02d}_WEBHOOK_ID'), config(f'{i:02d}_WEBHOOK_TOKEN'), 
                                                  adapter=RequestsWebhookAdapter())


async def resolve_mentions(mensagem):
    mentions = sorted([item for item in mensagem['entities'] if
                       item['type'] in ('mention', 'text_mention')], key=lambda i: i['offset'])
    mention_replace_list = []
    for item in mentions:
        mention_text = mensagem['text'][item['offset']:item['offset'] + item['length']]
        discord_user_id = ''
        if item['type'] == 'mention':
            discord_user_id = users[from_telegram_usernames[mention_text]]['discord']['id']
        elif item['type'] == 'text_mention':
            discord_user_id = users[from_telegram[item['user']['id']]]['discord']['id']
        mention_replace_list.append((mention_text, f'<@{discord_user_id}>'))

    for item in mention_replace_list:
        mensagem['text'] = mensagem['text'].replace(item[0], item[1], 1)

    return mensagem


async def resolve_author(mensagem):
    pass


async def handle(msg):
    chat_id = msg['chat']['id']
    autor = msg['from']
    autor_id = autor['id']
    autor_baia_id = from_telegram[autor_id]

    if chat_id != GROUP_ID or autor['is_bot']:
        return

    if 'text' not in msg.keys():
        sorry = f'Parece que o {autor["first_name"]} mandou algo lá no Telegram.\n'
        sorry += 'Infelizmente ainda não sei ler as figura.'

        discord_webhook['00'].send(sorry)
        return

    if 'entities' in msg.keys():
        msg = await resolve_mentions(msg)
    full_msg = msg['text']

    discord_webhook[autor_baia_id].send(full_msg)


telegram_bot = telepot.aio.Bot(TELEGRAM_TOKEN)
loop = asyncio.get_event_loop()

loop.create_task(MessageLoop(telegram_bot, handle).run_forever())
print('Listening...')

loop.run_forever()
