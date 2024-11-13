const fs = require('fs');
const path = require('path');
const moment = require('moment');
const { spawn } = require('child_process');
const Model = require('../models/chatAnalysisModels');

// main_chat: chat analysis 데이터 호출
exports.apiReqChatdata = async (req, res) => {
    try {
        const ca_name = req.params.ca_name;

        const result = await new Promise((resolve, reject) => {
            Model.select(ca_name, (result) => {
                if (result.state) {
                    resolve(result);
                } else {
                    reject(result);
                }
            });
        });

        return result.rows;

    } catch(error) {
        console.log("대화관리 페이지 호출 오류: ", error);
    }
};


// 특수문자와 날짜, 기관명을 제거하는 함수
function cleanContent(content) {
    return content
        .replace(/[{}[\]:"]/g, '') // {}, [], :, " 제거
        .replace(/(user|ai|items)/g, '') // item, user, ai 제거
        .replace(/[▲△◆■◇]/g, '') // 특수문자 제거
        .replace(/\s+/g, ' ') // 중복된 공백 제거
        .trim(); // 앞뒤 공백 제거
}

// post 호출 전용
exports.reqChatOption = async(req, res) => {
    try{
        const ca_name = req.body.ca_name;
        const type = req.body.type;
        let start_date = req.body.start_date;
        let end_date = req.body.end_date;

        if (type === 'm') {
            if (!start_date || !end_date) {
                // 월간: 현재 날짜를 기준으로 한 달 전 날짜 설정
                end_date = moment().format('YYYY-MM-DD');
                start_date = moment().subtract(1, 'months').format('YYYY-MM-DD');
            }
        } else if (type === 'w') {
            if (!start_date || !end_date) {
                // 주간: 현재 날짜를 기준으로 일주일 전 월요일부터 일요일까지 설정
                end_date = moment().endOf('week').format('YYYY-MM-DD');
                start_date = moment().subtract(1, 'weeks').startOf('week').format('YYYY-MM-DD');
            }
        }

        exports.callChatAnalysis(ca_name, type, start_date, end_date);
        res.status(200).json({ message: "OK" });

    }catch(e) {
        console.error(e);
        res.status(500).json({ message: "Error processing request" });
    }
}

// chatGPT 대화 내용 분석 모듈
/**
 * 조회일 기준 한달 치 월간 대화 내용 분석
 * 대화 내용이 10건 미만인 경우 모듈 종료. 10건 이상인 경우 대화 분석.
 * Es_write_chatdata 데이터 조회 및 wr_content 특수문자 제거 및 가공 후 txt 파일로 저장
 * txt 파일 경로를 chatAnalysis.py로 전달
 * chatAnalysis.py: gpt-4o-mini 엔진 기반 대화내용 분석(주요 관심사, 카테고리별 단어 분류 및 단어 개수 분석)
 * 전달받은 chatData json 가공 후  insert_FT 모듈로 전달 
 */
exports.callChatAnalysis = async (ca_name, type, start_date, end_date) => {
    try {
        console.log(`Type: ${type}, Start Date: ${start_date}, End Date: ${end_date}`);

        Model.select_chatData(ca_name, start_date, end_date, (result) => {
            if (!result.state) {
                console.error('Error fetching chat data.');
                return;
            }

            if (result.total_count < 10) {
                console.log('대화 데이터가 10건 미만으로 데이터 분석이 어렵습니다.');
                return;
            }

            const data = result.rows;
            const filteredContent = data.map(row => cleanContent(row.wr_content)).join(' ');
            const filename = moment().format('YYYYMMDD') + '_chatData_' + (type === 'm' ? 'month' : 'week') + '.txt';
            const filePath = path.join(__dirname, '../repo/text', filename);

            // 파일 유무 검사
            fs.writeFile(filePath, filteredContent, { encoding: 'utf-8' }, (err) => {
                if (err) {
                    console.error('Error writing chat data file:', err);
                    return;
                }

                // 파일이 정상적으로 생성되었는지 확인
                fs.access(filePath, fs.constants.F_OK, (err) => {
                    if (err) {
                        console.error('Chat data file not found after writing:', err);
                        return; // 파일이 없으면 종료
                    }

                    // 파일이 존재하는 경우, Python 스크립트 실행
                    const python = spawn('/home/file/escms_gs/venv/bin/python', ['bin/chatAnalysis.py', filePath]);

                    let chatData = "";
                    let errorOutput = '';

                    python.stdout.setEncoding('utf-8');
                    python.stdout.on('data', (data) => {
                        chatData += data.toString();
                    });

                    python.stderr.on('data', (data) => {
                        errorOutput += data.toString();
                        console.error(`stderr: ${errorOutput}`);
                    });

                    // Python 프로세스 종료 이벤트 처리
                    python.on('close', (code) => {
                        console.log(`Python process exited with code ${code}`);
                        if (code === 0) {
                            try {
                                // 백틱(```json`)과 불필요한 개행 문자 제거
                                const cleanedData = chatData
                                    .replace(/```json/g, '') // ```json 제거
                                    .replace(/```/g, '')     // ``` 제거
                                    .trim(); // 앞뒤 공백 제거

                                const resultData = JSON.parse(cleanedData);

                                const saveData = {
                                    resultData,
                                    ca_name: ca_name,
                                    type: type
                                };

                                exports.insert_FT(saveData);

                                console.log('Chat data inserted successfully');
                            } catch (jsonError) {
                                console.error('Error parsing JSON:', jsonError);
                            }
                        } else {
                            console.error(`Python script error: ${errorOutput}`);
                        }
                    });
                });
            });
        });

    } catch (e) {
        console.error('Error callChatAnalysis:', e);
    }
}

// Full Text 분석 결과 저장 모듈
/**
 * ca_name, wr_option, wr_subject 값 지정. 추후 요구사항에 따라 바뀔 수 있음
 * wr_contet: 전달받은 분석 결과를 JSON 형태로 저장
 * type: FT(Full Text) / WC(Word Cloud)
 * mainsubject: 주요 관심사
 * category: 기타 항목을 포함한 5개 카테고리 지정 후 해당 단어를 분류
 * category - name: 카테고리 명
 * category - keyword: 단어
 * category - count: 각 카테고리 별 단어 개수(중복허용) -> 카테고리별 pie chart 생성 시 사용
 * category - count: 0 으로 지정. 추후 바뀔 수 있음
 */
exports.insert_FT = async function (saveData) {
    try{
        const ca_name = saveData.ca_name
        let wr_option = "FT"
        let wr_subject;

        if (saveData.type === 'm') {
            wr_subject = "월간";
        } else if(saveData.type === 'w') {
            wr_subject = "주간";
        } else {
            wr_subject = "";
        }

        const wr_content = {
            type: "FT",
            mainsubject: saveData.resultData['주요 관심사'].join(', '),
            category: Object.entries(saveData.resultData['카테고리 분류']).map(([key, value]) => ({
                name: key,
                keyword: value['단어'],
                count: value['count'],
                percent: 0
            }))
        }

        const ftData = {
            ca_name: ca_name,
            wr_option: wr_option,
            wr_subject: wr_subject,
            wr_content: JSON.stringify(wr_content)
        };

        Model.insert_FT(ftData, (result) => {
            if (result.state) {
                console.log('Data successfully insert_FT:', result);
            } else {
                console.error('Data insert_FT failed:', result);
            }
        });

    } catch(e) {
        console.error('Error in insert_FT:', e);
    }
}

/*
// 워드클라우드 생성
exports.generateWordCloud = async (req, res) => {
    try {
        const data = await getDataFromDB();

        const filteredContent = data.map(row => cleanContent(row.wr_content)).join(' ');

        const filename = `${moment().format('YYYYMMDD')}_chatData.txt`;
        const filePath = path.join(__dirname, '../repo/text', filename);
        fs.writeFileSync(filePath, filteredContent, { encoding: 'utf-8' });

        const python = spawn('python', ['controllers/wordcloudOKT.py', filePath]);

        let top10Data = "";

        python.stdout.setEncoding('utf-8');
        python.stdout.on('data', (data) => {
            top10Data += data.toString();
        });

        python.on('close', (code) => {
            console.log(`Python process exited with code ${code}`);
            try {
                const pythonJson = JSON.parse(top10Data);

                // console.log(pythonJson);

                const top_words = pythonJson.top10;
                const top_words_30 = pythonJson.top30;

                exports.generateWordGraph(res, top_words_30);
            } catch (e) {
                console.error('Error parsing Python output:', e);
                res.status(500).send('Error parsing Python output.');
            }
        });

        python.stderr.on('data', (data) => {
            console.error(`stderr: ${data}`);
        });

    } catch (e) {
        console.error(e);
        res.status(500).send('Error generating word cloud');
    }
}
*/

/*
// pie chart 생성
exports.generateWordGraph = async (res, top_words_30) => {
    console.log(top_words_30);
    console.log(JSON.stringify(top_words_30))

    const python = spawn('python', ['controllers/wordGraph.py']);
    python.stdin.write(JSON.stringify(top_words_30), 'utf-8');
    python.stdin.end();

    let output = '';
    
    // stdout에서 데이터를 수신할 때마다 누적
    python.stdout.on('data', (data) => {
        output += data.toString();
    });

    python.on('close', (code) => {
        console.log(`Python process exited with code ${code}`);

        try {
            // Python 출력 결과가 JSON 형식이라고 가정하고 파싱
            const parsedOutput = JSON.parse(output);

            // 결과를 클라이언트에 전송
            res.send({
                wordGraphOutput: parsedOutput
            });
        } catch (e) {
            console.error('Error parsing Python output:', e);
            res.status(500).send('Error parsing Python output.');
        }
    });

    python.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });
};
*/