<template>
  <div  v-if="movie" class="movie-details-page">
   <div class="movie-page">
   <div class="movie-section" >
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
      Back
    </button>

    <!-- Contenu principal -->
    <div class="movie-content">
      <!-- Poster -->
      <div class="poster-section">
        <div class="poster-wrapper">
          <img 
            :src="getImageUrl(movie.posterPath)" 
            :alt="movie.title"
            @error="handleImageError"
            class="movie-poster"
          />
          <div class="notation_number">
            <Notation :notation="userRating" @rate = "handleRating" :class=" { disabled : hasVoted}"/>
            <p class="UserRatingValue">{{ userRating }}</p>
          </div>
        </div>
      </div>

      <!-- Infos du film -->
      <div class="info-section">
        <!-- Titre -->
        <h1 class="movie-title"><strong><em>{{ movie.title }}</em></strong></h1>
        
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
            {{ formatRuntime(movie.runtime) }}
          </span>
        </div>

        <!-- Genres -->
        <div class="genres" v-if="movie.genres">
          <div class="genre" v-for="genreId in movie.genres" :key="genreId">
              {{ getGenres(genreId) }}
          </div>
        </div>

        <!-- Synopsis -->
        <div class="synopsis-section">
          <h2 class="section-title"><strong><em>Overview</em></strong></h2>
          <p class="synopsis-text">{{ movie.overview }}</p>
        </div>

        <!-- Realisateur -->
      <div class="personne-section">
        <div v-if="cast && cast.length > 0" class="director-section">
          <h2 class="section-title"><strong><em>Cast</em></strong></h2>
          <p class="cast-names">{{ cast }}</p>
        </div>
        <div v-if="movie.director" class="director-section">
          <h2 class="section-title"><strong><em>Director</em></strong></h2>
          <p class="director-name">{{ movie.director }}</p>
        </div>
      </div>

        <!-- Stats en bas -->
        <div class="stats-row">
          <div class="stat-card">
            <div const movie = ref(history.state.movie) class="stat-icon rating-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ movie.voteAverage?.toFixed(1) }}/10</span>
              <span class="stat-label">Average Rating</span>
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
   </div>
   
    <div v-if="recommandationsSimilar.length" class="recommandationSimilar-section">
        <h2 class="sectionRec-title"><strong><em>You might also like</em></strong></h2>
        <div class="recommandationSimilar-row">
          <RouterLink 
            v-for="rec in recommandationsSimilar" 
            :key="rec.id" 
            :to="{ name: 'details' , params : { id: rec.movieId}}"
            class="rec-card"
            
          >
            <img 
              :src="getImageUrl(rec.posterPath)" 
              :alt="rec.title"
              @error="handleImageError"
              class="rec-poster"
            />
            <div class="rec-info">
              <p class="rec-title">{{ rec.title }}</p>
              <p class="rec-meta">★ {{ rec.voteAverage?.toFixed(1) }}</p>
            </div>
          </RouterLink>
        </div>
      </div>
  </div>
</template>

<script setup lang="ts">
import type { Schema } from "../../amplify/data/resource";
import Notation from '@/components/Notation.vue';
import { onMounted , ref , watch , nextTick} from 'vue';
import { generateClient } from 'aws-amplify/api';
import { useRoute , useRouter } from 'vue-router';
import { getCurrentUser } from "aws-amplify/auth";
import path from "path";

const genres = ref<Array<Schema['Genre']["type"]>>([]);
const route = useRoute();
const router = useRouter();
const client = generateClient <Schema>();
const userRating = ref(0);
const movie = ref<any>();
const hasVoted = ref(false);
const isSubmitting = ref(false);
const currentUserId = ref<string | null>(null);
const cast = ref<string>('');
const recommandationsSimilar = ref<any[]>([]);

onMounted(async () => {
  console.log("ROUTE PARAMS: ", route.params);
  try {
    const {data} = await client.models.Movie.get({
      id: route.params.id as string});

    if (!data) {
      movie.value = null;
      cast.value = '';
      recommandationsSimilar.value = [];
    return;
    }
    movie.value = data;
    cast.value = data.cast ?? '';

    await loadSimilarMovies(data.id);

    console.log("UUID DYNAMODB", data?.id, "| movieId entier=",data?.movieId);

    console.log("UUID DYNAMODB", data?.id, "| movieId entier=",data?.movieId);

    console.log("RESULT API court: ", data);
  } catch (error) {
    console.error("Error fetching movie details:", error);
   
  }
});

