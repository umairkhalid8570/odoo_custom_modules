odoo.define("looped_pos_ext.models", function (require){
    "use strict";
    const models = require('point_of_sale.models');
    var utils = require('web.utils');
    var field_utils = require('web.field_utils');

    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;

//    models.load_fields('product.product','extra_item');
//    models.load_fields('pos.order.line','remaining_qty');

    var posmodel_super = models.PosModel.prototype;



models.load_fields('res.partner','pos_order_count');



    var super_Orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        export_as_JSON: function() {
            let json = super_Orderline.export_as_JSON.apply(this, arguments);
            this.set_first_order_discount();
            return json;
        },
        // sets a discount [0,100]%
    set_discount: function(discount){

        var parsed_discount = typeof(discount) === 'number' ? discount : isNaN(parseFloat(discount)) ? 0 : field_utils.parse.float('' + discount);
        var disc = Math.min(Math.max(parsed_discount || 0, 0),100);
        this.discount = disc;
        this.discountStr = '' + disc;
//        this.trigger('change',this);
    },
    // returns the discount [0,100]%
        set_first_order_discount: function(){
            var order    = this.order;
            var lines    = order.get_orderlines();
            var discount = this.pos.config.customer_discount;
            const weekday = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
            const d = new Date();
            let day = weekday[d.getDay()];
            if(this.pos.get_client() != null && this.pos.get_client().pos_order_count < 1 && (day == "Thursday" || day == "Sunday")){
            for (var i = 0; i < lines.length; i++) {
                lines[i].set_discount(discount);
            }
            }
            else{
            for (var i = 0; i < lines.length; i++) {
                lines[i].set_discount('0');
            }
            }
        },


    });

});