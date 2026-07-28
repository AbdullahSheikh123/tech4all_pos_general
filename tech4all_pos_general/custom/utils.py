import frappe
from frappe import _



def validate_user_ip():
    user = frappe.session.user
    print(f"[IP VALIDATION] Logged-in user: {user}")
    frappe.logger().info(f"[IP VALIDATION] Logged-in user: {user}")

    if user in (None, "Guest", "Administrator"):
        print("[IP VALIDATION] Skipping check for system user.")
        frappe.logger().info("[IP VALIDATION] Skipping check for system user.")
        return

    user_doc = frappe.get_doc("User", user)
    allowed_ip = user_doc.get("custom_allowed_ip")

    print(f"[IP VALIDATION] Allowed IP for user {user}: {allowed_ip}")
    frappe.logger().info(f"[IP VALIDATION] Allowed IP for user {user}: {allowed_ip}")

    if not allowed_ip:
        print("[IP VALIDATION] No IP restriction set. Skipping.")
        frappe.logger().info("[IP VALIDATION] No IP restriction set. Skipping.")
        return

    client_ip = get_client_ip()
    print(f"[IP VALIDATION] Client IP received: {client_ip}")
    frappe.logger().info(f"[IP VALIDATION] Client IP received: {client_ip}")

    if client_ip != allowed_ip:
        print(f"[IP VALIDATION] BLOCKED: User {user} tried logging in from {client_ip}")
        frappe.logger().error(f"[IP VALIDATION] Blocked login for {user} from IP: {client_ip}")
        frappe.throw("You are not allowed to log in from this IP address.")


def get_client_ip():
    headers = frappe.local.request.headers
    print(f"[IP DETECTION] Request Headers: {dict(headers)}")
    frappe.logger().info(f"[IP DETECTION] Request Headers: {dict(headers)}")

    proxy_headers = [
        'X-Forwarded-For',
        'HTTP_X_FORWARDED_FOR',
        'X-Real-IP',
        'HTTP_CLIENT_IP'
    ]

    for header in proxy_headers:
        ip = headers.get(header)
        if ip:
            if ',' in ip:
                client_ip = ip.split(',')[0].strip()
                print(f"[IP DETECTION] Found IP '{client_ip}' from header '{header}'")
                frappe.logger().info(f"[IP DETECTION] Found IP '{client_ip}' from header '{header}'")
                return client_ip
            print(f"[IP DETECTION] Found IP '{ip.strip()}' from header '{header}'")
            frappe.logger().info(f"[IP DETECTION] Found IP '{ip.strip()}' from header '{header}'")
            return ip.strip()

    fallback_ip = frappe.local.request_ip
    print(f"[IP DETECTION] Using fallback IP: {fallback_ip}")
    frappe.logger().info(f"[IP DETECTION] Using fallback IP: {fallback_ip}")
    return fallback_ip
