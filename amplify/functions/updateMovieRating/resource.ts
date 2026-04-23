import { execSync } from "child_process";
import * as path from "path";
import { fileURLToPath } from "url";

import { defineFunction } from "@aws-amplify/backend";
import { DockerImage, Duration } from "aws-cdk-lib";
import { PolicyStatement } from "aws-cdk-lib/aws-iam";
import { Code, Function, Runtime } from "aws-cdk-lib/aws-lambda";

const functionDir = path.dirname(fileURLToPath(import.meta.url)); 

export const updateMovieRating = defineFunction((scope) => {
  const lambda = new Function(scope, "updateMovieRating", {
    runtime: Runtime.PYTHON_3_10,
    handler: "updateMovieRating.handler",
    timeout: Duration.seconds(15),
    memorySize: 256,
    environment: {
      RATING_TABLE_NAME: "Rating-ijhwxiff7nbgfe7pbxjat2dtxi-NONE",
      RATING_USER_ID_INDEX: "byUserId",
      RATING_MOVIE_ID_INDEX: "byMovieId",
      MOVIE_TABLE_NAME: "Movie-ijhwxiff7nbgfe7pbxjat2dtxi-NONE",
      MOVIE_MOVIE_ID_INDEX: "byMovieId", 
    },
    code: Code.fromAsset(functionDir, {
      bundling: {
        image: DockerImage.fromRegistry("public.ecr.aws/sam/build-python3.10"),
        local: { // Copier le fichier updateMovieRating.py dans le dossier de sortie pour la Lambda
          tryBundle(outputDir: string) {
            execSync(
              `copy ${path.join(functionDir, "updateMovieRating.py")} ${outputDir}`,
              { stdio: "inherit" }
            );
            return true;
          },
        },
      },
    }),
  });

  // Donner les permissions à la Lambda de lire et écrire dans la table Rating
  lambda.addToRolePolicy(
    new PolicyStatement({
      actions: ["dynamodb:Query", "dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:Scan"],
      resources: [
        "arn:aws:dynamodb:eu-west-3:080941085602:table/Rating-ijhwxiff7nbgfe7pbxjat2dtxi-NONE",
        "arn:aws:dynamodb:eu-west-3:080941085602:table/Rating-ijhwxiff7nbgfe7pbxjat2dtxi-NONE/index/byUserId",
      ],
    })
  );

  // Donner les permissions à la Lambda de lire et écrire dans la table Movie (pour mettre à jour la note moyenne du film)
  lambda.addToRolePolicy(
    new PolicyStatement({
      actions: ["dynamodb:UpdateItem", "dynamodb:Scan"],
      resources: [
        "arn:aws:dynamodb:eu-west-3:080941085602:table/Movie-ijhwxiff7nbgfe7pbxjat2dtxi-NONE", // à vérifier
      ],
    })
  );

  return lambda;
});