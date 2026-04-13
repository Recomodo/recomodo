import { defineBackend } from '@aws-amplify/backend';
import { auth } from './auth/resource';
import { data } from './data/resource';
import { recommender } from './functions/recommender/resource';

defineBackend({
  auth,
  data,
  recommender,
});
