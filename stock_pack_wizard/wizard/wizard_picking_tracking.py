# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#     Jon Chow <jon.chow@elico-corp.com>
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

from openerp.osv import fields,osv
from openerp.tools.translate import _


class  wizard_picking_tracking_line(osv.osv_memory):
    _name = 'wizard.picking.tracking.line'
    
    _columns = {
        'name':          fields.char('name', size=32),
        'wizard_id':     fields.many2one('wizard.picking.tracking', 'WPT'),
        'qty':           fields.float('Pack Quantity'),
        'stock_move_id': fields.many2one('stock.move',   'Stock move'),
        'product_id':    fields.related('stock_move_id', 'product_id',  type='many2one',relation='product.product', string='Product', readonly=True),
        'tracking_id':   fields.related('stock_move_id', 'tracking_id', type='many2one',relation='stock.tracking',  string='Pack',    readonly=True),
        'product_qty':   fields.related('stock_move_id', 'product_qty', type='float',   string='Delivery Quantity', readonly=True),
        'pack_no':   fields.related('stock_move_id', 'tracking_pack_no', type='integer',   string='Pack No', readonly=True),
        
    }
    
    def onchange_stock_move_id(self, cr, uid, ids, stock_move_id, context=None):
        data = {'product_id': False, 'tracking_id':False,'product_uos_qty':0, 'product_qty':0, 'qty':0 }
        if stock_move_id:
            stock_move  = self.pool.get('stock.move').browse(cr, uid, stock_move_id)
            product_id  = stock_move.product_id.id
            tracking_id = stock_move.tracking_id and stock_move.tracking_id.id or False
            product_qty = stock_move.product_qty
            product_ous_qty = stock_move.product_uos_qty
            qty         = not tracking_id and product_qty or 0.0
            data.update( {'product_id':product_id, 'tracking_id':tracking_id, 'product_uos_qty':product_uos_qty, 'product_qty':product_qty, 'qty':qty})
        return {'value': data}

wizard_picking_tracking_line()



