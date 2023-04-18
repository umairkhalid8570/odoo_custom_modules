"""Your docstring.

Here.

"""
# Standard library imports
import logging
from itertools import groupby
# Third party imports
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
# Local application imports

# CONSTANTS

# Module init variables
_logger = logging.getLogger(__name__)


class TMSExpense(models.Model):
    _inherit = 'tms.expense'

    invoice_ids = fields.Many2many('account.invoice', relation='account_expense_rel', column1='eid', column2='iid',
                                   string='Invoices')

    def get_grouped_by_product(self, list_of_dicts, model_name='Expense'):
        '''
        Group all the prepared lines by product_id
        :param list_of_dicts: [(0,0,{'product_id':1, 'name':'aaa'}), ...]
        :return: list of dicts or []
        '''
        grouped_lines = groupby(sorted(list_of_dicts, key=lambda x: x.get('product_id', False)), key=lambda x: x.get('product_id', False))
        new_lines = []
        for k, g in grouped_lines:
            '''
            so we group as quantity 1, price common
            '''
            product_id = self.env['product.product'].browse(k)
            if not product_id:
                continue

            tot_amounts = sum((x['price_unit']*x['quantity'] for x in g))
            if not tot_amounts:
                continue

            new_lines.append(dict(
                name=_('Sum of {}'.format(model_name)),
                quantity=1,
                product_id=k,
                account_id=product_id.property_account_expense_id.id,
                price_unit=tot_amounts,
            ))
        return new_lines

    @api.multi
    def get_prepared_invoice_lines(self):
        if not self:
            return []
        lines = []
        for expense in self:
            lines.append(dict(
                quantity=expense.product_qty,
                name=expense.description or 'F.l.',
                product_id=expense.product_id.id,
                account_id=expense.product_id.property_account_expense_id.id,
                currency_id=expense.currency_id.id,
                price_unit=expense.price_unit,
            ))
        FeeProduct = self.env.ref('tms_base.product_fee')

        fee_to_append_g = sum(self.mapped('fee'))
        if fee_to_append_g:
            lines.append(dict(
                quantity=1,
                name=_('Common Fees'),
                product_id=FeeProduct.id,
                price_unit=fee_to_append_g,
            ))

        return lines


class TMSTripExpenese(models.Model):
    _inherit = 'tms.trip.expense'

    @api.multi
    def get_prepared_invoice_lines(self):
        # tolls and other expenses
        if not self:
            return []
        lines = []
        for expense in self:
            lines.append(dict(
                quantity=expense.product_qty,
                name='a.c.',
                product_id=expense.product_id.id,
                account_id=expense.product_id.property_account_expense_id.id,
                currency_id=expense.currency_id.id,
                price_unit=expense.price_unit,
            ))
        FeeProduct = self.env.ref('tms_base.product_fee')

        fee_to_append_g = sum(self.mapped('fee'))
        if fee_to_append_g:
            lines.append(dict(
                quantity=1,
                name=_('Common Fees'),
                product_id=FeeProduct.id,
                price_unit=fee_to_append_g,
            ))

        return lines


class TMSFuelLog(models.Model):
    _inherit = 'tms.trip.fuel.log'

    @api.multi
    def get_prepared_invoice_lines(self):
        # fuel Logs
        if not self:
            return []
        lines = []
        for expense in self:
            lines.append(dict(
                quantity=expense.product_qty,
                name=expense.description or 'F.l.',
                product_id=expense.product_id.id,
                account_id=expense.product_id.property_account_expense_id.id,
                currency_id=expense.currency_id.id,
                price_unit=expense.price_unit,
            ))
        FeeProduct = self.env.ref('tms_base.product_fee')

        fee_to_append_g = sum(self.mapped('fee'))
        if fee_to_append_g:
            lines.append(dict(
                quantity=1,
                name=_('Common Fees'),
                product_id=FeeProduct.id,
                price_unit=fee_to_append_g,
            ))

        return lines

