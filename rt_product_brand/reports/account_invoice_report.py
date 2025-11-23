from odoo import api, fields, models


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    brand_id = fields.Many2one(comodel_name="product.brand", string="Brand")

    @api.model
    def _select(self):
        select_str = super(AccountInvoiceReport, self)._select()
        select_str += """
            , template.brand_id as brand_id
            """
        return select_str

    @api.model
    def _group_by(self):
        group_by_str = super(AccountInvoiceReport, self)._group_by()
        group_by_str += ", template.brand_id"
        return group_by_str
