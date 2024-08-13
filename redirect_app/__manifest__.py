{
    'name': 'Redirect App',
    'version': '16.0.0.0',
    'summary': 'App that redirects to a website URL',
    'description': 'An app icon that redirects to a website URL',
    'author': 'Your Name',
    'category': 'Tools',
    'depends': [
        'base_pnt',
        'custom_pnt',
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/redirect_app_views.xml',
        'views/res_config_settings_views.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'redirect_app/static/description/sek_1.png',
            'redirect_app/static/description/sek_2.png',
            'redirect_app/static/description/sek_3.png',
            'redirect_app/static/description/sek_4.png',
        ],
    },
    'installable': True,
    'application': True,
}