class  wizard_picking_tracking(osv.osv_memory):
    _name = 'wizard.picking.tracking'
    
    def _get_serial(self, cr, uid, context=None):
        src_model  = context.get('active_model')
        src_record = self.pool.get(src_model).browse(cr, uid, context.get('active_id',False))
        
        if src_model == 'stock.picking.out':
            return  src_record.partner_id.ref
        elif src_model == 'stock.move':
            return  src_record.picking_id.partner_id.ref
        else:
            return None
    
    
    def _get_lines(self, cr, uid, context=None):
        src_model  = context.get('active_model')
        src_record = self.pool.get(src_model).browse(cr, uid, context.get('active_id',False))
        
        data = []
        if src_model == 'stock.picking.out':
            picking = src_record
            for move in picking.move_lines:
                data.append( (0, 0, {
                   'stock_move_id': move.id, 
                   'product_id':    move.product_id.id, 
                   'product_qty':   move.product_qty,
                   'product_uos_qty':   move.product_uos_qty,
                   'pack_no':   move.tracking_pack_no,
                   'tracking_id':   move.tracking_id and move.tracking_id.id or False,
                   'qty':           not move.tracking_id and move.product_qty or 0.0 ,
                }))
        
        elif src_model == 'stock.move':
            move = src_record
            data.append( (0, 0, {
                   'stock_move_id': move.id, 
                   'product_id':    move.product_id.id, 
                   'product_qty':   move.product_qty,
                   'product_uos_qty':   move.product_uos_qty,
                   'pack_no':   move.tracking_pack_no,
                   'tracking_id':   move.tracking_id and move.tracking_id.id or False,
                   'qty':           not move.tracking_id and move.product_qty or 0.0 ,
            }))
        
        return data
    
    
    def _get_picking(self, cr, uid, context=None):
        src_model = context.get('active_model')
        if src_model == 'stock.picking.out':
            return context.get('active_id', False)
        elif src_model == 'stock.move':
            stock_move=self.pool.get(src_model).browse(cr, uid, context.get('active_id', False))
            return stock_move.picking_id.id 
    
    
    def _get_pack_address(self, cr, uid, context=None):
        src_model  = context.get('active_model')
        src_record = self.pool.get(src_model).browse(cr, uid, context.get('active_id',False))
        if src_model == 'stock.picking.out':
            picking_out = src_record
            packaddres = picking_out.partner_id.contact_address
            return packaddres or False
        
        elif src_model == 'stock.move':
            move       = src_record
            sale_order = move.picking_id.sale_id
            return sale_order.partner_shipping_id.contact_address or False

    def _get_pack_receiver(self, cr, uid, context=None):
        src_model  = context.get('active_model')
        src_record = self.pool.get(src_model).browse(cr, uid, context.get('active_id',False))
        if src_model == 'stock.picking.out':
            picking_out = src_record
            packreceiver = picking_out.partner_id.display_name
            return packreceiver or False
        elif src_model == 'stock.move':
            move       = src_record
            sale_order = move.picking_id.sale_id
            packreceiver = sale_order.partner_shipping_id.display_name
            return packreceiver or False

    def _get_pack_number(self, cr, uid, context=None):
        src_model  = context.get('active_model')
        src_record = self.pool.get(src_model).browse(cr, uid, context.get('active_id',False))
        packno=1
        if src_model == 'stock.picking.out':
            picking_out = src_record
            for pack in picking_out.packing_tracking_ids:
                packno = packno +1               
        return packno
   
    
    _columns={
        'name': fields.char('name', size=32, readonly=True),
        'picking_id': fields.many2one('stock.picking','Picking'),
        'ul_id': fields.many2one('product.ul', 'Pack Template', required=True),
        'lines': fields.one2many('wizard.picking.tracking.line', 'wizard_id', 'Lines'),
        
        'pack_receiver': fields.char('Receiver', size=200),
        'pack_address': fields.char('Address', size=300),
        'pack_note':    fields.char('Note', size=128),
        'gross_weight': fields.float('GW (Kg)'),
        'pack_no':       fields.integer('Pack No'),
        #'net_weight':   fields.float('NW (Kg)'),
    }
    
    _defaults={
        'lines': lambda self,cr,uid,context: self._get_lines(cr, uid, context=context), 
        'picking_id': lambda self,cr,uid,context: self._get_picking(cr, uid, context=context), 
        'pack_address': lambda self,cr,uid,context: self._get_pack_address(cr, uid, context=context),
        'pack_receiver': lambda self,cr,uid,context: self._get_pack_receiver(cr, uid, context=context),
        'pack_no': lambda self,cr,uid,context: self._get_pack_number(cr, uid, context=context),
         
    }
    
    
    def _action_check(self, wizard):
        if wizard.picking_id.state == 'done':
            raise osv.except_osv(_('Warning!'), _("Wizard split pack can not be used when state is done !"))
        for line in wizard.lines:
            if line.qty > line.product_qty:
                raise osv.except_osv(_('Warning!'), _("New pack quantity can not bigger than stock move quantity"))
        return True
    
    
    def action_split(self, cr, uid, ids, context=None):
        
        
        tracking_obj    = self.pool.get('stock.tracking')
        stock_move_obj  = self.pool.get('stock.move')
        procurement_obj = self.pool.get('procurement.order')
        wizard          = self.browse(cr,uid,ids[0],context=context)
        self._action_check(wizard)
        
        tracking_values = {
            'ul_id':  wizard.ul_id.id,
            'pack_lineorder': wizard.pack_no,            
            'pack_address': wizard.pack_address,
            'pack_receiver': wizard.pack_receiver,
            'pack_note':    wizard.pack_note,
            'gross_weight': wizard.gross_weight,
            'pack_h': wizard.ul_id.high,
            'pack_w': wizard.ul_id.width,
            'pack_l': wizard.ul_id.long,
            'pack_tare': wizard.ul_id.tare,
            'move_ids':     [],
         }
        
        new_pack_id = tracking_obj.create(cr, uid, tracking_values)
        
        for line in wizard.lines:
            stock_move  = line.stock_move_id
            old_pack_id = stock_move.tracking_id and stock_move.tracking_id.id or False
            
            if not line.qty:
                continue
            
            res_product_qty = stock_move.product_qty - line.qty
            
            if res_product_qty:
                # update old stock move count procurement count
                stock_move_obj.write(cr, uid, stock_move.id, {'product_uos_qty':res_product_qty, 'product_qty':res_product_qty})
                
                procurement_id = stock_move.procurements and stock_move.procurements[0].id
                
                if procurement_id:
                    procurement_obj.write(cr, uid, procurement_id, {'product_uos_qty':res_product_qty, 'product_qty':res_product_qty})
                
                new_move_data = stock_move_obj.copy_data(cr, uid, stock_move.id, default = {
                    'product_qty':     line.qty , 
                    'product_uos_qty': line.qty, 
                    'tracking_id':     new_pack_id,  
                    'procurements':    False,
                    'state':           stock_move.state,                                                       
                }) 
                new_move_id = stock_move_obj.create(cr, uid, new_move_data)
                
                if procurement_id:
                    procurement_data = procurement_obj.copy_data(cr, uid, procurement_id, default = {
                        'product_uos_qty': line.qty,
                        'product_qty':     line.qty,
                        'move':            new_move_id,
                    })
                    new_procurement_id = procurement_obj.create(cr, uid, procurement_data)
            
            else:
                #if not res_product_qty, only to change the package
                stock_move_obj.write(cr, uid, stock_move.id, {'tracking_id':new_pack_id})
        
        src_model  = context.get('active_model')
        src_record = self.pool.get(src_model).browse(cr, uid, context.get('active_id',False))
        if src_model == 'stock.picking.out':
            src_id=src_record.id
            self.pool.get(src_model).btn_calc_weight(cr,uid, [src_id])

        #return new_pack_id
        return {
          'name': _('Pack Split'),
          'view_type': 'form',
          "view_mode": 'form',
          'res_model': 'stock.picking.out',
          'res_id':    wizard.picking_id.id,
          'type':      'ir.actions.act_window',
        }
    
wizard_picking_tracking()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: