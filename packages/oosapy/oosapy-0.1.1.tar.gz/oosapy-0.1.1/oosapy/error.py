# oosapy
# Copyright 11870.com
# See LICENSE for details.

class OosApyError(Exception):
    """oosapy exception"""

    def __init__(self, reason, response=None):
        self.reason = str(reason)
        self.response = response

    def __str__(self):
        return self.reason
        