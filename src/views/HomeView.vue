<script setup lang="ts">
import {ref , computed , onMounted} from 'vue';
import Pagination from '../components/Pagination.vue';
import type { Schema } from "../../amplify/data/resource";
import { generateClient } from 'aws-amplify/api';

const client = generateClient <Schema>();

const movies = ref<Array<Schema['Movie']["type"]>>([]);


const currentPage = ref(1);
const itemsPerPage = 70;

onMounted(async () => {
    try {
        const { data } = await client.models.Movie.list({limit:2000});
        console.log("RESULT API: ", data);

        movies.value = data;

    } catch (error) {
        console.error("Error fetching movies:", error);
        movies.value = [];
    }
});

const totalPages = computed(() => Math.ceil((movies.value?.length) / itemsPerPage || 0 / itemsPerPage));

const paginatedMovies = computed(() => {
    const list = Array.isArray(movies.value) ? movies.value : [];
    const start = (currentPage.value - 1) * itemsPerPage;
    return list.slice(start, start + itemsPerPage);
});

function handlePageChange(page: number) {
    currentPage.value = page;
}
</script>


<template>
<div class="page">
    <h1>Welcome to Recomodo</h1>
<div class="content">
<div class="container">
    <RouterLink
        v-for="(movie) in paginatedMovies"
        :key="movie.movieId"
        :to=" { name: 'details', params: { id: movie.movieId },state: { movie} }"
         
        class="movie"
    >
        <img
            :src="'https://image.tmdb.org/t/p/w500' + movie.posterPath"
           
            :alt="movie.title"
       />
        <div class="discription">
            <p>{{ movie.title }}</p>
            <p>{{ movie.voteAverage }}</p>
        </div>
    </RouterLink>
</div>
<div class="pagination-wrapper">
    <Pagination
        :totalPages="totalPages" 
        :currentPage="currentPage" 
        @page-changed="handlePageChange"/>
</div>
</div>
</div>
</template>

<style scoped>
.page {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    
}

.pagination-wrapper {
    margin-top: auto;
    padding: 2rem 0;

    
    bottom: 20px;
    left:0;
    right:0;
    display: flex-end;
    justify-content: center;
    
    
}

html, body {
    height: 100%;
}

h1{
    color: white;
    margin: 0;
    padding-left: 4rem;
    padding-top: 2rem;
}

.movie {
  text-decoration: none; /* enlève le soulignement */
  color: inherit;        /* garde le texte blanc */
  display: block;
  cursor: pointer;
  transition: transform 0.2s;
}

img{
    width: 100px;
    height: 140px;
    display: block;
    justify-self: center;
    
}
.discription{
    display: flex;
    flex-direction:row;
    justify-content: space-around;
    align-items: center;
    font-size: small;
    position:relative;
    color: white;
}
.movie{
    height: 200px;
    width:150px;
    background-color:rgb(61,9,67);
    border-radius: 15px;
    padding-top: 15px;
    margin-top: 15px;
}

.container{
    display: grid;
    grid-template-columns: repeat(auto-fit, 150px);
    gap: 2rem;
    padding: 2rem 2rem;
    box-sizing: border-box;
    justify-content: start;
    margin-left: 1rem ;
    flex-grow: 1;
    align-self: start;
    height: 100%;

}


</style>