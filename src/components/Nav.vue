<template>
    <nav class="navbar">
        <div class="navbar_logo" >
            <img src="../assets/logo_rec.svg">
        </div>
        <div class="navbar_links">
            <div class="container_links">
            <router-link to="/"><b :class="{ active: activeLink === '/' }" class="nav_link">Home</b></router-link>
            <router-link to="/recommendations"><b :class="{ active: activeLink === '/recommendations' }" class="nav_link">Recommendations</b></router-link>
            </div>
            <profile-menu/>
            <!--<router-link to="/profile"><font-awesome-icon icon="fa-solid fa-circle-user" size="lg" style="color: white;" /></router-link>-->
        </div>
    </nav>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import ProfileMenu from './ProfileMenu.vue';

const route = useRoute();
const activeLink = computed(() => route.path);
</script>

<style >
.nav_link{
    color: #9c03be;
}
/*
.nav_link.active{
    color: #ff00fb;
}*/

</style>