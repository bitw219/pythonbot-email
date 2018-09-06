#from flask import Flask
#app = Flask(__name__)

from aiohttp import web
from botbuilder.schema import (Activity, ActivityTypes)
from botbuilder.core import (BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext,
                             ConversationState, MemoryStorage, UserState)
                             
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

APP_ID = 'af32d6e1-a97d-435b-a53a-783ec997eccc'
APP_PASSWORD = 'scDOOQ5}xzablKZD7275+);'
PORT = 9000
#EMAILS = ['aatish.jain@ellicium.com','shubham.shirude@ellicium.com','sonali.dorle@ellicium.com']
EMAILS = ['parasmk@gmail.com','sonali.dorle@ellicium.com']
SETTINGS = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)

# Create MemoryStorage, UserState and ConversationState
memory = MemoryStorage()
# Commented out user_state because it's not being used.
# user_state = UserState(memory)
conversation_state = ConversationState(memory)

# Register both State middleware on the adapter.
# Commented out user_state because it's not being used.
# ADAPTER.use(user_state)
ADAPTER.use(conversation_state)


async def create_reply_activity(request_activity, text) -> Activity:
    return Activity(
        type=ActivityTypes.message,
        channel_id=request_activity.channel_id,
        conversation=request_activity.conversation,
        recipient=request_activity.from_property,
        from_property=request_activity.recipient,
        text=text,
        service_url=request_activity.service_url)


async def handle_message(context: TurnContext) -> web.Response:
    # Access the state for the conversation between the user and the bot.
    state = await conversation_state.get(context)

    if hasattr(state, 'counter'):
        state.counter += 1
    else:
        state.counter = 1

    send_email(context.activity.text)
    response = await create_reply_activity(context.activity, f'{state.counter}: Following message has been emailed to client support: {context.activity.text}. We will get back shortly.')
    await context.send_activity(response)
    return web.Response(status=202)


async def handle_conversation_update(context: TurnContext) -> web.Response:
    if context.activity.members_added[0].id != context.activity.recipient.id:
        response = await create_reply_activity(context.activity, 'Welcome to the Ellicium Client Support Bot!')
        await context.send_activity(response)
    return web.Response(status=200)


async def unhandled_activity() -> web.Response:
    return web.Response(status=404)


async def request_handler(context: TurnContext) -> web.Response:
    if context.activity.type == 'message':
        return await handle_message(context)
    elif context.activity.type == 'conversationUpdate':
        return await handle_conversation_update(context)
    else:
        return await unhandled_activity()


async def messages(req: web.web_request) -> web.Response:
    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers['Authorization'] if 'Authorization' in req.headers else ''
    try:
        return await ADAPTER.process_activity(activity, auth_header, request_handler)
    except Exception as e:
        raise e

def send_email(msg_body):
  #msg_body = 'Farhan IS HERE'
  SUBJECT = 'BOT MESSAGE'
  msg = MIMEMultipart()
  msg.attach(MIMEText(msg_body,'plain'))
  message = 'Subject: {}\n\n{}'.format(SUBJECT, msg_body)
  server = smtplib.SMTP('smtp.gmail.com',25)
  server.ehlo()
  server.starttls()
  server.ehlo()
  server.login("aatish.jain@ellicium.com","9921610239")
  server.sendmail("aatish.jain@ellicium.com",EMAILS,message)
  server.quit()
  return msg_body

app = web.Application()
app.router.add_post('/api/messages', messages)

try:
    web.run_app(app, host='localhost', port=PORT)
    #web.run_app(app)
except Exception as e:
    raise e
