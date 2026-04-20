import { type ClientSchema, a, defineData } from "@aws-amplify/backend";//on importe les fonctions nécessaires pour définir le schéma de la base de données et les autorisations d'accès aux données depuis le backend Amplify
import {recommender} from "../functions/recommender/resource";

// On crée le schéma de la base de données
const schema = a.schema({

  // Table des films qui contient les informations de base sur les films importer depuis le dataset
  Movie: a
    .model({
      movieId: a.string().required(),// ID unique du film
      title: a.string().required(),// titre du film
      overview: a.string(),// résumé du film  
      genres: a.integer().array(),// genres du film
      keywords: a.string(),// mots-clés associés au film, séparés par des virgules
      releaseDate: a.string(),//date de sortie du film, au format "YYYY-MM-DD"
      voteAverage: a.float(), //note moyenne du film, entre 0 et 10
      voteCount: a.integer(),// nombre de votes du film
      director: a.string(),//depuis credits.csv
      posterPath: a.string(),// chemin d'accès à l'affiche du film, depuis credits.csv
      runtime: a.integer(),   // durée du film en minutes, depuis credits.csv
      cast: a.string(),// liste des acteurs principaux du film, séparés par des virgules, depuis credits.csv
    })
    .authorization((allow) => [allow.authenticated().to(["read"])]),//les utilisateurs authentifiés peuvent lire les films, mais pas les modifier

  // Table des notes (un utilisateur note un film)
  Rating: a
    .model({
      userId: a.string().required(), // ID de l'utilisateur qui a noté le film
      movieId: a.string().required(),
      rating: a.float().required(),//note donnée par l'utilisateur au film, entre 0 et 10
      //isInitial:a.boolean(),//pour différencier les notes du questionnaire initial ou celle rentrez manuellement(utilisé pour la remise à zéro)
    })

    .authorization((allow) => [allow.owner()]),//Sécurité : chaque utilisateur gère UNIQUEMENT ses propres notes

  // Table de genres 
  Genre: a
    .model({
      genreId: a.integer().required(), // ID unique du genre
      name: a.string().required(), // nom du genre
    })
    .authorization((allow) => [allow.authenticated().to(["read"])]),//les utilisateurs authentifiés peuvent lire les genres, mais pas les modifier
  
  // Table des profils d'utilisateurs qui stocke les informations du profil utilisateur qui ne sont pas gérées par Cognito 
  UserProfile: a
    .model({
      userId: a.string().required(), // ID de l'utilisateur (généré par cognito)
      username: a.string(), // nom de l'utilisateur
      //genres: a.integer().array(),  genres préférés de l'utilisateur
      hasCompleted: a.boolean(), // indique si l'utilisateur a complété son profil
      
    })
    .authorization((allow) => [allow.owner()]),
  
  // Type de retour de la Lambda de recommandation
  RecommendationResponse: a.customType({
    userId: a.string().required(),
    recommendations: a.string().array().required(),
  }),

  // Query AppSync qui appelle la Lambda recommender
  getRecommendations: a
    .query()
    .arguments({
      userId: a.string().required(),
    })
    .returns(a.ref("RecommendationResponse"))
    .authorization((allow) => [allow.authenticated()])
    .handler(a.handler.function(recommender)),
});

export type Schema = ClientSchema<typeof schema>;

export const data = defineData({
  schema,
  authorizationModes: {
    defaultAuthorizationMode: "userPool",
    // API Key is used for a.allow.public() rules
    apiKeyAuthorizationMode: {
      expiresInDays: 30,
    },
  },
});


/*== STEP 2 ===============================================================
Go to your frontend source code. From your client-side code, generate a
Data client to make CRUDL requests to your table. (THIS SNIPPET WILL ONLY
WORK IN THE FRONTEND CODE FILE.)

Using JavaScript or Next.js React Server Components, Middleware, Server 
Actions or Pages Router? Review how to generate Data clients for those use
cases: https://docs.amplify.aws/gen2/build-a-backend/data/connect-to-API/

/*
"use client"
import { generateClient } from "aws-amplify/data";
import type { Schema } from "@/amplify/data/resource";

const client = generateClient<Schema>() // use this Data client for CRUDL requests
*/

/*== STEP 3 ===============================================================
Fetch records from the database and use them in your frontend component.
(THIS SNIPPET WILL ONLY WORK IN THE FRONTEND CODE FILE.)

/* For example, in a React component, you can use this snippet in your
  function's RETURN statement */
// const { data: todos } = await client.models.Todo.list()

// return <ul>{todos.map(todo => <li key={todo.id}>{todo.content}</li>)}</ul>
