from odoo import models, fields


class BathroomKey(models.Model):
    """
    Modelo que representa cada llave física del baño del centro.
    Controla su disponibilidad y la solicitud actualmente vinculada.
    """
    _name = 'bathroom.key'
    _description = 'Llave del baño'

    # Nombre identificativo de la llave (ej: "Baño Planta 1", "Baño Planta 2")
    name = fields.Char(string='Nombre', required=True)
    # Estado actual de la llave
    state = fields.Selection([
        ('available', 'Disponible'),  # Llave libre para usar
        ('in_use', 'En uso'),         # Llave entregada a un alumno
    ], string='Estado', default='available', required=True)
    # Solicitud activa que tiene esta llave asignada
    current_request_id = fields.Many2one(
        'bathroom.request',
        string='Solicitud activa',
    )