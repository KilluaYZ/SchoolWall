import {createRouter, createWebHistory} from "vue-router";


const routes = [
    {
        path: "/",
        name: "Main",
        component: () => import("../view/mainpage.vue")
    },
    {
        path: "/login",
        name: "Login",
        component: () => import("../view/login.vue")
    },
    {
        path: "/register",
        name: "Register",
        component: () => import("../view/register.vue")
    },
    {
        path: "/detail",
        name: "Detail",
        component: () => import("../view/detail.vue")
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

export default router;
