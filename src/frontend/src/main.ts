import { createApp } from "vue";
import { createPinia } from "pinia";

import App from "./App.vue";
import router from "./router";

// Styles
import "./scss/styles.scss";

import "animate.css";

const app = createApp(App);

app.use(createPinia());
app.use(router);

app.mount("#app");
