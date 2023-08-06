from rwb.lib.decorators import cached_property
from logobjects import RobotSuite, RobotTest, RobotKeyword, RobotMessage, RobotStatistics
from logobjects import RobotLog
import xml.etree.ElementTree as ET
import ttk

'''
The following provides an OO interface to the data in
a robot output.xml file

A note on performance:

on my box, this code can zip through 10 suites * 100 tests * 2
keywords in under half a second. Bitchin'

toolbar: toggle all suites, all test cases, all first-level keywords, all keywords
[Suites] [Test Cases] [Keywords] [All Keywords] 

'''

class LogTree(ttk.Frame):
    def __init__(self, *args, **kwargs):
        ttk.Frame.__init__(self, *args, **kwargs)

        self.tree = ttk.Treeview(self, columns=("starttime", "endtime"), 
                                 displaycolumns="")
        self.tree.pack(side="top", fill="both", expand=True)

        self.tree.heading("starttime", text="Start Time")
        self.tree.heading("endtime", text="End Time")
        self.tree.column("starttime", width=100, stretch=False)
        self.tree.column("endtime", width=100, stretch=False)

        self.tree.tag_configure("DEBUG", foreground="gray")
        self.tree.tag_configure("TRACE", foreground="gray")
        self.tree.tag_configure("ERROR", background="#FF7e80")
        self.tree.tag_configure("FAIL", foreground="#b22222")
        self.tree.tag_configure("PASS", foreground="#009900")
        self.tree.tag_configure("WARN", background="#ffff00")

    def refresh(self, path=None):
        parser = RobotLog()
        parser.parse(sys.argv[1])
#            parser.parse(sys.argv[1])
        self.suites = parser.suites
        for item in self.tree.get_children(""):
            self.tree.delete(item)

        for suite in self.suites:
            self.after_idle(lambda suite=suite: self._add_suite(suite))

    def expand_all(self, node=""):
        self.tree.item(node, open=True)
        for child in self.tree.get_children(node):
            self.expand_all(child)

    def _add_test(self, test, parent_node=None):
        node = self.tree.insert(parent_node, "end", 
                                text=test.name,
                                values=(test.starttime,test.endtime),
                                open=True,
                                tags=("test",test.status))
        for kw in test.keywords:
            self._add_keyword(kw, parent_node=node)

    def _add_keyword(self, kw, parent_node=None):
        text = " | ".join([kw.name] + kw.args)
        kw_node = self.tree.insert(parent_node, "end", 
                                   text=text,
                                   values=(kw.starttime,kw.endtime),
                                   open=True,
                                   tags=("keyword",kw.status))

        # I think instead of doing sub-keywords and then messages,
        # I probably need to process children in order.
        for child_kw in kw.keywords:
            self._add_keyword(child_kw, parent_node=kw_node)

        for msg in kw.messages:
            self.tree.insert(kw_node, "end",
                             text="=> " + msg.text,
                             values=(msg.starttime, msg.endtime),
                             open=False,
                             tags=("message", msg.level))
                
            
    def _add_suite(self, suite, parent_node=""):
        tags=("foo",)
        node = self.tree.insert(parent_node, "end", 
                                text=suite.name,
                                values=(suite.starttime,suite.endtime),
                                open=True,
                                tags=("suite", suite.status))

        if hasattr(suite, "suites"):
            for child_suite in suite.suites:
                self.after_idle(lambda suite=child_suite: self._add_suite(suite, parent_node=node))

        if hasattr(suite, "tests"):
            # for performance reasons, only auto-open test suite directories
            if len([x for x in suite.tests]) > 0:
                self.tree.item(node, open=False)
            for test in suite.tests:
                self.after_idle(lambda test=test: self._add_test(test, parent_node=node))
            
if __name__ == "__main__":
    import sys
    import Tkinter as tk
    import ttk

    class SampleApp(tk.Tk):
        def __init__(self):
            tk.Tk.__init__(self)
            toolbar = tk.Frame(self)
            toolbar.pack(side="top", fill="x")
            button = tk.Button(self, text="Refresh", command=self.refresh)
            button.pack(in_=toolbar, side="left")
            b2 = tk.Button(self, text="Expand all", command=self.expand_all)
            b2.pack(in_=toolbar, side="left")
            ttk.Separator(toolbar, orient="vertical").pack(side="left", padx=4, fill="y", pady=2)
            for label in ("Suites", "Test Cases", "Test Keywords", "All Keywords"):
                b = tk.Button(self, text=label)
                b.pack(in_=toolbar, side="left", padx=(4,0))
            self.tree = LogTree(self)
            self.tree.pack(side="top", fill="both", expand=True)

        def expand_all(self):
            self.tree.expand_all()

        def refresh(self):
            self.tree.refresh(sys.argv[1])

#            self.after_idle(self.tree.refresh, sys.argv[1])
#             self.tree = ttk.Treeview(self, columns=("starttime", "endtime"), 
#                                      displaycolumns="")
#             self.tree.pack(side="top", fill="both", expand=True)

#             self.tree.heading("starttime", text="Start Time")
#             self.tree.heading("endtime", text="End Time")
#             self.tree.column("starttime", width=100, stretch=False)
#             self.tree.column("endtime", width=100, stretch=False)

#             self.tree.tag_configure("DEBUG", foreground="gray")
#             self.tree.tag_configure("TRACE", foreground="gray")
#             self.tree.tag_configure("ERROR", background="#FF7e80")
#             self.tree.tag_configure("FAIL", foreground="#b22222")
#             self.tree.tag_configure("PASS", foreground="#009900")
#             self.tree.tag_configure("WARN", background="#ffff00")

                
    app = SampleApp()
    app.mainloop()


