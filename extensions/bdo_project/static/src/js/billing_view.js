odoo.define('bdo_project.BillingView', function (require) {
"use strict";
var View = require('web.View');
var core = require('web.core');
var Model = require('web.DataModel');
var Widget = require('bdo_project.BillingWidget');
var QWeb = core.qweb;
var _lt = core._lt;

var BillingView = View.extend({
	template: "BillingView",
	display_name: _lt('Billing'),
	view_type: "billing",
	icon: 'fa-list',
	init: function () {
		this._super.apply(this, arguments);
		this.active_measure = '';
	},
	willStart: function () {
		var fields_def = 'id,name';
		return $.when(this._super(), fields_def);
	},
	render_buttons: function ($node) {
		self = this;
		var measures=[];

		if ($node) {
			console.log('a node: ' + $node);
			var service = new Model('bdo.project.service');
			service.query().all().then(function (records)  {
				_.each(records, function (record) {
                    $( ".o_graph_measures_list" ).append("<li data-field=" + record.name + "><a>" + record.name + "</a></li>");
                });
			});
			this.$buttons = $(QWeb.render('BillingView.buttons', {measures:measures}));
			this.$measure_list = this.$buttons.find('.o_graph_measures_list');
			this.update_measure();
			this.$buttons.find('button').tooltip();
            this.$buttons.click(this.on_button_click.bind(this));
			this.$buttons.appendTo($node);
		}
	},
	on_button_click: function (event) {
        var $target = $(event.target);
        if ($target.hasClass('o_graph_button')) {
            //this.widget.set_mode($target.data('mode'));
            this.$buttons.find('.o_graph_button.active').removeClass('active');
            $target.addClass('active');
        }
        else if ($target.parents('.o_graph_measures_list').length) {
            var parent = $target.parent();
            var field = parent.data('field');
            //this.active_measure = field;
            event.preventDefault();
            event.stopPropagation();
            this.update_measure();
            //this.widget.set_measure(this.active_measure);
        }
    },
    update_measure: function () {
        var self = this;
        this.$measure_list.find('li').each(function (index, li) {
            $(li).toggleClass('selected', $(li).data('field') === self.active_measure);
        });
    },
	do_show: function () {
        this.do_push_state({});
        return this._super();
    },
    do_search: function (domain, context, group_by) {
		var contents = this.$el[0].querySelector('.line');
		contents.innerHTML = "";
		//QWeb.render('line',{widget:this, line:this.service});
    },
    destroy: function () {
        return this._super.apply(this, arguments);
    }
});

core.view_registry.add('billing', BillingView);
return BillingView;
});