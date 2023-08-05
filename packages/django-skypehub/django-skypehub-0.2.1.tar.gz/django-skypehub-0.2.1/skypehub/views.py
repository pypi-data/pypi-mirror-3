from django.http import HttpResponse

from skypehub.utils import json, SkypeError
from skypehub.decorators import skype_required
from skypehub.forms import PostMessageForm, PostUserMessageForm


def make_json_response(content, status=200):
    return HttpResponse(json.dumps(content, indent=2), content_type='application/javascript', status=status)


def _list_chats(request, skype):
    chats = []
    for chat in skype.Chats:
        chats.append({
            'name': chat.Name,
            'topic': chat.Topic,
        })
    return make_json_response({'chats': chats})

list_chats = skype_required(_list_chats)


def _post_message(request, skype):
    form = PostMessageForm(request.POST or None)
    try:
        if form.is_valid():
            chat = skype.Chat(form.cleaned_data['chat'])
            chat.SendMessage(form.cleaned_data['message'])
            return make_json_response({'result': 'ok'})
        else:
            form = PostUserMessageForm(request.POST or None)
            if form.is_valid():
                chat = skype.CreateChatWith(form.cleaned_data['username'])
                chat.SendMessage(form.cleaned_data['message'])
                return make_json_response({'result': 'ok'})
    except SkypeError, e:
        # Invalid chat name (errno=105)
        # or Sending a message to failes (errno=511)
        if e.args[0] in [105, 511]:
            return make_json_response({'result': e.args[1]}, status=403)
        else:
            raise e
    return  make_json_response({'result': 'validation error.'})

post_message = skype_required(_post_message)