# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime as dt
import math
from odoo.exceptions import UserError


class ProjectTarget(models.Model):
	_name = 'bdo.project.invoice'
	_inherit = ['mail.thread']
	_order = 'date_period_start desc'
	
	project_id = fields.Many2one(comodel_name='bdo.project', string='Project', ondelete='restrict', store=True,
	                             required=True)
	project_line_id = fields.Many2one(comodel_name='bdo.project.lines', string='Service', required=True,
	                                  states={'draft': [('readonly', False)]}, readonly=True, store=True)
	date_invoice = fields.Date(string='Date Invoice', store=True)
	name = fields.Char(string='Invoice No', readonly=True)
	name_file = fields.Char(string='File')
	name_file_attachment = fields.Binary(string='Attachment')
	employee_id = fields.Many2one(comodel_name='hr.employee', string='PIC', readonly=True,
	                              default=lambda self: self.env.user.employee_id.id)
	user_id = fields.Many2one(comodel_name='res.users', default=lambda self: self.env.user.id, string='PIC',
	                          readonly=True)
	date_on_scheduled = fields.Date(string='Scheduled on', required=True, states={'draft': [('readonly', False)]},
	                                readonly=True)
	date_period_start = fields.Date(string='From', required=True, states={'draft': [('readonly', False)]},
	                                readonly=True)
	date_period_end = fields.Date(string='To', required=True, states={'draft': [('readonly', False)]}, readonly=True)
	date_period_month_total = fields.Integer(compute='_compute_period_month_total', string='Total Month', readonly=True,
	                                         store=True)
	jan_period = fields.Integer(string='Jan', readonly=True, store=True, default=0)
	feb_period = fields.Integer(string='Feb', readonly=True, store=True, default=0)
	mar_period = fields.Integer(string='Mar', readonly=True, store=True, default=0)
	apr_period = fields.Integer(string='Apr', readonly=True, store=True, default=0)
	may_period = fields.Integer(string='May', readonly=True, store=True, default=0)
	jun_period = fields.Integer(string='Jun', readonly=True, store=True, default=0)
	jul_period = fields.Integer(string='Jul', readonly=True, store=True, default=0)
	aug_period = fields.Integer(string='Aug', readonly=True, store=True, default=0)
	sept_period = fields.Integer(string='Sept', readonly=True, store=True,
	                             default=False)
	oct_period = fields.Integer(string='Oct', readonly=True, store=True, default=0)
	nov_period = fields.Integer(string='Nov', readonly=True, store=True, default=0)
	dec_period = fields.Integer(string='Dec', readonly=True, store=True, default=0)
	year_period = fields.Char(string='Year', size=4, store=True, readonly=True)
	amount = fields.Float(compute='_compute_period_month_total', string='Amount', readonly=True, store=True,
	                      digits=(16, 2))
	amount_equivalent = fields.Float(compute='_compute_period_month_total', string='Amount Equivalent', readonly=True,
	                                 store=True, digits=(16, 2))
	remarks = fields.Text(string='Remarks', states={'draft': [('readonly', False)]}, readonly=True)
	state = fields.Selection(
		[('draft', 'Draft'), ('invoice', 'Invoice'), ('paid', 'Paid')], 'Status', readonly=True, copy=False,
		default='draft')
	
	total_due = fields.Integer(string='Term of payment (days)', readonly=True)
	date_payment_due = fields.Date(string='Expected payment date', readonly=True, store=True)
	number_invoice = fields.Char(string='Invoice No.', readonly=True, store=True)
	partner_id = fields.Char(related='project_line_id.client_name', string='Name of the Company', readonly=True)
	service_id = fields.Char(related='project_line_id.service_id.name', string='Service', readonly=True)
	date_engagement = fields.Date(related='project_line_id.date_engagement', string='Date of engagement', readonly=True)
	currency_id = fields.Char(related='project_line_id.currency_id', string='Currency', readonly=True)
	amount_project_total = fields.Float(related='project_line_id.amount', string='Amount Project', readonly=True)
	amount_project_equivalent = fields.Float(related='project_line_id.amount_equivalent',
	                                         string='Amount Project Equivalent', readonly=True)
	
	_sql_constraints = [
		('unique_jan', 'unique(project_line_id, jan_period', 'January Period is ready to schedule for this project!'),
		('unique_feb', 'unique(project_line_id, feb_period', 'February Period is ready to schedule for this project!'),
		('unique_mar', 'unique(project_line_id, mar_period', 'March Period is ready to schedule for this project!'),
		('unique_apr', 'unique(project_line_id, apr_period', 'April Period is ready to schedule for this project!'),
		('unique_may', 'unique(project_line_id, may_period', 'May Period is ready to schedule for this project!'),
		('unique_jun', 'unique(project_line_id, jun_period', 'June Period is ready to schedule for this project!'),
		('unique_jul', 'unique(project_line_id, jul_period', 'July Period is ready to schedule for this project!'),
		('unique_aug', 'unique(project_line_id, aug_period', 'August Period is ready to schedule for this project!'),
		('unique_sept', 'unique(project_line_id, sept_period',
		 'September Period is ready to schedule for this project!'),
		('unique_oct', 'unique(project_line_id, oct_period', 'October Period is ready to schedule for this project!'),
		('unique_nov', 'unique(project_line_id, nov_period', 'November Period is ready to schedule for this project!'),
		('unique_dec', 'unique(project_line_id, dec_period', 'December Period is ready to schedule for this project!')
	]
	
	@api.multi
	def name_get(self):
		result = []
		for record in self:
			name = record.partner_id + ' > ' + record.service_id
			result.append((record.id, name))
		return result
	
	@api.onchange('project_id')
	def _onchange_project_id(self):
		if self.project_id:
			return {'domain': {'project_line_id': [('project_id', '=', self.project_id.id)]}}
		else:
			return {'domain': {'project_line_id': [('project_id', '=', 0)]}}
	
	@api.multi
	@api.depends('date_period_start', 'date_period_end', 'project_line_id')
	def _compute_period_month_total(self):
		koef = 0.0833333333333333
		for target in self:
			if target.project_line_id and target.date_period_start and target.date_period_end:
				month_total = self._month_between(target.date_period_start, target.date_period_end)
				target.date_period_month_total = month_total
				target.amount = (koef * month_total) * target.amount_project_total
				target.amount_equivalent = (koef * month_total) * target.amount_project_equivalent
	
	def _month_between(self, date_from, date_to):
		month_start = dt.strptime(date_from, "%Y-%m-%d")
		month_start = month_start.month
		month_end = dt.strptime(date_to, "%Y-%m-%d")
		month_end = month_end.month
		return (month_end - month_start) + 1
		
	@api.onchange('date_period_start', 'date_period_end', 'project_line_id')
	def _onchange_date_period(self):
		koef = 0.0833333333333333
		for target in self:
			if target.project_line_id and target.date_period_start and target.date_period_end:
				month_total = self._month_between(target.date_period_start, target.date_period_end)
				target.date_period_month_total = month_total
				target.amount = (koef * month_total) * target.amount_project_total
				target.amount_equivalent = (koef * month_total) * target.amount_project_equivalent

	def action_set_invoice(self, data):
		args = {
			'state': 'invoice',
			'date_invoice': data.get('date_invoice', fields.Date.today()),
			'name': data.get('name', ''),
			'name_file': data.get('name_file', ''),
			'name_file_attachment': data.get('name_file_attachment', ''),
			'total_due': data.get('total_due', 0),
			'date_payment_due': data.get('date_payment_due', fields.Date.today()),
			'number_invoice': data.get('payment_name', '')
		}
		self.write(args)
	
	def _get_jan_period(self,date_from,date_to):
		return 0
	
	@api.model
	def create(self, values):
		month_invoice = dt.strptime(values.get('date_invoice'), "%Y-%m-%d")
		month_invoice = month_invoice.month
		month_start = dt.strptime(values.get('date_period_start'), "%Y-%m-%d")
		month_start = month_start.month
		month_total = self._month_between(values.get('date_period_start'), values.get('date_period_end'))
		
		i = month_start
		jan = 13
		feb = 13
		mar = 13
		apr = 13
		may = 13
		jun = 13
		jul = 13
		aug = 13
		sept = 13
		oct = 13
		nov = 13
		dec = 13
		total = i + month_total
		
		while (i < total):
			if i == 1:
				jan = month_invoice
			elif i == 2:
				feb = month_invoice
			elif i == 3:
				mar = month_invoice
			elif i == 4:
				apr = month_invoice
			elif i == 5:
				may = month_invoice
			elif i == 6:
				jun = month_invoice
			elif i == 7:
				jul = month_invoice
			elif i == 8:
				aug = month_invoice
			elif i == 9:
				sept = month_invoice
			elif i == 10:
				oct = month_invoice
			elif i == 11:
				nov = month_invoice
			elif i == 12:
				dec = month_invoice
				
			i = i + 1
		
		values['jan_period'] = jan if jan <> 13 else 0
		values['feb_period'] = feb if feb <> 13 else 0
		values['mar_period'] = mar if mar <> 13 else 0
		values['apr_period'] = apr if apr <> 13 else 0
		values['may_period'] = may if may <> 13 else 0
		values['jun_period'] = jun if jun <> 13 else 0
		values['jul_period'] = jul if jul <> 13 else 0
		values['aug_period'] = aug if aug <> 13 else 0
		values['sept_period'] = sept if sept <> 13 else 0
		values['oct_period'] = oct if oct <> 13 else 0
		values['nov_period'] = nov if nov <> 13 else 0
		values['dec_period'] = dec if dec <> 13 else 0
		
		total_jan = self.env['bdo.project.invoice'].search_count(
			[('project_line_id', '=', values.get('project_line_id')), ('jan_period', '=', jan)])
		total_feb = self.env['bdo.project.invoice'].search_count(
			[('project_line_id', '=', values.get('project_line_id')), ('feb_period', '=', feb)])
		total_mar = self.env['bdo.project.invoice'].search_count(
			[('project_line_id', '=', values.get('project_line_id')), ('mar_period', '=', mar)])
		total_apr = self.env['bdo.project.invoice'].search_count(
			[('project_line_id', '=', values.get('project_line_id')), ('apr_period', '=', apr)])
		total_may = self.env['bdo.project.invoice'].search_count(
			[('project_line_id', '=', values.get('project_line_id')), ('may_period', '=', may)])
		total_jun = self.env['bdo.project.invoice'].search_count(
			[('project_line_id', '=', values.get('project_line_id')), ('jun_period', '=', jun)])
		total_jul = self.env['bdo.project.invoice'].search_count(
			[('project_line_id', '=', values.get('project_line_id')), ('jul_period', '=', jul)])
		total_aug = self.env['bdo.project.invoice'].search_count(
			[('project_line_id', '=', values.get('project_line_id')), ('aug_period', '=', aug)])
		total_sept = self.env['bdo.project.invoice'].search_count(
			[('project_line_id', '=', values.get('project_line_id')), ('sept_period', '=', sept)])
		total_oct = self.env['bdo.project.invoice'].search_count(
			[('project_line_id', '=', values.get('project_line_id')), ('oct_period', '=', oct)])
		total_nov = self.env['bdo.project.invoice'].search_count(
			[('project_line_id', '=', values.get('project_line_id')), ('nov_period', '=', nov)])
		total_dec = self.env['bdo.project.invoice'].search_count(
			[('project_line_id', '=', values.get('project_line_id')), ('dec_period', '=', dec)])
		
		if total_jan > 0:
			raise UserError(_("January Period has already for this project."))
		elif total_feb > 0:
			raise UserError(_("February Period has already for this project."))
		elif total_mar > 0:
			raise UserError(_("Maret Period has already for this project."))
		elif total_apr > 0:
			raise UserError(_("April Period has already for this project."))
		elif total_may > 0:
			raise UserError(_("May Period has already for this project."))
		elif total_jun > 0:
			raise UserError(_("June Period has already for this project."))
		if total_jul > 0:
			raise UserError(_("July Period has already for this project."))
		elif total_aug > 0:
			raise UserError(_("August Period has already for this project."))
		elif total_sept > 0:
			raise UserError(_("September Period has already for this project."))
		elif total_oct > 0:
			raise UserError(_("October Period has already for this project."))
		elif total_nov > 0:
			raise UserError(_("November Period has already for this project."))
		elif total_dec > 0:
			raise UserError(_("December Period has already for this project."))
		else:
			return super(ProjectTarget, self).create(values)