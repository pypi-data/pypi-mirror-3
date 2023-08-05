#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, ModelSingleton, fields
from trytond.pyson import Eval


class Configuration(ModelSingleton, ModelSQL, ModelView):
    'Party Configuration'
    _name = 'party.configuration'
    _description = __doc__

    party_sequence = fields.Property(fields.Many2One('ir.sequence',
        'Party Sequence', domain=[
            ('company', 'in', [Eval('company'), False]),
            ('code', '=', 'party.party'),
        ], required=True))
    party_lang = fields.Property(fields.Many2One("ir.lang", 'Party Language',
        help=('The value set on this field will preset the language on new '
            'parties')))

Configuration()
