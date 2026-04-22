import { defineBackend } from '@aws-amplify/backend';
import { auth } from './auth/resource';
import { data } from './data/resource';
import { recommender } from './functions/recommender/resource';
import { similar } from './functions/similar/resource';
import { updateMovieRating } from './functions/updateMovieRating/resource';

defineBackend({
  auth,
  data,
  recommender,
  similar,
  updateMovieRating,
});
