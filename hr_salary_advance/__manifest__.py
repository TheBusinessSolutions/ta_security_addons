# -*- coding: utf-8 -*-
{
    'name': 'HR Salary Advance',
    'version': '17.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Manage employee salary advances with running ledger and GL integration',
    'description': """
        HR Salary Advance Module
        ========================
        Features:
        - Multiple advances per employee per month
        - Running DR/CR ledger per employee (like a statement)
        - Finance Manager approval workflow
        - Salary deduction via payslip Other Inputs
        - Cash/Bank manual repayment registration
        - Outstanding balance visible on advance request form
        - Full GL integration with configurable accounts and journals
    """,
    'author': 'HR Consulting',
    'depends': ['hr_payroll_community', 'account', 'mail'],
    'data': [
        'security/hr_salary_advance_security.xml',
        'security/ir.model.access.csv',
        'data/hr_salary_advance_data.xml',
        'views/hr_salary_advance_views.xml',
        'views/hr_salary_advance_ledger_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_salary_advance_menu.xml',
        'wizard/hr_advance_payment_wizard_views.xml',
        'report/hr_salary_advance_report.xml',
        'report/hr_salary_advance_report_template.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
