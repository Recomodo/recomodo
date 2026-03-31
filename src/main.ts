import "./assets/main.css";
import { createApp } from "vue";
import App from "./App.vue";
import { Amplify } from "aws-amplify";
import outputs from "../amplify_outputs.json";
import { get } from "aws-amplify/api";
import { parseAmplifyConfig } from "aws-amplify/utils";

// Configuration d'Amplify avec les informations extraites du fichier amplify_outputs.json
const amplifyConfig = parseAmplifyConfig(outputs);

// Extraction des informations de l'API REST à partir des sorties personnalisées
const customOutputs = outputs as typeof outputs & {
  custom: {
    API: Record<string, { endpoint: string; region: string; apiName: string }>;
  };
};

// Configuration d'Amplify avec les informations extraites du fichier amplify_outputs.json
Amplify.configure({
  ...amplifyConfig,
  API: {
    ...amplifyConfig.API,
    REST: customOutputs.custom.API,
  },
});

createApp(App).mount("#app");

// appel de l'API REST pour récupérer la date actuelle
const restOperation = get({
  apiName: "Test_API",
  path: "date",
});

// Traitement de la réponse de l'API REST
const { body } = await restOperation.response;
const data = await body.json();

// Vérification de la structure de la réponse et affichage de la date
if (data && typeof data === "object" && "date" in data) {
  console.log(data.date);
} else {
  console.error("Réponse inattendue :", data);
}