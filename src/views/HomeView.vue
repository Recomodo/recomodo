<script setup lang="ts">
import "@/assets/filmCard.css";
import "@/assets/search.css";
import '@/assets/CssHomeView.css';
import '@/assets/CssPagination.css';
import {ref, onMounted} from 'vue';
import Pagination from '../components/Pagination.vue';
import type { Schema } from "../../amplify/data/resource";
import { generateClient } from 'aws-amplify/api';
import SearchBar from '@/components/SearchBar.vue';
import { handleImageError } from '@/utils/defaultPoster';

const client = generateClient <Schema>();
const movies = ref<Array<Schema['Movie']["type"]>>([]);
const currentPage = ref(1);
const itemsPerPage = 70;
const moviesByPage = ref<Record<number, Array<Schema['Movie']["type"]>>>({});
const nextTokens = ref<Record<number, string | null>>({});
const isLoading= ref(false);
const searchResults=ref<Array<Schema['Movie']["type"]>>([]);
const isSearching=ref(false);

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
});

function handlePageChange(page: number) {
  currentPage.value = page;
  loadMoviesPage(page);
}

//recherche


async function searchMovies(query:string) {
  const q=query.toLowerCase().trim();
    let results:any[]=[];
    let nextToken:string | null=null;
  if(!q){
    isSearching.value=false;
    searchResults.value=[];
    return;
  }
  isSearching.value=true;
  isLoading.value=true;
  try{
do{
    const {data,nextToken:newNextToken}:{data:any[]; nextToken?:string|null;} =await client.models.Movie.list({
      filter:{
        or:[
        {titleLower: {contains:q}},
        {keywords: {contains:q}},
      ]
      },
      limit:2000,
      nextToken,
    });
    results = [...results, ...(data ?? [])];
    nextToken=newNextToken?? null;
    console.log(data);
  }while(nextToken)
searchResults.value=results;
}catch(error){
  console.log("erreur recherche:",error);
}finally{
  isLoading.value=false;
}
}

function getImageUrl(posterPath: any) {
  const path = String(posterPath || '').trim();
  if (!path || path === 'null' || path === 'undefined' || path === '') return '/DEFAULTPOSTERJPG.jpg';
  if (path.startsWith('/')) {
    return `https://image.tmdb.org/t/p/w200${path}`;
  }
  return path;
}

</script>

<template>
<div class="page">
  <div class="haut-page">
    <div>
    <h1>Welcome to Recomodo</h1>
    </div>
    <div class="Search">
    <SearchBar @search="searchMovies"/>
    </div>
  </div>
<div class="content">
  <div v-if="isLoading" class="condition">
    Loading...<font-awesome-icon icon="fa-solid fa-hourglass" style="color: white;" />
  </div>
  <div v-else-if="isSearching && searchResults.length === 0" class="condition-2">
    No such a movie found <font-awesome-icon icon="fa-solid fa-xmark" style="color: brown;" />
  </div>
<div v-else class="container">
    <RouterLink
       v-for="movie in isSearching? searchResults:movies"
        :key="movie.movieId"
        :to=" { name: 'details', params: { id: movie.movieId } }"
         
        class="movie-card"
    >
      <img
        :src="getImageUrl(movie.posterPath)"   
        :alt="movie.title"
        @error="handleImageError"
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