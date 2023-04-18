# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2019. All rights reserved.
import pdb

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from twilio.rest import Client
import datetime


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    form_1099 = fields.Many2one('accounting.form.1099', string="Form 1099")
    # its_1099 = fields.Boolean(related='product_id.its_1099', string="Its 1099")


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    use_in_award = fields.Boolean(string='Can be used in Award')


class AccountingForm1099Line(models.Model):
    _name = 'accounting.form.1099.line'
    _description = 'Accounting Form 1099 Line'

    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')]).id, readonly=True)
    invoice_line_id = fields.Many2one('account.invoice.line', string='Invoice Line')
    form_1099_id = fields.Many2one('accounting.form.1099', string='Form')
    rm_form_1099_id = fields.Many2one('accounting.form.1099', string='Form')
    amount = fields.Monetary(string='Amount', currency_field='currency_id')
    product_id = fields.Many2one(related="invoice_line_id.product_id", string="Product")

    # variables for division
    settlement_item = fields.Boolean(related="product_id.x_settlement_item", string="Settlement Item")
    use_in_award = fields.Boolean(related="product_id.use_in_award", string="Award")
    driver_contractor_deduction = fields.Boolean(related="product_id.x_driver_contractor_deductions",
                                                 string="Deductions")
    scheduled_deduction = fields.Boolean(related="product_id.x_scheduled_deductions", string="Scheduled Deductions")
    use_for_fuel = fields.Boolean(related="product_id.x_use_for_fuel", string="Fuel")
    use_for_defd = fields.Boolean(related="product_id.x_use_for_defd", string="Fuel")

    def unlink(self):
        if self.rm_form_1099_id and not self.form_1099_id:
            self.invoice_line_id.form_1099 = False
            return super(AccountingForm1099Line, self).unlink()
        else:
            self.rm_form_1099_id = self.form_1099_id.id
            self.form_1099_id = False

    def reverse_entry(self):
        for rec in self:
            rec.form_1099_id = rec.rm_form_1099_id.id
            rec.rm_form_1099_id = False



