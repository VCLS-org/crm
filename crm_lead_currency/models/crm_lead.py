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

    """is_same_currency = fields.Boolean(
        string='Same currency',
        compute='_compute_is_same_currency',
    )"""
    
    def _compute_default_currency(self):
        self.default_currency_id = self.env.ref('base.EUR')
        """for rec in self:
            #raise UserError("{}".format(self.env.ref('base.EUR').name))
            rec.default_currency_id = self.env.ref('base.EUR')"""

    @api.onchange('amount_customer_currency','customer_currency_id')
    def get_revenue_in_company_currency(self):
        """
        Compute the planned revenue in the company currency.
        
        If the customer currency is different than the company currency,
        the planned revenue is computed in the company currency.
        
        self.ensure_one()
        #if self.is_same_currency:
            #return self.planned_revenue
        return self.customer_currency_id._convert(
            self.amount_customer_currency or 0,
            self.env.ref('base.EUR'),
            self.env.user.company_id,
            fields.Datetime.now(),
        )
        """
        for rec in self:
            rec.planned_revenue = rec.customer_currency_id._convert(
                rec.amount_customer_currency or 0,
                rec.default_currency_id or self.env.ref('base.EUR'),
                self.env.user.company_id,
                fields.Datetime.now(),
            )

    @api.onchange('partner_id')
    def _onchange_partner(self):
        self.customer_currency_id = self.partner_id.property_product_pricelist.currency_id or self.default_currency_id
        self.get_revenue_in_company_currency()

    """
    @api.onchange('customer_currency_id', 'amount_customer_currency')
    def _onchange_currency(self):
        self.planned_revenue = self.get_revenue_in_company_currency()
    
    @api.multi
    @api.depends('customer_currency_id', 'company_id.currency_id')
    def _compute_is_same_currency(self):
        for lead in self:
            lead.is_same_currency = False"""

    ################
    # CRUD Methods #
    ################
    
    #At creation, we force the planned revenue recompute
    """
    @api.model
    def create(self,vals):
        
        lead=super().create(vals)
        lead._onchange_currency()

    """

    """

    @api.onchange('customer_currency_id', 'amount_customer_currency')
    def _onchange_currency(self):
        self.planned_revenue = self.get_revenue_in_company_currency()

    @api.multi
    def get_revenue_in_company_currency(self):
        #Compute the planned revenue in the company currency.
        #
        #If the customer currency is different than the company currency,
        #the planned revenue is computed in the company currency.
        
        self.ensure_one()
        if self.is_same_currency:
            return self.planned_revenue
        return self.customer_currency_id._convert(
            self.amount_customer_currency or 0,
            self.company_currency,
            self.env.user.company_id,
            fields.Datetime.now(),
        )

    @api.multi
    @api.depends('customer_currency_id', 'company_id.currency_id')
    def _compute_is_same_currency(self):
        for lead in self:
            lead.is_same_currency = (
                lead.customer_currency_id == (
                    lead.company_currency or
                    self.env.user.company_id.currency_id
                )
            )
    """
