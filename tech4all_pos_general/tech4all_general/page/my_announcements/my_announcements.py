# Copyright (c) 2015, tech4allERP Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.utils import get_datetime

@frappe.whitelist()
def fetch_announcements(filters=None):
	announcements = frappe.get_all("Announcements", filters={"published": 1}, fields=["*"])
	return announcements