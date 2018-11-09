# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class MedicalMedicationAdministration(models.Model):
    _name = 'medical.medication.administration'
    _inherit = 'medical.event'

    def _default_patient_location(self):
        return self.env.ref('medical_medication_request.location_patient')

    internal_identifier = fields.Char(
        string="Medication administration"
    )
    medication_request_id = fields.Many2one(
        comodel_name='medical.medication.request',
        ondelete='restrict', index=True,
    )
    location_id = fields.Many2one(
        comodel_name='res.partner',
        ondelete='restrict', index=True,
        domain=[
            ('is_location', '=', True),
            ('stock_picking_type_id', '!=', False),
            ('stock_location_id', '!=', False)],
    )
    stock_location_id = fields.Many2one(
        comodel_name='stock.location',
        related='location_id.stock_location_id',
        ondelete='restrict', index=True,
    )
    stock_picking_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        related='location_id.stock_picking_type_id',
        ondelete='restrict', index=True,
    )
    patient_location_id = fields.Many2one(
        comodel_name='stock.location',
        default=_default_patient_location,
        ondelete='restrict', index=True,
    )
    product_id = fields.Many2one(
        'product.product',
        'Product',
        ondelete='restrict', index=True,
        required=True,
        states={'done': [('readonly', True)]},
    )
    product_uom_id = fields.Many2one(
        'product.uom',
        'Unit of Measure',
        ondelete='restrict', index=True,
        required=True,
        states={'done': [('readonly', True)]},
    )
    tracking = fields.Selection(
        'Product Tracking',
        readonly=True,
        related="product_id.tracking",
    )
    lot_id = fields.Many2one(
        'stock.production.lot',
        'Lot',
        ondelete='restrict', index=True,
        states={'done': [('readonly', True)]},
        domain="[('product_id', '=', product_id)]",
    )
    package_id = fields.Many2one(
        'stock.quant.package',
        'Package',
        ondelete='restrict', index=True,
        states={'done': [('readonly', True)]},
    )
    qty = fields.Float(
        'Quantity',
        default=1.0,
        required=True,
        states={'done': [('readonly', True)]},
    )
    picking_ids = fields.One2many(
        'stock.picking',
        inverse_name='medication_administration_id'
    )

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id

    def _get_internal_identifier(self, vals):
        return self.env['ir.sequence'].next_by_code(
            'medical.medication.administration') or '/'

    def _prepare_picking_values(self):
        self.ensure_one()
        return {
            'origin': self.internal_identifier,
            'location_id': self.stock_location_id.id,
            'location_dest_id': self.patient_location_id.id,
            'medication_administration_id': self.id,
            'picking_type_id': self.stock_picking_type_id.id,
            'name': self.stock_picking_type_id.sequence_id.next_by_id(),
            'move_lines': [(0, 0, {
                'picking_type_id': self.stock_picking_type_id.id,
                'name': self.product_id.name,
                'product_id': self.product_id.id,
                'product_uom': self.product_uom_id.id,
                'product_uom_qty': self.qty,
            })]
        }

    @api.multi
    def in_progress2completed(self):
        self.ensure_one()
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        available_qty = sum(self.env['stock.quant']._gather(
            self.product_id,
            self.stock_location_id,
            self.lot_id,
            self.package_id,
            strict=True
        ).mapped('quantity'))
        if (
            self.product_id.type == 'consu' or
            self.stock_location_id.should_bypass_reservation() or
            float_compare(
                available_qty, self.qty, precision_digits=precision
            ) >= 0
        ):
            self.generate_move()
            return super(
                MedicalMedicationAdministration, self).in_progress2completed()
        raise ValidationError(_('Insufficient quantity'))

    @api.multi
    def generate_move(self):
        for event in self:
            if not self.location_id:
                raise ValidationError(_(
                    'Location must be defined in order to complete'))
            event.picking_ids = self.env['stock.picking'].create(
                event._prepare_picking_values()
            )
            event.picking_ids.action_confirm()
            event.picking_ids.action_assign()
            for move in event.picking_ids.move_lines:
                if move.move_line_ids:
                    for move_line in move.move_line_ids:
                        move_line.qty_done = move_line.product_uom_qty
                else:
                    move.quantity_done = move.product_uom_qty
            event.picking_ids.action_done()
            event.write({
                'occurrence_date': fields.Datetime.now()
            })

    def action_view_stock_moves(self):
        self.ensure_one()
        action = self.env.ref('stock.do_view_pickings').read([])[0]
        action['domain'] = [('medication_administration_id', '=', self.id)]
        if len(self.picking_ids) == 1:
            action['views'] = [(False, 'form')]
            action['res_id'] = self.picking_ids.id
        return action
