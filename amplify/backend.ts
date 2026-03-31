import { defineBackend } from '@aws-amplify/backend';
import { defineFunction } from '@aws-amplify/backend'; 
import { auth } from './auth/resource';
import { data } from './data/resource';
import { Stack } from 'aws-cdk-lib';
import { Cors, LambdaIntegration,RestApi } from 'aws-cdk-lib/aws-apigateway';
import { BackupVaultEvents } from 'aws-cdk-lib/aws-backup';
import { get } from 'aws-amplify/api';

//créarion d'une constante qui définit une fonction lambda avec un point d'entrée vers le fichier test.mjs
const test = defineFunction({
  name: 'test',
  entry: './function/test.mjs',
});

const backend = defineBackend({
  auth,
  data,
  test,
});

//création d'une stack pour l'API REST
const apiStack = backend.createStack("api-stack");

//création d'une API REST avec le nom "Test_API" et des options de déploiement
const restApi = new RestApi(apiStack, "RestApi", {
  restApiName: "Test_API",
  deploy: true,
  deployOptions: {
    stageName: "dev",
  },
  defaultCorsPreflightOptions: {
    allowOrigins: Cors.ALL_ORIGINS,
    allowMethods: Cors.ALL_METHODS,
    allowHeaders: Cors.DEFAULT_HEADERS,
  },
});

//intégration de la fonction lambda "test" à l'API REST
const lambdaIntegration = new LambdaIntegration(
  backend.test.resources.lambda
);

//création d'une ressource "date" dans l'API REST et ajout d'une méthode GET qui utilise l'intégration lambda
const dateResource = restApi.root.addResource("date");
dateResource.addMethod("GET", lambdaIntegration);

//ajout d'une sortie personnalisée à l'API REST pour fournir les informations nécessaires à la configuration d'Amplify dans le frontend(amplify_outputs.json)
backend.addOutput({
    custom: {
      API: {
        [restApi.restApiName]: {
          endpoint: restApi.url,
          region : Stack.of(restApi).region,
          apiName: restApi.restApiName,
        },
      },
    },
});
