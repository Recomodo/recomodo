<template>
  <!--<p style="color: white;"> id : {{ movie.id }} /movieId : {{ movie.movieId }} </p>-->
  <div  v-if="movie" class="movie-details-page">
    <!-- Background blur avec le poster -->
    <div class="backdrop-container">
      <img 
        :src="getImageUrl(movie.posterPath)" 
        :alt="movie.title"
        class="backdrop-image"
      />
      <div class="backdrop-overlay"></div>
    </div>

    <!-- Bouton retour -->
    <button @click="goBack" class="back-button">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M19 12H5M12 19l-7-7 7-7"/>
      </svg>
      Retour
    </button>

    <!-- Contenu principal -->
    <div class="movie-content">
      <!-- Poster -->
      <div class="poster-section">
        <div class="poster-wrapper">
          <img 
            :src="getImageUrl(movie.posterPath)" 
            :alt="movie.title"
            class="movie-poster"
          />
          <div>
            <h1>Votre note</h1>
            <Notation v-model="userRating" />
            <p class="UserRatingValue">{{ userRating }}/5</p>
          </div>
          <!-- Badge note sur le poster 
          <div class="rating-badge">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
            <span>{{ movie.voteAverage?.toFixed(1) }}</span>
          </div>-->
        </div>
      </div>

      <!-- Infos du film -->
      <div class="info-section">
        <!-- Titre -->
        <h1 class="movie-title">{{ movie.title }}</h1>
        
        <!-- Meta infos: annee, duree -->
        <div class="meta-row">
          <span class="meta-item">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
            {{ getYear(movie.releaseDate) }}
          </span>
          <span class="meta-divider"></span>
          <span class="meta-item">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            {{ movie.runtime || '2h 15min' }}
          </span>
        </div>

        <!-- Genres -->
        <div class="genres-row">
          <span 
            v-for="(genre, index) in movie.genres" 
            :key="index" 
            class="genre-tag"
          >
            {{ genre }}
          </span>
        </div>

        <!-- Synopsis -->
        <div class="synopsis-section">
          <h2 class="section-title">Résumé</h2>
          <p class="synopsis-text">{{ movie.overview }}</p>
        </div>

        <!-- Realisateur -->
        <div v-if="movie.director" class="director-section">
          <h2 class="section-title">Realisateur</h2>
          <p class="director-name">{{ movie.director }}</p>
        </div>

        <!-- Stats en bas -->
        <div class="stats-row">
          <div class="stat-card">
            <div clconst movie = ref(history.state.movie) ass="stat-icon rating-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ movie.voteAverage?.toFixed(1) }}/10</span>
              <span class="stat-label">Note moyenne</span>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon votes-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ formatNumber(movie.voteCount) }}</span>
              <span class="stat-label">Votes</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    

  </div>
</template>

<script setup>
import Notation from '@/components/Notation.vue';
import { onMounted , ref } from 'vue';
import { generateClient } from 'aws-amplify/api';
import { useRoute , useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const client = generateClient ();

const movie = ref(undefined);
const movieId = route.params.id;

const getMovieQuery = `
  query GetMovie($id: ID!) {
    getMovie(id: $id) {
      
      movieId
      title
      overview
      genres
      posterPath
      releaseDate
      voteAverage
      voteCount
      director
    }
  }
`;

onMounted(async () => {
  console.log("ROUTE PARAMS: ", route.params);
  //const movieId = route.params.id;
  try {
    const result = await client.graphql({
      query: getMovieQuery,
      variables: { id: movieId }
    });
    console.log("RESULT API: ", result);
    movie.value = result?.data?.getMovie || null;
  } catch (error) {
    console.error("Error fetching movie details:", error);
    movie.value = null;
  }
});



// Donnees statiques en attendant l'API
/*const movie = ref({
  id: 1,
  movieId: 862,
  title: "Toy Story",
  overview: "Woody, un cowboy en peluche, est le jouet prefere d'Andy, un petit garcon. Mais l'arrivee de Buzz l'Eclair, un ranger de l'espace, va bouleverser sa vie. Entre jalousie et aventures, Woody va decouvrir le vrai sens de l'amitie.",
  genres: ["Animation", "Aventure", "Comedie", "Familial"],
  posterPath: "/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg",
  releaseDate: "1995-10-30",
  voteAverage: 7.9,
  voteCount: 17849,
  director: "John Lasseter",
  runtime: "1h 21min"
});
*/

function goBack() {
  router.back();
}

function getImageUrl(posterPath) {
  if (!posterPath) return '/placeholder-movie.jpg';
  if (posterPath.startsWith('/')) {
    return `https://image.tmdb.org/t/p/w500${posterPath}`;
  }
  return posterPath;
}

function getYear(dateString) {
  if (!dateString) return '';
  return new Date(dateString).getFullYear();
}

function formatNumber(num) {
  if (!num) return '0';
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
}
</script>

<style >

html, body{
  margin: 0;
  padding: 0;
  height: 100%;
  min-height: 100%;
  background: #000;
}

.movie-details-page {
  min-height: 100vh;
  margin: 0;
  padding: 0;
  /*background: #0a0a0f;*/
  color: #ffffff;
  position: relative;
  overflow-x: hidden;
  width:100%;
  flex-wrap: wrap;
  background-image: url("https://image.tmdb.org/t/p/w500/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg") , linear-gradient(to bottom, rgba(68, 68, 68, 0.6), rgb(39, 39, 39)) ;
  background-blend-mode: darken;
  background-size: cover;
  
  
}

/* Background blur */
.backdrop-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100%;
  overflow: hidden;
  z-index: 0;
  width: 100%;
}

