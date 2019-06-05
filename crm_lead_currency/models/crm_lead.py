# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    default_currency_id = fields.Many2one(
        string='Default Currency',
        comodel_name='res.currency',
        compute='_compute_default_currency', 
        readonly = True,
        store = True,
    )
    
    customer_currency_id = fields.Many2one(
        string='Customer Currency',
        comodel_name='res.currency',
    )

    amount_customer_currency = fields.Monetary(
        string='Customer amount',
        currency_field='customer_currency_id',
    )

    planned_revenue = fields.Monetary(
        currency_field='default_currency_id',
    )


    def get_revenue_in_company_currency(self):
        """
        Compute the planned revenue in the company currency.
        
        If the customer currency is different than the company currency,
        the planned revenue is computed in the company currency.
        """
        self.ensure_one()
        return self.customer_currency_id._convert(
            self.amount_customer_currency or 0,
            self.default_currency_id or self.env.ref('base.EUR'),
            self.env.user.company_id,
            fields.Datetime.now(),
        )

    @api.depends('amount_customer_currency')
    def _compute_default_currency(self):
        for rec in self:
            rec.default_currency_id = self.env.ref('base.EUR')

    @api.onchange('amount_customer_currency','customer_currency_id')
    def _onchange_currency(self):
        self.planned_revenue = self.get_revenue_in_company_currency()

    @api.onchange('partner_id')
    def _onchange_partner(self):
        self.customer_currency_id = self.partner_id.property_product_pricelist.currency_id or self.default_currency_id
        self.planned_revenue = self.get_revenue_in_company_currency()


    ###############
    # ORM Methods #
    ###############
    
    @api.multi
    def write(self, vals):
        lead = super().write(vals)
        # IF planned revenue not converted
        if 'amount_customer_currency' in vals:
            print("GO STAN GO")
            if vals['amount_customer_currency'] > 0 and vals['planned_revenue'] == 0:
                print("GO ROGER GO")
                lead.planned_revenue = lead.get_revenue_in_company_currency()

        return lead
