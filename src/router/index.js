import Vue from 'vue'
import VueRouter from 'vue-router'
import MyHtmlPage from "../components/MyHtmlPage.vue";
import Info from "../components/Info.vue"
Vue.use(VueRouter)

const routes = [

  {
    path: '/about',
    name: 'about',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  },
  {
    path: "/MyHtmlPage",
    name: "MyHtmlPage",
    component: MyHtmlPage,
  },
  {
    path: "/",
    name: "Info",
    component: Info,
  },
]

const router = new VueRouter({
  routes
})

export default router
