from odoo import api, fields, models, _
from odoo.addons.purchase.models.account_invoice import AccountMove as OdooAccountMove
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    pnt_picking_supplier_id = fields.Many2one(
        string="Picking Supplier Code",
        comodel_name="pnt.stock.picking.supplier",
        store=False,
        check_company=True,
    )

    pnt_loaded_supplier_ids = fields.One2many(
        comodel_name='pnt.stock.picking.supplier',
        inverse_name='pnt_account_move_loaded_id',
        string="Processed Supplier ids",
        readonly=False,
        domain="[('id', 'in', pnt_history_supplier_ids)]",
    )

    pnt_history_supplier_ids = fields.One2many(
        comodel_name='pnt.stock.picking.supplier',
        string="Processed Supplier ids History",
        inverse_name='pnt_account_move_history_id',
        readonly=False,
    )

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        if 'pnt_loaded_supplier_ids' in vals and 'pnt_history_supplier_ids' not in vals:
            self._delete_invoice_lines_if_supplier_id_removed()
        return res

    def unlink(self):
        if self.pnt_loaded_supplier_ids:
            raise UserError(
                _(
                    "Before deleting an invoice, remove any linked supplier ids: \n %s"
                )
                % ", ".join(self.pnt_loaded_supplier_ids.mapped('pnt_name'))
            )
        res = super(AccountMove, self).unlink()
        return res

    def _delete_invoice_lines_if_supplier_id_removed(self):
        for record in self:
            remaining_supplier_ids = set(record.pnt_loaded_supplier_ids.ids)
            original_supplier_ids = set(record.pnt_history_supplier_ids.ids)
            removed_supplier_ids = original_supplier_ids - remaining_supplier_ids

            if removed_supplier_ids:
                record._delete_invoice_lines_for_removed_supplier_ids(removed_supplier_ids)
                record._sync_account_move_supplier_ids()
                record.env['pnt.stock.picking.supplier'].browse(list(removed_supplier_ids)).pnt_picking_ids.write({'pnt_is_invoiced': False})

    def _delete_invoice_lines_for_removed_supplier_ids(self, removed_supplier_ids):

        lines_to_delete = self.env['account.move.line'].search([
            ('move_id', '=', self.id),
            ('pnt_picking_supplier_id', 'in', list(removed_supplier_ids))
        ])

        lines_not_to_delete = self.env['account.move.line'].search([
            ('move_id', '=', self.id),
        ]) - lines_to_delete

        arr = []
        for line in lines_not_to_delete:
            arr.append((4, line.id, False))
        for line in lines_to_delete:
            arr.append((2, line.id, False))

        self.write({'invoice_line_ids': arr})

    def _sync_account_move_supplier_ids(self):
        supplier_ids = self.pnt_loaded_supplier_ids.ids
        self.write({
            'pnt_history_supplier_ids': [(6, 0, supplier_ids)]
        })

    @api.onchange("pnt_picking_supplier_id")
    def _onchange_pnt_picking_supplier_id(self):
        if self.pnt_picking_supplier_id:

            # ==== GET PICKINGS, MARK AS INVOICED AND ADD TO MANY2MANY ====
            supplier_picking_ids = self.pnt_picking_supplier_id.pnt_picking_ids
            if supplier_picking_ids.ids:
                supplier_picking_ids.write({'pnt_is_invoiced': True})
                self.write({
                    'pnt_history_supplier_ids': [(4, self.pnt_picking_supplier_id.id)],
                    'pnt_loaded_supplier_ids': [(4, self.pnt_picking_supplier_id.id)],
                })
            # ====#

            purchase_ids = self.pnt_picking_supplier_id.mapped(
                "pnt_picking_ids.move_ids_without_package.purchase_line_id.order_id"
            )

            purchase_bill_union_ids = self.env["purchase.bill.union"].search(
                [("purchase_order_id", "in", purchase_ids.ids)]
            )
            for purchase_bill_union in purchase_bill_union_ids:
                self.purchase_vendor_bill_id = purchase_bill_union.id
                self._onchange_purchase_auto_complete()

            self.pnt_picking_supplier_id = False

    @api.onchange('purchase_vendor_bill_id', 'purchase_id')
    def _onchange_purchase_auto_complete(self):
        if self.purchase_vendor_bill_id.vendor_bill_id:
            self.invoice_vendor_bill_id = self.purchase_vendor_bill_id.vendor_bill_id
            self._onchange_invoice_vendor_bill()
        elif self.purchase_vendor_bill_id.purchase_order_id:
            self.purchase_id = self.purchase_vendor_bill_id.purchase_order_id
        self.purchase_vendor_bill_id = False
        if not self.purchase_id:
            return

        # ===== INVOICE HEADER ==== #
        invoice_vals = self.purchase_id.with_company(self.purchase_id.company_id)._prepare_invoice()
        invoice_vals['currency_id'] = self.line_ids and self.currency_id or invoice_vals.get('currency_id')
        invoice_vals.pop('ref', None)
        self.update(invoice_vals)
        # ==== #

        # ==== COPY LINES AND LINK TO PO =====
        self._copy_purchase_lines()
        self.purchase_id.order_line._compute_qty_invoiced()
        self._get_invoice_headers()
        # ===== #

    def _copy_purchase_lines(self):
        original_po_lines = self.purchase_id.order_line
        if self.pnt_picking_supplier_id:
            purchase_line_ids = self.pnt_picking_supplier_id.mapped(
                'pnt_picking_ids.move_ids_without_package.purchase_line_id'
            ).ids
            original_po_lines = original_po_lines.filtered(lambda x: x.id in purchase_line_ids)

        new_lines = self.env['account.move.line']
        sequence = max(self.line_ids.mapped('sequence')) + 1 if self.line_ids else 10
        for line in original_po_lines.filtered(lambda l: not l.display_type):
            line_vals = line._prepare_account_move_line(self)
            self._update_line_vals_with_picking_quantity(line, line_vals)
            line_vals.update({
                'sequence': sequence,
                'pnt_stock_picking_ids': [(6, 0, self.pnt_picking_supplier_id.pnt_picking_ids.ids)],
                'pnt_stock_supplier_ids': [(6, 0, [self.pnt_picking_supplier_id.id])],
                'pnt_picking_supplier_id': self.pnt_picking_supplier_id.id,
            })
            sequence += 1

            new_line = new_lines.new(line_vals)
            new_line.account_id = new_line._get_computed_account()
            new_line._onchange_price_subtotal()
            line.write({
                'invoice_lines': [(4, new_line.id)]
            })

            new_lines += new_line
        new_lines._onchange_mark_recompute_taxes()

    def _update_line_vals_with_picking_quantity(self, line, line_vals):
        if not self.pnt_picking_supplier_id:
            return

        picking_quantity = self.pnt_picking_supplier_id.mapped('pnt_picking_ids.move_ids_without_package').filtered(
            lambda x: x.purchase_line_id == line
        ).quantity_done

        pending_to_invoice = line.qty_received - line.qty_invoiced
        if picking_quantity:
            if pending_to_invoice <= 0:
                return
            else:
                line_vals.update({'quantity': picking_quantity})

    def _get_invoice_headers(self):
        # Compute invoice_origin
        origins = set(self.line_ids.mapped('purchase_line_id.order_id.name'))
        self.invoice_origin = ','.join(list(origins))

        # Compute ref
        refs = self._get_invoice_reference()
        self.ref = ', '.join(refs)

        # Compute payment_reference
        if len(refs) == 1:
            self.payment_reference = refs[0]

        self.purchase_id = False
        self._onchange_currency()

    # Override Odoo's default method with the custom one
    OdooAccountMove._onchange_purchase_auto_complete = _onchange_purchase_auto_complete


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    pnt_picking_supplier_id = fields.Many2one(
        string="Picking Supplier",
        comodel_name="pnt.stock.picking.supplier",
        readonly=False,
    )

    pnt_stock_picking_ids = fields.Many2many(
        'stock.picking',
        string='Stock Pickings',
        store=True,
    )

    pnt_stock_supplier_ids = fields.Many2many(
        'pnt.stock.picking.supplier',
        string='Stock Pickings',
        store=True,
    )

