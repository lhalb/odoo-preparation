from odoo import models, fields


class IconModel(models.Model):
    _name = "all.icons"
    _description = "Displays all icons"

    name = fields.Char()




