# -*- coding: utf-8 -*-
# from odoo import http


# class SequenceFacturasWsfe(http.Controller):
#     @http.route('/sequence_facturas_wsfe/sequence_facturas_wsfe/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sequence_facturas_wsfe/sequence_facturas_wsfe/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sequence_facturas_wsfe.listing', {
#             'root': '/sequence_facturas_wsfe/sequence_facturas_wsfe',
#             'objects': http.request.env['sequence_facturas_wsfe.sequence_facturas_wsfe'].search([]),
#         })

#     @http.route('/sequence_facturas_wsfe/sequence_facturas_wsfe/objects/<model("sequence_facturas_wsfe.sequence_facturas_wsfe"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sequence_facturas_wsfe.object', {
#             'object': obj
#         })