EXPENSE_MODEL_SELECTIONS = (
    ('tms.trip.expense', _('Trip Expenses')),
    ('tms.trip.fuel.log', _('Fuel Logs')),
    ('tms.expense', _('Expense'))
)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    expense_ids = fields.Many2many('tms.expense', relation='account_expense_rel', column1='iid', column2='eid', string='Expenses', readonly=True, states={'draft': [('readonly', False)]})
    # exp_model_selector = fields.Selection(EXPENSE_MODEL_SELECTIONS, string='Expense Model', default='tms.expense')

    # @api.onchange('exp_model_selector')
    # def _onchange_exp_model_selector(self):
    #     if not self.env.context.get('from_expense', False):
    #         self.expense_ids = False

    @api.onchange('expense_ids')
    def _onchange_expense_ids(self):
        if self.expense_ids:
            # objects = self.env['tms.expense'].search([('expense_id','in',self.expense_ids.ids)])
            lines = self.expense_ids.get_prepared_invoice_lines()
            lines = self.env['tms.expense'].get_grouped_by_product(lines)

            self.invoice_line_ids = False
            self.invoice_line_ids = [(0, 0, x) for x in lines]
            self.invoice_line_ids._onchange_product_id()
        return {'domain':{}, 'readonly':{'partner_id': bool(self.expense_ids)}}


    @api.model
    def default_get(self, default_fields):
        res = super().default_get(default_fields)
        if 'from_expense' in self.env.context and self.env.context.get('from_expense') and self.env.context.get('active_ids', []):
            expense_ids = self.env[self.env.context.get('active_model')].search([('id','in', self.env.context.get('active_ids',[])),('invoice_ids','=',False)])
            if not expense_ids:
                raise UserError(_('No expenses selected!'))

            # collect fee for different currencies
            # deprecated for the full automation of bill making: for different companies, currencies etc.

            # down is small example

            # fee_to_append_g = groupby(sorted(expense_ids, key=lambda x: x.currency_id), key=lambda x: x.currency_id.id)
            #
            # for k, g in fee_to_append_g:
            #     tot_fee = sum((x['fee'] for x in g))
            #     if not tot_fee:
            #         continue
            #     lines.append(dict(
            #         quantity=1,
            #         product_id=FeeProduct.id,
            #         price_unit=tot_fee,
            #     ))

            partner_id = expense_ids.mapped('vendor_id')
            company_id = expense_ids.mapped('company_id')
            currency_id = expense_ids.mapped('currency_id')

            if len(partner_id.ids) != 1:
                raise UserError(_('There should be only one vendor in expenses you want to bill!'))
            if len(currency_id) > 1:
                raise UserError(_('All the transactions should be in one currency!'))
            if len(company_id) > 1:
                raise UserError(_('All the transactions should be for one Company!'))
            # lines = expense_ids.get_prepared_invoice_lines()
            journal_id = self.env['account.journal'].search([
                '|', ('currency_id', '=', currency_id.id), ('currency_id', '=', False),
                ('company_id', '=', company_id.id),
                ('type', '=', 'purchase')], limit=1)

            if self.env.context.get('active_model') == 'tms.expense':
                e_ids = expense_ids.ids
            else:
                e_ids = expense_ids.mapped('expense_ids').ids

            update_dict = dict(
                expense_ids=[(6, 0, e_ids)],
                partner_id=partner_id.id,
                # exp_model_selector=self.env.context.get('active_model'),
                # invoice_line_ids=[(0, 0, x) for x in lines],
                company_id=company_id.id,
                currency_id=currency_id.id,
                journal_id=journal_id.id,
                date_invoice=fields.Date.today(),
            )

            res.update(update_dict)
            # add all the expenses to bill

        return res


class TMSExpenseServices(models.Model):
    _inherit = 'tms.expense.fleet_service'

    e_amount = fields.Float(related='expense_id.amount', string='Amount', store=True)

    def onclick_create_invoice_expense(self):
        invoice_ids = self.env['account.invoice'].search([('expense_ids', 'in', self.expense_ids.ids)])

        if not invoice_ids:
            context = self._context.copy()
            context.update(dict(from_expense=True, active_ids=self.ids, default_type='in_invoice'))

            return {
                'type': 'ir.actions.act_window',
                'name': 'New Bill',
                'res_model': 'account.invoice',
                'view_mode': 'form',
                'context': context,
                'target': 'new'
            }
        else:
            action = {
                'name': 'Bill',
                'type': 'ir.actions.act_window',
                'res_model': 'account.invoice',
                'target': 'current',
                'res_is': invoice_ids[:1].id,
                'view_mode': 'form',
                'context': dict(self.env.context, default_type='in_invoice'),
            }
            return action
        return
