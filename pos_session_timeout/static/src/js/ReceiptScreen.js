odoo.define('pos_session_timeout.ReceiptScreen', function(require) {
    'use strict';

    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const Registries = require('point_of_sale.Registries');
    const Login = require('pos_hr.LoginScreen');
    var session = require("web.session");

    const LoginScreen = Login =>
        class extends Login {
            back() {
                super.back(...arguments);
                if(this.props.timeout){
                    this.showScreen('ProductScreen');
                }
            }
        }
    const POSSessionTimeoutReceiptScreen = ReceiptScreen =>
        class extends ReceiptScreen {
            /**
             * The receipt has signature if one of the paymentlines
             * is paid with mercury.
             */
			get nextScreen() {
                if (this.env.pos.config.auto_logout_on_each_sale){
                    session.timeout = true;
                    return { name: 'LoginScreen', props: {'timeout': true} };
                }else{
                    session.timeout = false;
                    return { name: 'ProductScreen'};
                }
            }
            orderDone() {
                this.currentOrder.finalize();
                const { name, props } = this.nextScreen;
                if(props){
                    if(props.timeout){
                        this.showTempScreen(name, props);
                    }
                }else{
                    this.showScreen(name, props);
                }
            }
        };

    Registries.Component.extend(ReceiptScreen, POSSessionTimeoutReceiptScreen);
    Registries.Component.extend(Login, LoginScreen);

    return {
        ReceiptScreen: ReceiptScreen,
        Login: Login
    };
});
