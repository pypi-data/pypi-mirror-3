import logging, re, urllib, urllib2
import json

import base
import network

from video import Video
from mylist import Mylist

logger = logging.getLogger(__name__)

class Watch(base.BaseObject):
    """Watch objects, such as favorite mylists, favorites users, and so on.

    Attributes to be noted
        - mylists
    """

    def __init__(self):
        base.BaseObject.__init__(self)
        self.prop_info = (
            #watchtoken
            ("oldtoken",   self._gettoken),
            ("token",       self._gettoken),
        )

    def _gettoken(self):
        html = network.urlopen("http://www.nicovideo.jp/my/fav/mylist").read()
        token_re = r'''csrf_token = '([^']+)';'''
        oldtoken_re = r'''old_csrf_token = '([^']+)';'''

        self._token     = re.search(token_re, html).group(1)
        self._oldtoken = re.search(oldtoken_re, html).group(1)

    def add_mylist(self, mlist):
        req = urllib2.Request("http://www.nicovideo.jp/api/watchitem/add")
        data = {
            "item_type":    7,
            "item_id":      mlist.mid,
            "token":        mlist.favtoken,
        }
        req.add_data(urllib.urlencode(data))
        res = json.loads( network.urlopen(req).read() )
        return res['status'] == 'ok'

    def remove_mylist(self,mlist):
        req = urllib2.Request("http://www.nicovideo.jp/api/watchitem/delete")
        data = {
            "id_list[7][]": mlist.mid,
            "token":        self.oldtoken,
        }
        req.add_data(urllib.urlencode(data))
        res = json.loads( network.urlopen(req, "WatchAPI", "watchitem/delete").read() )
        return res['status'] == 'ok'

