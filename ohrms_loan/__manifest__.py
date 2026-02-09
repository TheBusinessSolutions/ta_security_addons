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
{
    'name': 'Employee Loan Management with Accounting',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Manage employee loans with full accounting integration',
    'description': """
        Employee Loan Management
        ========================
        * Create and approve employee loans
        * Automatic installment calculation
        * Payslip integration for deductions
        * Direct payment registration
        * Full accounting integration
        * Loan receivable tracking in Chart of Accounts
        * Support for multiple payment methods
    """,
    'author': 'Your Company',
    'depends': ['hr', 'account', 'hr_payroll_community'],

    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/hr_loan_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}