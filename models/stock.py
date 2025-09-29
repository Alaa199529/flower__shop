from odoo import models, fields, api
from collections import defaultdict

class FlowerWater(models.Model):
    _name = "flower.water"
    _description = "Flower Watering"
    _order = "date desc"

    date = fields.Datetime(string="Watering Date", default=fields.Datetime.now, required=True)
    serial_id = fields.Many2one("stock.lot", string="Flower Serial Number", required=True)

class StockLot(models.Model):
    _inherit = "stock.lot"

    water_ids = fields.One2many("flower.water", "serial_id", string="Watering Records")
    is_flower = fields.Boolean(related='product_id.is_flower', string="Is Flower", store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "product_id" in vals and vals.get("product_id"):
                product = self.env["product.product"].browse(vals["product_id"])
                if product and product.sequence_id:
                    vals["name"] = product.sequence_id.next_by_id()
        return super().create(vals_list)

    def action_water_flower(self):
        lots = self.filtered(lambda rec: rec.is_flower)
        today = fields.Date.today()
        for record in lots:
            frequency = 0
            if record.product_id and record.product_id.flower_id:
                frequency = record.product_id.flower_id.watering_frequency or 0
            if record.water_ids:
                last_watered_date = record.water_ids[0].date and record.water_ids[0].date.date()
                if last_watered_date and frequency:
                    if (today - last_watered_date).days < frequency:
                        continue
            self.env['flower.water'].create({
                'serial_id': record.id,
                'date': fields.Datetime.now(),
            })

    @api.model
    def action_needs_watering(self):
        flowers = self.env["product.product"].search([("is_flower", "=", True)])
        serials = self.env["stock.lot"].search([("product_id", "in", flowers.ids)])
        lot_vals = defaultdict(bool)
        for serial in serials:
            if serial.water_ids:
                last_watered_date = serial.water_ids[0].date and serial.water_ids[0].date.date()
                frequency = serial.product_id.flower_id.watering_frequency if serial.product_id and serial.product_id.flower_id else 0
                today = fields.Date.today()
                needs_watering = False
                if not last_watered_date:
                    needs_watering = True
                else:
                    needs_watering = (today - last_watered_date).days >= (frequency or 0)
                lot_vals[serial.product_id.id] |= needs_watering
            else:
                lot_vals[serial.product_id.id] = True
        for flower in flowers:
            flower.needs_watering = bool(lot_vals.get(flower.id, False))
