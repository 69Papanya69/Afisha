import { createStore } from 'vuex';
import auth from './modules/auth';
import cart from './modules/cart';
import orders from './modules/orders';

export default createStore({
    modules: {
        auth,
        cart,
        orders,
    },
});