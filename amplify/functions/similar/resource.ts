import { execSync } from "child_process";
import * as path from "path";
import { fileURLToPath } from "url";
 
import { defineFunction } from "@aws-amplify/backend";
import { DockerImage, Duration } from "aws-cdk-lib";
import { PolicyStatement } from "aws-cdk-lib/aws-iam";
import { Code, Function, Runtime } from "aws-cdk-lib/aws-lambda";
 
const functionDir = path.dirname(fileURLToPath(import.meta.url));
 
export const similar = defineFunction((scope) => {
  const lambda = new Function(scope, "similar", {
    functionName: "similar",
    runtime: Runtime.PYTHON_3_10,
    handler: "similar.handler",
    timeout: Duration.seconds(10), // plus court que le recommender car c'est juste un .get() sur le JSON
    memorySize: 512, // moins de mémoire que le recommender car pas de calcul lourd
    environment: {
      DATA_BUCKET_NAME: "amplify-d3v79e9tgrgj6d-ma-amplifydataamplifycodege-kdsjbfaiy1u9",
      MOVIES_RECOMMENDATIONS_KEY: "recomodo/movie_recommendations_genre.json",
    },
    code: Code.fromAsset(functionDir, {
      bundling: {
        image: DockerImage.fromRegistry("public.ecr.aws/sam/build-python3.10"),
        local: {
          tryBundle(outputDir: string) {
            execSync(
              `cp ${path.join(functionDir, "similar.py")} ${outputDir}`,
              { stdio: "inherit" }
            );
            return true;
          },
        },
      },
    }),
  });
 
  // Permission de lire le fichier JSON des recommandations dans S3
  lambda.addToRolePolicy(
    new PolicyStatement({
      actions: ["s3:GetObject"],
      resources: [
        "arn:aws:s3:::amplify-d3v79e9tgrgj6d-ma-amplifydataamplifycodege-kdsjbfaiy1u9/recomodo/movie_recommendations_genre.json",
      ],
    })
  );
 
  return lambda;
});