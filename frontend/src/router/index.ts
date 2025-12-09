import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/pages/Login.vue'
import Register from '@/pages/Register.vue'
import Home from "@/pages/Home.vue";


const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    // meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 添加路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')

  // ⚡ 已登录用户访问 login/register → 自动跳回首页
  if (token && (to.name === 'Login' || to.name === 'Register')) {
    return next('/')
  }

  // ⚡ 未登录访问需要鉴权的页面 → 跳转登录
  if (!token && to.meta.requiresAuth) {
    return next('/login')
  }

  next()
})

// Workaround for https://github.com/vitejs/vite/issues/11804
router.onError((err, to) => {
  if (err?.message?.includes?.('Failed to fetch dynamically imported module')) {
    if (localStorage.getItem('vuetify:dynamic-reload')) {
      console.error('Dynamic import error, reloading page did not fix it', err)
    } else {
      console.log('Reloading page to fix dynamic import error')
      localStorage.setItem('vuetify:dynamic-reload', 'true')
      location.assign(to.fullPath)
    }
  } else {
    console.error(err)
  }
})

router.isReady().then(() => {
  localStorage.removeItem('vuetify:dynamic-reload')
})

export default router
