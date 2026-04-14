# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class StockCardReportWizard(models.TransientModel):
    _name = "stock.card.report.wizard"
    _description = "Stock Card Report Wizard"

    date_range_id = fields.Many2one(comodel_name="date.range", string="Period")
    date_from = fields.Date(string="Start Date")
    date_to = fields.Date(string="End Date")
    # FIXED: Optional location (removed required=True)
    location_id = fields.Many2one(
        comodel_name="stock.location", string="Location", required=False
    )
    product_ids = fields.Many2many(
        comodel_name="product.product", string="Products", required=True
    )

    @api.onchange("date_range_id")
    def _onchange_date_range_id(self):
        if self.date_range_id:
            self.date_from = self.date_range_id.date_start
            self.date_to = self.date_range_id.date_end

    def button_export_html(self):
        self.ensure_one()
        action = self.env.ref("stock_card_report.action_report_stock_card_report_html")
        vals = action.sudo().read()[0]
        context = vals.get("context", {})
        if context:
            context = safe_eval(context)
        model = self.env["report.stock.card.report"]
        report = model.create(self._prepare_stock_card_report())
        context["active_id"] = report.id
        context["active_ids"] = report.ids
        vals["context"] = context
        return vals

    def button_export_pdf(self):
        self.ensure_one()
        return self._export("qweb-pdf")

    def button_export_xlsx(self):
        self.ensure_one()
        return self._export("xlsx")

    def _prepare_stock_card_report(self):
        self.ensure_one()
        return {
            "date_from": self.date_from,
            "date_to": self.date_to or fields.Date.context_today(self),
            "product_ids": [(6, 0, self.product_ids.ids)],
            # FIXED: Allow False when location is empty
            "location_id": self.location_id.id if self.location_id else False,
        }

    def _export(self, report_type):
        model = self.env["report.stock.card.report"]
        report = model.create(self._prepare_stock_card_report())
        return report.print_report(report_type)