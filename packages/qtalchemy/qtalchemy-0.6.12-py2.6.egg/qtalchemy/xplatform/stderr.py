# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
##############################################################################
"""
This module contains tools to enable cross platform support.

For the most part, we have functions here which do something for windows 
and something else for everything else.
"""

class StdErrEater(object):
    """
    Instead of printing to stderr a GUI app may want to log the stderr stream 
    to a text file.  This is particularly relevant in cross-platform situations 
    because py2exe logs and messages the user at app exit.  We'd like to have a 
    friendlier approach.
    
    For windows, future possibilities include directing stderr lines to the 
    windows event log.
    """
    
    # we ignore some errors we expect and don't care about
    ignore_these = [
        "does *not* support Decimal objects natively, and SQLAlchemy must convert from floating point"]

    def __init__(self):
        self.file = None
    
    def init_file(self):
        import tempfile
        import os
        import datetime
        x = tempfile.gettempdir()
        file_name = os.path.join(x,"camp_rental_error_{date}_{pid}.log".format(date=datetime.date.today().strftime("%Y%m%d"),pid=0))
        self.file = open(file_name,"a")
        self.file.write( """\
The following errors were logged during this program.  Please consider sending 
them to joel@kiwistrawberry.us for him to fix.  He might further inquire about 
whether you can reproduce the problem, but it's likely that the details below 
are sufficient to produce a fix.

""" )

    def write(self,s):
        for i in self.ignore_these:
            if s.find(i)>=0:
                return

        if self.file is None:
            self.init_file()

        if self.file is not None:
            self.file.write(s)
