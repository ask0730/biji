import TabsView from '@/layouts/tabs/TabsView'
import BlankView from '@/layouts/BlankView'
import PageView from '@/layouts/PageView'

// 路由配置
const options = {
  routes: [
    {
      path: '/login',
      name: '登录页',
      component: () => import('@/pages/login')
    },
    {
      path: '*',
      name: '404',
      component: () => import('@/pages/exception/404'),
    },
    {
      path: '/403',
      name: '403',
      component: () => import('@/pages/exception/403'),
    },
    {
      path: '/',
      name: '首页呃呃',
      component: TabsView,
      redirect: '/login',
      children: [
        
        {
          name: '工作台',
          path: 'task',
          meta: {
            icon: 'dashboard'
          },
          component: () => import('@/pages/task/main')
        },
        {
          name: '识别结果',
          path: 'task/result',
          meta: {
            icon: 'dashboard',
            invisible: true
          },
          component: () => import('@/pages/task/result')
        },
        {
          name: '数据集',
          path: 'dataset',
          meta: {
            icon: 'table'
          },
          component: () => import('@/pages/dataset/main')
        },
        {
          name: '数据详情',
          path: 'dataset/list',
          meta: {
            icon: 'table',
            invisible: true
          },
          component: () => import('@/pages/dataset/list')
        },
        {
          name: '模型管理',
          path: 'models',
          meta: {
            icon: 'profile'
          },
          component: () => import('@/pages/models/main')
        },
        {
          name: '模型训练配置',
          path: 'models/config',
          meta: {
            icon: 'profile',
            invisible: true
          },
          component: () => import('@/pages/models/config')
        },
        {
          name: '数据标注',
          path: 'dataset/labeling',
          meta: {
            icon: 'check-circle-o',
            invisible: true,
            query: {
              name: '数据标注'
            }
          },
          component: () => import('@/pages/dataset/label')
        },
        {
          name: '结构处理',
          path: 'structure',
          meta: {
            icon: 'project'
          },
          component: () => import('@/pages/structure/main')
        },
        {
          name: '结构处理详情',
          path: 'structure/detail',
          meta: {
            icon: 'project',
            invisible: true
          },
          component: () => import('@/pages/structure/detail')
        }
      ]
    },
  ]
}

export default options
