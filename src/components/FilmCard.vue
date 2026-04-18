

<script setup lang="ts">
import { generateClient } from 'aws-amplify/data';
import type {Schema} from "../../amplify/data/resource";
import {data} from "../../amplify/data/resource";
import{ref} from 'vue'


const client = generateClient<Schema>();

// Now you should be able to make CRUDL operations with the
// Data client
const bitch = ref<Array<Schema['Movie']["type"]>>([]);
const fetchMovies = async () => {
  const { data: movies, errors } = await client.models.Movie.list();
};
bitch.value=data;
console.log(data);

</script>