var AWS = require('aws-sdk');
const { LexRuntimeV2 } = require("@aws-sdk/client-lex-runtime-v2");

const lexruntime = new LexRuntimeV2({ 
  region: "ap-northeast-2",      // Set your Bot Region
  credentials: new AWS.Credentials({
    accessKeyId: "accessKeyId", // Add your access IAM accessKeyId
    secretAccessKey: "secretAccessKey+secretAccessKey" // Add your access IAM secretAccessKey
  })     
});

const lexparams = {
  "botAliasId": "TSTALIASID",   // Enter the botAliasId
  "botId": "EUP4FPPIPL",         // Enter the botId
  "localeId": "ko_KR",
  "text": "I would like to book a hotel",
  "sessionId": "some_session_id"
};

lexruntime.recognizeText(lexparams, function(err, data) {
  if (err) console.log(err, err.stack); // an error occurred
  else     console.log(data);           // successful response
});
