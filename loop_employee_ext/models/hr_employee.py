# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    full_time_ability = fields.Boolean(string='Full Time Ability')