class AccountingForm1099(models.Model):
    _name = 'accounting.form.1099'
    _description = 'Accounting Form 1099'

    form_based = fields.Selection(
        [('driver', 'Driver'), ('vehicle', 'Vehicle'), ('contract', 'Contract'), ('partner', 'Partner')],
        string="For Based on"
    )
    driver_id = fields.Many2one('hr.employee', string='Driver')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    contract_id = fields.Many2one('hr.contract', string='Contract')
    partner_id = fields.Many2one('res.partner', string='Partner')
    partner_filter_id = fields.Many2one('res.partner', string='Partner')
    division_id = fields.Many2one('operating.unit', string='Partner')
    line_ids = fields.One2many('accounting.form.1099.line', 'form_1099_id', string='Lines')
    rm_line_ids = fields.One2many('accounting.form.1099.line', 'rm_form_1099_id', string='Remove Lines')
    sett_items_line_ids = fields.One2many(
        'accounting.form.1099.line',
        'form_1099_id',
        string='Settlement Items',
        ondelete='cascade',
        domain=[('settlement_item', '=', True)]
    )
    award_line_ids = fields.One2many(
        'accounting.form.1099.line',
        'form_1099_id',
        string='Award',
        ondelete='cascade',
        domain=[('use_in_award', '=', True),('settlement_item', '=', False)]
    )
    deduction_line_ids = fields.One2many(
        'accounting.form.1099.line',
        'form_1099_id',
        string='Deduction',
        ondelete='cascade',
        domain=[('driver_contractor_deduction', '=', True),('use_in_award', '=', False),('settlement_item', '=', False)]
    )
    sch_deduction_line_ids = fields.One2many(
        'accounting.form.1099.line',
        'form_1099_id',
        string='Scheduled Deduction',
        ondelete='cascade',
        domain=[('scheduled_deduction', '=', True),('driver_contractor_deduction', '=', False),('use_in_award', '=', False),('settlement_item', '=', False)]
    )
    fuel_line_ids = fields.One2many(
        'accounting.form.1099.line',
        'form_1099_id',
        string='Fuel',
        ondelete='cascade',
        domain=[('scheduled_deduction', '=', False),('driver_contractor_deduction', '=', False),('use_in_award', '=', False),('settlement_item', '=', False),'|',('use_for_fuel', '=', True),('use_for_defd', '=', True)]
    )
    rm_fuel_line_ids = fields.One2many(
        'accounting.form.1099.line',
        'rm_form_1099_id',
        string='Fuel',
        ondelete='cascade',
        domain=['|',('use_for_fuel', '=', True),('use_for_defd', '=', True)]
    )

    rm_sett_items_line_ids = fields.One2many(
        'accounting.form.1099.line',
        'rm_form_1099_id',
        string='Settlement Items',
        ondelete='cascade',
        domain=[('settlement_item', '=', True)]
    )
    rm_award_line_ids = fields.One2many(
        'accounting.form.1099.line',
        'rm_form_1099_id',
        string='Credits',
        ondelete='cascade',
        domain=[('use_in_award', '=', True)]
    )
    rm_deduction_line_ids = fields.One2many(
        'accounting.form.1099.line',
        'rm_form_1099_id',
        string='Deduction',
        ondelete='cascade',
        domain=[('driver_contractor_deduction', '=', True)]
    )
    rm_sch_deduction_line_ids = fields.One2many(
        'accounting.form.1099.line',
        'rm_form_1099_id',
        string='Scheduled Deduction',
        ondelete='cascade',
        domain=[('scheduled_deduction', '=', True)]
    )
    year = fields.Selection([(num, str(num)) for num in range(2012, (datetime.datetime.now().year) + 1)], 'Year')
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')]).id, readonly=True)
    total_amount = fields.Monetary(string='Total Amount', currency_field='currency_id', compute='_compute_total_amount',
                                   store=True)
    sett_total_amount = fields.Monetary(string='Total Amount', currency_field='currency_id',
                                        compute='_compute_total_amount',
                                        store=True)
    award_total_amount = fields.Monetary(string='Total Amount', currency_field='currency_id',
                                         compute='_compute_total_amount',
                                         store=True)
    ded_total_amount = fields.Monetary(string='Total Amount', currency_field='currency_id',
                                       compute='_compute_total_amount',
                                       store=True)
    sch_total_amount = fields.Monetary(string='Total Amount', currency_field='currency_id',
                                       compute='_compute_total_amount',
                                       store=True)

    @api.depends('line_ids')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = sum((x.amount for x in rec.line_ids))
            rec.sett_total_amount = sum((x.amount for x in rec.sett_items_line_ids))
            rec.award_total_amount = sum((x.amount for x in rec.award_line_ids))
            rec.ded_total_amount = sum((x.amount for x in rec.deduction_line_ids))
            rec.sch_total_amount = sum((x.amount for x in rec.sch_deduction_line_ids))

    def generate_lines(self):
        for rec in self.line_ids:
            rec.unlink()
        first_day = datetime.datetime.strptime('%s-01-01' % (self.year), '%Y-%m-%d')
        last_day = datetime.datetime.strptime('%s-12-31' % (self.year), '%Y-%m-%d')
        lines = False
        if self.driver_id:
            lines = self.env['account.invoice.line'].search(
                [('driver_id', '=', self.driver_id.id), ('form_1099', '=', False),
                 ('statement_date', '>=', first_day.date()),
                 ('statement_date', '<=', last_day.date()), ('x_its_1099', '=', True),
                 ('division_id', '=', self.division_id.id), ('partner_id', '=', self.partner_filter_id.id)])

        if self.vehicle_id:
            lines = self.env['account.invoice.line'].search(
                [('truck_id', '=', self.vehicle_id.id), ('form_1099', '=', False),
                 ('statement_date', '>=', first_day.date()),
                 ('statement_date', '<=', last_day.date()), ('x_its_1099', '=', True),
                 ('division_id', '=', self.division_id.id), ('partner_id', '=', self.partner_filter_id.id)])
        if self.partner_id:
            lines = self.env['account.invoice.line'].search(
                [('partner_id', '=', self.partner_id.id), ('form_1099', '=', False),
                 ('statement_date', '>=', first_day.date()),
                 ('statement_date', '<=', last_day.date()), ('x_its_1099', '=', True),
                 ('division_id', '=', self.division_id.id)])
        if self.contract_id:
            lines = self.env['account.invoice.line'].search(
                [('contract_id', '=', self.contract_id.id), ('form_1099', '=', False),
                 ('statement_date', '>=', first_day.date()),
                 ('statement_date', '<=', last_day.date()), ('x_its_1099', '=', True),
                 ('division_id', '=', self.division_id.id), ('partner_id', '=', self.partner_filter_id.id)])
        for rec in lines:
            data = {
                'invoice_line_id': rec.id,
                'form_1099_id': self.id,
                'amount': rec.price_subtotal
            }
            self.env['accounting.form.1099.line'].create(data)
            rec.form_1099 = self.id


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    assigned_driver_id = fields.Many2one('hr.employee', string='Driver 1', compute='_compute_assignations')
    assigned_driver2_id = fields.Many2one('hr.employee', string='Driver 2', compute='_compute_assignations')

    assigned_driver_phone = fields.Char(string='Driver 1 Phone', compute='_compute_assignations')
    assigned_driver2_phone = fields.Char(string='Driver 2 Phone', compute='_compute_assignations')

    assigned_driver_email = fields.Char(string='Driver 1 Email', compute='_compute_assignations')
    assigned_driver2_email = fields.Char(string='Driver 2 Email', compute='_compute_assignations')


class TmsExpensePreliminary(models.Model):
    _inherit = 'tms.expense.preliminary'

    sett_id = fields.Many2one('tms.settlement', 'Driver Settlement (Not Used)')
    v_sett_id = fields.Many2one('tms.vehicle.settlement', 'Vehicle Settlement (Not Used)')

    @api.depends('settlement_id','v_settlement_id')
    def remove_sett_line(self):
        for rec in self:
            if not(rec.settlement_line_id.settlement_id and rec.settlement_line_id.v_settlement_id):
                rec.settlement_line_id = False

class TmsSettlementLine(models.Model):
    _inherit = 'tms.settlement.line'

    settlement_id = fields.Many2one('tms.settlement', string='Driver Settlement')
    v_settlement_id = fields.Many2one('tms.vehicle.settlement', string='Vehicle Settlement')
    trip_track_id = fields.Many2one('tms.trip', string='Trip Track')
