# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo import api, fields, models


class HrLoan(models.Model):
    _inherit = 'hr.loan'

    # Link to payment records
    payment_ids = fields.One2many(
        'hr.loan.payment',
        'loan_id',
        string='Payments'
    )

    # Computed total paid and remaining balance
    total_paid_amount = fields.Float(
        compute='_compute_payment_amounts',
        store=True,
        string='Total Paid'
    )

    balance_amount = fields.Float(
        compute='_compute_payment_amounts',
        store=True,
        string='Balance Amount'
    )

    @api.depends('loan_amount', 'payment_ids.amount')
    def _compute_payment_amounts(self):
        """ Compute total paid and remaining balance """
        for loan in self:
            total_paid = sum(loan.payment_ids.mapped('amount'))
            loan.total_paid_amount = total_paid
            loan.balance_amount = loan.loan_amount - total_paid
