import asyncio
from pyrogram import Client, filters, types, enums
from pyrogram.handlers import MessageHandler
import os
import json
from datetime import datetime
from pyrogram.errors.exceptions.bad_request_400 import MsgIdInvalid
from collections import defaultdict
from pyrogram.raw import functions, types
from random import randint
import re


# Use your own values here
api_id = 20158386
api_hash = '2516d92450ed017c8a976d1838ab2558'
phone_number = '+79277998905'

app = Client("my_account", api_id, api_hash, phone_number)
print(f'app started at {datetime.now()}')

girls = defaultdict(dict, {})
channels = defaultdict(dict, {})
source_girls_and_channels = defaultdict(list) #where I met them
private_channels = defaultdict(list)

channels_list = ['anastasiaalabugina']

cities =  ['Москв', 'Питер', 'Санкт', 'Новосибирск', 'Екатеринбург', 'Липецк', 'Воронеж', 'Курск', 'Белгород', 'Шерегеш', 'Алта', 'Киев', 'Минск', 'Улан-Удэ', 'Кемеров']

@app.on_message(filters.command('girl'))
async def find_girls(client, message:types.Message):
  #chat = 'pogodki_11' #channel
  print('STARTED...')
  for chat in channels_list:
    print(f'Chat name: {chat}')
    first_message = await app.get_messages(chat, 1)
    channels[chat]['channel_creation'] = first_message.date
    async for post in app.get_chat_history(chat, limit=10):
      #print('here')
      #print(post.id, end='->')

      await asyncio.sleep(randint(1, 20))
      #try:
        #if post.caption:
          #print(post.views)
          #if any(word in post.caption for word in cities):
            #print(post.caption)
        #if post.photo:
          #await app.download_media(post.photo.file_id, file_name=f'/home/eduvm/{chat}/{post.photo.file_id}_{post.photo.date}.jpg')
      try:
        async for rep in app.get_discussion_replies(chat, post.id):
          if rep.from_user:
            user = rep.from_user
            #print(user)
            if not user.id in girls.keys():
              
              await asyncio.sleep(12)
              user_id = await app.resolve_peer(user.id)
              bio = await app.invoke(functions.users.GetFullUser(id=user_id))
              if bio.full_user.personal_channel_id:
                girls[user.id]['first_name'] = user.first_name
                girls[user.id]['last_name'] = user.last_name
                girls[user.id]['channel_id'] = bio.full_user.personal_channel_id
                girls[user.id]['channel_username'] = bio.chats[0].username
                girls[user.id]['channel_name'] = bio.chats[0].title
                girls[user.id]['channel_user_count'] = bio.chats[0].participants_count

                channels_list.append(bio.chats[0].username)

                print(f'Found chat from Premium user: {bio.chats[0].username}')

                source_girls_and_channels[user.id].append(chat)
              else:
                about = bio.full_user.about
                tg_channel_link = re.findall(r'https://t.me/([\w\d\-_+]+)', about)
                if tg_channel_link[0] != '+':
                  girls[user.id]['first_name'] = user.first_name
                  girls[user.id]['last_name'] = user.last_name
                  girls[user.id]['channel_username'] = tg_channel_link

                  channels_list.append(tg_channel_link)

                  print(f'Found chat from regular user: {tg_channel_link}')

                  source_girls_and_channels[user.id].append(chat)
                else:
                  private_channels[user.id].append(tg_channel_link)

            else:
              pass
          else: 
             if not rep.sender_chat.id in channels.keys():
               channels[rep.sender_chat.username]['channel_name'] = rep.sender_chat.username
               channels[rep.sender_chat.username]['channel_id'] = rep.sender_chat.id
               chat_comment = await app.get_chat(rep.sender_chat.id)
               channels[rep.sender_chat.id]['bio'] = chat_comment.bio

               channels_list.append(rep.sender_chat.username)

               print(f'Found chat from discussion: {rep.sender_chat.username}')
               source_girls_and_channels[rep.sender_chat.username].append(chat)  

      except MsgIdInvalid:
        print('Message not found or deleted')
      print('PARSING DONE!')
    
  #print(girls)
  #print(channels)
  #print(source_girls_and_channels)
  print(f'All channels parsed: {channels_list}')
  print(f'Private channles: {private_channels}')

  with open('girls.json', 'w+', encoding='utf-8') as file:
    json.dump(girls, file, indent='\t')

  with open('channels.json', 'w+', encoding='utf-8') as file:
    json.dump(channels, file, indent='\t')

  with open('source_girls_and_channels.json', 'w+', encoding='utf-8') as file:
    json.dump(source_girls_and_channels, file, indent='\t')


'''
@app.on_message(filters.me & filters.command('read', prefixes='#'))
async def reader(client, message: types.Message):
  await asyncio.sleep(4)
  with open('chats.json', 'w+', encoding='utf-8') as file:
    chats_list = []
    async for dialog in app.get_dialogs():
      if dialog.chat.type == enums.ChatType.CHANNEL:
        chats_list.append(dialog.chat.id)
        print('here')
    json.dump(chats_list, file, indent='\t')
'''

try:
  app.run()
except KeyboardInterrupt:
  print('program finished')


'''
async def main():
    async with Client("my_account", api_id, api_hash, phone_number) as app:
        await app.send_message("me", "Greetings from **Pyrogram**!")


asyncio.run(main())
'''