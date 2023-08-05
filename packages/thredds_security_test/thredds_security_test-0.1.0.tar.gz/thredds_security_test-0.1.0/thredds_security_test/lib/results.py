'''
Checker results class

Created on 29 Sep 2011

@author: rwilkinson
'''
class Results(object):
    def __init__(self, access_allowed_count=0, access_denied_count=0, inconsistent_count=0):
        self.access_allowed_count = access_allowed_count
        self.access_denied_count = access_denied_count
        self.inconsistent_count = inconsistent_count

    def add_access_allowed(self):
        self.access_allowed_count += 1

    def add_access_denied(self):
        self.access_denied_count += 1

    def add_inconsistent(self):
        self.inconsistent_count += 1

    def __eq__(self, other):
        return (isinstance(other, Results)
                and (self.access_allowed_count == other.access_allowed_count)
                and (self.access_denied_count == other.access_denied_count)
                and (self.inconsistent_count == other.inconsistent_count))

    def __repr__(self):
        return("(allowed=%d, denied=%d, inconsistent=%d)" %
               (self.access_allowed_count, self.access_denied_count, self.inconsistent_count))
