import unittest
import jsonrpclib

class TestJsolait(unittest.TestCase):
    def test_heads(self):
        s = jsonrpclib.ServerProxy("http://127.0.0.1:8000/JSON", verbose=0)
        reply = s.heads()
        print reply
        #self.assert_(reply["result"] == "foo bar")

    def test_item(self):
        s = jsonrpclib.ServerProxy("http://127.0.0.1:8000/JSON", verbose=0)
        reply = s.heads()
        print reply
        itemlist = reply['result'][0]['commit']['tree']['contents']
        commit_id = reply['result'][0]['commit']['id']
        print
        #commit_id = 'f4a8b1fdd29350de0ee7af0c936fa9ecf40f1a47'
        print "commit_id", commit_id
        for item in itemlist:
            reply = s.item(commit_id, item, True)
            print "item", item, reply

        reply = s.itemspath(commit_id, "", itemlist, True)
        print
        print "including data", reply

        reply = s.items_in(commit_id, "pyjamas/public", True)
        print "jsonserver", reply
        #reply = s.items_in(0,  'dfff1d9185d19f509ec2e81b348ca39de2cb5aad', False)

        print 
        print "commit id", commit_id
        commit_id = 'f4a8b1fdd29350de0ee7af0c936fa9ecf40f1a47'

        reply = s.items_in_by_commit_id(commit_id, 'pyjamas', False)
        print reply

        reply = s.items_in_by_commit_id(commit_id, 'README', True)
        print "README", reply
        #self.assert_(reply["result"] == "foo bar")

        reply = s.commits()
        print "commits", reply

        commit_id = reply['result'][1]['id']
        print "commit_id", commit_id

        #self.assert_(reply["result"] == "foo bar")


if __name__=="__main__":
    unittest.main()
