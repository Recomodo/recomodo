import { execSync } from "child_process";
import * as path from "path";
import { fileURLToPath } from "url";
 
import { defineFunction } from "@aws-amplify/backend";
import { DockerImage, Duration } from "aws-cdk-lib";
import { PolicyStatement } from "aws-cdk-lib/aws-iam";
import { Code, Function, Runtime } from "aws-cdk-lib/aws-lambda";
 
const functionDir = path.dirname(fileURLToPath(import.meta.url));
 
export const getMovieByGenre = defineFunction((scope) => {
  const lambda = new Function(scope, "getMovieByGenre", {
    functionName: "getMovieByGenre",
    runtime: Runtime.PYTHON_3_10,
    handler: "getMovieByGenre.handler",
    timeout: Duration.seconds(10),
    memorySize: 256,
    environment: {
      MOVIE_TABLE_NAME: "Movie-ijhwxiff7nbgfe7pbxjat2dtxi-NONE",
      MOVIE_MAIN_GENRE_INDEX: "byMainGenre",
    },
    code: Code.fromAsset(functionDir, {
      bundling: {
        image: DockerImage.fromRegistry("public.ecr.aws/sam/build-python3.10"),
        local: {
          tryBundle(outputDir: string) {
            execSync(`cp -r ${path.join(functionDir, "getMovieByGenre.py")} ${outputDir}`, {
              stdio: "inherit",
            });
            return true;
          },
        },
      },
    }),
  });
 
  // Permission de querier la table Movie et le GSI byMainGenre
  lambda.addToRolePolicy(
    new PolicyStatement({
      actions: ["dynamodb:Query"],
      resources: [
        "arn:aws:dynamodb:eu-west-3:080941085602:table/Movie-ijhwxiff7nbgfe7pbxjat2dtxi-NONE",
        "arn:aws:dynamodb:eu-west-3:080941085602:table/Movie-ijhwxiff7nbgfe7pbxjat2dtxi-NONE/index/byMainGenre",
      ],
    })
  );
 
  return lambda;
});
