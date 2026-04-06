const axios = require('axios');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '.env') });

const token = process.env.TELEGRAM_BOT_TOKEN || '8219607432:AAFU0zcdxUJDcvI7kh3c-a23vchoparfKdg';

async function sendMonthlyAlarm() {
    try {
        let chatId = process.env.CEO_CHAT_ID ? process.env.CEO_CHAT_ID.replace(/"/g, '') : null;
        
        if (!chatId) {
            const updatesRes = await axios.get(`https://api.telegram.org/bot${token}/getUpdates`);
            const updates = updatesRes.data.result;
            if (updates.length === 0) {
                console.log('No recent chats found and CEO_CHAT_ID missing in .env');
                process.exit(1);
            }
            chatId = updates[updates.length - 1].message.chat.id;
        }

        const currentMonth = new Date().getMonth() + 1;
        const msg = `🚨 *[NDB Hub Admin] Action Required*

대표님! ${currentMonth}월 마지막 주 경영회의가 다가왔습니다.
이번 달 *[이달의 빛나는 우수직원]*을 선정할 시간입니다.

수석 관리자 패널(PIN: 1122)에 접속하여 접수된 추천서를 검토하고 수상자를 공표해주십시오!`;

        await axios.post(`https://api.telegram.org/bot${token}/sendMessage`, {
            chat_id: chatId,
            text: msg,
            parse_mode: 'Markdown'
        });
        
        console.log(`[Success] Alarm sent to chat ID: ${chatId}`);
    } catch (e) {
        if (e.response && e.response.data) {
            console.error('Telegram API Error:', JSON.stringify(e.response.data, null, 2));
        } else {
            console.error(e.message);
        }
        process.exit(1);
    }
}

sendMonthlyAlarm();
