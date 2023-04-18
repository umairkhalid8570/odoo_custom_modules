# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class PosConfigExtended(models.Model):
    _inherit = 'pos.config'

    customer_discount = fields.Integer(string='Customer Discount', help='Enter Customer Discount (0 - 100)%')
