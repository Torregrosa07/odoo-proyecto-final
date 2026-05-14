import base64
import csv
import io

from odoo import models, fields, _
from odoo.exceptions import UserError


class ImportStudentWizard(models.TransientModel):
    _name = 'import.student.wizard'
    _description = 'Asistente de importación de alumnos desde CSV'

    file = fields.Binary(string='Archivo CSV', required=True)
    filename = fields.Char(string='Nombre del archivo')

    def action_import(self):
        if not self.file:
            raise UserError(_('Debe seleccionar un archivo CSV.'))

        # Decodificar el archivo
        data = base64.b64decode(self.file)
        try:
            file_content = data.decode('utf-8')
        except UnicodeDecodeError:
            file_content = data.decode('latin-1')

        reader = csv.DictReader(io.StringIO(file_content), delimiter=';')

        # Validar columnas requeridas
        required_columns = {'nombre', 'curso'}
        if not required_columns.issubset(set(reader.fieldnames or [])):
            raise UserError(
                _('El CSV debe tener al menos las columnas: nombre, curso\n'
                  'Columnas opcionales: email, telefono')
            )

        created = 0
        updated = 0
        student_model = self.env['bathroom.student']

        for row in reader:
            nombre = row.get('nombre', '').strip()
            curso = row.get('curso', '').strip()

            if not nombre or not curso:
                continue

            # Buscar si ya existe el alumno
            existing = student_model.search([
                ('name', '=', nombre),
                ('course', '=', curso),
            ], limit=1)

            vals = {
                'name': nombre,
                'course': curso,
                'email': row.get('email', '').strip(),
                'phone': row.get('telefono', '').strip(),
            }

            if existing:
                existing.write(vals)
                updated += 1
            else:
                student_model.create(vals)
                created += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Importación completada'),
                'message': _('%d alumnos creados, %d actualizados.') % (created, updated),
                'type': 'success',
                'sticky': False,
            }
        }
