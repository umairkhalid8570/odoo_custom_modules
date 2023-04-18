odoo.define('pos_session_timeout.PosComponent', function (require) {
    'use strict';

    const Chrome = require('point_of_sale.Chrome');
    const Registries = require('point_of_sale.Registries');
    var session = require("web.session");

    const SessionTimeout = Chrome =>
        class extends Chrome {
            set_idle_session_timer(timeout=60) {
                var self = this;
                timeout = timeout * 1000;
                clearTimeout(this.idle_session_timer);
                this.idle_session_timer = setTimeout(function () {
                    if(session.timeout){
                        self.showTempScreen('LoginScreen', {'timeout': session.timeout});
                        session.timeout = false;
                    }else{
                        self.showTempScreen('LoginScreen');
                    }
                }, timeout);
            }
            __showScreen({ detail: { name, props = {} } }) {
                var self = this;
                super.__showScreen(...arguments);
                if (this.env.pos.config.session_timeout) {
                    $(document).bind("mousemove mousedown touchstart click scroll keypress", function () {
                        self.set_idle_session_timer(self.env.pos.config.session_timeout);
                    });
                    this.set_idle_session_timer(this.env.pos.config.session_timeout);
                }
            }
        }

    Registries.Component.extend(Chrome, SessionTimeout);

    return SessionTimeout;
});