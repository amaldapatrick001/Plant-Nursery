from asterisk.ami import AMIClient, SimpleAction
from django.conf import settings

class AsteriskHandler:
    def __init__(self):
        self.client = AMIClient(
            host=settings.ASTERISK_HOST,
            port=settings.ASTERISK_PORT
        )
        self.client.login(
            username=settings.ASTERISK_USERNAME,
            secret=settings.ASTERISK_SECRET
        )

    def schedule_call(self, from_number, to_number):
        action = SimpleAction(
            'Originate',
            Channel=f'SIP/{from_number}',
            Exten=to_number,
            Context='from-internal',
            Priority=1,
            Timeout=30000
        )
        return self.client.send_action(action)

    def send_notification(self, to_number, message):
        # Use a text-to-speech service or pre-recorded message
        action = SimpleAction(
            'Originate',
            Channel=f'SIP/{to_number}',
            Application='Playback',
            Data=f'custom/{message}',
            Priority=1
        )
        return self.client.send_action(action) 