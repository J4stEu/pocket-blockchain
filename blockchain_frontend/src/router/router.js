import Main from "@/views/Main.vue";
import InfoAndActions from "@/views/BcInstance.vue";
import SystemInfo from "@/views/SystemInfo.vue";
import NotFound from "@/views/NotFound.vue";
import {createRouter, createWebHistory} from "vue-router";
const routes = [
    {
        path: "/",
        component: Main
    },
    {
        path: "/system-info",
        component: SystemInfo
    },
    {
        path: "/bc-instance",
        component: InfoAndActions,
    },
    {
        path: "/bc-instance/:name",
        component: InfoAndActions,
    },
    {   path: "/:pathMatch(.*)*",
        component: NotFound
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

export default router;