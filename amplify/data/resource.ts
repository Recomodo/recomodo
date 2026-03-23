import { type ClientSchema, a, defineData } from "@aws-amplify/backend";//on importe les fonctions nécessaires pour définir le schéma de la base de données et les autorisations d'accès aux données depuis le backend Amplify

// On crée le schéma de la base de données
const schema = a.schema({

  // Table des films qui contient les informations de base sur les films importer depuis le dataset
  Movie: a
    .model({
      movieId: a.string().required(),// ID unique du film
      title: a.string().required(),// titre du film
      overview: a.string(),// résumé du film  
      genres: a.string(),// genres du film, séparés par des virgules
      releaseDate: a.string(),//date de sortie du film, au format "YYYY-MM-DD"
      voteAverage: a.float(),// note moyenne du film, entre 0 et 10
      voteCount: a.integer(),// nombre de votes du film
      director: a.string(),//depuis credits.csv
      posterPath: a.string(),// chemin d'accès à l'affiche du film, depuis credits.csv
    })
    .authorization((allow) => [allow.authenticated().to(["read"])]),//les utilisateurs authentifiés peuvent lire les films, mais pas les modifier

  // Table des notes (un utilisateur note un film)
  Rating: a
    .model({
      userId: a.string().required(), // ID de l'utilisateur qui a noté le film
      movieId: a.string().required(),
      rating: a.float().required(),//note donnée par l'utilisateur au film, entre 0.5 et 5.0
      isInitial:a.boolean(),//pour différencier les notes du questionnaire initial ou celle rentrez manuellement(utilisé pour la remise à zéro)
      createdAt: a.string(),//date de création de la note, pour pouvoir trier les notes d'un film par date et afficher les plus récentes en premier
      updatedAt: a.string(),//date de dernière mise à jour de la note, pour pouvoir trier les notes d'un film par date et afficher les plus récentes en premier
    })

    .authorization((allow) => [allow.owner()]),//Sécurité : chaque utilisateur gère UNIQUEMENT ses propres notes

  // Table des préférences  qui contient les préférences des utilisateurs
  Preference: a
    .model({
      userId: a.string().required(), // ID de l'utilisateur généré automatiquement à partir du pool d'utilisateurs Cognito
      genres: a.string(), // genre préféré de l'utilisateur
      hasCompleted: a.boolean(), // indique si l'utilisateur a complété le questionnaire de préférences
      createdAt: a.string(),//date de création de la préférence, pour pouvoir trier les préférences d'un utilisateur par date et afficher les plus récentes en premier
     /* updatedAt: a.string().required(),//date de dernière mise à jour de la préférence, pour pouvoir trier les préférences d'un utilisateur par date et afficher les plus récentes en premier*/
    })
    .authorization((allow) => [allow.owner()]),//Sécurité : chaque utilisateur gère UNIQUEMENT ses propres préférences

    // Table des profils d'utilisateurs qui stocke les informations du profil utilisateur qui ne sont pas gérées par Cognito 
    UserProfile: a
    .model({
      userId: a.string().required(), // ID de l'utilisateur (généré par cognito)
      username: a.string(), // nom de l'utilisateur
      createdAt: a.string(), //date de création du profil, pour pouvoir trier les profils d'utilisateurs par date et afficher les plus récents en premier
      //updatedAt: a.string().required(),//date de dernière mise à jour du profil, pour pouvoir trier les profils d'utilisateurs par date et afficher les plus récents en premier
    })
    .authorization((allow) => [allow.owner()]),//Sécurité : chaque utilisateur gère UNIQUEMENT son propre profil
});

export type Schema = ClientSchema<typeof schema>;

export const data = defineData({
  schema,
  authorizationModes: {
    defaultAuthorizationMode: "userPool", // Mode d'authentification par défaut:Cognito User Pool, chaque requête doit avoir un token JWT valide généré par Cognito
  },
});
