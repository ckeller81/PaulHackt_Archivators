import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
      meta: {
        transition: "zoom-transition",
      },
    },
    {
      path: "/archive",
      name: "archive",
      component: () => import("../views/ArchiveView.vue"),
      meta: {
        transition: "zoom-transition",
      },
    },
  ],
});

export default router;
