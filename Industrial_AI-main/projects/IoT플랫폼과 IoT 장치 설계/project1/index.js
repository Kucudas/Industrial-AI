var AWS = require('aws-sdk');

AWS.config.update({
    accessKeyId: 'accessKeyId',
    secretAccessKey: 'secretAccessKey',
    region: 'ap-northeast-2'
});

var params = {
    Image: {
        S3Object: {
            Bucket : "bucket",
            Name : "tiger.jpg"
        }
    },
    MaxLabels: 5,
    MinConfidence : 80
};

const rekognition = new AWS.Rekognition();
rekognition.detectLabels(params, function(err, data) {
    if (err) console.log(err, err.stack);
    else console.log(data);
});