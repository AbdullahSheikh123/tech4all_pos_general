# Copyright (c) 2015, tech4allerp Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.auth import CookieManager, LoginManager

@frappe.whitelist()
def login_as_user(user):
	frappe.local.login_manager = LoginManager()
	frappe.local.cookie_manager = CookieManager()
	frappe.local.login_manager.login_as(user)
	