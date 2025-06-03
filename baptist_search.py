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
from elasticsearch import Elasticsearch, exceptions

es_client = Elasticsearch(
    "https://localhost:9200",  # Elasticsearch endpoint
    api_key="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX==",
)





# Use your own values here
# Get them at api.telegram.org
api_id = NNNNNNNN
api_hash = 'XXXXXXXXXXXXXXXXXXXXXXXXXXX'
phone_number = '+NNNNNNNNNNN'

app = Client("my_account", api_id, api_hash, phone_number)
print(f'app started at {datetime.now()}')

girls = defaultdict(dict, {})
channels = defaultdict(dict, {})
source_girls_and_channels = defaultdict(list) #where I met them
private_channels = defaultdict(list)

channels_list = ['pogodki_11']

cities =  ['Москв', 'Питер', 'Санкт', 'Новосибирск', 'Екатеринбург', 'Липецк', 'Воронеж', 'Курск', 'Белгород', 'Шерегеш', 'Алта', 'Киев', 'Минск', 'Улан-Удэ', 'Кемеров', 'Омск']

@app.on_message(filters.command('girl'))
async def find_girls(client, message:types.Message):
	print('STARTED...')
	for chat in channels_list:
		if len(channels_list) > 500:
			break
		if chat != 'kanal_ne_prokanal' and chat != 'BooksAssistantrobot':
			print(f'Chat name: {chat}')

			first_message = await app.get_messages(chat, 1)
			channels[chat]['channel_creation'] = first_message.date
			try:
				es_client.update(index="baptist_channels", id=chat, doc={
				    "channel_creation_date": first_message.date
				})
			except exceptions.NotFoundError:
				pass

			async for post in app.get_chat_history(chat, limit=30):
				print(post.id, end='->')

				await asyncio.sleep(randint(1, 20))
				try:
					if post.caption:
						if any(word in post.caption for word in cities):
							es_client.index(
								index="baptist_geo",
								id=str(post.id) + '_' + chat,
								document={
									"channel_name": chat,
								    "post_text": post.caption,
								    "city": word
								}
							)
					
					if post.photo:
						await app.download_media(post.photo.file_id, file_name=f'/home/eduvm/{chat}/{post.photo.file_id}_{post.photo.date}.jpg')
					
				except:
					print('Error downloading text or photo')
				try:
					async for rep in app.get_discussion_replies(chat, post.id):
						if rep.from_user:
							user = rep.from_user

							source_girls_and_channels[user.id].append(chat)
							if not user.id in girls.keys() and not user.id in private_channels.keys():
								
								await asyncio.sleep(12)
								try:
									user_id = await app.resolve_peer(user.id)
									bio = await app.invoke(functions.users.GetFullUser(id=user_id))
									#print(bio)
									if bio.full_user.personal_channel_id:
										girls[user.id]['first_name'] = user.first_name
										girls[user.id]['last_name'] = user.last_name
										girls[user.id]['channel_id'] = bio.full_user.personal_channel_id
										girls[user.id]['channel_username'] = bio.chats[0].username
										girls[user.id]['channel_name'] = bio.chats[0].title
										girls[user.id]['channel_user_count'] = bio.chats[0].participants_count

										es_client.index(
										    index="baptist_channels",
										    id=bio.chats[0].username,
										    document={
										    	"channel_name": bio.chats[0].title,
										    	"channel_id": bio.full_user.personal_channel_id,
										        "user_id": user.id,
										        "user_first_name": user.first_name,
										        "user_last_name": user.last_name,
										        "channel_user_count": bio.chats[0].participants_count

										    }
										)


										if bio.chats[0].username not in channels_list:

											channels_list.append(bio.chats[0].username)
											print(f'Found chat from Premium user: {bio.chats[0].username}')

										#source_girls_and_channels[bio.chats[0].username].append(chat)
									else:
										about = bio.full_user.about
										if about:
											tg_channel_link = re.findall('https://t.me/([\w\d\-_+]+)', about)

											if tg_channel_link:
												for link in tg_channel_link:
													if link[0] != '+':
														girls[user.id]['first_name'] = user.first_name
														girls[user.id]['last_name'] = user.last_name
														girls[user.id]['channel_username'] = link
														if link not in channels_list:
															channels_list.append(link)

															print(f'Found chat from regular user: {link}')

														#source_girls_and_channels[link].append(chat)
													else:
														private_channels[user.id].append(link)
													try:
														chat_info = await app.get_chat(link)
														es_client.index(
														    index="baptist_channels",
														    id=link,
														    document={
														    	"channel_name": chat_info.title,
														        "user_id": user.id,
														        "user_first_name": user.first_name,
														        "user_last_name": user.last_name,
														        "channel_user_count": await app.get_chat_members_count(link)

														    }
														)
													except:
														pass
											else:
												pass
										else:
											pass
								except:
									pass

							else:
								pass
						else: 
							if rep.sender_chat.username is not None:
								source_girls_and_channels[rep.sender_chat.username].append(chat)
							else:
								pass
							if not rep.sender_chat.username in channels.keys() and rep.sender_chat.username is not None:
		 						channels[rep.sender_chat.username]['channel_name'] = rep.sender_chat.username
		 						channels[rep.sender_chat.username]['channel_id'] = rep.sender_chat.id
		 						#chat_comment = await app.get_chat(rep.sender_chat.id)
		 						#channels[rep.sender_chat.id]['bio'] = chat_comment.bio

		 						if rep.sender_chat.username not in channels_list:
		 							channels_list.append(rep.sender_chat.username)

		 							print(f'Found chat from discussion: {rep.sender_chat.username}')
		 						chat_info = await app.get_chat(rep.sender_chat.username)
		 						
		 						es_client.index(
									index="baptist_channels",
									id=rep.sender_chat.username,
									document={
										"channel_name": chat_info.title,
										"channel_id": rep.sender_chat.id,
										"channel_user_count": await app.get_chat_members_count(rep.sender_chat.username)

									}
								)	

				except MsgIdInvalid:
					print('Message not found or deleted')
				print('PARSING DONE!')
		
	print(f'All channels parsed: {channels_list}')
	print(f'Private channles: {private_channels}')

	with open('girls.json', 'w+', encoding='utf-8') as file:
		json.dump(girls, file, indent='\t', default=str)

	with open('channels.json', 'w+', encoding='utf-8') as file:
		json.dump(channels, file, indent='\t', default=str)

	with open('source_girls_and_channels.json', 'w+', encoding='utf-8') as file:
		json.dump(source_girls_and_channels, file, indent='\t', default=str)

	print(f'app finished at {datetime.now()}')


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
