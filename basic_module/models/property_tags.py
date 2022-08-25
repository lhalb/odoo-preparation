from odoo import models, fields


class TagModel(models.Model):
    _name = "estate.property.tags"
    _description = "Estate Tags"
    _order = "name desc"

    name = fields.Char(required=True)
    color = fields.Integer()

    _sql_constraints = [
        ('type_constraint',
         'unique ( name )',
         'The Property tag has to be unique'),
    ]


