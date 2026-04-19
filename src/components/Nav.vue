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

<style scoped>
.navbar {
    display:flex;
    justify-content: space-between;
    align-items: center;
    padding-inline: 6px;
    background-color:#15001d;
    width: 100%;
    border-bottom: #E8DEF8 solid 1px;
}
.navbar_links{
    display: flex;
    gap : 10rem;
    padding-bottom: 0px;
   margin-block: 10px;
}
.container_links{
    display:flex;
    gap : 7rem;
    border-style: solid;
    border-width:1px;
    border-radius: 12px;
    border-color:#E8DEF8;
    padding-inline: 7rem;
    padding-block: 2px;
}
.navbar_logo img{
    width: 10rem;
    padding-top: 5px;
    position: static;
}
</style>
