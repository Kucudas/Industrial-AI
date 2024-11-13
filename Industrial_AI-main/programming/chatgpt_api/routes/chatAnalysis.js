const fs = require('fs');
const path = require('path');
var express = require('express');
var router = express.Router();

// 현재 파일의 이름을 추출하여 controllerName으로 설정
const currentFileName = path.basename(__filename, path.extname(__filename));
const controllerName = currentFileName;
const controllerPath = path.join(__dirname, `../controllers/${controllerName}Controller.js`);

const data = require(controllerPath);



router.get('/chatAnalysis', data.reqChatOption);
//router.get('/wordCloud', data.generateWordCloud);
//router.get('/wordGraph', data.generateWordGraph);

module.exports = router;