import { execSync } from "child_process";
import * as path from "path";
import { fileURLToPath } from "url";

import { defineFunction } from "@aws-amplify/backend";
import { DockerImage,Duration } from "aws-cdk-lib";
import { PolicyStatement } from "aws-cdk-lib/aws-iam";
import { Code, Function, Runtime } from "aws-cdk-lib/aws-lambda";

const functionDir = path.dirname(fileURLToPath(import.meta.url));

export const recommender = defineFunction((scope) => {
  const lambda = new Function(scope, "recommender", {
    //functionName: "recommender",
    runtime: Runtime.PYTHON_3_10,
    handler: "recommender.handler",
    timeout: Duration.seconds(30),
    memorySize: 2048,
    environment: {
      RATINGS_TABLE_NAME: "Rating-ijhwxiff7nbgfe7pbxjat2dtxi-NONE",
      RATINGS_USER_ID_INDEX: "byUserId",
      DATA_BUCKET_NAME: "amplify-d3v79e9tgrgj6d-ma-amplifydataamplifycodege-kdsjbfaiy1u9",
      MOVIES_RECOMMENDATIONS_KEY: "recomodo/movie_recommendations_genre.json",
    },
    code: Code.fromAsset(functionDir, {
      bundling: {
        image: DockerImage.fromRegistry("public.ecr.aws/sam/build-python3.10"),
        local: {
          tryBundle(outputDir: string) {
            execSync(
              `cp ${path.join(functionDir, "recommender.py")} ${outputDir}`,
              { stdio: "inherit" }
            );
            return true;
          },
        },
      },
    }),
  });

  lambda.addToRolePolicy(
    new PolicyStatement({
      actions: ["dynamodb:Query"],
      resources: [
        "arn:aws:dynamodb:eu-west-1:080941085602:table/Rating-pmu5tm5u2vfw5gpeaqtiqqs2be-NONE",
        "arn:aws:dynamodb:eu-west-1:080941085602:table/Rating-pmu5tm5u2vfw5gpeaqtiqqs2be-NONE/index/byUserId",
      ],
    })
  );

  lambda.addToRolePolicy(
    new PolicyStatement({
      actions: ["s3:GetObject"],
      resources: [
        "arn:aws:s3:::amplify-d3v79e9tgrgj6d-ma-amplifydataamplifycodege-kdsjbfaiy1u9/recomodo/movie_recommendations.json",
      ],
    })
  );

  return lambda;
});
