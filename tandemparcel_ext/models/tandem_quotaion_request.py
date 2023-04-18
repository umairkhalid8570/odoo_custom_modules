import pdb

from odoo import api, fields, models
import requests
import json
import re
import base64
import urllib3
from datetime import datetime, timedelta, time
from odoo.exceptions import ValidationError
import codecs
import xml.etree.ElementTree as ET

STATUS = [
    ('draft', 'Draft'),
    ('processed', 'Processed'),
    ('cancel', 'Cancel'),
]


class TandemQuotationRequest(models.Model):
    _name = 'tandem.quotation.request'
    _description = 'Tandem Quotation Request'

    name = fields.Char(string="Name")
    sender_name = fields.Char(sring="Sender name")
    sender_phone = fields.Char(sring="Sender Phone")
    email = fields.Char(sring="Sender Email")
    sending_from = fields.Char(sring="Sending From")
    sending_to = fields.Many2one('nova.warehouse', sring="Sending To")
    receiver_name = fields.Char(sring="Receiver Name")
    receiver_phone = fields.Char(sring="Receiver Phone")
    receiver_email = fields.Char(sring="Receiver Email")
    freight_description = fields.Char(sring="Freight Description")
    product_price = fields.Integer(sring="Product Price")
    box_len = fields.Integer(sring="Box Length")
    box_width = fields.Integer(sring="Box Width")
    box_height = fields.Integer(sring="Box Height")
    box_weight = fields.Integer(sring="Box Weight")
    state = fields.Selection(STATUS, string='State', default='draft')
    city = fields.Char(string='City')

    parcel_transfer_expense = fields.Float(sring="Parcel Transfer Expense")
    parcel_rate = fields.Float(sring="Parcel Rate")
    profit = fields.Float(sring="Profit", compute="calculate_profit", store=True)


    # server response

    ew_id = fields.Char('Server EW ID')
    state_id = fields.Char('Server State ID')
    filedata = fields.Binary('File')


    def local_delivery(self):
        for rec in self:
            rec.product_price = 10

    @api.depends('parcel_transfer_expense', 'parcel_rate')
    def calculate_profit(self):
        for rec in self:
            rec.profit = rec.parcel_rate - rec.parcel_transfer_expense

    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('tandem.quotation.request')
        result = super().create(vals)
        return result

    def send_to_nova(self):
        xml_body = """<npi:createRegistryShipment xmlns:npi="http://npi">""" \
               + """<npi:registryID>""" + str(datetime.now()) + """</npi:registryID>""" \
               + """<npi:registryDate>""" + str(datetime.now().date()) + """</npi:registryDate>""" \
               + """<npi:orders>""" \
               + """<npi:order>""" \
               + """<npi:trackNo>""" + self.name + """</npi:trackNo>""" \
               + """<npi:serviceID>9</npi:serviceID><npi:additionalServices/>""" \
               + """<npi:shipperInfo>""" \
               + """<npi:accountNumber>1000000240</npi:accountNumber>""" \
               + """<npi:clientType>2</npi:clientType>""" \
               + """<npi:contactPerson>""" \
               + """<npi:surname>""" + self.sender_name + """</npi:surname>""" \
               + """<npi:name>""" + self.sender_name + """</npi:name>""" \
               + """<npi:fullName>""" + self.sender_name + """</npi:fullName>""" \
               + """</npi:contactPerson>""" \
               + """<npi:contacts>""" \
               + """<npi:phones>""" \
               + """<npi:phone>""" \
               + """<npi:phoneNumber>""" + self.sender_phone + """</npi:phoneNumber>""" \
               + """<npi:phoneType>1</npi:phoneType>""" \
               + """<npi:smsNotificate>1</npi:smsNotificate>""" \
               + """</npi:phone>""" \
               + """</npi:phones>""" \
               + """</npi:contacts>""" \
               + """<npi:addresses>""" \
               + """<npi:address>""" \
               + """<npi:addressKind>1</npi:addressKind>""" \
               + """<npi:addressType>1</npi:addressType>""" \
               + """<npi:country>US</npi:country>""" \
               + """<npi:city>Glenview</npi:city>""" \
               + """<npi:zipCode>60025</npi:zipCode>""" \
               + """<npi:address>""" + self.sending_from + """</npi:address>""" \
               + """</npi:address>""" \
               + """</npi:addresses>""" \
               + """</npi:shipperInfo>""" \
               + """<npi:consigneeInfo>""" \
               + """<npi:clientType>1</npi:clientType>""" \
               + """<npi:contactPerson>""" \
               + """<npi:surname>""" + self.receiver_name + """</npi:surname>""" \
               + """<npi:name>""" + self.receiver_name + """</npi:name><npi:fullName>""" + self.receiver_name + """</npi:fullName>""" \
               + """</npi:contactPerson>""" \
               + """<npi:contacts>""" \
               + """<npi:phones>""" \
               + """<npi:phone>""" \
               + """<npi:phoneNumber>""" + self.receiver_phone + """</npi:phoneNumber>""" \
               + """<npi:phoneType>1</npi:phoneType>""" \
               + """<npi:smsNotificate>1</npi:smsNotificate>""" \
               + """</npi:phone>""" \
               + """</npi:phones>""" \
               + """</npi:contacts>""" \
               + """<npi:addresses>""" \
               + """<npi:address>""" \
               + """<npi:addressKind>1</npi:addressKind>""" \
               + """<npi:addressType>1</npi:addressType>""" \
               + """<npi:country>UA</npi:country>""" \
               + """<npi:city>""" + str(self.sending_to.warehouse_city) + """</npi:city>""" \
               + """<npi:zipCode>""" + str(self.sending_to.warehouse_zipcode) + """</npi:zipCode>""" \
               + """<npi:address>""" + str(self.sending_to.name) + """</npi:address>""" \
               + """</npi:address>""" \
               + """</npi:addresses>""" \
               + """</npi:consigneeInfo>""" \
               + """<npi:cargo>""" \
               + """<npi:invoiceNo></npi:invoiceNo>""" \
               + """<npi:cargoType>1</npi:cargoType>""" \
               + """<npi:countOfParcels>1</npi:countOfParcels>""" \
               + """<npi:generalDescription>""" + str(self.freight_description) + """</npi:generalDescription>""" \
               + """<npi:parcels>""" \
               + """<npi:parcel>""" \
               + """<npi:length>""" + str(self.box_len) + """</npi:length>""" \
               + """<npi:width>""" + str(self.box_width) + """</npi:width>""" \
               + """<npi:height>""" + str(self.box_height) + """</npi:height>""" \
               + """<npi:actualWeight>""" + str(self.box_weight) + """</npi:actualWeight>""" \
               + """</npi:parcel></npi:parcels>""" \
               + """<npi:goods>""" \
               + """<npi:good>""" \
               + """<npi:description>""" + self.freight_description + """</npi:description>""" \
               + """<npi:quantity>1</npi:quantity>""" \
               + """<npi:unitsOfMeasurement>2</npi:unitsOfMeasurement>""" \
               + """<npi:costPerUnit>""" + str(self.product_price) + """</npi:costPerUnit>""" \
               + """<npi:subtotalCostPerGood>"""+str(self.product_price) +"""</npi:subtotalCostPerGood>""" \
               + """</npi:good>""" \
               + """</npi:goods>""" \
               + """</npi:cargo>""" \
               + """<npi:currency>USD</npi:currency>""" \
               + """<npi:incoterms>EXW</npi:incoterms>""" \
               + """<npi:exportReason>""" \
               + """<npi:reasonID>6</npi:reasonID>""" \
               + """<npi:reason>no commercial</npi:reason>""" \
               + """</npi:exportReason>""" \
               + """<npi:payer>3</npi:payer>""" \
               + """<npi:paymentMethod>2</npi:paymentMethod>""" \
               + """<npi:schemeID>11</npi:schemeID>""" \
               + """<npi:thirdPartyPerson>""" \
               + """<npi:accountNumber>1234567890</npi:accountNumber>""" \
               + """<npi:clientType>2</npi:clientType>""" \
               + """</npi:thirdPartyPerson>""" \
               + """<npi:additionalInfo/>""" \
               + """</npi:order>""" \
               + """</npi:orders>""" \
               + """<npi:totalCost>"""+str(self.product_price) +"""</npi:totalCost>""" \
               + """<npi:totalWeight>0.181</npi:totalWeight>""" \
               + """</npi:createRegistryShipment>"""
        xml_body = xml_body.encode('utf-8')
        # pdb.set_trace()
        headers = {
            'Content-Type': 'application/xml',
            'Authorization': self.get_basic_auth_token()

        }
        url = "https://api.novaposhta.international:8243/api/PublicAPI/createRegistryShipment"
        response = requests.post(url=url, data=xml_body, headers=headers)
        if response.status_code == 200:
            new_id = re.search(r'\<npi:ewID\>(.+)\<.+', response.text, re.MULTILINE)
            new_id = new_id.groups()[0]
            state_id = re.search(r'\<npi:stateID\>(.+)\<.+', response.text, re.MULTILINE)
            state_id = state_id.groups()[0]
            self.ew_id = new_id
            self.state_id = state_id
            self.state = 'processed'
            self.print_tag()

            # raise ValidationError("Request send to Nova Server successfully")

    def print_tag(self):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.get_basic_auth_token()

        }
        url = "https://api.novaposhta.international:8243/npi/IEW/print"
        data = {
            'number': self.ew_id,
            'label_format': 'LF_40',
            'mime_type': 'PDF',
        }
        response = requests.post(url=url, data=json.dumps(data), headers=headers)


        if response.status_code == 200:
            response = response.json()
            self.filedata = response['result']['document']

            # b64 = response['result']['document']
            # bytes = base64.b64decode(b64)
            # f = open('file.pdf', 'wb')
            # f.write(bytes)
            # f.close()
            # pdb.set_trace()
            # f.close()

    def cancel_record(self):
        self.state = 'cancel'



    def get_basic_auth_token(self):
        """Gets HTTP basic authentication header (string).

        :return: The token for basic HTTP authentication.
        """
        return urllib3.util.make_headers(
            basic_auth='TANDEM_LOGISTICS:PdEy3289mMaU3d'
        ).get('authorization')





