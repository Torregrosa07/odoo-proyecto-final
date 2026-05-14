from odoo import models, fields, api


class BathroomStudent(models.Model):
    """
    Modelo que representa a cada alumno del centro educativo.
    Almacena sus datos personales y mantiene el historial de solicitudes.
    """
    _name = 'bathroom.student'
    _description = 'Alumno del centro'
    _order = 'name'  # Ordenar alfabéticamente

    # --- Datos personales ---
    name = fields.Char(string='Nombre completo', required=True)
    course = fields.Char(string='Curso', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Teléfono')

    # --- Relación inversa: todas las solicitudes de este alumno ---
    request_ids = fields.One2many(
        'bathroom.request', 'student_id', string='Solicitudes'
    )

    # --- Campos estadísticos (computed) ---
    total_requests = fields.Integer(
        string='Total solicitudes', compute='_compute_total_requests', store=True
    )
    average_duration = fields.Float(
        string='Duración media (min)', compute='_compute_average_duration', store=True
    )

    @api.depends('request_ids')
    def _compute_total_requests(self):
        """Cuenta el número total de solicitudes del alumno."""
        for record in self:
            record.total_requests = len(record.request_ids)

    @api.depends('request_ids.duration')
    def _compute_average_duration(self):
        """Calcula la duración media de las visitas al baño del alumno."""
        for record in self:
            durations = record.request_ids.filtered(
                lambda r: r.duration > 0
            ).mapped('duration')
            if durations:
                record.average_duration = sum(durations) / len(durations)
            else:
                record.average_duration = 0
