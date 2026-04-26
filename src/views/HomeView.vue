<script setup lang="ts">
import {ref, computed , onMounted} from 'vue';
import Pagination from '../components/Pagination.vue';
import type { Schema } from "../../amplify/data/resource";
import { generateClient } from 'aws-amplify/api';
import SearchBar from '@/components/SearchBar.vue';

const client = generateClient <Schema>();

const movies = ref<Array<Schema['Movie']["type"]>>([]);
const currentPage = ref(1);
const itemsPerPage = 70;

const moviesByPage = ref<Record<number, Array<Schema['Movie']["type"]>>>({});
const nextTokens = ref<Record<number, string | null>>({});



async function loadMoviesPage(page: number) {
   try {
    // ne pas chargé si l'utilisateur recherche
   // if (isSearching.value) return;
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
    //loadAllMovies();  
});

function handlePageChange(page: number) {
    currentPage.value = page;
    loadMoviesPage(page);
}

//recherche

//algo le plus rapide mais plus de bugs
/*
const searchResults=ref<Array<Schema['Movie']["type"]>>([]);
const isSearching=ref(false);

// Ajoutez ces 3 refs en plus de ceux existants
const allMovies = ref<Array<Schema['Movie']["type"]>>([]);
const isLoadingAll = ref(false);
const allMoviesLoaded = ref(false);

// Chargement en arrière-plan de tous les films
async function loadAllMovies() {
  isLoadingAll.value = true;
  let token: string | null = null;
  const results: Array<Schema['Movie']["type"]> = [];

  do {
    const { data, nextToken } = await client.models.Movie.list({
      limit: 500,
      nextToken: token,
    });
    results.push(...(data ?? []));
    token = nextToken ?? null;
  } while (token);

  allMovies.value = results;
  allMoviesLoaded.value = true;
  isLoadingAll.value = false;
}


// Remplacer searchMovies — plus de async, plus d'appel réseau
function searchMovies(query: string) {
  const q = query.toLowerCase().trim();
  if (!q) {
    isSearching.value = false;
    searchResults.value = [];
    return;
  }

  isSearching.value = true;

  searchResults.value = allMovies.value.filter(movie => {
    const title = movie.title?.toLowerCase() ?? "";
    const keywords = movie.keywords?.toLowerCase() ?? "";
    return title.includes(q) || keywords.includes(q);
  });

}*/

//algo2
/*async function searchMovies(query: string) {
  const q = query.toLowerCase().trim();
  if (!q) {
    isSearching.value = false;
    searchResults.value = [];
    return;
  }

  isSearching.value = true;

  try {
    const { data } = await client.models.Movie.list({
      filter: {
        or: [
          { title: { contains: q } },
          { keywords: { contains: q } },
        ]
      },
      limit: 20,
    });
    searchResults.value = data ?? [];
  } catch (error) {
    console.error("Erreur recherche :", error);
  }
}*/
/*async function searchMovies(query: string) {
  const q = query.toLowerCase().trim();
  if (!q) {
    isSearching.value = false;
    searchResults.value = [];
    return;
  }

  isSearching.value = true;

  try {
    const { data } = await client.models.Movie.list({
      filter: {
        or: [
          { title: { contains: q } },
          { keywords: { contains: q } },
        ]
      },
      limit: 20,
    });
    searchResults.value = data ?? [];
  } catch (error) {
    console.error("Erreur recherche :", error);
  }
}*/

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
    <h1>Welcome to Recomodo</h1>
    <div class="Search">
    <!-- <SearchBar @search="searchMovies"/> -->
    <SearchBar/>
    </div>
<div class="content">
<div class="container">
    <RouterLink
       v-for="movie in movies"
        :key="movie.movieId"
        :to=" { name: 'details', params: { id: movie.movieId } }"
         
        class="movie-card"
    >
        <img
            :src="'https://image.tmdb.org/t/p/w200' + movie.posterPath"
           
            :alt="movie.title"
            @error="e => e.target.src = '/defaultPoster.webp'"
       />
        <div class="movie-info">
             <p class="movie-title">{{ movie.title }}</p>
             <p class="movie-meta">★ {{ movie.voteAverage }}</p>
        </div>
    </RouterLink>
</div>

<div class="pagination-wrapper">
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

.search{
    display: flex;
    align-self: flex-end;
    position:fixed;
    right:0rem;
}


</style>