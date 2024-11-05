from odoo import models, fields


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"

    name = fields.Char(required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id')

    _sql_constraints = [("name_unique", "UNIQUE(name)", "The name must be unique")]
