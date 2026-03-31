import { defineBackend } from '@aws-amplify/backend';
import { defineFunction } from '@aws-amplify/backend'; 
import { auth } from './auth/resource';
import { data } from './data/resource';
import { Stack } from 'aws-cdk-lib';
import { Cors, LambdaIntegration,RestApi } from 'aws-cdk-lib/aws-apigateway';
import { BackupVaultEvents } from 'aws-cdk-lib/aws-backup';
import { get } from 'aws-amplify/api';

const test = defineFunction({
  name: 'test',
  entry: './function/test.mjs',
});

const backend = defineBackend({
  auth,
  data,
  test,
});

const apiStack = backend.createStack("api-stack");

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

const lambdaIntegration = new LambdaIntegration(
  backend.test.resources.lambda
);

const dateResource = restApi.root.addResource("date");
dateResource.addMethod("GET", lambdaIntegration);

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
