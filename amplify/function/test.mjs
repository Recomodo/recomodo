export const handler = async (event) => {
  // TODO implement
  const date = new Date();
  const formattedFR = date.toLocaleString('fr-FR',{
    timeZone: 'Europe/Paris',
  });
  console.log(formattedFR);
  // const response = {
  //   statusCode: 200,
  //   body: JSON.stringify('Hello from Lambda!'),
  // };
  return {
    statusCode: 200,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Headers": "*",
      "Access-Control-Allow-Methods": "GET,OPTIONS",
    },
    body: JSON.stringify({
      date: formattedFR,
    }),
  };
};
