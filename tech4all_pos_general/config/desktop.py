from frappe import _

def get_data():
	return [
		{
			"module_name": "Tech4all POS General",
			"type": "module",
			"label": _("Tech4all POS General")
		},
		{
			"module_name": "Tech4all General",
			"color": "grey",
			"icon": "octicon octicon-file-directory",
			"type": "module",
			"label": _("Tech4all General")
		}
	]
