from dateutil.relativedelta import relativedelta
from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare

# import logging
# _logger = logging.getLogger(__name__)


class OfferModel(models.Model):
    _name = "estate.property.offers"
    _description = "Estate Offers"
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection([('dp', 'Decision Pending'), ('accepted', 'Accepted'), ('refused', 'Refused')],
                              required=True, copy=False, default='dp')
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    property_id = fields.Many2one('test.model', string='Property', required=True)

    valid_duration = fields.Integer("Validity", default=7)
    date_created = fields.Date(
        "Created", copy=False, readonly=True,
        default=lambda self: fields.Date.today()
    )
    date_deadline = fields.Date(compute="_compute_deadline", inverse="_compute_validity")

    _sql_constraints = [
        ('offer_price_constrain',
         'CHECK ( price >= 0 )',
         'The offer price has to be positive'),
    ]

    @api.depends("valid_duration")
    def _compute_deadline(self):
        for record in self:
            record.date_deadline = record.date_created + relativedelta(days=record.valid_duration)

    @api.depends("date_deadline")
    def _compute_validity(self):
        for record in self:
            record.valid_duration = (record.date_deadline - record.date_created).days

    @api.constrains('status')
    def _validate_status(self):
        for record in self:
            if record.status == 'accepted':
                if float_compare(record.price, record.property_id.expected_price * 0.9, precision_rounding=2) <= 0:
                    raise ValidationError("The offer you want to accept is less than 90% of your expected price.\n"
                                          "Either lower your expected price or increase the offer.")

    @api.model
    def create(self, vals):
        current_best_price = self.property_id.best_price
        if current_best_price > self.price:
            raise ValidationError(f'The offer has to be greater than {current_best_price}')
        return super().create(vals)

    def refuse_offer(self):
        self.status = 'refused'

    def accept_offer(self):
        self.status = 'accepted'

