 # -*- coding: utf-8 -*-
import pdb
import requests
import json
from odoo import http
from odoo.http import request
import urllib3
import re
import jxmlease
class PartnerForm(http.Controller):
    @http.route(['/'], type='http', method=['POST'], auth="public", website=True, csrf=False)
    # next controller with url for submitting data from the form#
    def home_page(self, **post):
        # warehouse_list = http.request.env['nova.warehouse'].read_group([], fields=['warehouse_city'], groupby=['warehouse_city'])
        values = { "warehouse_list": http.request.env['nova.warehouse'].sudo().read_group([], fields=['warehouse_city'], groupby=['warehouse_city']) }
        return http.request.render('website.homepage', values)

    @http.route(['/city/change'], type='http', auth="public", website=True, method=['GET', 'POST'], csrf=False)
    def city_change(self, **kw):
        try:
            current_user = http.request.env.user
            location_data = []
            city_name = kw.get('city_name')

            location_ids = http.request.env['nova.warehouse'].sudo().search([('warehouse_city', '=', city_name)])
            for location_id in location_ids:
                location_data.append({'warehouse_id': location_id.id, 'location_name': location_id.name})
            record = {
                'status_is': "noerror",
                'tasks': location_data,
            }

        except:
            record = {'status_is': "error"}

        return json.dumps(record)


    #mention class name
    @http.route(['/nova/form'], type='http', auth="public", website=True)
    #mention a url for redirection.
    #define the type of controller which in this case is ‘http’.
    #mention the authentication to be either public or user.
    def partner_form(self, **post):
    #create method
    #this will load the form webpage
        return request.render("tandemparcel_ext.tmp_nova_form", {})


    @http.route(['/tracking/parcel'], type='http', method=['POST'], auth="public", website=True, csrf=False)
    def tracking_parcel(self, **post):
        xml_body = """<npi:getTrackStatus xmlns:npi="http://npi">""" \
                   + """<npi:trackNo>""" + post.get('tracking_no') + """</npi:trackNo>""" \
                   + """</npi:getTrackStatus>"""
        xml_body = xml_body.encode('utf-8')

        headers = {
            'Content-Type': 'application/xml',
            'Authorization': urllib3.util.make_headers(basic_auth='TANDEM_LOGISTICS:PdEy3289mMaU3d').get('authorization')

        }
        url = "https://api.novaposhta.international:8243/api/PublicAPI/getEWTrackStatus"
        response = requests.post(url=url, data=xml_body, headers=headers)
        status_text = "No Found"
        date_text = "No Found"
        if response.status_code == 200:
            count = 0
            for item in response.text.split("</npi:statusInfoEN>"):
                if "<npi:statusInfoEN>" in item and count == 0:
                    status_text = 'Status: ' + item[item.find("<npi:statusInfoEN>") + len("<npi:statusInfoEN>"):]
                count=count+1
            count = 0
            for item in response.text.split("</npi:statusTime>"):
                if "<npi:statusTime>" in item and count == 0:
                    date_text = 'Date: ' + item[item.find("<npi:statusTime>") + len("<npi:statusTime>"):]
                count = count + 1

        vals = {'status_text': status_text,
                'date_text': date_text.split('T')[0],}
        return request.render("tandemparcel_ext.tmp_nova_form_response", vals)


    @http.route(['/ukraine/form/submit'], type='http', method=['POST'], auth="public", website=True, csrf=False)
    #next controller with url for submitting data from the form#
    def ukraine_form_submit(self, **post):
        partner = request.env['tandem.quotation.request'].sudo().create({
            'sender_name': post.get('sender_name'),
            'sender_phone': post.get('sender_phone'),
            'email': post.get('email'),
            'sending_from': post.get('sending_from'),
            'sending_to': post.get('sending_to_location'),
             'receiver_name': post.get('receiver_name'),
            'receiver_phone': post.get('receiver_phone'),
            'receiver_email': post.get('receiver_email'),
            'freight_description': post.get('freight_description'),
            'product_price': post.get('product_price'),
             'box_len': post.get('box_len'),
            'box_width': post.get('box_width'),
            'box_height': post.get('box_height'),
            'box_weight': post.get('box_weight'),
            'city': 'ukraine',
        })
        vals = {
            'partner': partner,
        }
        #inherited the model to pass the values to the model from the form#
        return request.render("tandemparcel_ext.tmp_nova_form_success", vals)
        #finally send a request to render the thank you page#
    @http.route(['/georgia/form/submit'], type='http', method=['POST'], auth="public", website=True, csrf=False)
    #next controller with url for submitting data from the form#
    def georgia_form_submit(self, **post):
        partner = request.env['tandem.quotation.request'].sudo().create({
            'sender_name': post.get('sender_name'),
            'sender_phone': post.get('sender_phone'),
            'email': post.get('email'),
            'sending_from': post.get('sending_from'),
            'sending_to': post.get('sending_to'),
             'receiver_name': post.get('receiver_name'),
            'receiver_phone': post.get('receiver_phone'),
            'receiver_email': post.get('receiver_email'),
            'freight_description': post.get('freight_description'),
             'box_len': post.get('box_len'),
            'box_width': post.get('box_width'),
            'box_height': post.get('box_height'),
            'box_weight': post.get('box_weight'),
            'city': 'georgia',
        })
        vals = {
            'partner': partner,
        }
        #inherited the model to pass the values to the model from the form#
        return request.render("tandemparcel_ext.tmp_nova_form_success", vals)
        #finally send a request to render the thank you page#