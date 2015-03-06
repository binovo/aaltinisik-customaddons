# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013-Present Acespritech Solutions Pvt. Ltd. (<http://acespritech.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import osv, fields
import math


class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _columns = {
        'packing_tracking_ids': fields.one2many('stock.tracking', 'picking_out_id', 'Packing Details'),
#        'total_grosswg': fields.float('Total Gross Weight'),
#        'total_netwg': fields.float('Total Net Weight'),
#        'total_num_pack': fields.integer('Total Packages'),
#        'total_volume': fields.float('Total Volume'),
#        'total_land': fields.integer('Total Land Weight'),
#        'total_air': fields.integer('Total Air Weight'),
    }

    def _prepare_invoice(self, cr, uid, picking, partner, inv_type, journal_id, context=None):
        po_id = [picking.id]
        self.pool.get('stock.picking.out').btn_calc_weight(cr, uid, po_id)
        invoice_vals = super(stock_picking, self)._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, context)

        invoice_tracking_ids = []
        for pack in picking.packing_tracking_ids:
            if pack.id:
                invoice_tracking_ids.append(pack.id)
        invoice_vals.update({'packing_tracking_ids': [(6, 0, invoice_tracking_ids)],
                             'carrier_id': picking.carrier_id.id,
                             'address_contact_id': picking.partner_id.id,
                             })
        return invoice_vals

    def _prepare_invoice_group(self, cr, uid, picking, partner, invoice, context=None):
        """ Inherit the original function of the 'stock' module in order to add stock_tracking_ids to 
            grouped invoices
        """
        invoice_vals = super(stock_picking, self)._prepare_invoice_group(cr, uid, picking, partner, invoice, context)

        invoice_tracking_ids = []
        for pack in invoice.packing_tracking_ids:
            if pack.id:
                invoice_tracking_ids.append(pack.id)
        for pack in picking.packing_tracking_ids:
            if pack.id:
                invoice_tracking_ids.append(pack.id)
        invoice_vals.update({'packing_tracking_ids': [(6, 0, invoice_tracking_ids)],
                             'carrier_id': picking.carrier_id.id,
                             'address_contact_id': picking.partner_id.id,
                             })
        if picking.sale_id:
            invoice_vals['name'] = (invoice.name or '') + ', ' + (picking.sale_id.client_order_ref or '')
        return invoice_vals    
    

    def action_invoice_create(self, cr, uid, ids, journal_id=False, group=False, type='out_invoice', context=None):
        res = super(stock_picking, self).action_invoice_create(cr, uid, ids, journal_id, group, type, context)
        invoice_id = int(res.values()[0])
        if invoice_id:
            self.pool.get('account.invoice').btn_calc_weight_inv(cr, uid, [invoice_id])
            self.pool.get('account.invoice').merge_invoice_lines(cr, uid, [invoice_id])
        return res

stock_picking()


class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"
    _columns = {
        'packing_tracking_ids': fields.one2many('stock.tracking', 'picking_out_id', 'Packing Details'),
#        'total_grosswg': fields.float('Total Gross Weight'),
#        'total_netwg': fields.float('Total Net Weight'),
#        'total_num_pack': fields.integer('Total Packages'),
#        'total_volume': fields.float('Total Volume'),
#        'total_land': fields.integer('Total Land Weight'),
#        'total_air': fields.integer('Total Air Weight'),
    }

    def btn_calc_weight(self, cr, uid, ids, context=None):
        total_g, total_n, total_p = 0, 0, 0
        total_vol = total_air = total_land = 0

        tracking_ids = []
        for move in self.browse(cr, uid, ids[0], context).move_lines:
            if move.tracking_id.id:
                if move.tracking_id.id not in tracking_ids:
                    tracking_ids.append(move.tracking_id.id)
                    total_g += move.tracking_id.gross_weight
                    total_n += move.tracking_id.net_weight
                    total_p += 1
                    total_vol += (((move.tracking_id.pack_h * move.tracking_id.pack_w * move.tracking_id.pack_l) * 1.0) / 1000000)
                    total_air += math.ceil(((move.tracking_id.pack_h * move.tracking_id.pack_h * move.tracking_id.pack_h) * 1.0) / 5000)
                    total_land += math.ceil(((move.tracking_id.pack_h * move.tracking_id.pack_h * move.tracking_id.pack_h) * 1.0) / 3000)
        vals = {
           'packing_tracking_ids': [(6, 0, tracking_ids)],
            'total_grosswg': total_g,
           'total_netwg': total_n,
           'total_num_pack': total_p,
           'total_volume': total_vol,
           'total_air': total_air,
           'total_land': total_land,
        }
        self.write(cr, uid, ids, vals, context)
        return True

    def btn_print_pack(self, cr, uid, ids, context=None):
        self.btn_calc_weight(cr, uid, ids, context)
        
        for pack in self.browse(cr, uid, ids[0], context).packing_tracking_ids:
            denemepackname=pack.name
            denemeids=pack.move_ids
            for move in pack.move_ids:
                produename = move.product_id.name
                produeqty = move.product_qty 
                        
        return True

stock_picking_out()


class stock_move(osv.osv):
    _inherit = "stock.move"
    _columns = {
        'tracking_pack_no':   fields.related('tracking_id', 'pack_lineorder', type='integer', string='Pack No', readonly=True),


    }
    
stock_move()    
                
                