.backdrop-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: blur(40px);
  transform: scale(1.1);
  display: block;
  transform-origin: top;
  opacity: 0;
}

/*.backdrop-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  background: linear-gradient(
    to bottom,
    rgba(10, 10, 15, 0.3) 0%,
    rgba(10, 10, 15, 0.8) 50%,
    rgba(10, 10, 15, 1) 100%
  );
}*/


/* Bouton retour */
.back-button {
  position: relative;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 1.5rem 0 0 1.5rem;
  padding: 0.75rem 1.25rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 50px;
  color: #ffffff;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateX(-5px);
}

/* Contenu principal */
.movie-content {
  position: relative;
  z-index: 5;
  display: flex;
  gap: 3rem;
  max-width: 100%;
  width: 1200px;
  margin: 0 auto;
  padding: 0 2rem 4rem;
  box-sizing: border-box;
  flex-wrap: wrap;
}

/* Section poster */
.poster-section {
  flex-shrink: 0;
  margin-top: 50px;
}

.poster-wrapper {
  position: relative;
  width: 320px;
}

.movie-poster {
  width: 100%;
  border-radius: 16px;
  box-shadow: 
    0 25px 50px -12px rgba(0, 0, 0, 0.5),
    0 0 0 1px rgba(255, 255, 255, 0.1);
}

.rating-badge {
  position: absolute;
  top: -12px;
  right: 0;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem 1rem;
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  border-radius: 50px;
  color: #000;
  font-weight: 700;
  font-size: 1rem;
  box-shadow: 0 4px 15px rgba(251, 191, 36, 0.4);
}

/* Section infos */
.info-section {
  flex: 1;
  padding-top: 1rem;
}

.movie-title {
  font-size: 3rem;
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 1.25rem;
  text-wrap: balance;
}

/* Meta row */
.meta-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #a1a1aa;
  font-size: 1rem;
}

.meta-divider {
  width: 4px;
  height: 4px;
  background: #52525b;
  border-radius: 50%;
}

/* Genres */
.genres-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.genre-tag {
  padding: 0.5rem 1rem;
  background: rgba(139, 92, 246, 0.15);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 50px;
  color: #a78bfa;
  font-size: 0.875rem;
  font-weight: 500;
}

/* Synopsis */
.synopsis-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  /*color: #71717a;*/
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.75rem;
}

.synopsis-text {
  font-size: 1.1rem;
  line-height: 1.8;
  color: #d4d4d8;
}

/* Realisateur */
.director-section {
  margin-bottom: 2.5rem;
}

.director-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: #ffffff;
}

/* Stats row */
.stats-row {
  display: flex;
  gap: 1.5rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  min-width: 0;
  flex:1;
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
}

.rating-icon {
  background: rgba(251, 191, 36, 0.15);
  color: #fbbf24;
}

.votes-icon {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #ffffff;
}

.stat-label {
  font-size: 0.875rem;
  color: #71717a;
}

/* Responsive */
@media (max-width: 900px) {
  .movie-content {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .poster-wrapper {
    width: 280px;
  }

  .movie-title {
    font-size: 2.25rem;
  }

  .meta-row,
  .genres-row,
  .stats-row {
    justify-content: center;
  }

  .synopsis-text {
    text-align: left;
  }
}

@media (max-width: 600px) {
  .movie-content {
    padding: 0 1rem 3rem;
  }

  .poster-wrapper {
    width: 220px;
  }

  .movie-title {
    font-size: 1.75rem;
  }

  .stats-row {
    flex-direction: column;
  }

  .stat-card {
    width: 100%;
    justify-content: center;
  }
}
</style>


