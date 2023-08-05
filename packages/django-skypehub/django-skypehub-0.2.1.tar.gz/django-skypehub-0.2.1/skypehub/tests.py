from django.test import TestCase

from skypehub.decorators import skype_required
from skypehub.views import _list_chats, _post_message
from skypehub.utils import json
from skypehub.test import MockSkype, MockChat


class SkypeRequiredDecoratorTest(TestCase):
    def test_decorate(self):
        """skype_required decorator
        """
        decorated = skype_required(lambda req, skype: skype)
        self.assertNotEqual(decorated, None)


class SkypeViewListChatsTest(TestCase):
    def setUp(self):
        self.skype = MockSkype()
        self.chat = MockChat('chatname', 'topic')
        self.skype.add_chat(self.chat)

    def test_list_chats(self):
        response = _list_chats(None, self.skype)
        self.assertEqual(json.loads(response.content), {
          "chats": [
            {
              "topic": "topic",
              "name": "chatname"
            }
          ]
        })