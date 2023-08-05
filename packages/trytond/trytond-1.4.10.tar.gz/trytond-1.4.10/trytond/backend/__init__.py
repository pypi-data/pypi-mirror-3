#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from trytond.config import CONFIG
if CONFIG['db_type'] == 'sqlite':
    from sqlite import *
else:
    from postgresql import *
