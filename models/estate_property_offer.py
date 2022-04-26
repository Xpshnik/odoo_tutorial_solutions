from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import UserError


class Offer(models.Model):
    _name = 'estate.property.offer'
    _description = "Don't shout at me, console"
    _order = 'price desc'

    price = fields.Float()
    state = fields.Selection(copy=False, string="Status", selection=[
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
    ])
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)
    validity = fields.Integer(default=7, string='Validity (days)')
    deadline_date = fields.Date(string='Deadline', compute='_compute_deadline_date', inverse='_inverse_deadline_date')

    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)', 'The offer price must be positive.'),
    ]

    @api.depends('validity', 'create_date')
    def _compute_deadline_date(self):
        for record in self:
            if record.create_date:
                record.deadline_date = fields.Date.to_date(record.create_date) + relativedelta(days=3)
            else:
                record.deadline_date = fields.Date.add(fields.Date.today(), days=record.validity)

    def _inverse_deadline_date(self):
        for record in self:
            record.validity = (record.deadline_date - fields.Date.to_date(record.create_date)).days

    def action_accept_offer(self):
        for record in self:
            #should I go via record.mapped('property_id') somehow?
            if record.property_id.buyer_id:
                raise UserError('The buyer has already been set.')
            record.state = 'accepted'
            #rewrite with update
            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.partner_id.id #[(4, record.partner_id.id, 0)]
            record.property_id.state = 'offer_accepted'
        return True

    def action_refuse_offer(self):
        for record in self:
            record.state = 'refused'
        return True
