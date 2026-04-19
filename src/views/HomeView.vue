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
         
        class="movie"
    >
        <img
            :src="'https://image.tmdb.org/t/p/w500' + movie.posterPath"
           
            :alt="movie.title"
       />
        <div class="discription">
            <p><strong><em>{{ movie.title }}</em></strong></p>
            <p><strong><em>{{ movie.voteAverage }}</em></strong></p>
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
    flex: 1;

}


</style>