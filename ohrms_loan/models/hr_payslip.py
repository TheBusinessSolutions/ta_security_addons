from odoo import models, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    def get_inputs(self, contract_ids, date_from, date_to):
        """ Add loan installments to payslip inputs """
        res = super(HrPayslip, self).get_inputs(contract_ids, date_from, date_to)
        
        employee_id = self.env['hr.contract'].browse(
            contract_ids[0].id).employee_id if contract_ids else self.employee_id
        
        loans = self.env['hr.loan'].search([
            ('employee_id', '=', employee_id.id),
            ('state', '=', 'approve')
        ])
        
        for loan in loans:
            for loan_line in loan.loan_lines:
                if (date_from <= loan_line.date <= date_to and not loan_line.paid):
                    for result in res:
                        if result.get('code') == 'LO':
                            result['amount'] = loan_line.amount
                            result['loan_line_id'] = loan_line.id
        
        return res

    def action_payslip_done(self):
        """ Mark loan installments as paid """
        for payslip in self:
            for line in payslip.input_line_ids:
                if line.code == 'LO' and line.amount != 0:
                    # Link loan line if missing
                    if not line.loan_line_id:
                        loan_line = self.env['hr.loan.line'].search([
                            ('employee_id', '=', payslip.employee_id.id),
                            ('date', '>=', payslip.date_from),
                            ('date', '<=', payslip.date_to),
                            ('paid', '=', False)
                        ], limit=1)
                        if loan_line:
                            line.loan_line_id = loan_line.id
                    
                    # Mark as paid
                    if line.loan_line_id:
                        line.loan_line_id.write({
                            'paid': True,
                            'payslip_id': payslip.id
                        })
        
        return super(HrPayslip, self).action_payslip_done()
