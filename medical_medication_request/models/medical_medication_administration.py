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
        # return self.env.ref('stock.stock_location_customers')
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
        store=True,
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
    move_ids = fields.One2many(
        'stock.move',
        inverse_name='medication_administration_id'
    )

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id

    def _get_internal_identifier(self, vals):
        return self.env['ir.sequence'].next_by_code(
            'medical.medication.administration') or '/'

    def _get_procurement_group(self):
        return self.env['procurement.group'].create({
            'name': self.internal_identifier,
            'move_type': 'direct',
            'partner_id': self.patient_id.partner_id.id,
        })

    def _get_origin(self):
        return self.internal_identifier

    def _get_qty_procurement(self):
        self.ensure_one()
        qty = 0.0
        for move in self.move_ids.filtered(lambda r: r.state != 'cancel'):
            if move.picking_code == 'outgoing':
                qty += move.product_uom._compute_quantity(
                    move.product_uom_qty, self.product_id.uom_id,
                    rounding_method='HALF-UP')
            elif move.picking_code == 'incoming':
                qty -= move.product_uom._compute_quantity(
                    move.product_uom_qty, self.product_id.uom_id,
                    rounding_method='HALF-UP')
        return qty

    @api.multi
    def in_progress2completed(self):
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        for event in self:
            qty = event._get_qty_procurement()
            if float_compare(
                qty, event.qty, precision_digits=precision
            ) >= 0:
                continue
            if not event.stock_location_id:
                raise ValidationError(_('That is not an stock location'))
            group = event._get_procurement_group()
            values = event._prepare_procurement_values(group)
            self.env['procurement.group'].run(
                event.product_id, event.qty, event.product_id.uom_id,
                event.patient_location_id, event.internal_identifier,
                event._get_origin(), values)
            if not self.env.context.get('no_post_move', False):
                event._post_move_create()
        return super().in_progress2completed()

    def _post_move_create(self):
        self.move_ids._action_assign()

    def in_progress2completed_values(self):
        res = super().in_progress2completed_values()
        res['occurrence_date'] = fields.Datetime.now()
        return res

    def _prepare_procurement_values(self, group):
        wh = self.stock_location_id.get_warehouse()
        return {
            'group_id': group,
            'medication_administration_id': self.id,
            'warehouse_id': wh,
            'partner_dest_id': group.partner_id,
            'route_ids': self.env['stock.location.route']
        }

    def action_view_stock_moves(self):
        self.ensure_one()
        action = self.env.ref('stock.stock_move_action').read([])[0]
        action['domain'] = [('medication_administration_id', '=', self.id)]
        if len(self.move_ids) == 1:
            action['views'] = [(False, 'form')]
            action['res_id'] = self.move_ids.id
        return action

    @api.constrains('medication_request_id', 'patient_id')
    def _check_patient_medication(self):
        if not self.env.context.get('no_check_patient', False):
            if (
                self.medication_request_id and
                self.patient_id != self.medication_request_id.patient_id
            ):
                raise ValidationError(_('Patient inconsistency'))
