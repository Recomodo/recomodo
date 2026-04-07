<script setup lang="ts">
import { useRouter } from 'vue-router';
const router = useRouter();

const movies=[
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
        movieId: 4,
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
        movieId: 7,
        title: "The Dark Knight",
        voteAverage: 4.2,
        posterPath:"https://m.media-amazon.com/images/I/51EbJjlL8-L._AC_.jpg"
    },
    {
        movieId: 8,
        title: "12 Angry Men",
        voteAverage: 4.2,
        posterPath:"https://m.media-amazon.com/images/I/41VZ27J7J-L._AC_.jpg"

    },
    {
        movieId: 9,
        title: "Schindler's List",
        voteAverage: 4.2,
        posterPath:"https://m.media-amazon.com/images/I/51T8KQYJQ-L._AC_.jpg"
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
        title: "The Godfather",
        voteAverage: 4.2,
        posterPath:"https://m.media-amazon.com/images/I/41+eK8zBwQL._AC_.jpg"
    },
    {
        movieId: 13,
        title: "The Dark Knight",
        voteAverage: 4.2,
        posterPath:"https://m.media-amazon.com/images/I/51EbJjlL8-L._AC_.jpg"
    },
    {
        movieId: 14,
        title: "12 Angry Men",
        voteAverage: 4.2,
        posterPath:"https://m.media-amazon.com/images/I/41VZ27J7J-L._AC_.jpg"

    },
    {
        movieId: 15,
        title: "Schindler's List",
        voteAverage: 4.2,
        posterPath:"https://m.media-amazon.com/images/I/51T8KQYJQ-L._AC_.jpg"
    }
];


function filmDetails(movieId:number): void {
    router.push(`/movie/details/id:${movieId}`);
}
</script>


<template>
<div class="recommendationsContainer">
<div  class="movie"v-for="(movie) in movies" :key="movie.movieId" @click="filmDetails(movie.movieId)">
    <img :src="movie.posterPath" :alt="movie.title">
    <div class="discription">
       <p>{{ movie.title }}</p>
       <p>{{ movie.voteAverage }}</p>
    </div>   

</div>
</div>
</template>

<style scoped>

</style>