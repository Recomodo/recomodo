import "./assets/main.css";
import { createApp } from "vue";
import App from "./App.vue";
import { Amplify } from "aws-amplify";
import outputs from "../amplify_outputs.json";
import { get } from "aws-amplify/api";
import { parseAmplifyConfig } from "aws-amplify/utils";

const amplifyConfig = parseAmplifyConfig(outputs);

const customOutputs = outputs as typeof outputs & {
  custom: {
    API: Record<string, { endpoint: string; region: string; apiName: string }>;
  };
};

Amplify.configure({
  ...amplifyConfig,
  API: {
    ...amplifyConfig.API,
    REST: customOutputs.custom.API,
  },
});

createApp(App).mount("#app");

const restOperation = get({
  apiName: "Test_API",
  path: "date",
});

const { body } = await restOperation.response;
const data = await body.json();

if (data && typeof data === "object" && "date" in data) {
  console.log(data.date);
} else {
  console.error("Réponse inattendue :", data);
}