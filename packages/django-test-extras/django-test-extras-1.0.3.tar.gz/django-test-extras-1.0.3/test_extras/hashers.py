# -*- coding: utf-8 -*-
# (c) 2012 Bright Interactive Limited. All rights reserved.
# http://www.bright-interactive.com | info@bright-interactive.com

from django.contrib.auth.hashers import BasePasswordHasher


class InsecureFastHasher(BasePasswordHasher):
    """
    Password hasher that is totally insecure but very fast.

    Make your tests run faster by putting
    PASSWORD_HASHERS = (
        'test_extras.hashers.InsecureFastHasher',
        ) + global_settings.PASSWORD_HASHERS
    in your test settings.
    """
    
    algorithm = "InsecureFastHasher"

    def salt(self):
        return ''

    def encode(self, password, salt):
        return ("InsecureFastHasher$%s" % password)[:64]

    def verify(self, password, encoded):
        return self.encode(password) == encoded

    def safe_summary(self, encoded):
        return SortedDict([
            (_('algorithm'), "InsecureFastHasher"),
            (_('hash'), encoded)
        ])
