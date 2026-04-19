<template>
    <nav class="navbar">
        <div class="navbar_logo" >
            <img src="../assets/logo_rec.svg">
        </div>
        <div class="navbar_links">
            <div class="container_links">
            <router-link to="/">Home</router-link>
            <router-link to="/recommendations">Recommendations</router-link>
            </div>
            <router-link to="/profile"><font-awesome-icon icon="fa-solid fa-circle-user" size="lg" style="color: white;" /></router-link>
        </div>
    </nav>
</template>

