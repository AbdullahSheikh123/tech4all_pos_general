frappe.ui.form.on('Branch Expense', {
    setup: function(frm) {
        frm.set_query('branch_expense_template', function() {
            return {
                filters: {
                    company: frm.doc.company || '',
                    pos_profile: frm.doc.pos_profile || '',
                    branch: frm.doc.branch || ''
                }
            };
        });
        frm.set_query('pos_opening_shift', function() {
            return {
                filters: {
                    pos_profile: frm.doc.pos_profile || '',
                    status: 'Open',
                    docstatus: 1
                }
            };
        });
    },
    branch_expense_template: function(frm) {
        
    },
    refresh(frm) {
        if (frm.doc.pos_opening_shift) {
            frm.add_custom_button(__('View POS Opening Shift'), function () {
                frappe.set_route('Form', 'POS Opening Shift', frm.doc.pos_opening_shift);
            }, __('Links'));
        }
    },
    validate: function(frm) {
        let total = 0;
        if (frm.doc.branch_expense_item) {
            frm.doc.branch_expense_item.forEach(function(row) {
                total += flt(row.amount || 0);
            });
        }
        frm.set_value('total_amount', total);
    }
});