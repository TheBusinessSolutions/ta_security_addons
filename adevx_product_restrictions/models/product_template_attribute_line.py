from odoo import api, models
from odoo.exceptions import UserError


class ProductTemplateAttributeLine(models.Model):
    _inherit = 'product.template.attribute.line'

    def _check_values_in_purchase(self, values, tmpl):
        query = """
                SELECT  pav.name->>'en_US'
                FROM purchase_order_line pol
                LEFT JOIN product_product pp ON(pol.product_id = pp.id)
                LEFT JOIN product_template pt ON(pp.product_tmpl_id = pt.id)
                LEFT JOIN product_variant_combination pvc ON(pp.id = pvc.product_product_id)
                LEFT JOIN product_template_attribute_value ptav ON(pvc.product_template_attribute_value_id = ptav.id)
                LEFT JOIN product_attribute_value pav ON(ptav.product_attribute_value_id = pav.id)
                WHERE (pav.id IN %s)
                AND (pt.id = %s)
                GROUP BY pav.name
        """
        self.env.cr.execute(query, (tuple(values, ), tmpl.id))
        result = self.env.cr.fetchall()
        if result:
            del_variant = []
            for row in result:
                del_variant.append(row[0])
            return del_variant
        return

    @api.model
    def create(self, values):
        pro_tmpl = self.env['product.template'].browse(values.get('product_tmpl_id'))
        for attr in pro_tmpl.attribute_line_ids:
            if attr.attribute_id.id == values.get('attribute_id'):
                raise UserError('Attribute Line ' + attr.attribute_id.name + ' Already Exist')
        return super(ProductTemplateAttributeLine, self).create(values)

    def write(self, values):
        if values.get('value_ids'):
            old_values = self.value_ids.ids
            updated_values = values.get('value_ids')[0]
            new_values = list(set(old_values).intersection(updated_values))
            if new_values:
                del_variant = self._check_values_in_purchase(new_values, self.product_tmpl_id)
                if del_variant:
                    raise UserError(
                        f"You Try To Remove {str(del_variant)} Values From This Product: [{self.product_tmpl_id.name}]"
                        f" That Have Po \n  So You Must Choose {str(del_variant)}  Again Before Save")

        return super(ProductTemplateAttributeLine, self).write(values)

    def unlink(self):
        del_variant = self._check_values_in_purchase(self.value_ids.ids, self.product_tmpl_id)
        if del_variant:
            raise UserError(
                f"You Try To Remove [ {self.attribute_id.name} ] Attribute Record \n"
                f" Which Have {str(del_variant)} Values That Have Po For This Product: [{self.product_tmpl_id.name}]\n"
                f" So Please Discard These Changes !!")

        return super(ProductTemplateAttributeLine, self).unlink()
