from odoo import models, fields


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tag"
    _order = "name"

    name = fields.Char(required=True)

    _check_name_unique = models.Constraint("UNIQUE(name)", "The name must be unique")
