<script setup lang="ts">
import '@/assets/CssDetailsPage.css';
import '@/assets/CssNotation.css';
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
    return `https://image.tmdb.org/t/p/w200${path}`;
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

<template>
  <div  v-if="movie" class="movie-details-page">
    <!-- Bouton retour -->
    <button @click="goBack" class="back-button">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M19 12H5M12 19l-7-7 7-7"/>
      </svg>
      Back
    </button>

   <div class="movie-page">
   <div class="movie-section" >

    <!-- Contenu principal -->
    <div class="movie-content">
      <!-- Poster -->
      <div class="poster-section">
        <div class="poster-wrapper">
          <img
            :src="getImageUrl(movie.posterPath)"
            :alt="movie.title"
            class="poster-backdrop"
            aria-hidden="true"
          />
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
        <h1 class="movie-title-details"><strong><em>{{ movie.title }}</em></strong></h1>
        
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