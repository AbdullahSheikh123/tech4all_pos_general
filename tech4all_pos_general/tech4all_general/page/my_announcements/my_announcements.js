frappe.pages['my-announcements'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Announcements',
		single_column: true
	});

	wrapper.pos = new tech4all.tech4allAnnouncements(wrapper);
}

tech4all.tech4allAnnouncements = class {
	constructor(wrapper) {
		this.wrapper = $(wrapper).find('.layout-main-section');
		this.page = wrapper.page;

		this.get_announcements();
	}

	get_announcements(){
		this.fetch_announcements().then((r) => {
			if (r.message) {
				// assuming only one opening voucher is available for the current user
				this.prepare_data(r.message);
			}
			else{
				console.log("No Announcements");
			}
		});
	}


	fetch_announcements() {
		return frappe.call("tech4all_pos_general.tech4all_pos_general.page.my_announcements.my_announcements.fetch_announcements");
	}

	async prepare_data(data){
		this.announcements = data;
		this.make_page();
	}

	make_page() {
		this.prepare_dom();
		this.prepare_components();
	}

	prepare_dom(){
		this.wrapper.append(
			`<div class="my-announcements container" style="background: #ffffff; padding: 10px;"></div>`
		);

		this.$components_wrapper = this.wrapper.find('.my-announcements');
	}

	prepare_components() {
		this.init_filters();
		this.init_announcements();
	}

	init_filters(){

	}

	init_announcements(){
		var me = this;
		$.each(this.announcements, function(i, v){
			var announcement_template = me.announcement_template(v);
			me.$components_wrapper.append(announcement_template);
		});
	}

	announcement_template(announcement){
		return `<div class="alert alert-${announcement.color}" role="alert">
				  <h4 class="alert-heading">${announcement.title}</h4>
				  ${announcement.description}
				</div>`;
	}
};


