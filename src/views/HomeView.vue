<script setup lang="ts">
import {ref, computed , onMounted} from 'vue';
import Pagination from '../components/Pagination.vue';
import type { Schema } from "../../amplify/data/resource";
import { generateClient } from 'aws-amplify/api';
import SearchBar from '@/components/SearchBar.vue';
import FirstSigninPage from '@/views/FirstSigninPage.vue';

const client = generateClient <Schema>();

const movies = ref<Array<Schema['Movie']["type"]>>([]);
const currentPage = ref(1);
const itemsPerPage = 70;

const moviesByPage = ref<Record<number, Array<Schema['Movie']["type"]>>>({});
const nextTokens = ref<Record<number, string | null>>({});



async function loadMoviesPage(page: number) {
   try {
    // ne pas chargé si l'utilisateur recherche
    if (isSearching.value) return;
     if(moviesByPage.value[page]) {
        movies.value = moviesByPage.value[page];
        return;
      }

      let token=null;

      for (let i=1;i<page;i++){
        token = nextTokens.value[i];
        if(!token){
            break;
        }
      }

      const { data, nextToken} = await client.models.Movie.list({ limit: itemsPerPage, nextToken: token });
        moviesByPage.value[page] = data ?? [];
        nextTokens.value[page] = nextToken ?? null;
        movies.value = moviesByPage.value[page];
    } catch (error) {
        console.error("Error fetching movies for page " ,error);
    }  
}


onMounted(() => {
    loadMoviesPage(1);
});

function handlePageChange(page: number) {
    currentPage.value = page;
    loadMoviesPage(page);
}

//recherche
const searchResults=ref<Array<Schema['Movie']["type"]>>([]);
const isSearching=ref(false);
const seen = new Set<string>();

async function searchMovies(query:string){
    const q=query.toLowerCase().trim();
    if(!q){
        isSearching.value=false;
        searchResults.value=[];
        return;
    }

    isSearching.value=true;
    let results: Array<Schema['Movie']["type"]> = [];

    //recherche dans les pages déjà chargées parla pagination
    Object.values(moviesByPage.value).forEach(page=>{
        page.forEach(movie=>{
            const title=movie.title?.toLowerCase() || "";
            const keywords= movie.keywords?.toLowerCase() || "";

            if(
                keywords.includes(q) ||
                title.includes(q)
            ){
                if ((keywords.includes(q) || title.includes(q)) && !seen.has(movie.movieId)) {
                 seen.add(movie.movieId);
                 results.push(movie);
                }
            }

            
        });
    });

    //si pas de résultats dans les pages déjà chargées ou resultats<20
    let currentNextToken: string | null= nextTokens.value[currentPage.value] ?? null;
    while(results.length<10 && currentNextToken){
        const response =await client.models.Movie.list({
            limit: itemsPerPage,
            nextToken: currentNextToken
        });

        const page=response.data ?? [];
        page.forEach(movie=>{
            const title=movie.title?.toLowerCase() || "";
            const keywords=movie.keywords?.toLowerCase() || "";
            if(
                keywords.includes(q) ||
                title.includes(q)
            ){
                if ((keywords.includes(q) || title.includes(q)) && !seen.has(movie.movieId)) {
                   seen.add(movie.movieId);
                   results.push(movie);
                }
            }
        });
        currentNextToken=response.nextToken ?? null;
    } 
    //limiter les résultats à 20
    //searchResults.value=results.slice(0,20);
    searchResults.value=results
} 

function getImageUrl(posterPath: any) {
   const path = String(posterPath || '').trim();
  if (!posterPath || posterPath === 'null' || posterPath === 'undefined' || posterPath === '') return '/defaultPoster.webp';
  if (posterPath.startsWith('/')) {
    return `https://image.tmdb.org/t/p/w500${path}`;
  }
  return posterPath;
}
</script>


<template>
<div class="page">
    <FirstSigninPage/>
    <h1>Welcome to Recomodo</h1>
    <SearchBar @search="searchMovies"/>
<div class="content">
<div class="container">
    <RouterLink
       v-for="movie in isSearching? searchResults : movies"
        :key="movie.movieId"
        :to=" { name: 'details', params: { id: movie.movieId } }"
         
        class="movie-card"
    >
        <img
            :src="getImageUrl(movie?.posterPath)"
            :alt="movie.title"
            @error="e => e.target.src = '/defaultPoster.webp'"
       />
        <div class="movie-info">
             <p class="movie-title">{{ movie.title }}</p>
             <p class="movie-meta">★ {{ movie.voteAverage }}</p>
        </div>
    </RouterLink>
</div>

<div v-if="!isSearching" class="pagination-wrapper">
    <Pagination 
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
    /*margin-top: auto;*/
    padding: 2rem 0;
    justify-content: center;
    display: flex;
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

/* CARD */
.movie-card {
  text-decoration: none;
  color: white;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  width: 150px;
  height: 265px;
  overflow: hidden;
  transition: transform 0.2s ease;
  box-shadow: 0 4px 20px rgba(114, 55, 136, 0.6);
  border: 1px solid #7a2a8a;
  border-radius: 6px;
}

.movie-card:hover {
  transform: scale(1.04);
}

.movie-card img {
  width: 150px;
  height: 220px;
  object-fit: cover;
  display: block;
}

.movie-info {
  background: #3d0943;
  padding: 4px 8px;
  width: 100%;
  height: 45px;
  box-sizing: border-box;
  flex-shrink: 0;
}

.movie-title {
  margin: 0;
  font-size: 12px;
  font-weight: 500;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.movie-meta {
  margin: 3px 0 0 0;
  font-size: 11px;
  color: #f5c518;
}
.container{
  display: grid;
  grid-template-columns: repeat(auto-fill, 150px);
  grid-auto-rows: 270px;
  gap: 1.5rem;
  padding: 2rem;
  box-sizing: border-box;
  width: 100%;
  overflow-x: hidden;
  max-width: 100%;

}


</style>