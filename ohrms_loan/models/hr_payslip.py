from odoo import models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_done(self):
        res = super().action_payslip_done()

        for slip in self:
            loan_inputs = slip.input_line_ids.filtered(
                lambda l: l.code == 'LO' and l.amount > 0
            )

            for line in loan_inputs:
                loan = self.env['hr.loan'].search([
                    ('employee_id', '=', slip.employee_id.id),
                    ('state', '=', 'approve'),
                    ('balance_amount', '>', 0)
                ], limit=1)

                if loan:
                    self.env['hr.loan.payment'].create({
                        'loan_id': loan.id,
                        'amount': line.amount,
                        'payment_method': 'payroll',
                        'payslip_id': slip.id,
                        'date': slip.date_to,
                    })

        return res
