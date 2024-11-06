from odoo import models, fields


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"
    _order = 'sequence, name'

    name = fields.Char(required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id')
    sequence = fields.Integer('Sequence', default=1)

    _sql_constraints = [("name_unique", "UNIQUE(name)", "The name must be unique")]
