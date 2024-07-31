# Copyright (c) 2023, admin and contributors
# For license information, please see license.txt

import frappe
import requests
import json
from frappe.model.document import Document

class JMIQRViewLog(Document):
	def before_insert(self):
		self.get_ip_and_location()

	def get_ip_and_location(self):
		# make API call to get geolocation data
		response = requests.get('http://ip-api.com/json')
		# parse JSON response
		location_data = json.loads(response.content)
		self.user_ip_address = location_data.get('query')
		self.latitude = location_data.get('lat')
		self.longitude = location_data.get('lon')
		self.user_location = location_data.get('city')
