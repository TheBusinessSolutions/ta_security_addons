/** @odoo-module **/

import AbstractAction from "web.AbstractAction";
import ReportWidget from "web.Widget";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

export const report_backend = AbstractAction.extend({
    hasControlPanel: true,
    events: {
        "click .o_stock_card_reports_print": "print",
        "click .o_stock_card_reports_export": "export",
    },
    init: function (parent, action) {
        this._super.apply(this, arguments);
        this.actionManager = parent;
        this.given_context = {};
        this.odoo_context = action.context;
        this.controller_url = action.context.url;
        if (action.context.context) {
            this.given_context = action.context.context;
        }
        this.given_context.active_id =
            action.context.active_id || action.params.active_id;
        this.given_context.model = action.context.active_model || false;
        this.given_context.ttype = action.context.ttype || false;
    },
    willStart: function () {
        return Promise.all([this._super.apply(this, arguments), this.get_html()]);
    },
    set_html: function () {
        var self = this;
        var def = Promise.resolve();
        if (!this.report_widget) {
            this.report_widget = new ReportWidget(this, this.given_context);
            def = this.report_widget.appendTo(this.$(".o_content"));
        }
        def.then(function () {
            self.report_widget.$el.html(self.html);
        });
    },
    start: function () {
        this.set_html();
        return this._super();
    },
    get_html: function () {
        var self = this;
        // In Odoo 17, use the rpc service instead of this._rpc
        return rpc("/web/dataset/call_kw", {
            model: this.given_context.model,
            method: "get_html",
            args: [self.given_context],
            kwargs: { context: self.odoo_context },
        }).then(function (result) {
            self.html = result.html;
            return self.update_cp();
        });
    },
    update_cp: function () {
        if (this.$buttons) {
            var status = {
                breadcrumbs: this.actionManager.get_breadcrumbs(),
                cp_content: {$buttons: this.$buttons},
            };
            return this.update_control_panel(status);
        }
    },
    do_show: function () {
        this._super();
        this.update_cp();
    },
    print: function () {
        var self = this;
        return rpc("/web/dataset/call_kw", {
            model: this.given_context.model,
            method: "print_report",
            args: [this.given_context.active_id, "qweb-pdf"],
            kwargs: { context: self.odoo_context },
        }).then(function (result) {
            self.do_action(result);
        });
    },
    export: function () {
        var self = this;
        return rpc("/web/dataset/call_kw", {
            model: this.given_context.model,
            method: "print_report",
            args: [this.given_context.active_id, "xlsx"],
            kwargs: { context: self.odoo_context },
        }).then(function (result) {
            self.do_action(result);
        });
    },
    canBeRemoved: function () {
        return Promise.resolve();
    },
});

// The standard Odoo 17 way to register a legacy action
registry.category("actions").add("stock_card_report_backend", report_backend);