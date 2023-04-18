# -*- coding: utf-8 -*-
import pdb

from odoo import api, fields, models, tools, _
from functools import partial
import logging
import psycopg2
from odoo.tools import float_is_zero, float_round
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)

# _validate_session

    

class PosOrder(models.Model):
    _inherit = 'pos.order'

    c_untaxed_amount = fields.Float('Untaxed Amount')
    c_amount = fields.Float('Amount')
    c_discount_amount = fields.Float('Discount Amount')
    c_total_amount = fields.Float('Discount Amount')
    c_tax_amount = fields.Float('Tax Amount')

    @api.model
    def create_from_ui(self, orders, draft=False):
        order_ids = []
        for order in orders:
            existing_order = False
            if 'server_id' in order['data']:
                existing_order = self.env['pos.order'].search(
                    ['|', ('id', '=', order['data']['server_id']), ('pos_reference', '=', order['data']['name'])],
                    limit=1)
                order_ids.append(existing_order.id)
            elif 'name' in order['data']:
                existing_order = self.env['pos.order'].search([('pos_reference', '=', order['data']['name'])], limit=1)

            if existing_order:
                order_ids.append(existing_order.id)
            else:
                # if (existing_order and existing_order.state == 'draft') or not existing_order:
                #     order_ids.append(self._process_order(order, draft, existing_order))
                order_ids.append(self._process_order(order, draft, existing_order))

        return self.env['pos.order'].search_read(domain=[('id', 'in', order_ids)], fields=['id', 'pos_reference'])

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        if ui_order.get('c_untaxed_amount', False):
            order_fields.update({
                'c_untaxed_amount': ui_order['c_untaxed_amount']
            })
        if ui_order.get('c_amount', False):
            order_fields.update({
                'c_amount': ui_order['c_amount']
            })
        if ui_order.get('c_discount_amount', False):
            order_fields.update({
                'c_discount_amount': ui_order['c_discount_amount']
            })
        if ui_order.get('c_total_amount', False):
            order_fields.update({
                'c_total_amount': ui_order['c_total_amount']
            })
        return order_fields

class PosConfig(models.Model):
    _inherit = 'pos.config'

    street_part = fields.Text(related='branch_id.address', store=True)
