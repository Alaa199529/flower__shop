from odoo import models, fields

class Flower(models.Model):
    _name = 'flower.flower'
    _description = 'Flower'

    common_name = fields.Char(string="Common Name", required=True)
    scientific_name = fields.Char(string="Scientific Name")
    season_start = fields.Date(string="Season Start Date")
    season_end = fields.Date(string="Season End Date")
    watering_frequency = fields.Integer(string="Watering Frequency (days)", help="Number of days between waterings", default=7)
    watering_amount = fields.Float(string="Watering Amount (ml)", help="Amount of water per watering")

    def name_get(self):
        """
        يعرض الاسم بالصيغة: Scientific Name (Common Name)
        """
        result = []
        for flower in self:
       
            name = "{} ({})".format(flower.scientific_name, flower.common_name)
            result.append((flower.id, name))
        return result