from odoo import fields, models, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Properties"
    _order = 'id desc'

    name = fields.Char(required=True, string="Title")
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(
        copy=False,
        default=fields.Date.today() + relativedelta(months=3),
        string="Available From",
    )
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection(
        selection=[
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ]
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="new",
        string="Status",
    )
    property_type_id = fields.Many2one("estate.property.type")
    buyer_id = fields.Many2one("res.partner", copy=False)
    salesperson_id = fields.Many2one(
        "res.users", default=lambda self: self.env.user, string="Salesman"
    )
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    total_area = fields.Integer(
        compute="_compute_total_area", string="Total Area (sqm)"
    )
    best_offer = fields.Float(compute="_compute_best_offer")

    _sql_constraints = [
        (
            "expected_price_strictly_positive",
            "CHECK(expected_price > 0)",
            "The expected price must be strictly positive",
        ),
        (
            "selling_price_positive",
            "CHECK(selling_price >= 0)",
            "The selling price must be positive",
        ),
    ]

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_offer(self):
        for record in self:
            offers = record.offer_ids

            record.best_offer = 0 if len(offers) == 0 else max(offers.mapped("price"))

    @api.onchange("garden")
    def _onchange_garden(self):
        garden = self.garden

        self.garden_area = 10 if garden else None
        self.garden_orientation = "north" if garden else None

    @api.onchange("offer_ids", "state")
    def _onchange_offer_ids(self):
        if self.state == "new" and len(self.offer_ids) > 0:
            self.state = "offer_received"

    @api.constrains("selling_price", "expected_price")
    def _check_selling_price(self):
        precision_digits = 2

        for record in self:
            if float_is_zero(record.selling_price, precision_digits=precision_digits):
                continue

            if (
                float_compare(
                    record.selling_price,
                    record.expected_price * 0.9,
                    precision_digits=precision_digits,
                )
                == -1
            ):
                raise ValidationError(
                    "The selling price cannot be less than 90% of the expected price"
                )

    def action_sell_property(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError("Cancelled properties cannot be sold")

            record.state = "sold"

        return True

    def action_cancel_property(self):
        for record in self:
            if record.state == "sold":
                raise UserError("Sold properties cannot be cancelled")

            record.state = "cancelled"

        return True
