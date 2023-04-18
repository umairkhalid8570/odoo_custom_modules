odoo.define("itelenoc_pos_ext.models", function (require){
    "use strict";
    const models = require('point_of_sale.models');
    var utils = require('web.utils');

    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;

    var posmodel_super = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var self = this;
            // some new code in this method
//            models.load_fields('pos.order.line',['product_subsidy']);
            models.load_fields('pos.order',['c_untaxed_amount', 'c_amount', 'c_discount_amount', 'c_total_amount','c_tax_amount']);
//            models.load_fields('res.partner',['identification_number']);
            posmodel_super.initialize.apply(this, arguments);
        },
    });

    var super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attributes,options){
            let res = super_order.initialize.apply(this,arguments);
            if (!options.json) {
                this.c_untaxed_amount = 0;
                this.c_amount = 0;
                this.c_discount_amount = 0;
                this.c_total_amount = 0;
                this.c_tax_amount = 0;
                this.street_part = 0;
            }
            return res;
        },
        export_as_JSON: function() {
            let json = super_order.export_as_JSON.apply(this, arguments);
            json.c_untaxed_amount = this.get_c_untaxed_amount();
            json.c_amount = this.get_c_amount();
            json.c_discount_amount = this.get_c_discount_amount();
            json.c_total_amount = this.get_c_total_amount();
            json.c_tax_amount = this.get_c_tax_amount();
            json.street_part = this.get_street_part();
            return json;
        },
        export_for_printing: function(){
            let json = super_order.export_for_printing.apply(this, arguments);
            json.c_untaxed_amount = this.get_c_untaxed_amount();
            json.c_amount = this.get_c_amount();
            json.c_discount_amount = this.get_c_discount_amount();
            json.c_total_amount = this.get_c_total_amount();
            json.c_tax_amount = this.get_c_tax_amount();
            json.street_part = this.get_street_part();
            return json;
        },
        get_all_prices: function(){
        var self = this;

        var price_unit = this.get_unit_price() * (1.0 - (this.get_discount() / 100.0));
        var taxtotal = 0;

        var product =  this.get_product();
        var taxes =  this.pos.taxes;
        var taxes_ids = _.filter(product.taxes_id, t => t in this.pos.taxes_by_id);
        var taxdetail = {};
        var product_taxes = [];

        _(taxes_ids).each(function(el){
            var tax = _.detect(taxes, function(t){
                return t.id === el;
            });
            product_taxes.push.apply(product_taxes, self._map_tax_fiscal_position(tax, self.order));
        });
        product_taxes = _.uniq(product_taxes, function(tax) { return tax.id; });

        var all_taxes = this.compute_all(product_taxes, price_unit, this.get_quantity(), this.pos.currency.rounding);
        var all_taxes_before_discount = this.compute_all(product_taxes, this.get_unit_price(), this.get_quantity(), this.pos.currency.rounding);
        _(all_taxes.taxes).each(function(tax) {
            taxtotal += tax.amount;
            taxdetail[tax.id] = tax.amount;
        });

        return {
            "priceWithTax": all_taxes.total_included,
            "priceWithoutTax": all_taxes.total_excluded,
            "priceSumTaxVoid": all_taxes.total_void,
            "priceWithTaxBeforeDiscount": all_taxes_before_discount.total_included,
            "tax": taxtotal,
            "taxDetails": taxdetail,
        };
    },

        get_c_untaxed_amount: function() {
            return this.get_total_without_tax() + this.get_c_discount_amount();
        },
        set_c_untaxed_amount: function(c_untaxed_amount) {
            this.c_untaxed_amount=c_untaxed_amount;
        },
        get_street_part: function() {
        return this.street_part;
        },

        set_street_part: function(street_part) {
            this.street_part=street_part;
        },
        get_total_tax: function() {
        if (this.pos.company.tax_calculation_rounding_method === "round_globally") {
            // As always, we need:
            // 1. For each tax, sum their amount across all order lines
            // 2. Round that result
            // 3. Sum all those rounded amounts
            var groupTaxes = {};
            this.orderlines.each(function (line) {
                var taxDetails = line.get_tax_details();
                var taxIds = Object.keys(taxDetails);
                for (var t = 0; t<taxIds.length; t++) {
                    var taxId = taxIds[t];
                    if (!(taxId in groupTaxes)) {
                        groupTaxes[taxId] = 0;
                    }
                    groupTaxes[taxId] += taxDetails[taxId];
                }
            });

            var sum = 0;
            var taxIds = Object.keys(groupTaxes);
            for (var j = 0; j<taxIds.length; j++) {
                var taxAmount = groupTaxes[taxIds[j]];
                sum += round_pr(taxAmount, this.pos.currency.rounding);
            }
            return sum;
        } else {
            return round_pr(this.orderlines.reduce((function(sum, orderLine) {
                return sum + orderLine.get_tax();
            }), 0), this.pos.currency.rounding);
        }
    },
        get_c_tax_amount: function() {
            return this.get_total_tax();
//            return this.full_product_name;
        },
        set_c_tax_amount: function(c_tax_amount) {
            this.c_tax_amount=c_tax_amount;
        },
        get_c_amount: function() {
            return this.get_c_untaxed_amount() + this.get_c_tax_amount();
        },
        set_c_amount: function(c_amount) {
            this.c_amount=c_amount;
        },
        get_c_discount_amount: function() {
            return this.get_total_discount();

        },
        set_c_discount_amount: function(c_discount_amount) {
            this.c_discount_amount=c_discount_amount;
        },

        set_c_total_amount: function(c_total_amount) {
            this.c_total_amount=c_total_amount;
        },
        get_c_total_amount: function() {
            return this.get_c_amount() - this.get_c_discount_amount();
        },


    });

    var super_Orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function (attributes, options) {
            let res = super_Orderline.initialize.apply(this, arguments);
            if (!options.json) {
                this.product_subsidy = null;
            }
            return res;
        },

        init_from_JSON: function (json) {
            super_Orderline.init_from_JSON.apply(this, arguments);
            if (json.product_subsidy) {
                this.product_subsidy = json.product_subsidy;
            }
        },
        export_as_JSON: function () {
            let json = super_Orderline.export_as_JSON.apply(this, arguments);
            json.product_subsidy = this.get_product_subsidy();
            return json;
        },
        export_for_printing: function(){
            var json = super_Orderline.export_for_printing.apply(this, arguments);
            json.product_subsidy = this.get_product_subsidy();
            return json;
        },

        get_all_prices: function(){
        var self = this;

        var price_unit = this.get_unit_price() * (1.0 - (this.get_discount() / 100.0));
        var taxtotal = 0;

        var product =  this.get_product();
        var taxes =  this.pos.taxes;
        var taxes_ids = _.filter(product.taxes_id, t => t in this.pos.taxes_by_id);
        var taxdetail = {};
        var product_taxes = [];

        _(taxes_ids).each(function(el){
            var tax = _.detect(taxes, function(t){
                return t.id === el;
            });
            product_taxes.push.apply(product_taxes, self._map_tax_fiscal_position(tax, self.order));
        });
        product_taxes = _.uniq(product_taxes, function(tax) { return tax.id; });

        var all_taxes = this.compute_all(product_taxes, price_unit, this.get_quantity(), this.pos.currency.rounding);
        var all_taxes_before_discount = this.compute_all(product_taxes, this.get_unit_price(), this.get_quantity(), this.pos.currency.rounding);
        _(all_taxes_before_discount.taxes).each(function(tax) {
            taxtotal += tax.amount;
            taxdetail[tax.id] = tax.amount;
        });

        return {
            "priceWithTax": all_taxes.total_included,
            "priceWithoutTax": all_taxes.total_excluded,
            "priceSumTaxVoid": all_taxes.total_void,
            "priceWithTaxBeforeDiscount": all_taxes_before_discount.total_included,
            "tax": taxtotal,
            "taxDetails": taxdetail,
        };
    },
        get_product_subsidy: function() {
            let order = this.order;
            let orderlines = this.order.get_orderlines();
            let bisp_return;
            let original_price = this.get_lst_price();
            let product_display_unit_price = this.get_unit_price();
            let product_quantity = this.get_quantity();
            let price_manually_set = this.price_manually_set;
            let product_tmp_id = this.product.product_tmpl_id;

            // Check if price is set manually from UI if not calculate bisp discount
            if (typeof price_manually_set === 'undefined' || price_manually_set === false){
                bisp_return = calculate_bisp_discount();
                return bisp_return;
            }
            // If set manually and product id is in pricelist items then calcualte bisp discount
            else {
                if (check_pricelist() === true){
                    bisp_return = calculate_bisp_discount();
                    return bisp_return;
                }
                else{
                    return 0;
                }
            }
            function check_pricelist(){
                let list_items = order.pricelist.items;
                // TODO: Need some thorough insight
                if (list_items.length > 1){
                    let arr = list_items.map(x => x.product_tmpl_id);
                    let status = arr.some(row => row.includes(product_tmp_id));
                    return status;
                }
                else{
                    return false;
                }
            }
            // Calculate Bisp discount
            function calculate_bisp_discount(){
                let discount_price = 0;
                discount_price = (original_price - product_display_unit_price) * product_quantity;
                return discount_price;
            }
        },
    });

});