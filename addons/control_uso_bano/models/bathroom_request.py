from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BathroomRequest(models.Model):
    """
    Modelo que registra cada solicitud de uso del baño.
    Gestiona el flujo completo: entrega de llave -> uso -> devolución.
    """
    _name = 'bathroom.request'
    _description = 'Solicitud de uso del baño'
    _order = 'time_out desc'  # Ordenar por fecha de salida descendente

    # --- Campos relacionales ---
    student_id = fields.Many2one(
        'bathroom.student', string='Alumno', required=True, ondelete='restrict'
    )
    # Campo related: se autocompleta con el curso del alumno seleccionado
    course = fields.Char(
        string='Curso', related='student_id.course', store=True, readonly=True
    )
    key_id = fields.Many2one('bathroom.key', string='Llave', required=True)

    # --- Campos de tiempo ---
    time_out = fields.Datetime(
        string='Hora de salida', default=fields.Datetime.now, required=True
    )
    time_in = fields.Datetime(string='Hora de regreso')
    # Campo computed: calcula la duración automáticamente al registrar el regreso
    duration = fields.Float(
        string='Duración (min)', compute='_compute_duration', store=True
    )

    # --- Estado del flujo ---
    state = fields.Selection([
        ('active', 'Activo'),       # Llave entregada, alumno fuera
        ('returned', 'Devuelto'),   # Llave devuelta correctamente
        ('delayed', 'Retrasado'),   # Tiempo excedido
    ], string='Estado', default='active', required=True)

    notes = fields.Text(string='Observaciones')

    @api.depends('time_out', 'time_in')
    def _compute_duration(self):
        """Calcula la duración en minutos entre la salida y el regreso."""
        for record in self:
            if record.time_out and record.time_in:
                diff = record.time_in - record.time_out
                record.duration = diff.total_seconds() / 60
            else:
                record.duration = 0

    @api.constrains('key_id', 'state')
    def _check_key_available(self):
        """Valida que una llave no esté asignada a dos solicitudes activas a la vez."""
        for record in self:
            if record.state == 'active':
                other = self.search([
                    ('key_id', '=', record.key_id.id),
                    ('state', '=', 'active'),
                    ('id', '!=', record.id),
                ])
                if other:
                    raise ValidationError(
                        f'La llave "{record.key_id.name}" ya está en uso.'
                    )

    def action_return_key(self):
        for record in self:
            record.state = 'returned'
            record.time_in = fields.Datetime.now()
            record.key_id.state = 'available'
            record.key_id.current_request_id = False

    def action_deliver_key(self):
        for record in self:
            record.key_id.state = 'in_use'
            record.key_id.current_request_id = record.id
            