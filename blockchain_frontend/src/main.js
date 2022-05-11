import { createApp } from "vue";
import App from "@/App.vue";
import router from "@/router/router";
import "@/assets/styles/main.scss";
import {createPinia} from "pinia";

const app = createApp(App);
app.use(router);
app.use(createPinia());
app.mount("#app");
