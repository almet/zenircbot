import json
import re
import requests
import sys

from zenircbot_api import ZenIRCBot, load_config


bot_config = load_config('../bot.json')

zen = ZenIRCBot(bot_config['redis']['host'],
                bot_config['redis']['port'],
                bot_config['redis']['db'])


ISSUE = re.compile('^#(\d*)| #(\d*)')
URL = 'https://api.github.com/repos/%s/issues/{nb}' % sys.argv[1]

sub = zen.get_redis_client().pubsub()
sub.subscribe('in')
for msg in sub.listen():
    if msg['type'] != 'message':
        continue
    message = json.loads(msg['data'])
    if message['version'] == 1:
        if message['type'] == 'privmsg':
            text = message['data']['message']
            match = ISSUE.match(text)
            if match:
                issue_nb = match.groups()[0] or match.groups()[1]
                resp = requests.get(URL.format(nb=issue_nb))
                msg = "{title} ({state}) - {html_url}".format(**resp.json)
                zen.send_privmsg(message['data']['channel'], msg)
