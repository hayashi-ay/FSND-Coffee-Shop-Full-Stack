export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'hayashi-ay', // the auth0 domain prefix
    audience: 'coffee_shop_auth', // the audience set for the auth0 app
    clientId: 't57Eeudrrl8Kdx1Z4JduARlmyzqYBcY1', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:8100', // the base url of the running ionic application. 
  }
};
