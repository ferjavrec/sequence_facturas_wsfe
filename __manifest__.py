# -*- coding: utf-8 -*-
{
    'name': "sequence_facturas_wsfe",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        La finalidad de este modulo es prevenir el defasale de las secuencias de las facturas electronicas.
    """,

    'author': "Geneos Coop.",
    'website': "http://www.geneos.com.ar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['l10n_ar','l10n_ar_afipws_fe'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizards/recuperar_afip_wizard.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
