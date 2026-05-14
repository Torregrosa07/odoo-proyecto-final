from odoo import models, fields, api


class BathroomStudent(models.Model):
    _name = 'bathroom.student'
    _description = 'Alumno del centro'
    _order = 'name'

    name = fields.Char(string='Nombre completo', required=True)
    course = fields.Char(string='Curso', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Teléfono')
    request_ids = fields.One2many(
        'bathroom.request', 'student_id', string='Solicitudes'
    )
    total_requests = fields.Integer(
        string='Total solicitudes', compute='_compute_total_requests', store=True
    )
    average_duration = fields.Float(
        string='Duración media (min)', compute='_compute_average_duration', store=True
    )

    @api.depends('request_ids')
    def _compute_total_requests(self):
        for record in self:
            record.total_requests = len(record.request_ids)

    @api.depends('request_ids.duration')
    def _compute_average_duration(self):
        for record in self:
            durations = record.request_ids.filtered(
                lambda r: r.duration > 0
            ).mapped('duration')
            if durations:
                record.average_duration = sum(durations) / len(durations)
            else:
                record.average_duration = 0
