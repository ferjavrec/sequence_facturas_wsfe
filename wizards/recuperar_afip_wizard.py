# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import datetime


class RecuperarFromAfip(models.TransientModel):
    _name = "recuperar.from.afip"
    _description = "Recuperar comprobantes desde Afip"

    tipo_comprobante = fields.Char('Tipo comprobante', required=True)
    punto_venta = fields.Char('Punto de venta', required=True)
    comprobante = fields.Char('Comprobante', required=True)

    #producto para crear las lineas, ya que este dato no se obtiene desde Afip
    product_id = fields.Many2one("product.product", string="Producto", required=True)


    def _get_iva_tax(self, code):
        if code == '5':
            tax = 21
        elif code == '4':
            tax = 10.5
        elif code == '9':
            tax = 2.5
        elif code == '8':
            tax = 5
        else:
            tax = 6
        account_tax = self.env['account.tax'].search([
            ('type_tax_use', '=', 'sale'),
            ('price_include', '=', False),
            ('amount', '=', float(tax))
        ])
        if account_tax:
            return account_tax[0].id
        else:
            return None


    def recuperar_comprobante_afip(self):
        invoice_id = self._context.get('active_id', False)
        invoice = self.env['account.move'].browse(invoice_id)
        if invoice.state != 'draft':
            raise UserError(_(
                'Para poder recuperar datos desde AFIP el comprobante debe estar en borrador.'))

        company = self.env.company
        ws = company.get_connection('wsfe').connect()
        consulta = ws.CompConsultar(self.tipo_comprobante, self.punto_venta, self.comprobante)
        if not consulta:
            raise UserError(_(
                'El comprobante ingresado no existe en AFIP.'))

        #buscar cliente por el cuit sino lo agregamos
        documento = str(ws.factura['nro_doc'])
        tipo_doc = str(ws.factura['tipo_doc'])
        Cliente = self.env['res.partner']
        cliente = Cliente.search([('vat', '=', documento)])
        if not cliente:
            tipo_documento = self.env['l10n_latam.identification.type'].search([
                ('l10n_ar_afip_code', '=', tipo_doc)])
            agregar_cliente = {
                'name': 'Comprobante recuperado AFIP',
                'vat': documento,
                'l10n_latam_identification_type_id': tipo_documento[0].id
            }
            cliente = Cliente.create(agregar_cliente)

        #convierto la fecha, la consulta retorna 20230811
        anio = ws.FechaCbte[:4]
        mes = ws.FechaCbte[4:6]
        dia = ws.FechaCbte[6:8]
        fecha_factura = datetime.datetime(int(anio), int(mes), int(dia), 0, 0, 0)
        comprobante = '{:>05s}-{:>08s}'.format(str(ws.PuntoVenta), str(ws.CbteNro))
        msg = u"\n".join([ws.Obs or "", ws.ErrMsg or ""])

        invoice.write({
            'invoice_date': fecha_factura,
            'afip_pv': ws.PuntoVenta,
            'afip_numero': ws.CbteNro,
            'name': comprobante,
            'invoice_payment_ref': comprobante,
            'l10n_latam_document_number': comprobante,
            'l10n_latam_document_type_id': ws.factura['tipo_cbte'],
            'afip_xml_request': ws.XmlRequest,
            'afip_xml_response': ws.XmlResponse,
            'afip_result': ws.Resultado,
            'afip_message': msg,
            'afip_auth_mode': 'CAE',
            'afip_auth_code': ws.CAE,
            'partner_id': cliente.id,
        })

        product_cta = self.product_id.property_account_income_id or \
                        self.product_id.categ_id.property_account_income_categ_id

        for item in ws.factura['iva']:
            tipo_iva = self._get_iva_tax(str(item['iva_id']))
            line = self.env['account.move.line'].with_context(check_move_validity=False).create({
                'payment_id': False,
                'move_id': invoice.id,
                'account_id': product_cta.id,
                'quantity': 1,
                'product_id': self.product_id.product_variant_id.id,
                'partner_id': cliente.id,
                'price_unit': item['base_imp'],
                'tax_ids': [[6, False, [tipo_iva]]],
            })

            line.name = line._get_computed_name()
            line.account_id = line._get_computed_account()
            line.tax_ids = line._get_computed_taxes()
            line.product_uom_id = line._get_computed_uom()
            line._set_price_and_tax_after_fpos()

            company = line.move_id.company_id
            line.price_unit = company.currency_id._convert(line.price_unit, line.move_id.currency_id, company,
                                                           line.move_id.date, round=False)

        invoice.with_context(check_move_validity=False)._recompute_dynamic_lines(recompute_all_taxes=True)
