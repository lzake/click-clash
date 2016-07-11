import json
from channels import Group
from channels.auth import channel_session_user_from_http, channel_session_user

def dump_to_ws_format(obj):
    return {'text': json.dumps(obj)}

### WebSocket handling ###


# This decorator copies the user from the HTTP session (only available in
# websocket.connect or http.request messages) to the channel session (available
# in all consumers with the same reply_channel, so all three here)
@channel_session_user_from_http
def ws_connect(message):
    mode = message.content['path'].strip("/")
#    if mode == 'scoreboard':
#        #message.channel_session['scoreboard'] = True
    Group('scoreboard').add(message.reply_channel)
    #else:
    #    message.channel_session['scoreboard'] = False
    Group('scoreboard').send(dump_to_ws_format({'action': 'update', 'user': message.user.username, 'count': message.user.counter.count}))


@channel_session_user
def ws_receive(message):
    payload = json.loads(message['text'])
    if payload.get('increment', False):
        message.user.counter.count += 1
        message.user.counter.save()
    message.reply_channel.send(dump_to_ws_format({'action': 'update_self', 'count': message.user.counter.count}))
    Group('scoreboard').send(dump_to_ws_format({'action': 'update', 'user': message.user.username, 'count': message.user.counter.count}))


@channel_session_user
def ws_disconnect(message):
    Group('scoreboard').discard(message.reply_channel)
    Group('scoreboard').send(dump_to_ws_format({'action': 'discard', 'user': message.user.username}))


