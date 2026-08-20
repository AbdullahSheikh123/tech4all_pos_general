# Copyright (c) 2026, tech4allERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils.password import get_decrypted_password


@frappe.whitelist()
def get_qz_credentials(branch):
    """Serve that branch's QZ Tray certificate + private key to a logged-in
    session so the browser can connect to the local QZ Tray agent and sign
    print requests client-side.

    Scoped per branch (QZ Tray Settings.name == branch) - a leaked key only
    ever gets deliberately used in its own branch's context. Never served to
    a Guest - the private key must stay restricted to users who have already
    authenticated against the site.
    """
    if frappe.session.user == "Guest":
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    if not branch:
        frappe.throw(_("branch is required"))

    if not frappe.db.exists("QZ Tray Settings", branch):
        frappe.throw(_("No QZ Tray Settings configured for branch {0}.").format(branch))

    settings = frappe.get_doc("QZ Tray Settings", branch)
    if not settings.certificate or not settings.private_key:
        frappe.throw(
            _("QZ Tray Settings for branch {0} has no certificate/private key configured.").format(
                branch
            )
        )

    return {
        "certificate": settings.certificate,
        "private_key": get_decrypted_password(
            "QZ Tray Settings", branch, "private_key"
        ),
    }
