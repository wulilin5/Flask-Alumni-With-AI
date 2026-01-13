# 前端项目创建指南

## 创建新的前端仓库

由于你选择前后端独立仓库，请在新的目录下创建前端项目：

### 1. 创建 Vue 3 项目

在新的目录执行：

```bash
# 创建 Vue 3 项目
npm create vue@latest alumni-frontend

# 进入项目目录
cd alumni-frontend

# 安装依赖
npm install
```

在创建项目时，选择以下选项：
- ✅ TypeScript: No
- ✅ JSX: No
- ✅ Vue Router: Yes
- ✅ Pinia: Yes
- ✅ Vitest: No
- ✅ End-to-End Testing: No
- ✅ ESLint: No
- ✅ Prettier: No

### 2. 安装 Element Plus

```bash
npm install element-plus @element-plus/icons-vue
```

### 3. 安装 Axios（用于 HTTP 请求）

```bash
npm install axios
```

### 4. 项目结构

创建后的项目结构应该是：

```
alumni-frontend/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   ├── router/
│   ├── stores/
│   ├── views/
│   ├── App.vue
│   └── main.js
├── package.json
└── vite.config.js
```

### 5. 配置 API 请求

在 `src/` 目录下创建以下文件：

#### `src/utils/request.js` - Axios 配置
```javascript
import axios from 'axios'

// 创建 axios 实例
const request = axios.create({
  baseURL: 'http://localhost:8001/api', // 后端 API 地址
  timeout: 10000,
  withCredentials: true // 携带 cookie（用于 session）
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data
    // 统一处理响应
    if (res.code === 200) {
      return res.data
    } else {
      return Promise.reject(new Error(res.message || '请求失败'))
    }
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

export default request
```

#### `src/api/user.js` - 用户相关 API
```javascript
import request from '@/utils/request'

// 登录
export function login(data) {
  return request({
    url: '/auth/login',
    method: 'post',
    data
  })
}

// 登出
export function logout() {
  return request({
    url: '/auth/logout',
    method: 'post'
  })
}

// 获取当前用户
export function getCurrentUser() {
  return request({
    url: '/auth/current',
    method: 'get'
  })
}
```

#### `src/api/alumni.js` - 校友相关 API
```javascript
import request from '@/utils/request'

// 获取校友列表
export function getAlumniList(params) {
  return request({
    url: '/users',
    method: 'get',
    params
  })
}

// 获取校友详情
export function getAlumniDetail(id) {
  return request({
    url: `/users/${id}`,
    method: 'get'
  })
}

// 新增校友
export function createAlumni(data) {
  return request({
    url: '/users',
    method: 'post',
    data
  })
}

// 更新校友
export function updateAlumni(id, data) {
  return request({
    url: `/users/${id}`,
    method: 'put',
    data
  })
}

// 删除校友
export function deleteAlumni(id) {
  return request({
    url: `/users/${id}`,
    method: 'delete'
  })
}

// AI 摘要
export function aiSummary(data) {
  return request({
    url: '/ai/summary',
    method: 'post',
    data
  })
}

// AI 邮件
export function aiDraftEmail(data) {
  return request({
    url: '/ai/draft_email',
    method: 'post',
    data
  })
}
```

### 6. 配置路由

#### `src/router/index.js`
```javascript
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/add',
    name: 'Add',
    component: () => import('@/views/Add.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/edit/:id',
    name: 'Edit',
    component: () => import('@/views/Edit.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
  } else if (to.path === '/login' && userStore.isLoggedIn) {
    next('/')
  } else {
    next()
  }
})

export default router
```

### 7. 配置 Pinia Store

#### `src/stores/user.js`
```javascript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, logout as logoutApi, getCurrentUser } from '@/api/user'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)

  const isLoggedIn = computed(() => !!user.value)

  async function login(username, password) {
    try {
      const data = await loginApi({ username, password })
      user.value = data
      return true
    } catch (error) {
      console.error('登录失败:', error)
      return false
    }
  }

  async function logout() {
    try {
      await logoutApi()
      user.value = null
      return true
    } catch (error) {
      console.error('登出失败:', error)
      return false
    }
  }

  async function fetchCurrentUser() {
    try {
      const data = await getCurrentUser()
      user.value = data
      return true
    } catch (error) {
      user.value = null
      return false
    }
  }

  return {
    user,
    isLoggedIn,
    login,
    logout,
    fetchCurrentUser
  }
})
```

### 8. 配置主应用

#### `src/main.js`
```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)
app.use(ElementPlus)

app.mount('#app')
```

### 9. 运行项目

```bash
npm run dev
```

访问 `http://localhost:5173`

---

## 下一步

请按照上述步骤创建前端项目，完成后我会帮你实现具体的页面组件（登录、列表、新增、编辑等）。