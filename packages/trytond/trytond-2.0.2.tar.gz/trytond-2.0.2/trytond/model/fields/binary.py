#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from trytond.model.fields.field import Field


class Binary(Field):
    '''
    Define a binary field (``str``).
    '''
    _type = 'binary'

    def __init__(self, string='', help='', required=False, readonly=False,
            domain=None, states=None, change_default=False, select=0,
            on_change=None, on_change_with=None, depends=None, filename=None,
            order_field=None, context=None, loading='lazy'):
        if filename is not None:
            self.filename = filename
            if depends is None:
                depends = [filename]
            else:
                depends.append(filename)
        super(Binary, self).__init__(string=string, help=help,
            required=required, readonly=readonly, domain=domain, states=states,
            change_default=change_default, select=select, on_change=on_change,
            on_change_with=on_change_with, depends=depends,
            order_field=order_field, context=context, loading=loading)

    @staticmethod
    def get(ids, model, name, values=None):
        '''
        Convert the binary value into ``str``

        :param ids: a list of ids
        :param model: a string with the name of the model
        :param name: a string with the name of the field
        :param values: a dictionary with the read values
        :return: a dictionary with ids as key and values as value
        '''
        if values is None:
            values = {}
        res = {}
        for i in values:
            res[i['id']] = i[name] and str(i[name]) or None
        for i in ids:
            res.setdefault(i, None)
        return res
