<script setup lang="ts">
import {ref , computed , onMounted} from 'vue';
import Pagination from '../components/Pagination.vue';

import { generateClient } from 'aws-amplify/api';

const listMoviesQuery = `
  query ListMovies {
    listMovies {
      items {
        movieId
        title
        voteAverage
        posterPath
      }
    }
  }
`;

const client = generateClient();

const movies = ref([]);

const currentPage = ref(1);
const itemsPerPage = 28;

onMounted(async () => {
    try {
        const result = await client.graphql({
                query: listMoviesQuery
        });

        console.log("RESULT API: ", result);
        
        const items = result?.data?.listMovies?.items;


        movies.value = Array.isArray(items) ? items : [];

    } catch (error) {
        console.error("Error fetching movies:", error);
        movies.value = [];
    }
});
/*const movies=[
    {
        movieId: 1,
        title: "The Godfather",
        voteAverage: 4.2,
        posterPath:"https://m.media-amazon.com/images/I/41+eK8zBwQL._AC_.jpg"
    },
    {
        movieId: 2,
        title: "The Dark Knight",
        voteAverage: 4.2,
        posterPath:"https://m.media-amazon.com/images/I/51EbJjlL8-L._AC_.jpg"
    },
    {
        movieId: 3,
        title: "12 Angry Men",
        voteAverage: 4.2,
        posterPath:"https://m.media-amazon.com/images/I/41VZ27J7J-L._AC_.jpg"

    },
    {
        movieId: 5,
        title: "Schindler's List",
        voteAverage: 4.2,
        posterPath:"https://m.media-amazon.com/images/I/51T8KQYJQ-L._AC_.jpg"
    },
    {
        movieId: 6,
        title: "The Godfather",
        voteAverage: 4.2,
        posterPath:"https://m.media-amazon.com/images/I/41+eK8zBwQL._AC_.jpg"
    },
    {
        movieId: 4,
        title: "The Dark Knight",
        voteAverage: 4.2,
        posterPath:"https://m.media-amazon.com/images/I/51EbJjlL8-L._AC_.jpg"
    },
    {
        movieId: 7,
        title: "12 Angry Men",
        voteAverage: 4.2,
        posterPath:"https://m.media-amazon.com/images/I/41VZ27J7J-L._AC_.jpg"

    },
    {
        movieId: 8,
        title: "Schindler's List",
        voteAverage: 4.2,
        posterPath:"https://m.media-amazon.com/images/I/51T8KQYJQ-L._AC_.jpg"
    },
    {
        movieId: 9,
        title: "Toy Story",
        voteAverage: 4.2,
        posterPath:"https://image.tmdb.org/t/p/w500"
    },
    {
        movieId: 10,
        title: "12 Angry Men",
        voteAverage: 4.2,
        posterPath:"https://m.media-amazon.com/images/I/41VZ27J7J-L._AC_.jpg"

    },
    {
        movieId: 11,
        title: "Schindler's List",
        voteAverage: 4.2,
        posterPath:"https://m.media-amazon.com/images/I/51T8KQYJQ-L._AC_.jpg"
    },
    {
        movieId: 12,
        title: "Toy Story",
        voteAverage: 4.2,
        posterPath:"https://image.tmdb.org/t/p/w500"
    },
        {
        movieId: 13,
        title: "Schindler's List",
        voteAverage: 4.2,
        posterPath:"https://m.media-amazon.com/images/I/51T8KQYJQ-L._AC_.jpg"
    },
    {
        movieId: 14,
        title: "Toy Story",
        voteAverage: 4.2,
        posterPath:"https://image.tmdb.org/t/p/w500"
    },
    {
        movieId: 15,
        title: "12 Angry Men",
        voteAverage: 4.2,
        posterPath:"https://m.media-amazon.com/images/I/41VZ27J7J-L._AC_.jpg"

    },
    {
        movieId: 16,
        title: "Schindler's List",
        voteAverage: 4.2,
        posterPath:"https://m.media-amazon.com/images/I/51T8KQYJQ-L._AC_.jpg"
    },
    {
        movieId: 17,
        title: "Toy Story",
        voteAverage: 4.2,
        posterPath:"https://image.tmdb.org/t/p/w500"
    },
    {
        movieId: 18,
        title: "Toy Story",
        voteAverage: 4.2,
        posterPath:"https://image.tmdb.org/t/p/w500"
    }
];
*/

const totalPages = computed(() => Math.ceil(movies.value?.length || 0 / itemsPerPage));

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
        <!-- <p style="color: white;">{{ movie.posterPath }}</p> -->
        <!--<div  class="movie"v-for="(movie) in movies" :key="movie.movieId">-->
        <!--<img :src="movie.posterPath" :alt="movie.title">-->
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
    display: flex;
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
}
.movie{
    height: 200px;
    width:150px;
    background-color:rgba(226, 163, 255, 0.4);
    border-radius: 15px;
    padding-top: 15px;
    margin-top: 15px;
}
/*.container{
    display: flex;
    flex-wrap: wrap;
    /*justify-content:flex-start;*/
   /* justify-content: center;
    gap: 2rem;
   padding: 2rem 2rem 2rem 2rem;
   
   
}
*/
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
}


</style>