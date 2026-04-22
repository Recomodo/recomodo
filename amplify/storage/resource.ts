import { defineStorage } from '@aws-amplify/backend';
import {recommender} from "../functions/recommender/resource";
import {similar} from "../functions/similar/resource";

export const storage = defineStorage({
  name: 'recomodoStorage',
  access: (allow) => ({
    'recomodo/*': [
        allow.resource(recommender).to(['read']),
        allow.resource(similar).to(['read']),
    ]
  }),
});
