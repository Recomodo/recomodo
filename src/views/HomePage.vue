<script setup lang="ts">
import SearchBar from '@/components/SearchBar.vue'
import FirstSigninPage from './FirstSigninPage.vue';


/*import { onMounted, ref } from 'vue'
import { getMovies } from '@/services/movies'

const movies = ref<Movie[]>([])

onMounted(async () => {
  const data = await getMovies()
  movies.value = data.listMovies.items
})*/

</script>


<template>
   <div>
      <SearchBar/>
   </div>
   <FirstSigninPage />
   <h1>Home</h1>
</template>