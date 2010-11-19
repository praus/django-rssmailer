from django.test import TestCase

from models import EntryHash
from tasks import feeder

class MatcherTest(TestCase):
    def setUp(self):
        self.entries = [
            {'title': '1'},
            {'title': '2'},
            {'title': '3'},
            {'title': '4'},
            {'title': '5'},
        ]
        
        self.seen_hashes = [
        'c4ca4238a0b923820dcc509a6f75849b', # 1
        #'c81e728d9d4c2f636f067f89cc14862c', # 2
        'eccbc87e4b5ce2fe28308fd9f2a7baf3', # 3
        #'a87ff679a2f3e71d9181a67b7542122c', # 4
        'e4da3b7fbbce2345d7772b0674a318d5', # 5
        ]
        self.seen = map(lambda hash: EntryHash(hash).save(), self.seen_hashes)
        
    def test_matcher(self):
        """
        Tests that matcher correctly identifies new and seen entries.
        """
        new_entries = feeder.matcher(self.entries)
        new_hashes = map(lambda e: e[0], new_entries)
        
        self.failUnless(len(new_entries) == 2 and
                    new_hashes[0] == 'c81e728d9d4c2f636f067f89cc14862c' and
                    new_hashes[1] == 'a87ff679a2f3e71d9181a67b7542122c',
                    "new_entries has wrong number of elements or wrong elements.")

