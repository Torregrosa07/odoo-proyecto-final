import base64
import csv
import io

from odoo import models, fields, _
from odoo.exceptions import UserError


class ImportStudentWizard(models.TransientModel):
    """
    Wizard para importar alumnos desde un archivo CSV.
    Usa TransientModel porque los datos del wizard son temporales
    y se eliminan automáticamente después de su uso.
    
    Formato CSV esperado (separacon ;):
        nombre;curso;email;telefono
    """
    _name = 'import.student.wizard'
    _description = 'Asistente de importación de alumnos desde CSV'

    # Campo binario para subir el archivo CSV
    file = fields.Binary(string='Archivo CSV', required=True)
    filename = fields.Char(string='Nombre del archivo')

    def action_import(self):
        """Lee el CSV, valida las columnas y crea o actualiza alumnos."""
        if not self.file:
            raise UserError(_('Debe seleccionar un archivo CSV.'))

        # Decodificar el archivo de base64 a texto
        data = base64.b64decode(self.file)
        try:
            file_content = data.decode('utf-8')
        except UnicodeDecodeError:
            # Fallback para archivos con codificación latina (Excel español)
            file_content = data.decode('latin-1')

        reader = csv.DictReader(io.StringIO(file_content), delimiter=';')

        # Validar que el CSV tenga las columnas obligatorias
        required_columns = {'nombre', 'curso'}
        if not required_columns.issubset(set(reader.fieldnames or [])):
            raise UserError(
                _('El CSV debe tener al menos las columnas: nombre, curso\n'
                  'Columnas opcionales: email, telefono')
            )

        created = 0
        updated = 0
        student_model = self.env['bathroom.student']

        # Recorrer cada fila del CSV
        for row in reader:
            nombre = row.get('nombre', '').strip()
            curso = row.get('curso', '').strip()

            # Saltar filas vacías
            if not nombre or not curso:
                continue

            # Buscar si ya existe un alumno con el mismo nombre y curso
            existing = student_model.search([
                ('name', '=', nombre),
                ('course', '=', curso),
            ], limit=1)

            # Preparar los valores a crear/actualizar
            vals = {
                'name': nombre,
                'course': curso,
                'email': row.get('email', '').strip(),
                'phone': row.get('telefono', '').strip(),
            }

            if existing:
                existing.write(vals)  # Actualizar alumno existente
                updated += 1
            else:
                student_model.create(vals)  # Crear nuevo alumno
                created += 1

        # Mostrar notificación con el resultado de la importación

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
