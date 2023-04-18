# -*- coding: utf-8 -*-
import pdb

from odoo import http
from odoo.addons.odoocms_admission_portal.controllers.onlineregistration import AdmissionApplication


class AdmissionApplication2(AdmissionApplication):
    def process_personal_data(self, kw):
        data = super().process_personal_data(kw)

        data.update({
            'merit_type': kw.get('merit_type'),
            'app_hostal_required': True if kw.get('hostel_required') == 'on' else False
        })
        return data