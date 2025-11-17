# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2024 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com)
#    contact@zbeanztech.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields,api,_
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    
    def action_post(self):
        for rec in self:
            unapproved_products = ", ".join(line.product_id.name for line in rec.invoice_line_ids if line.product_id and line.product_id.state != 'approved')
            if unapproved_products and rec.move_type == 'in_invoice':
                raise UserError("These Products are Not Approved ({}) Please Approve all Products Before Posting the Vendor Bill.".format(unapproved_products))
            elif unapproved_products and rec.move_type == 'out_refund':
                raise UserError("These Products are Not Approved ({}) Please Approve all Products Before Posting the Credit Note.".format(unapproved_products))
            elif unapproved_products and rec.move_type == 'in_refund':
                raise UserError("These Products are Not Approved ({}) Please Approve all Products Before Posting the Refund.".format(unapproved_products))
            elif unapproved_products:
                raise UserError("These Products are Not Approved ({}) Please Approve all Products Before Posting the Invoice.".format(unapproved_products))
        return super(AccountMove, self).action_post()