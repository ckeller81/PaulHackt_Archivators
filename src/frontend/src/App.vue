<template>
  <header>
    <b-navbar type="dark" variant="dark" expand="md">
      <b-navbar-brand :to="'/'">
        <img
          src="/assets/images/logo_archivators.png"
          class="header-logo"
          alt="Paul Hackt - Archivators"
        />
        <span class="ms-3">Archivators - Paul Klee erleben</span>
      </b-navbar-brand>
      <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

      <b-collapse id="nav-collapse" is-nav>
        <b-navbar-nav>
          <b-nav-item v-for="route in routes" :key="route.path" :to="route.path" exact>
            {{ route.meta?.title }}
          </b-nav-item>
        </b-navbar-nav>
      </b-collapse>
      <div class="d-none d-md-block me-n3">
        <img src="/assets/images/logo-zpk-nt.png" />
      </div>
    </b-navbar>
  </header>
  <b-container fluid>
    <b-row>
      <b-col cols="12">
        <router-view v-slot="{ Component }">
          <transition name="zoom-transition">
            <component :is="Component" />
          </transition>
        </router-view>
      </b-col>
    </b-row>
  </b-container>
</template>

<script lang="ts">
import { RouterView, useRouter } from "vue-router";

export default {
  setup() {
    const router = useRouter();

    const routes = router.options.routes.filter((route) => route.meta && route.meta.title);

    return {
      routes,
    };
  },
};
</script>

<style lang="scss">
@import "@/scss/variables.scss";
@import "bootstrap/scss/bootstrap-utilities";

.header-logo {
  height: 125px;

  @include media-breakpoint-down(md) {
    height: 50px;
  }
}
</style>
