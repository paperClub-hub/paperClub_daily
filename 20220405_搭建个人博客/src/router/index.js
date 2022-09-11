import Vue from 'vue'
import Router from 'vue-router'
import HelloWorld from '../components/HelloWorld'
import Home from '../pages/home'
import Detail from '../pages/article'

Vue.use(Router)


// 创建路由
const routes = [
  {
    path: '/helloworld',
    component: HelloWorld
  },
  {
    path: "/",
    component: Home,
  },
  {
    path: "/detail",
    component: Detail,
  },

]


// 实例化
let router = new Router({
  routes
})


export default router; // 路由导出




