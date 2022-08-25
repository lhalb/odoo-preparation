from dateutil.relativedelta import relativedelta
from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare


class MyModel(models.Model):
    _name = "test.model"
    _description = "Real Estate"
    _order = "name desc"

    active = fields.Boolean(default=True)
    name = fields.Char(required=True, default="Unknown")
    type = fields.Char(default="House")
    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    salesperson_id = fields.Many2one('res.users', string='Salesperson',
                                     index=True,
                                     default=lambda self: self.env.user)
    buyer_id = fields.Many2one('res.partner', string='Buyer', index=True)
    categ_ids = fields.Many2many('estate.property.tags', string="Tags")
    offer_ids = fields.One2many('estate.property.offers', 'property_id', string='Offers', copy=False)

    description = fields.Text()
    postcode = fields.Char()
    date_created = fields.Date(
        "Created", copy=False, readonly=True,
        default=lambda self: fields.Date.today()
    )
    date_availability = fields.Date(
        "Available from", copy=False,
        default=lambda self: fields.Date.today() + relativedelta(months=+3)
    )

    expected_price = fields.Float("Expected Price", required=True)
    selling_price = fields.Float("Selling Price", compute="_set_selling_price", copy=False, default=0)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer("Garden area [sqft]")
    select_list = [
        ('n', 'North'),
        ('e', 'East'),
        ('s', 'South'),
        ('w', 'West')
    ]
    garden_orientation = fields.Selection(select_list)
    state_list = [
        ('n', 'New'),
        ('r', 'Offer received'),
        ('a', 'Offer accepted'),
        ('s', 'Sold'),
        ('c', 'Cancelled')
    ]
    state = fields.Selection(state_list, string="Ad state", default='n', copy=False)

    total_area = fields.Float("Total Area [sqft]", compute="_compute_total_area")
    best_price = fields.Float(compute="_compute_best_price")

    _sql_constraints = [
        ('expected_price_constrain',
         'CHECK ( expected_price >= 0 )',
         'The expected price has to be positive'),
    ]

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price", "offer_ids")
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(offer.price for offer in record.offer_ids)
            else:
                record.best_price = 0.0
        if self._check_state(record):
            record._set_state(self._check_state(record))

    def _check_state(self, record):
        if record.state not in ['c', 's']:
            if not record.offer_ids or all(offer.status == 'refused' for offer in record.offer_ids):
                return 'n'
            if any(offer.status == 'accepted' for offer in record.offer_ids):
                return 'a'
            else:
                return 'r'

    def _set_state(self, state_to_set):
        self.state = state_to_set

    @api.depends("offer_ids.status")
    def _set_selling_price(self):
        for record in self:
            if self._check_state(record) == 'a':
                record.selling_price = max(offer.price for offer in record.offer_ids if offer.status == 'accepted')
                record._set_state('a')
            else:
                record.selling_price = 0

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 's'
        else:
            self.garden_area = 0
            self.garden_orientation = ''

    @api.ondelete(at_uninstall=False)
    def _unlink_only_new_and_canceled(self):
        if self.state not in ['n', 'c']:
            raise UserError('You can only delete items that are new or canceled')

    def action_cancel_ad(self):
        for record in self:
            if record.state == 's':
                raise UserError("You can't cancel an ad, that is marked as 'Sold'")
            record.state = 'c'

    def action_mark_as_sold(self):
        for record in self:
            if record.state == 'c':
                raise UserError("You can't sell an ad, that has been marked as 'Cancelled'")
            if record.state == 'n' or not record.offer_ids:
                raise UserError("You can't sell an ad without offers")
            record.state = 's'

    def action_mark_as_new(self):
        for record in self:
            record.state = 'n'

    def show_best_price(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'best_price',
            'view_mode': 'tree',
            'res_model': 'test.model',
            'domain': [('offer_ids.property_id', '=', self.id)],
            'context': "{'create': False}"
        }
