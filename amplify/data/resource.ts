import { type ClientSchema, a, defineData } from "@aws-amplify/backend";//on importe les fonctions nécessaires pour définir le schéma de la base de données et les autorisations d'accès aux données depuis le backend Amplify
import {recommender} from "../functions/recommender/resource";
import {similar} from "../functions/similar/resource";
import { updateMovieRating } from "../functions/updateMovieRating/resource";

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

  // Query AppSync qui appelle la Lambda similar
  SimilarMoviesResponse: a.customType({
    movieId: a.string().required(),
    similar: a.string().array().required(),
  }),
  getSimilarMovies: a
    .query()
    .arguments({
      movieId: a.string().required(),
    })
    .returns(a.ref("SimilarMoviesResponse"))
    .authorization((allow) => [allow.authenticated()])
    .handler(a.handler.function(similar)),

  updateMovieRatingResponse: a.customType({
    success: a.boolean().required(),
    message: a.string(),
  }),
  // Mutation AppSync qui appelle la Lambda updateMovieRating
  //  pour enregistrer ou mettre à jour une note de film par un utilisateur
  updateUserRating: a
    .mutation()
    .arguments({
      userId: a.string().required(),  // qui note
      movieId: a.string().required(), // quel film
      rating: a.float().required(),   // combien (ex: 8.5)
    })
    .returns(a.ref("updateMovieRatingResponse"))
    .authorization((allow) => [allow.authenticated()])
    .handler(a.handler.function(updateMovieRating)),

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