# -*- coding: utf-8 -*-
import pdb

from odoo import http
from odoo.http import request


class LoopedEmployee(http.Controller):

    # @http.route('/get/token',method=['POST'],type='json', auth='none')
    # def user_authentication(self, **kw):
    #     # req = request.session.authenticate('looped_task',username,password)
    #     pdb.set_trace()
    #     return request.env['ir.http'].session_info().session_id



    @http.route('/getemployee',type='json', auth='none')
    def get_employee(self, **kw):
        username = request.httprequest.headers.get('username')
        password = request.httprequest.headers.get('password')
        employee = []
        if request.session.authenticate('looped_task',username,password):
            employee_recs  =  request.env['hr.employee'].sudo().search([])
            for rec in employee_recs:
                vals =  {
                    'ID':rec.id,
                    'Name': rec.name,
                    'Full Time Ability': rec.full_time_ability,
                }
                employee.append(vals)
            data={'status':200,'response':employee,'message': 'Employee Record'}
        else:
            data = {'status': 200, 'response': employee, 'message': 'Authentication Fail'}
        return data


    @http.route('/setemployee',type='json', auth='none')
    def set_employee(self, **kw):
        username = request.httprequest.headers.get('username')
        password = request.httprequest.headers.get('password')
        employee = []
        if request.session.authenticate('looped_task',username,password) and kw.get('id'):
            employee_rec  =  request.env['hr.employee'].sudo().search([('id','=',kw.get('id'))])
            if employee_rec:
                employee_rec.write({
                    'full_time_ability':kw.get('full_time') if kw.get('full_time') else False
                })
            data={'status':200,'response':{
                'Name': employee_rec.name,
                'ID':employee_rec.id,
                'Full Time Ability':employee_rec.full_time_ability,
            },'message': 'Employee Record updates sucess fully'}
        else:
            data = {'status': 200, 'response': employee, 'message': 'Employee Id Not Set'}
        return data