onMounted(async () => {
    try {
        const { data, errors } = await client.models.Genre.list();
        genres.value = data ?? [];
    } catch (error) {
        console.error("Error fetching genres:", error);
        genres.value = [];
    }
});

onMounted(async () => {
  try {
    const user = await getCurrentUser();
    console.log("user",user);
    currentUserId.value = user.userId; // ou user.attributes.sub selon votre configuration Cognito
    const { data } = await client.models.Rating.list({
      filter: {
        movieId: { eq: route.params.id as string },
        userId: { eq: currentUserId.value ?? undefined } // Remplacez par l'ID de l'utilisateur connecté
      }
    });
    if (data.length > 0) {
      hasVoted.value = true;
      userRating.value = data[0].rating;
    }
  } catch (error) {
    console.error("Error fetching user rating:", error);
  }
});

watch(() => route.params.id, async (newId) => {
  if (!newId) return;
  try {
    const { data } = await client.models.Movie.get ({
      id : newId as string
    });

    if (!data) {
      movie.value = null;
      cast.value = '';
      recommandationsSimilar.value = [];
      userRating.value = 0;
      hasVoted.value = false;
      return;
    }
    movie.value =  data;
    cast.value = data.cast ?? '';

    await loadSimilarMovies(data.id);

    const { data: ratings } = await client.models.Rating.list ({
      filter : {
        movieId : { eq: newId as string},
        userId: { eq: currentUserId.value ?? undefined }
      }
    });
    if (ratings.length>0) {
      hasVoted.value=true;
      userRating.value=ratings[0].rating;
    }
    else {
      userRating.value=0;
      hasVoted.value=false;
    }
  }catch(error) {
    console.error("Error fetching movie details",error);
  }
});

function goBack() {
  router.back();
}

function getImageUrl(posterPath: any) {
  const path = String(posterPath || '').trim();
  if (!posterPath || posterPath === 'null' || posterPath === 'undefined' || posterPath === '') return '/defaultPoster.webp';
  if (posterPath.startsWith('/')) {
    return `https://image.tmdb.org/t/p/w500${path}`;
  }
  return posterPath;
}

function getYear(dateString: any) {
  if (!dateString) return '';
  return new Date(dateString).getFullYear();
}

function formatNumber(num: any) {
  if (!num) return '0';
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
}
function formatRuntime(minutes: any) {
  if (!minutes) return '';
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return `${h}h ${m.toString().padStart(2, '0')}min`;

}

function getGenres(id:number|null|undefined){
  if(!id){
      return "";
  }else{
      const genre = genres.value.find(g => Number(g.genreId) === Number(id));
      return genre? genre.name : "";
  }
}

function handleImageError(event: Event) {
  const target = event.target as HTMLImageElement | null;
  if (target) {
    target.src = '/defaultPoster.webp';
  }
}

async function handleRating(rating: number) {
  if (!movie.value || hasVoted.value || isSubmitting.value) return;
  if (!currentUserId.value) return;

  isSubmitting.value = true;

  try {
    const { data: existingRatings } = await client.models.Rating.list({
      filter: {
        movieId: { eq: movie.value.movieId as string},
        userId: { eq: currentUserId.value}
      }
    });

    if (existingRatings.length  > 0) {
      await client.models.Rating.update({
        id: existingRatings[0].id,
        rating
      });
    }else{
      await client.mutations.updateUserRating({
      movieId: movie.value.movieId,
      userId: currentUserId.value,
      rating
    });
    }

    console.log("movieId envoyé",movie.value.id);
    console.log("userId", currentUserId.value);
    console.log("rating", rating);

    const { data: updatedMovie } = await client.models.Movie.get({ 
      id: movie.value.id 
    });
    
    if (updatedMovie) {
      movie.value = updatedMovie;
    }

    userRating.value = rating;
    hasVoted.value   = true;

  } catch (error) {
    console.error("Error submitting rating:", error);
  } finally {
    isSubmitting.value = false;
  }
}

