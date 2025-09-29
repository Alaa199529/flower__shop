from odoo import models, fields, api
import requests, logging

_logger = logging.getLogger(__name__)

class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    partner_latitude = fields.Float(related='partner_id.partner_latitude', string="Latitude")
    partner_longitude = fields.Float(related='partner_id.partner_longitude', string="Longitude")

    def _get_api_key_and_location(self, show_error=True):
        api_key = self.env['ir.config_parameter'].sudo().get_param('flower_shop.weather_api_key')
        if not api_key or api_key == 'unset':
            if show_error:
                _logger.warning('Weather API key is not set for flower_shop.weather_api_key')
            return False, False, False
        if not self.partner_id or not self.partner_id.partner_latitude or not self.partner_id.partner_longitude:
            if show_error:
                _logger.warning('Warehouse %s has no coordinates', self.name)
            return False, False, False
        return api_key, self.partner_id.partner_latitude, self.partner_id.partner_longitude

    def get_weather(self, show_error=True):
        self.ensure_one()
        api_key, lat, lng = self._get_api_key_and_location(show_error)
        if not api_key:
            return
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={api_key}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            entries = response.json()
            _logger.info('Weather for %s: %s', self.name, entries.get('weather', [{}])[0].get('description'))
        except requests.exceptions.RequestException as e:
            _logger.exception('Error fetching weather data: %s', e)

    def get_weather_all_warehouses(self):
        for warehouse in self.search([]):
            try:
                warehouse.get_weather(show_error=False)
            except Exception:
                _logger.exception('Failed to get weather for warehouse %s', warehouse.id)

    def get_forecast_all_warehouses(self, show_error=True):
        flower_serials_to_water = self.env['stock.lot']
        for warehouse in self:
            api_key, lat, lng = warehouse._get_api_key_and_location(show_error)
            if not api_key:
                continue
            url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lng}&appid={api_key}"
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                entries = response.json()
                is_rainy_today = False
                for i in range(0, min(4, len(entries.get('list', [])))):
                    item = entries['list'][i]
                    rain = 0
                    if 'rain' in item:
                        rain = item['rain'].get('3h', 0)
                    if rain > 0.2:
                        is_rainy_today = True
                        break
                if is_rainy_today:
                    flower_products = self.env['product.product'].search([('is_flower', '=', True)])
                    quants = self.env['stock.quant'].search([
                        ('product_id', 'in', flower_products.ids),
                        ('location_id', '=', warehouse.lot_stock_id.id)
                    ])
                    flower_serials_to_water |= quants.mapped('lot_id')
            except Exception as e:
                _logger.exception('Failed forecast for warehouse %s: %s', warehouse.id, e)
        for flower_serial in flower_serials_to_water:
            self.env['flower.water'].create({
                'serial_id': flower_serial.id,
                'date': fields.Datetime.now(),
            })
