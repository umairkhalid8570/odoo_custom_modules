odoo.define('itelenoc_pos_ext.OrderCartWidget', function(require) {
    'use strict';

    const { useState, useRef, onPatched } = owl.hooks;
    const { useListener } = require('web.custom_hooks');
    const { onChangeOrder } = require('point_of_sale.custom_hooks');
    const OrderWidget = require('point_of_sale.OrderWidget');
    const Registries = require('point_of_sale.Registries');

    const OrderCartWidget = (OrderWidget) => {
        class OrderCartWidget extends OrderWidget {
            constructor() {
                super(...arguments);
                useListener('select-line', this._selectLine);
                useListener('edit-pack-lot-lines', this._editPackLotLines);
                onChangeOrder(this._onPrevOrder, this._onNewOrder);
                this.scrollableRef = useRef('scrollable');
                this.scrollToBottom = false;
//                onPatched(() => {
//                    // IMPROVEMENT
//                    // This one just stays at the bottom of the orderlines list.
//                    // Perhaps it is better to scroll to the added or modified orderline.
//                    if (this.scrollToBottom) {
//                        this.scrollableRef.el.scrollTop = this.scrollableRef.el.scrollHeight;
//                        this.scrollToBottom = false;
//                    }
//                });
                this.state = useState({ c_untaxed_amount: 0, c_amount: 0, c_discount_amount: 0, c_total_amount: 0, c_tax_amount: 0, street_part:0});
                this._updateSummary();
            }
            _updateSummary() {
                this.order.set_street_part(this.env.pos.config.street_part);

                const c_untaxed_amount = this.order ? this.order.get_c_untaxed_amount() : 0;
                const c_amount = this.order ? this.order.get_c_amount() : 0;
                const c_discount_amount = this.order ? this.order.get_c_discount_amount() : 0;
                const c_total_amount = this.order ? this.order.get_c_total_amount() : 0;
                const c_tax_amount = this.order ? this.order.get_c_tax_amount() : 0;
                onst street_part = this.order ? this.order.get_street_part() : 0;


                this.state.c_untaxed_amount = this.env.pos.format_currency(c_untaxed_amount);
                this.state.c_amount = this.env.pos.format_currency(c_amount);
                this.state.c_discount_amount = this.env.pos.format_currency(c_discount_amount);
                this.state.c_total_amount = this.env.pos.format_currency(c_total_amount);
                this.state.c_tax_amount = this.env.pos.format_currency(c_tax_amount);
                if (!this.order.get_client() && this.order.get_c_total_amount() >=300){
                this.showPopup('ErrorPopup', {
                                    title: this.env._t('Customer Error'),
                                    body: this.env._t(
                                        "Customer is not set."
                                    ),
                                });

                }
                this.render();
            }
        }
        OrderCartWidget.template = 'OrderWidget';
        return OrderCartWidget;
    };

    Registries.Component.extend(OrderWidget, OrderCartWidget);
    return OrderCartWidget;
});