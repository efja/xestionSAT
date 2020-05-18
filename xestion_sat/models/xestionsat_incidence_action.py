# 1: imports of python lib
from datetime import datetime
from lxml import etree

# 2: import of known third party lib

# 3:  imports of odoo
from odoo import models, fields, api, _

# 4:  imports from odoo modules
from .xestionsat_common import NEW_ACTION
from .xestionsat_common import ORDER_MODEL, INVOICE_MODEL

# 5: local imports

# 6: Import of unknown third party lib


class IncidenceAction(models.Model):
    """Model that describes the actions taken in incidences.
    """
    ###########################################################################
    # Private attributes
    ###########################################################################
    _name = 'xestionsat.incidence.action'
    _description = _('Action taken in an incidence')
    _inherits = {'product.template': 'template_id'}
    _order = 'date_start desc'

    ###########################################################################
    # Default methods
    ###########################################################################

    ###########################################################################
    # Fields declaration
    ###########################################################################
    # -------------------------------------------------------------------------
    # Relational Fields
    # -------------------------------------------------------------------------
    executed_by = fields.Many2one(
        'res.users',
        string='Executed_by',
        ondelete='restrict',
        default=lambda self: self.env.user,
        required=True,
    )

    incidence_id = fields.Many2one(
        'xestionsat.incidence',
        ondelete='restrict',
    )

    template_id = fields.Many2one(
        'product.template',
        string='Action',
        required=True,
        ondelete='restrict',
    )

    tax_ids = fields.Many2many(
        'account.tax',
        string='Taxes',
    )
    # -------------------------------------------------------------------------
    # Other Fields
    # -------------------------------------------------------------------------
    date_start = fields.Date(
        string='Date start',
        default=lambda *a: datetime.now().strftime('%Y-%m-%d'),
        required=True,
    )
    date_end = fields.Date(
        string='Date ends',
    )
    observation = fields.Char(
        string='Observations',
    )
    quantity = fields.Float(
        string='Quantity',
        default=1.0,
    )
    discount = fields.Float(
        string='Discount (%)',
        inverse='_check_discount',
        default=0.0,
    )
    subtotal_discount = fields.Float(
        string='Subtotal discount',
        readonly=True,
        compute='_compute_subtotal',
    )
    subtotal = fields.Float(
        string='Subtotal',
        readonly=True,
        compute='_compute_subtotal',
    )

    ###########################################################################
    # compute and search fields, in the same order that fields declaration
    ###########################################################################
    @api.depends('discount')
    def _check_discount(self):
        """Check that the discount is between 1 and 100.
        """
        for line in self:
            if line.discount < 0:
                line.update({
                    'discount': 0,
                })
            elif line.discount > 100:
                line.update({
                    'discount': 100,
                })

    @api.depends('quantity', 'discount', 'list_price')
    def _compute_subtotal(self):
        """Recalculate the price of the line.
        """
        for line in self:
            unit_discount = line.list_price * line.discount / 100
            unit_price = line.list_price - unit_discount

            taxes = 0.0

            for tax in line.tax_ids:
                if tax.amount_type == 'fixed':
                    taxes += tax.amount
                elif tax.amount_type == 'percent':
                    taxes += unit_price * tax.amount / 100

            # Price without applying the discount
            subtotal_price = line.quantity * line.list_price + taxes

            # Price after applying the discount
            line.subtotal = line.quantity * unit_price + taxes

            # Discounted price
            line.subtotal_discount = subtotal_price - line.subtotal

    @api.multi
    def prepare_action_line(self, res_model):
        """Prepare the dict of values to create the new sales order or invoice
        line.

        :param res_model: Model for which it is generated.
        """
        self.ensure_one()

        action_line = {
            'name': self.name,
            'product_id': self.id,
            'discount': self.discount,
            'product_uom': self.uom_id.id,
            'price_unit': self.list_price, }

        if res_model == ORDER_MODEL:
            action_line['product_uom_qty'] = self.quantity
            action_line['tax_id'] = [(6, 0, self.tax_ids.ids)]

        if res_model == INVOICE_MODEL:
            account = self.incidence_id.customer_id.property_account_payable_id
            action_line['quantity'] = self.quantity
            action_line['account_id'] = account.id
            action_line['invoice_line_tax_ids'] = [(6, 0, self.tax_ids.ids)]

        return (0, 0, action_line)

    ###########################################################################
    # Constraints and onchanges
    ###########################################################################
    @api.constrains('executed_by')
    def _check_executed_by(self):
        """Verify that the creation of the action is not assigned to a
        different system user than the one running the application.
        """
        error_message = 'One user cannot create Actions in the name of another'

        for line in self:
            if line.executed_by \
                    and line.executed_by != self.env.user:
                raise models.ValidationError(_(error_message))

    @api.onchange('tax_ids')
    def _check_tax_ids(self):
        """Execute the _compute_subtotal () method to calculate the price of the
        line.
        """
        self._compute_subtotal()

    ###########################################################################
    # CRUD methods
    ###########################################################################
    @api.multi
    def create_new_action(
        self, name=NEW_ACTION, context=None, flags=None
    ):
        """Method to add a new action for the current incidence.
        """
        if type(name) != str:
            name = NEW_ACTION

        return {
            'name': _(name),
            'type': 'ir.actions.act_window',
            'res_model': 'xestionsat.incidence.action',
            'view_type': 'form',
            'view_mode': 'form',
            'context': context,
            'target': 'new',
            'flags': flags,
        }

    ###########################################################################
    # Action methods
    ###########################################################################

    ###########################################################################
    # Business methods
    ###########################################################################
    @api.model
    def fields_view_get(self, view_id=None, view_type=None, **kwargs):
        """Modify the resulting view according to the past context.
        """
        context = self.env.context

        result = super(IncidenceAction, self).fields_view_get(
            view_id=view_id, view_type=view_type, **kwargs
        )

        if view_type == 'form':
            lock = False

            if 'lock_view' in context:
                lock = context['lock_view']

            if lock:
                doc = etree.XML(result['arch'])

                # btn_close
                for node in doc.xpath("//button[@name='btn_close']"):
                    node.set('modifiers', '{}')

                result['arch'] = etree.tostring(doc)
        return result
