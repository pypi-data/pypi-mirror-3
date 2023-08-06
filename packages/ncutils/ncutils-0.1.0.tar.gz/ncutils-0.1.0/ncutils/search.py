import urllib, json, time
import logging
logger = logging.getLogger(__name__)

import network
import base
from video import Video

class Search(base.BaseObject):
    """Search object.

    niconico provides search API. We have two methods for searching video, one
    is keywordsearch, and the other is tagsearch. This class handles both by
    passing ''mode'' keword when instantiated.If you need more than 32 videoes,
    max_pages keyword is required.
    """

    def __init__(self, keyword, mode="keyword", max_pages=1):
        assert mode in ["keyword", "tag"]
        self.keyword = keyword
        self.mode = mode
        self.max_pages = max_pages

        self.prop_info = (
            ("status",      self._search),
            ("count",       self._search),
            ("page",        self._search),
            ("videolist",   self._search),
        )

    def _search(self):
        if self.mode == 'keyword':
            API_URL   = "http://www.nicovideo.jp/api/search/search/%s?" % (urllib.quote(self.keyword.encode("utf8")),)
        else:
            API_URL   = "http://www.nicovideo.jp/api/search/tag/%s?" % (urllib.quote(self.keyword.encode("utf8")),)

        self._videolist = []
        for i in range (self.max_pages):
            query_str = "mode=watch&order=d&page=%d&sort=n" % (i+1,)
            data = json.loads(network.urlopen(API_URL+query_str, "searchAPI", "search").read())

            self._status    = data["status"]
            self._count     = data["count"]
            self._page      = data["page"]

            for vinfo in data["list"]:
                video = Video(vinfo["id"])
                video._title = vinfo["title"]
                self._videolist.append(video)

            if (i+1) * 32 > self.count: #32 denotes items/search
                break
            time.sleep(1)

    def print_summary(self,enc="utf8"):
        print "Result for '%s'" %(self.keyword)
        print "Count:%d" % (self.count)
