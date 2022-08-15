from odoo import models, fields


class MyModel(models.Model):
    _name = "test.model"
    _description = "Real Estate"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date()
    expected_price = fields.Float(required=True)
    selling_price = fields.Float()
    bedrooms = fields.Integer()
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    select_list = [('n', 'North'), ('e', 'East'), ('s', 'South'), ('w', 'West')]
    garden_orientation = fields.Selection(select_list)