async function loadSimilarMovies(movieId: string) {
    try {
      const result = await client.queries.getSimilarMovies({
        movieId: movieId
      });
      console.log("IDS", result.data?.similar);
      const ids = (result.data?.similar ?? []).filter(
        (id): id is string => id !== null
      );

      const movies = await Promise.all (
        ids.map(async (id: string) => {
            const { data } = await client.models.Movie.get({ id });
            return data;
          })
      );
      recommandationsSimilar.value = movies
      .filter(
        (m): m is NonNullable<(typeof movies)[number]> => m !== null
      )
      .filter((m)=>m.id !== movieId);
      console.log(recommandationsSimilar.value[0]);
    } catch (error) {
      console.error("Error fetching similar movies:", error);
      recommandationsSimilar.value = [];
}
}

function goToMovie(id: string){
  console.log("goToMovie id :",id);
  router.push({name: 'details',params: {id}});
}

</script>
<style scoped>
html, body{
  margin: 0;
  padding: 0;
  height: 100%;
  min-height: 100%;
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
  background-size: cover;
  display: block;
}

.movie-page {
  position: relative;
  width:100%;
  max-width: 1200px;
  margin: 0 auto;
  overflow-x: hidden;
}

.movie-section {
  position: relative;
  overflow: hidden;
  width: 100%;
  z-index: 1;
}

/* Background blur */
.backdrop-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 500px;
  z-index: 0;
  width: 100%;
}

.backdrop-image {
  width: 100%;
  height: 100%;
  position: absolute;
  object-fit: contain;
  object-position: left bottom;
  filter: blur(10px) brightness(0.5);
  transform: scale(1.1) translateX(7.5%) translateY(31%);
  display: block;
  transform-origin: top;
  opacity:0.8;
  top: 0;
  left: 0;
}

.backdrop-image-bg {
  position:absolute;
  width: 100%;
  height:100%;
  object-fit: cover;
  filter: blur(10px) brightness(0.5);
  transform: scale(1.1);
}

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
  padding:  2rem;
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

.notation_number {
  display: flex;
  align-items: baseline;
  gap: 11px;
  transform: translateX(-50px);
}

.UserRatingValue {
  font-size: 1.5rem;
  font-weight: 600;
  color: #ffffff;
  margin: 0;
  line-height: 0;
  transform: translateY(3px);
}

.rating-badge {
  position: absolute;
  top: -12px;
  right: 0;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem 1rem;
  background: linear-gradient(135deg, rgb(222, 106, 222) 0%, rgb(222, 106, 222) 100%);
  border-radius: 50px;
  color: rgb(222, 106, 222);
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
  color: #ffffff;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
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
.genres {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.genre {
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
  margin: 0;
  color: #a1a1aa;
}

.synopsis-text {
  font-size: 1.1rem;
  line-height: 1.8;
  color: #e4e4e7;
  max-width: 800px;
}

/* Realisateur */
.director-section {
  margin-bottom: 2.5rem;
  display: flex;
  flex-direction: column;
  min-width: 150px;
  gap: 0.5rem;
}

.director-name, .cast-names {
  font-size: 1.25rem;
  font-weight: 600;
  color: #f4f4f5;
  line-height: 1.4;
  margin: 0;
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
  color:#f5c518;
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

  .personne-section{
  flex-direction: column;
  gap: 1.5rem;
  }
}

.disabled {
  pointer-events: none;
  opacity: 0.5; 
}

.personne-section {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  gap: 3rem;
  margin-bottom: 2.5rem;
  margin-top: 2rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.movie-section,
.recommandationSimilar-section {
  background: #15001d;
  padding: 3rem 2rem;
}

.recommandationSimilar-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, 150px);
  gap: 1.5rem;
  justify-content: left;
  margin-top: -40px;
}

.rec-card {
  text-decoration: none;
  width: 150px;
  height: 265px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: transform 0.2 ease;
  box-shadow: 0 4px 20px rgba(114, 55, 136, 0.6);
  border: 1px solid #7a2a8a;
  border-radius: 6px;
}

.rec-card:hover {
  transform: scale(1.04);
}

.rec-poster {
  width: 150px;
  height: 220px;
  object-fit: cover;
  border-radius: 0;
  display: block;
}

.rec-info {
  background: #3d0943;
  padding: 4px 8px;
  height: 45px;
  box-sizing: border-box;
  flex-shrink: 0;
  width: 100%;
}

.rec-title {
  font-size: 12px;
  margin-top: 5px;
  color: #fff;
  text-align: left;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rec-meta {
  margin-top: -12px;
  font-size: 11px;
  color: #f5c518;
}

.sectionRec-title {
  padding: 0 0 2rem 0;
  margin-top: -35px;
  color: white;
  font-size: 1.5rem;
}
</style>
