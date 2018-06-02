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
        query = event.get_argument()

        if query:
            query = query.split()
            url = query[0] if match('\w+://', query[0]) else 'http://' + query[0]
            custom = query[1] if len(query) > 1 else None

            try:
                urlopen(url)
                sly = 'https://5ly.me/api/shorten.php?url=%s' % url

                if custom:
                    sly += '&custom=%s' % custom

                request = get(sly)

                if request.status_code == 200:
                    short = request.text
                    if short == 'Custom URL Not Available':
                        name = short
                        description = 'Please pick a different custom domain'
                        on_enter = None
                    else:
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
