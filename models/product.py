from odoo import models, fields

class Product(models.Model):
    _inherit = "product.product"

    is_flower = fields.Boolean(string="Is Flower Product?")
    flower_id = fields.Many2one("flower.flower", string="Flower")
    sequence_id = fields.Many2one("ir.sequence", string="Flower Sequence")
    needs_watering = fields.Boolean(string="Needs Watering", default=False, help="Computed by scheduled job")
