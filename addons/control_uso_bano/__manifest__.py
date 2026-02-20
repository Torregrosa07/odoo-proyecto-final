{
    'name': 'Control de Uso del Baño',
    'version': '17.0.1.0.0',
    'summary': 'Gestión del control de llaves y acceso al baño',
    'category': 'Education',
    'author': 'Tu Nombre',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/bathroom_key_views.xml',
        'views/bathroom_request_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
}