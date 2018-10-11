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

    errors = {
        400: ('Bad Request', 'Please check if this URL actually exists and try again'),
        406: ('Not Acceptable', 'Please pick a different custom domain'),
        502: ('Bad Gateway', 'Our rate limit was exceeded (please tray again later)'),
        503: ('Service Unavailable', 'Service is down')
    }

    def on_event(self, event, extension):
        query = event.get_argument()

        if query:
            query = query.split()
            url = query[0] if match('\w+://', query[0]) else 'http://' + query[0]
            custom = query[1] if len(query) > 1 else None

            if not (5 <= len(custom) <= 30 and custom.replace("_", "").isalnum()):
                name = 'Invalid custom name'
                description = 'Must be 5-30 characters long and contain only english characters.'
                on_enter = HideWindowAction()
            else:
                try:
                    urlopen(url)
                except (URLError, ValueError):
                    name = 'Not a valid URL'
                    description = 'Please check if this URL actually exists and try again'
                    on_enter = HideWindowAction()
                else:
                    req_url = 'https://is.gd/create.php?format=simple&url=%s' % url

                    if custom:
                        req_url += '&shorturl=%s' % custom

                    request = get(req_url)

                    if request.status_code == 200:
                        short = request.text
                        name = 'Shortened URL: %s' % short
                        description = 'Copy to clipboard'
                        on_enter = CopyToClipboardAction(short)
                    else:
                        name = ('Oops... (Error: %s - %s)'
                            % (request.status_code, self.errors[request.status_code][0]))
                        description = self.errors[request.status_code][1]
                        on_enter = HideWindowAction()

            item = [ExtensionResultItem(icon='images/icon.png', name=name, description=description, on_enter=on_enter)]
            return RenderResultListAction(item)

if __name__ == '__main__':
    Shortener().run()
