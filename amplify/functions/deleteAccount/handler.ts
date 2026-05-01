import type { Schema } from '../../data/resource';
import { Amplify } from 'aws-amplify';
import { generateClient } from 'aws-amplify/data';
import { getAmplifyDataClientConfig } from '@aws-amplify/backend/function/runtime';
import { env } from '$amplify/env/deleteAccount';
import {
  AdminDeleteUserCommand,
  CognitoIdentityProviderClient,
} from '@aws-sdk/client-cognito-identity-provider';

const { resourceConfig, libraryOptions } = await getAmplifyDataClientConfig(env);
Amplify.configure(resourceConfig, libraryOptions);

const client = generateClient<Schema>();
const cognito = new CognitoIdentityProviderClient();

export const handler: Schema['deleteMyAccount']['functionHandler'] = async (event) => {
    const identity = event.identity;
    if (!identity || !("sub" in identity) || !identity.sub) {
        throw new Error("Utilisateur non authentifie");
    }
    const userId = identity.sub;

    const { data: ratings } = await client.models.Rating.list({
        filter: {
            userId: { eq: userId },
        },
    });

    await Promise.all(
        (ratings ?? []).map((rating) =>
            client.models.Rating.delete({ id: rating.id })
        )
    );

    await client.models.UserProfile.delete({ id: userId });

    await cognito.send(
        new AdminDeleteUserCommand({
            UserPoolId: env.AMPLIFY_AUTH_USERPOOL_ID,
            Username: userId,
        })
    );

    return true;
};
