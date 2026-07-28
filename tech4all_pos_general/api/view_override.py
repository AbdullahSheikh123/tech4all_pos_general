import frappe
import json
import pytz
from datetime import datetime, timedelta
from frappe.desk.reportview import get

@frappe.whitelist()
def custom_get_list(doctype, **kwargs):
    view = kwargs.get("view")

    kwargs.pop("cmd", None)  
    kwargs.pop("view", None)  # Ensure 'view' does not interfere

    # Convert fields from JSON string to list (if necessary)
    fields = kwargs.get("fields")
    if isinstance(fields, str):
        try:
            kwargs["fields"] = json.loads(fields)
        except json.JSONDecodeError:
            kwargs["fields"] = ["name"]  # Default fallback
    
    # Convert filters from JSON string to list (if necessary)
    filters = kwargs.get("filters", [])
    if isinstance(filters, str):
        try:
            filters = eval(filters)  # Convert string to list
        except Exception:
            filters = []
    elif not isinstance(filters, list):
        filters = []

    kwargs["filters"] = filters

    pk_timezone = pytz.timezone("Asia/Karachi")
    now = datetime.now(pk_timezone)

    user = frappe.session.user
    user_permission_setting = frappe.get_single("User permission Setting")

    allowed_users = [u.user for u in user_permission_setting.users]
    allowed_doctypes = {d.doctypelink: d for d in user_permission_setting.doctypes}

    if user in allowed_users and doctype in allowed_doctypes:
        doctype_settings = allowed_doctypes[doctype]
        filter_type = doctype_settings.filter_type
        filter_apply_on = doctype_settings.filter_apply_on
        time_span = doctype_settings.time_span

        if filter_type == "Hide All Documents":
            return []  # Return an empty list to hide all documents for this doctype

        if filter_type == "Time" and filter_apply_on:
            start_date, end_date = None, None

            if time_span == "Today":
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            elif time_span == "Yesterday":
                start_date = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = (now - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)
            elif time_span == "Last 3 Days":
                start_date = (now - timedelta(days=3)).replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            elif time_span == "Last 7 days":
                start_date = (now - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            elif time_span == "Last 30 days":
                start_date = (now - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            elif time_span == "Last 1 Hour":
                start_date = now - timedelta(hours=1)
                end_date = now

            if start_date and end_date:
                date_filter = [
                    filter_apply_on, "between",
                    [start_date.strftime("%Y-%m-%d %H:%M:%S"), end_date.strftime("%Y-%m-%d %H:%M:%S")]
                ]
                filters.append(date_filter)

        elif filter_type == "Session":
            latest_shift = frappe.get_list(
                "POS Opening Shift",
                filters=[["user", "=", user], ["status", "=", "Open"]],
                fields=["name"],
                order_by="creation desc",
                limit_page_length=1
            )

            if latest_shift:
                session_filter = ["posa_pos_opening_shift", "=", latest_shift[0]["name"]]
            else:
                session_filter = ["posa_pos_opening_shift", "=", ""]  # Apply empty value filter

            filters.append(session_filter)

        kwargs["filters"] = filters
    if view == "Report":
        
        # Prepare the report filters
        report_filters = kwargs.get("filters", [])
        
        return get(doctype=doctype, filters=report_filters, fields=kwargs.get("fields"))
    return frappe.get_list(doctype, **kwargs)