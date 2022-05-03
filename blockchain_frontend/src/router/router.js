import Main from "@/views/Main.vue";
import InfoAndActions from "@/views/BcInstance.vue";
import Info from "@/views/Info.vue";
import {createRouter, createWebHistory} from "vue-router";
const routes = [
    {
        path: "/",
        component: Main
    },
    {
        path: "/info",
        component: Info
    },
    {
        path: "/bc-instance",
        component: InfoAndActions,
    },
    {
        path: "/bc-instance/:name",
        component: InfoAndActions,
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

export default router;