#/usr/bin/env python
# -*- coding: utf-8 -*-

import whois

domain = whois.query('google.com')
print domain.__dict__
print domain.expiration_date
print domain.name