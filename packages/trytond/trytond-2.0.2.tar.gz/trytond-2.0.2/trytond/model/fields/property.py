#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

import copy
from trytond.model.fields.function import Function
from trytond.model.fields.field import Field
from trytond import backend
from trytond.transaction import Transaction


class Property(Function):
    '''
    Define a property field that is stored in ir.property (any).
    '''

    def __init__(self, field):
        '''
        :param field: The field of the function.
        '''
        super(Property, self).__init__(field, True, True, True)

    __init__.__doc__ += Field.__init__.__doc__

    def __copy__(self):
        return Property(copy.copy(self._field))

    def get(self, ids, model, name, values=None):
        '''
        Retreive the property.

        :param ids: A list of ids.
        :param model: The model.
        :param name: The name of the field or a list of name field.
        :param values:
        :return: a dictionary with ids as key and values as value
        '''
        property_obj = model.pool.get('ir.property')
        res = property_obj.get(name, model._name, ids)
        return res


    def set(self, ids, model, name, value):
        '''
        Set the property.

        :param ids: A list of ids.
        :param model: The model.
        :param name: The name of the field.
        :param value: The value to set.
        '''
        property_obj = model.pool.get('ir.property')
        return property_obj.set(name, model._name, ids,
                (value and getattr(self, 'model_name', '')  + ',' + str(value)) or
                False)


    def search(self, model, name, clause):
        '''
        :param model: The model.
        :param clause: The search domain clause. See ModelStorage.search
        :return: New list of domain.
        '''
        rule_obj = model.pool.get('ir.rule')
        property_obj = model.pool.get('ir.property')
        model_obj = model.pool.get('ir.model')
        field_obj = model.pool.get('ir.model.field')
        cursor = Transaction().cursor

        field_class = backend.FIELDS[self._type]
        if not field_class:
            return []
        sql_type = field_class.sql_type(model._columns[name])
        if not sql_type:
            return []
        sql_type = sql_type[0]

        property_query, property_val = rule_obj.domain_get('ir.property')

        #Fetch res ids that comply with the domain
        cursor.execute(
            'SELECT CAST(' \
                    'SPLIT_PART("' + property_obj._table + '".res,\',\',2) ' \
                    'AS INTEGER), '\
                '"' + property_obj._table + '".id '\
            'FROM "' + property_obj._table + '" '\
                'JOIN "' + field_obj._table + '" ON ' \
                    '("' + field_obj._table + '"'+ \
                        '.id = "' + property_obj._table + '".field) '\
                'JOIN "' + model_obj._table +'" ON ' \
                    '("' + model_obj._table + \
                        '".id = "' + field_obj._table + '".model) '\
            'WHERE '\
              'CASE WHEN "' +\
                model_obj._table + '".model = %s ' \
                'AND "' + field_obj._table + '".name = %s AND ' \
                + property_query + \
              ' THEN '  + \
                self.get_condition(sql_type, clause) + \
              ' ELSE '\
                'FALSE '\
              'END',
            [model._name, name] + property_val + \
                    self.get_condition_args(clause))

        props = cursor.fetchall()
        default = None
        for prop in props:
            if not prop[0]:
                default = prop[1]
                break

        if not default:
            return [('id', 'in', [x[0] for x in props])]

        #Fetch the res ids that doesn't use the default value
        cursor.execute(
            "SELECT cast(split_part(res,',',2) as integer) "\
            'FROM "' + property_obj._table +'"'\
            'WHERE ' \
              + property_query + ' AND res is not null',
            property_val)

        fetchall = cursor.fetchall()
        if not fetchall:
            return [('id', 'in', [x[0] for x in props])]

        else:
            other_ids = [x[0] for x in cursor.fetchall()]

            res_ids = model.search(['OR',
                ('id', 'in', [x[0] for x in props]),
                ('id', 'not in', other_ids)
                ])

            return [('id', 'in', res_ids)]

    @staticmethod
    def get_condition(sql_type, clause):
        if clause[1] in ('in', 'not in'):
            return ("(cast(split_part(value,',',2) as %s) %s ("+ \
                ",".join(('%%s',) * len(clause[2])) + ")) ") % \
                (sql_type, clause[1])
        else:
            return "(cast(split_part(value,',',2) as %s) %s %%s) " % \
                (sql_type, clause[1])

    @staticmethod
    def get_condition_args(clause):
        res = []
        if clause[1] in ('in', 'not in'):
            res.extend(clause[2])
        else:
            res.append(clause[2])
        return res


