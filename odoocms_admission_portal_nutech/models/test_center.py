from odoo import fields, models

class OdooCMSEntryTestCenter(models.Model):
    _inherit = "odoocms.application"

    center_id2 = fields.Many2one('odoocms.admission.test.center', 'Test Center 2')
    slot_id2 = fields.Many2one('odoocms.admission.test.time', 'Time 2')
    paper_name = fields.Selection([('paper1', 'Pre Engineering'), ('paper2', 'BET')])
    paper_name2 = fields.Selection([('paper1', 'Pre Engineering'), ('paper2', 'BET')])
    confirm_test_center2 = fields.Boolean('Confirm Test Slot 2', default=False)
