from odoo import models, fields


class TypeModel(models.Model):
    _name = "estate.property.type"
    _description = "Estate Types"
    _order = "name desc"

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")

    _sql_constraints = [
        ('type_constraint',
         'unique ( name )',
         'The Property type has to be unique'),
    ]

    property_ids = fields.One2many('test.model', 'property_type_id', string="Property O2M")


