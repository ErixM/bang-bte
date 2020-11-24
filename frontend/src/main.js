import Vue from 'vue'
import App from './App.vue'

Vue.config.productionTip = false
import VueSocketIO from 'vue-socket.io'
Vue.use(new VueSocketIO({
	debug: Vue.config.devtools,
	connection: Vue.config.devtools?'http://localhost:5001':'http://bang.xamin.it:5001',
}))

new Vue({
  render: h => h(App),
}).$mount('#app')
