#!/usr/bin/env python

import logging
import os

from blessings import Terminal
from table import Table

class BlessingPainter(object):
    """
    A sample painter based on blessings package

    http://pypi.python.org/pypi/blessings
    """
    def __init__(self):
        self.term = Terminal()
        super(BlessingPainter, self).__init__()

    def _term_size(self):
        """
        Retrieve the size of the terminal

        @return (width, height)
        """
        return os.popen('stty size', 'r').read().split()

    def _format(self, tbl):
        """
        Format table based, according to metadata
        """
        if not tbl or not isinstance(tbl, Table):
            logging.error("unable to format table: invalid object")
            return False

    def enter_fullscreen(self):
        """
        Invoke before printing out anything.
        This method should be replaced by or merged to blessings package
        """
        self.term.stream.write(self.term.enter_fullscreen)
        self.term.stream.write(self.term.hide_cursor)

    def exit_fullscreen(self):
        """
        Invoke before printing out anything.
        This method should be replaced by or merged to blessings package
        """
        self.term.stream.write(self.term.exit_fullscreen)
        self.term.stream.write(self.term.normal_cursor)

    def paint(self, tbl):
        """
        Paint the table on terminal
        Currently only print out basic string format
        """
        if not isinstance(tbl, Table):
            logging.error("unable to paint table: invalid object")
            return False

#        self._format(tbl)
        self.term.stream.write(self.term.clear)

        self.term.stream.write(str(tbl))
        return True
