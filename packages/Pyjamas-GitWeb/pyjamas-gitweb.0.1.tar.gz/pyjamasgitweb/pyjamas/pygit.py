import pyjd # dummy in pyjs

from pyjamas.ui.RootPanel import RootPanel
from pyjamas.ui.TextArea import TextArea
from pyjamas.ui.Label import Label
from pyjamas.ui.Button import Button
from pyjamas.ui.HTML import HTML
from pyjamas.ui.Hyperlink import Hyperlink
from pyjamas import History
from pyjamas.ui.Grid import Grid
from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.HorizontalPanel import HorizontalPanel
#from pyjamas.ui.ScrollPanel import ScrollPanel
#from pyjamas.ui.DialogBox import DialogBox
from pyjamas.JSONService import JSONProxy
from pyjamas import DOM
from __pyjamas__ import doc
import gitjson
import base64
from pyjamas import Window

# sadly both of these are too heavy.
#import cgi
#import htmlentitydefs

def escape(s, quote=None):
    '''Replace special characters "&", "<" and ">" to HTML-safe sequences.
    If the optional flag quote is true, the quotation mark character (")
    is also translated.'''
    s = s.replace("&", "&amp;") # Must be done first!
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    if quote:
        s = s.replace('"', "&quot;")
    return s

def process_item_to_html(item):
    if item.mimetype.startswith("text/") or \
       item.mimetype.startswith("application-x-httpd-php") or \
       item.mimetype in ["application/x-javascript",
                         "application/x-sh"]:
        txt = base64.b64decode(item.data)

        # this turns out to be too heavy in pyjs: use escape instead
        #for c in txt:
        #    rep = htmlentitydefs.codepoint2name.get(ord(c))
        #    if rep:
        #        res += "&%s;" % rep
        #    else:
        #        res += c
        
        # import cgi too heavy on pyjd.  copy function to here.
        txt = escape(txt, quote=True)
        txt = "<pre>%s</pre>" % txt
    else:
        txt = item.data
    return txt


class StyleSheetCssChanger:

    def __init__(self, text=''):
        self._e = DOM.createElement('style')
        self._e.setAttribute('type', 'text/css')
        DOM.appendChild(self._e, doc().createTextNode(text))

        doc().getElementsByTagName("head").item(0).appendChild(self._e)
      
    def remove(self):
        parent = DOM.getParent(self._e)
        DOM.removeChild(parent, self._e) 
        
styles = """
<!--
.codetitle {
  background-color: #C3D9FF;
  padding: 3px;
  margin: 2px;
  font-weight: bold;
}

.codetext {
    text-align: left;
    font-size: 80%;
  padding: 3px;
  margin: 2px;
  border: 2px outset;
}

.gwt-DialogBox {
  sborder: 8px solid #C3D9FF;
  border: 2px outset;
  background-color: white;
}

.gwt-DialogBox .Caption {
  background-color: #C3D9FF;
  padding: 3px;
  margin: 2px;
  font-weight: bold;
  cursor: default;
}
--> 
"""

class JSONRPCExample:
    def onModuleLoad(self):
        self.TEXT_WAITING = "Waiting for response..."
        self.TEXT_ERROR = "Server Error"

        self.remote = GitService()
        self.grid = Grid()

        self.status = Label()
        self.back_button = Hyperlink()
        
        self.cache_items = {}
        self.cache_files = {}

        self.root_commits = {}
        self.heads = Grid()
        self.commits = Grid()
        self.file_view = HTML(StyleName="codeview")
        self.file_title = HTML("File Viewer", StyleName="codetitle")

        method_panel = VerticalPanel()
        method_panel.add(HTML("Branches", StyleName="codetitle"))
        method_panel.add(self.heads)
        method_panel.add(HTML("Commits", StyleName="codetitle"))
        method_panel.add(self.commits)
        method_panel.setSpacing(8)

        self.buttons = HorizontalPanel()
        self.buttons.add(self.back_button)
        self.buttons.setSpacing(8)
        
        l = Window.getLocation()
        d = l.getSearchDict()
        self.repo = d.get('repo', 'pyjamas.git')

        info = """<h2>Git Repository Viewer: %s</h2>
           """ % self.repo
        
        panel = VerticalPanel()
        panel.add(HTML(info))
        panel.add(method_panel)
        panel.add(self.buttons)
        panel.add(self.grid)
        panel.add(self.file_title)
        panel.add(self.file_view)
        panel.add(self.status)
        
        RootPanel().add(panel)

        History.addHistoryListener(self)

        self.remote.heads(self.repo, self)
        self.remote.commits(self.repo, self)

        self.initial_token = History.getToken()

    def onHistoryChanged(self, token):
        tokens = token.split("&")
        kw = {}
        for token in tokens:
            eq = token.find("=")
            kw[token[:eq]] = token[eq+1:]
        self.text = kw['file']
        self.cid = kw['id']

        print "onhistory", kw

        cache_key = '%s:%s' % (self.cid, self.text)

        if self.text == '':
            top_commit = self.root_commits[self.cid]
            if self.cache_items.has_key(cache_key):
                response = self.cache_items[cache_key]
                self.setupTree(self.cid, self.text, response)
            else:
                self.remote.items(self.repo, self.cid, top_commit.tree.contents, False,
                                  self)
        else:
            if kw.has_key('mimetype'):
                if self.cache_files.has_key(cache_key):
                    response = self.cache_files[cache_key]
                    self.popupItem(self.text, response)
                else:
                    self.remote.item(self.repo, self.cid, self.text, True, self)
            else:
                if self.cache_items.has_key(cache_key):
                    response = self.cache_items[cache_key]
                    self.setupTree(self.cid, self.text, response)
                else:
                    self.remote.items_in(self.repo, self.cid, self.text, self)

    def onRemoteResponse(self, response, request_info):
        method = request_info.method
    
        if method == 'heads':
            self.heads.resize(1 + len(response), 2)
            self.heads.setHTML(0, 0, "Branch Name")
            for (i, item) in enumerate(response):
                self.root_commits[item.commit.id] = item.commit
                b = create_hyperlink(item.name, '',
                                id=item.commit.id)
                self.heads.setWidget(i+1, 0, b)
        elif method == 'commits':
            self.commits.resize(1 + len(response), 3)
            self.commits.setHTML(0, 0, "Date")
            self.commits.setHTML(0, 1, "Commit")
            self.commits.setHTML(0, 2, "Comment")
            for (i, item) in enumerate(response):
                self.root_commits[item.id] = item
                b = create_hyperlink(item.id, '',
                                id=item.id)
                comment = HTML(item.message[:35], WordWrap=False)
                d = HTML(item.committed_date, WordWrap=False)
                self.commits.setWidget(i+1, 0, d)
                self.commits.setWidget(i+1, 1, b)
                self.commits.setWidget(i+1, 2, comment)
                if i == 0:
                    History.newItem(b.targetHistoryToken)
        elif method == 'items_in' or method == 'items':
            self.cache_items["%s:%s" % (self.cid, self.text)]= response
            self.setupTree(self.cid, self.text, response)
            if self.initial_token:
                slash = self.text.rfind("/")
                if slash >= 0:
                    self.text = self.txt[:slash]
                tok = self.initial_token
                self.initial_token = None
                History.newItem(tok)
                self.onHistoryChanged(tok)

        elif method == 'item':
            html = process_item_to_html(response)
            self.cache_files["%s:%s" % (self.cid, self.text)] = html
            self.popupItem(self.text, html)

    def popupItem(self, path, txt):
        self.file_title.setHTML(path)
        self.file_view.setHTML(txt)
        #db = DialogBox(modal=False, centered=True, Closeable=True, HTML=path)
        #txt = HTML(txt, StyleName="codetext")
        #sp = ScrollPanel(Width="40em", Height="600px")
        #sp.setWidget(txt)
        #db.setWidget(sp)
        #db.show()

    def onRemoteError(self, code, errobj, request_info):
        # onRemoteError gets the HTTP error code or 0 and
        # errobj is an jsonrpc 2.0 error dict:
        #     {
        #       'code': jsonrpc-error-code (integer) ,
        #       'message': jsonrpc-error-message (string) ,
        #       'data' : extra-error-data
        #     }
        message = errobj['message']
        if code != 0:
            self.status.setText("HTTP error %d: %s" % 
                                (code, message))
        else:
            code = errobj['code']
            self.status.setText("JSONRPC Error %s: %s" %
                                (code, message))

    def setupTree(self, parent_id, text, contents):
        # TODO: make this a series of back_buttons
        dirbelow = "/".join(text.split("/")[:-1])
        set_hyperlink(self.back_button, "{%s} %s" % (self.cid, text),
                      dirbelow, id=self.cid)
        self.grid.resize(1 + len(contents), 3)
        self.grid.setHTML(0, 0, "Mode")
        self.grid.setHTML(0, 1, "Name")
        self.grid.setHTML(0, 2, "Size")
        print contents
        for (i, item) in enumerate(contents):
            if text == '':
                newname = item.name
            else:
                newname = "%s/%s" % (text, item.name)
            if isinstance(item, gitjson.Blob):
                b = create_hyperlink(item.name, newname,
                                id=self.cid, mimetype=item.mimetype)
                size = str(item.size)
            else:
                b = create_hyperlink(item.name, newname,
                                id=self.cid)
                size = "&nbsp;"
            self.grid.setHTML(i+1, 0, item.mode)
            self.grid.setWidget(i+1, 1, b)
            self.grid.setHTML(i+1, 2, size)

def set_hyperlink(h, displayname, filename, **kwargs):
    tok = "file=%s" % filename
    for (k, v) in kwargs.items():
        tok += "&%s=%s" % (k, v)
    h.setText(displayname)
    h.setTargetHistoryToken(tok)

def create_hyperlink(displayname, filename, **kwargs):
    h = Hyperlink()
    set_hyperlink(h, displayname, filename, **kwargs)
    return h

class GitService(JSONProxy):
    def __init__(self):
        JSONProxy.__init__(self, "/JSON",
                            ["heads", "commits",
                             "item",
                             "items",
                             "items_in",
                            ])

if __name__ == '__main__':
    pyjd.setup("http://127.0.0.1:8000/JSONRPCExample.html?repo=seikatsu.be")
    StyleSheetCssChanger(styles)
    app = JSONRPCExample()
    app.onModuleLoad()
    pyjd.run()

