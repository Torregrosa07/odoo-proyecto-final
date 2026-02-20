from odoo import models, fields

class BathroomKey(models.Model):
    _name = 'bathroom.key'
    _description = 'Llave del baño'

    name = fields.Char(string='Nombre', required=True)  # "Baño Hombres" / "Baño Mujeres"
    state = fields.Selection([
        ('available', 'Disponible'),
        ('in_use', 'En uso'),
    ], string='Estado', default='available', required=True)
    current_request_id = fields.Many2one(
        'bathroom.request',
        string='Solicitud activa',
    )