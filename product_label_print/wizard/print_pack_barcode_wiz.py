# coding: utf-8

from openerp import api, fields, models, _
from openerp.exceptions import Warning


class print_pack_barcode_wiz(models.TransientModel):
    _name = 'print.pack.barcode.wiz'
    _description = 'Product Label Print'
    product_label_ids = fields.Many2many('product.product.label', string="Products")
    label_ids = fields.Many2many('label.twoinrow', string="Labels")
    skip_first = fields.Boolean('Skip First Label')
    restrict_single = fields.Boolean('Restrict to single product', default=False)

    single_label_id = fields.Many2one('product.product.label',compute='_compute_single_label')
    single_label_name = fields.Char(string="Name",related='single_label_id.name')
    single_label_nameL1 = fields.Char(string="NameL1",related='single_label_id.nameL1')
    single_label_nameL2 = fields.Char(string="NameL1",related='single_label_id.nameL2')
    single_label_nameL3 = fields.Char(string="NameL2",related='single_label_id.nameL3')
    single_label_nameL4 = fields.Char(string="NameL3",related='single_label_id.nameL4')
    single_label_default_code = fields.Char(string="Default Code",related='single_label_id.default_code')
    single_label_short_code = fields.Char(string="Short Code",related='single_label_id.short_code')
    single_label_note = fields.Char(string="Note",related='single_label_id.note')
    single_label_pieces_in_pack = fields.Float(string="# in Cartoon", related='single_label_id.pieces_in_pack')
    single_label_label_to_print = fields.Integer(string='# of label to be printed', related='single_label_id.label_to_print')
    single_label_product_id = fields.Many2one('product.product', string="Product", related='single_label_id.product_id')
    single_label_barcode = fields.Char(string="Barcode", related='single_label_id.barcode')
    single_label_uom_name = fields.Char(string="UOM Name", related='single_label_id.uom_name')
    
    
    @api.one
    @api.depends('product_label_ids')
    def _compute_single_label(self):
        if self.product_label_ids:
            self.single_label_id = self.product_label_ids[0]
    
    @api.model
    def default_get(self, fields):
        ''' 
        To get default values for the object.
        '''
        product_label_obj = self.env['product.product.label']
        res = super(print_pack_barcode_wiz, self).default_get(fields)
        product_ids = []
        
        if self.env.context.get('default_restrict_single',False) and len(self.env.context.get('active_ids')) > 1:
            raise Warning(_('Printing multiple labels is restricted!'))
            
        for product in self.env.context.get('active_ids'):
            product_id = self.env['product.product'].browse(product)
            codeparts = product_id.default_code.split('-')

            if len(codeparts) > 4:
                if codeparts[3]=='0':
                    if codeparts[2]=='0':
                        shortcode = ('-'.join(codeparts[0:2]))
                    else:
                        shortcode = ('-'.join(codeparts[0:3]))
                else:
                    shortcode = ('-'.join(codeparts[0:4]))
            else:
                shortcode = product_id.default_code

            nameline = 1
            nameL = {1:'',
                     2:'',
                     3:'',
                     4:''}

            for word in product_id.name_variant.split():
                if len(nameL[nameline]+' '+word) < 27:
                    nameL[nameline]=(nameL[nameline]+' '+word).strip()
                else:
                    nameline = nameline +1
                    nameL[nameline] = (nameL[nameline] + ' ' + word).strip()


            product_label_id = product_label_obj.create({
                    'name': product_id.name_variant,
                    'nameL1': nameL[1],
                    'nameL2': nameL[2],
                    'nameL3': nameL[3],
                    'nameL4': nameL[4],
                'default_code': product_id.default_code,
                    'short_code': shortcode,
                    'note': '',
                    'pieces_in_pack': product_id.pieces_in_pack,
                    'label_to_print': 1,
                    'barcode': product_id.ean13,
                    'uom_name': product_id.uom_id.name,
                    'product_id': product_id.id
            })
            product_ids.append(product_label_id.id)
        res.update({'product_label_ids': [(6, 0, product_ids)] or [],
                    'skip_first': False
                    })
        return res

    @api.multi
    def generate_labels(self):
        last_label = self.product_label_ids[0]
        leap_label = False
        Label_Res = []
        label_template_obj = self.env['label.twoinrow']
        for product_label in self.product_label_ids:
            labels_to_print = product_label.label_to_print
            while labels_to_print > 0:
                if self.skip_first:
                    Label_l = label_template_obj.create({
                        'first_label_empty' : True,
                        'label1': product_label.id,
                        'second_label_empty': False,
                        'label2': product_label.id,
                        'copies_to_print': 1,
                    })
                    Label_Res.append(Label_l.id)
                    self.skip_first = False
                    labels_to_print = labels_to_print - 1
                if leap_label:
                    Label_l = label_template_obj.create({
                        'first_label_empty': False,
                        'label1': last_label.id,
                        'second_label_empty': False,
                        'label2': product_label.id,
                        'copies_to_print': 1,
                    })
                    Label_Res.append(Label_l.id)
                    leap_label = False
                    labels_to_print = labels_to_print -1

                if labels_to_print > 1:
                    # 1 1
                    Label_l = label_template_obj.create({
                        'first_label_empty': False,
                        'label1': product_label.id,
                        'second_label_empty': False,
                        'label2': product_label.id,
                        'copies_to_print': labels_to_print/2,
                    })
                    labels_to_print = labels_to_print - ((labels_to_print/2)*2)
                    Label_Res.append(Label_l.id)
                if labels_to_print == 1:
                    leap_label = True
                    last_label = product_label
                    labels_to_print = 0
        if leap_label:
            Label_l = label_template_obj.create({
                #Tek last label
                'first_label_empty': False,
                'label1': product_label.id,
                'second_label_empty': True,
                'label2': product_label.id,
                'copies_to_print': 1,
                })
            Label_Res.append(Label_l.id)
        self.label_ids =[(6, 0, Label_Res)]
        return False


    @api.multi
    def show_label(self):
        self.generate_labels()
        datas = {
                'ids': self.env.context.get('active_ids'),
                'model': 'print.pack.barcode.wiz'
            }

        res = {
            'type' : 'ir.actions.report.xml',
            'report_name': 'product_label_print',
            'datas' : datas,
        }
        return self.env['report'].get_action(self, 'product_label_print')


    @api.multi
    def print_label(self):
        cr  = self.env.cr
        uid = self.env.uid
        ids = self.ids
        context = self.env.context
        self.generate_labels()

        server_action_ids = [1176]
        server_action_ids = map(int, server_action_ids)
        action_server_obj = self.pool.get('ir.actions.server')
        ctx = dict(context, active_model='print.pack.barcode.wiz', active_ids=ids, active_id=ids[0])
        action_server_obj.run(cr, uid, server_action_ids, context=ctx)

        return {'type': 'ir.actions.act_window_close'}