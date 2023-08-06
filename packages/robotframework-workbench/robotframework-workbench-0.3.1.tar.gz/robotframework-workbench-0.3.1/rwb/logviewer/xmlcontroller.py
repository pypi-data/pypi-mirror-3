import xml.etree.ElementTree as ET
#from listener import RemoteRobotListener
import logging
import os
import threading
import Queue

'''
*SIGH* This works but is *dreadfully* slow (but still much faster than firefox "expand all")

Pushing things on the queue seems lickety split, but 
updating the tree is crazy slow.

New game plan:
    only load suites initially, then go back and do test cases
'''

class ThreadedXMLParser(threading.Thread):
    def __init__(self, queue, filename):
        threading.Thread.__init__(self)
        self.filename = filename
        self._queue = queue
        self._stop_requested = False

    def abort(self):
        self._stop_requested = True

    def run(self):
        tree = ET.parse(self.filename)
        root = tree.getroot()
        if root.tag != "robot":
            raise Exception("expect root tag 'keywordspec', got '%s'" % root.tag)

        print "starting the parsing process..."
        import sys; sys.stdout.flush()
        for suite in root.findall("suite"):
            if self._stop_requested: return
            self._load_suite(suite, [])
        print "done with the parsing process..."
        import sys; sys.stdout.flush()

    def _load_suite(self, suite, ancestors):
        '''Load the given suite'''
        doc = suite.find("doc")
        longname = ".".join(ancestors + [suite.get("name")])
        status = suite.find("status")
        attrs = {
            "longname": longname,
            "doc": doc.text if doc is not None else "",
            "metadata": [],
            "suites": [s.get("name") for s in suite.findall("suite")],
            "tests": [t.get("name") for t in suite.findall("test")],
            "totaltests": 0,
            "starttime": status.get("starttime"),
            }
        if self._stop_requested: return
        self._add_to_queue("start_suite", suite.get("name"), attrs)

        ancestors = ancestors + [suite.get("name")]
        for child_suite in suite.findall("suite"):
            if self._stop_requested: return
            self._load_suite(child_suite, ancestors)
        if self._stop_requested: return
        print "loading tests..."
        import sys; sys.stdout.flush()
        for child_test in suite.findall("test"):
            if self._stop_requested: return
            self._load_test(child_test, ancestors)
        print "done loading tests..."
        import sys; sys.stdout.flush()

        if self._stop_requested: return
        attrs = {
            "longname": longname,
            "doc": doc.text if doc is not None else "",
            "metadata": [],
            "starttime": status.get("starttime"),
            "endtime": status.get("endtime"),
            "status": status.get("status"),
            "critical": status.get("critical"),
            }
        self._add_to_queue("end_suite", suite.get("name"), attrs)

    def _load_test(self, test, ancestors=[]):
        if self._stop_requested: return
        doc = test.find("doc")
        longname = ".".join(ancestors + [test.get("name")])
        status = test.find("status")
        attrs = {
            "longname": longname,
            "doc": doc.text if doc is not None else "",
            "tags": [],
            "critical": status.get("critical"),
            "template": "",
            "starttime": status.get("starttime"),
            "status": status.get("status"),
            }
        self._add_to_queue("start_test", test.get("name"), attrs)
        for kw in test.findall("kw"):
            self._load_keyword(kw)
            
        self._add_to_queue("end_test", test.get("name"), attrs)

    def _load_keyword(self, kw, ancestors=[]):
        kwstatus = kw.find("status")
        attrs = {
            "type": kw.get("type"),
            "doc": "<fixme>", 
            "starttime": kwstatus.get("starttime"),
            "endtime": kwstatus.get("endtime"),
            "status": kwstatus.get("status"),
            "args": [],
            }
#        print "FIXME: messages is busted because it takes fewer args than other events"
        # for msg in kw.findall("msg"):
        #     self._add_to_queue("log_message", "log_message", {
        #             "message": msg.text,
        #             "level": msg.get("level"),
        #             "timestamp": msg.get("timestamp"),
        #             "html": "unknown"
        #             })

        self._add_to_queue("start_keyword", kw.get("name"), attrs)
        self._add_to_queue("end_keyword", kw.get("name"), attrs)
        
    def _add_to_queue(self, event, name, attrs):
        self._queue.put((event, (name, attrs)))

if __name__ == "__main__":
    import sys
    import Tkinter as tk
    import rwb.runner
    from rwb.runner import RobotLogTree, RobotLogMessages

    def expand_all(node=""):
        global tree
        print "expanding..."; sys.stdout.flush()
        tree.expand_all()
        print "done expanding"; sys.stdout.flush()

    root = tk.Tk()
    button = tk.Button(root, text="Expand All", command=expand_all)
    button.pack(side="top")
    tree = RobotLogTree(root)
    tree.pack(fill="both", expand=True)
    tree.autoscroll=False
    tree.auto_open=["failed"]
    msgs = RobotLogMessages(root)
    msgs.pack(fill="both", expand=True)
    
    tree.reset()
    msgs.reset()
    q = Queue.Queue()
    f = sys.argv[1]
    p = ThreadedXMLParser(q,f)
    p.start()

    def poll(root, q):
        try:
            # process in blocks of 100, otherwise it's just too slow
            # 100 is arbitrary, but 1000 clogs the pipes
            for i in range(200):
                result = q.get(block=False)
                if result is not None:
                    tree.listen(1, *result)
                    msgs.listen(1, *result)
        except Queue.Empty:
            pass

        root.after(10, poll, root, q)

    root.after_idle(poll, root, q)
    root.mainloop()

    print "now, waiting to join()"
    p.join()
    print "joined."
    print "done."
