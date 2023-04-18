from odoo import fields, models

class PosConfig(models.Model):
    _inherit = "pos.config"

    pos_order_timeout = fields.Integer(
        string="PoS Order(s) Timeout",
        help="Defines the value of the"
             " client-side timeout for the creation of PoS Order(s)"
             " from the POS UI.\n"
             " The value is expressed in seconds, for a single order.\n"
             " If not defined, the default Odoo value will be used: 30 seconds.\n"
             " If the call contains more than one order"
             " (after a long disconnection period for example, or if the previous"
             " call raised the timeout),\n the effective timeout value applied will"
             " be equal to the defined timeout value multiplied by the number of"
             " orders.\n",
    )
    session_timeout = fields.Integer(
        string="Session Timeout",
        help="Defines the value of the"
        " client-side timeout if screen is idle in POS UI.\n"
        " The value is expressed in seconds.\n",
    )
    auto_logout_on_each_sale = fields.Boolean('Auto logout after each sale order')
