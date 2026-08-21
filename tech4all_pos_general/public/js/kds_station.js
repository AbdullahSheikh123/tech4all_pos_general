// Loads the live printer list from the QZ Tray agent reachable at this
// station's qz_host (or localhost if blank) and lets you pick one into
// printer_name - never typed by hand.
//
// Credentials are looked up per branch (QZ Tray Settings is one row per
// Branch, not a single shared record) - this station's own Branch field
// decides which row gets used.
//
// Depends on qz-tray.js and jsrsasign being loaded app-wide (see
// app_include_js in hooks.py) and on a QZ Tray Settings row existing for
// this station's branch (tech4all_pos_general.api.qz_tray_api.get_qz_credentials).

let qz_credentials_cache = {}; // branch -> Promise<{certificate, private_key}>
let qz_current_branch = null; // which branch the next signed call should use
let qz_connected_host = undefined; // host the active websocket connection is on
let qz_security_configured = false;

function get_qz_credentials(branch) {
	if (!qz_credentials_cache[branch]) {
		qz_credentials_cache[branch] = frappe
			.call("tech4all_pos_general.api.qz_tray_api.get_qz_credentials", { branch })
			.then((r) => r.message);
	}
	return qz_credentials_cache[branch];
}

function connect_qz(host, branch) {
	if (typeof qz === "undefined") {
		return Promise.reject(
			new Error("QZ Tray browser library did not load (qz-tray.js).")
		);
	}
	if (!branch) {
		return Promise.reject(new Error("This station has no Branch set."));
	}

	// Read by the cert/signature promises below at call time, so switching
	// which KDS Station record is open and reconnecting picks up the right
	// branch's credentials without re-registering the promises.
	qz_current_branch = branch;

	if (!qz_security_configured) {
		// Tells qz-tray.js what to DECLARE as the signing algorithm in each
		// outgoing message - separate from, and must match, the alg used in
		// setSignaturePromise below. Without this, qz-tray.js silently
		// declares its own legacy default (SHA1) regardless of what's
		// actually used to compute the signature, causing every request to
		// fail server-side verification ("Bad signature" in QZ Tray's log)
		// no matter which algorithm the signing code below uses.
		qz.security.setSignatureAlgorithm("SHA1");

		qz.security.setCertificatePromise((resolve, reject) => {
			get_qz_credentials(qz_current_branch)
				.then((c) => resolve(c.certificate))
				.catch(reject);
		});

		qz.security.setSignaturePromise((toSign) => (resolve, reject) => {
			get_qz_credentials(qz_current_branch)
				.then((c) => {
					console.log("[QZ SIGN] private_key starts with:", c.private_key?.slice(0, 30));
					console.log("[QZ SIGN] private_key length:", c.private_key?.length);
					console.log("[QZ SIGN] toSign:", toSign);

					const pk = KEYUTIL.getKey(c.private_key);
					console.log("[QZ SIGN] parsed key type/bitLength:", pk?.type, pk?.n?.bitLength?.());

					const sig = new KJUR.crypto.Signature({ alg: "SHA1withRSA" });
					sig.init(pk);
					sig.updateString(toSign);
					const hexSig = sig.sign();
					console.log("[QZ SIGN] signature hex length:", hexSig.length);

					resolve(stob64(hextorstr(hexSig)));
				})
				.catch((e) => {
					console.error("[QZ SIGN] signing threw:", e);
					reject(e);
				});
		});
		qz_security_configured = true;
	}

	if (qz.websocket.isActive() && qz_connected_host === host) {
		return Promise.resolve();
	}

	const reconnect = () => {
		qz_connected_host = host;
		return qz.websocket.connect(host ? { host } : undefined);
	};

	// Already connected, but to a different station's host - drop it first
	// so we don't stay talking to the wrong machine after switching branches.
	if (qz.websocket.isActive()) {
		return qz.websocket.disconnect().then(reconnect);
	}
	return reconnect();
}

frappe.ui.form.on("KDS Station", {
	refresh(frm) {
		frm.add_custom_button(__("Load QZ Printers"), () => {
			if (!frm.doc.branch) {
				frappe.msgprint(
					__("Set Branch first - QZ Tray credentials are looked up per branch.")
				);
				return;
			}

			const host = frm.doc.qz_host;
			frappe.show_alert({
				message: __("Connecting to QZ Tray at {0}...", [host || "localhost"]),
				indicator: "blue",
			});

			connect_qz(host, frm.doc.branch)
				.then(() => qz.printers.find())
				.then((printers) => {
					if (!printers || !printers.length) {
						frappe.msgprint(__("QZ Tray reported no printers on this machine."));
						return;
					}
					frappe.prompt(
						[
							{
								fieldname: "printer_name",
								fieldtype: "Select",
								label: __("Printer"),
								options: printers,
								default: frm.doc.printer_name || printers[0],
								reqd: 1,
							},
						],
						(values) => {
							frm.set_value("printer_name", values.printer_name);
							frm.save();
						},
						__("Select QZ Printer")
					);
				})
				.catch((err) => {
					console.error("QZ Tray error:", err);
					frappe.msgprint({
						title: __("QZ Tray Connection Failed"),
						indicator: "red",
						message: __(
							"Could not reach QZ Tray at {0}. Make sure QZ Tray is running there, this branch's certificate has been Allowed on that machine, QZ Tray Settings has a row for branch {1}, and (if qz_host is set) it's reachable over the LAN.",
							[host || "localhost", frm.doc.branch]
						),
					});
				});
		});
	},
});
