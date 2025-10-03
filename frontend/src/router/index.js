import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'

const routes = [
    { path: '/', redirect: '/port-status' },
    { path: '/about', component: () => import('../views/About.vue') },
    { path: '/call-records', component: () => import('../views/CallRecords.vue') },
    { path: '/phone-lookup', component: () => import('../views/PhoneLookup.vue') },
    { path: '/port-status', component: () => import('../views/PortStatus.vue') },
    { path: '/pbx-sync', component: () => import('../views/PbxSync.vue') },

]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router
