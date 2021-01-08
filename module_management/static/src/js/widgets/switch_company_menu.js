console.log("Vao day === ");

odoo.define('module_management.SwitchCompanyMenu', function(require) {
"use strict";
    // require original module JS
    var web_company_menu = require('web.SwitchCompanyMenu');

    // Extend widget
    web_company_menu.SwitchCompanyMenu.willStart.include({
        console.log("Vao day willStart ===");
        this.user_companies = this.allowed_company_ids[0];
        return this._super();
    });
}