class NovaWarehouses(models.Model):
    _name = 'nova.warehouse'
    _description = 'Nova Warehuse List'

    name = fields.Char(sring="Name")
    warehouse_name = fields.Char(sring="Warehouse Name")
    warehouse_city = fields.Char(sring="Warehouse City")
    nova_reference = fields.Char(sring="Warehouse Name")
    warehouse_zipcode = fields.Char(sring="Warehouse ZipCode")

    def update_list(self):
        url = "https://api.novaposhta.international:8243/npi/Dictionary/getWarehouses"
        headers = {
            'Content-Type': 'application/json',
            'Login': 'TANDEM_LOGISTICS',
            'Password': 'TANDEM_LOGISTICS'
        }
        data = {

            "country": "UA",
            "ext": "0",
            "language": "EN"
        }
        response = requests.post(url=url, data=json.dumps(data), headers=headers)
        if response.status_code == 200:

            for rec in response.json()['warehouse_list']:
                if not self.env['nova.warehouse'].search([('warehouse_name', '=', rec['name'])]):
                    name = ""
                    if rec['address'][0].get('street'):
                        name = name + rec['address'][0]['street'] + ", "
                    if rec['address'][0].get('building'):
                        name = name + rec['address'][0]['building'] + ", "
                    if rec['address'][0].get('state_province'):
                        name = name + rec['address'][0]['state_province'] + ", "
                    if rec['address'][0].get('zipcode'):
                        name = name + rec['address'][0]['zipcode'] + ", "
                    if rec.get('name'):
                        name = name + rec['name']

                    self.env['nova.warehouse'].create({
                        'warehouse_name': rec['name'],
                        'warehouse_city': rec['address'][0]['city'] if rec['address'][0].get('city') else "",
                        'name': name,
                        'nova_reference': rec['reference'],
                        'warehouse_zipcode': rec['address'][0]['zipcode'] if rec['address'][0].get('zipcode') else "",
                    })
