from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from requests import get
from urllib2 import urlopen, URLError
from re import match


class Shortener(Extension):

    def __init__(self):
        super(Shortener, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        query = event.get_argument() if match('\w+://', event.get_argument()) else 'http://' + event.get_argument()

        try:
            urlopen(query)
            request = get('https://5ly.me/api/shorten.php?url=%s' % query)
            if request.status_code == 200:
                short = request.text
                name = 'Shortened URL: %s' % short
                description = 'Copy to clipboard'
                on_enter = CopyToClipboardAction(short)
            else:
                name = 'Oops... Something went wrong (Returned code: %s)' % request.status_code
                description = 'Please try again'
                on_enter = HideWindowAction()
        except (URLError, ValueError):
            name = 'Not a valid URL'
            description = 'Please check if this URL actually exists and try again'
            on_enter = HideWindowAction()

        item = [ExtensionResultItem(icon='images/icon.png', name=name, description=description, on_enter=on_enter)]
        return RenderResultListAction(item)

if __name__ == '__main__':
    Shortener().run()
