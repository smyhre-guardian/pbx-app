
import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

const routes = [
    { path: '/', component: Home },
    { path: '/about', component: () => import('../views/About.vue') },
    { path: '/call-records', component: () => import('../views/CallRecords.vue') },
    { path: '/phone-lookup', component: () => import('../views/PhoneLookup.vue') },
    { path: '/port-status', component: () => import('../views/PortStatus.vue') },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router
