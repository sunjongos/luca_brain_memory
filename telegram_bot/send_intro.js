const axios = require('axios');
const fs = require('fs');
const FormData = require('form-data');
require('dotenv').config();

const token = process.env.TELEGRAM_BOT_TOKEN || '8219607432:AAFU0zcdxUJDcvI7kh3c-a23vchoparfKdg';

async function sendIntro() {
    try {
        const updatesRes = await axios.get(`https://api.telegram.org/bot${token}/getUpdates`);
        const updates = updatesRes.data.result;
        if (updates.length === 0) {
            console.log('No recent chats found. Please send any message to the bot first.');
            return;
        }
        const chatId = updates[updates.length - 1].message.chat.id;

        // 두 번째 생성된 간지나는 본부장 이미지 경로
        const imagePath = 'C:\\Users\\USER\\.gemini\\antigravity\\brain\\01e1645f-5ecf-46ef-9c0c-00603e40dfd8\\luca_super_agent_ready_1772437718885.png';
        const caption = `충성! 🫡 대표님!\n\n저 [전설의 AI 자동화 기술 본부장 Luca]가 최상위 [Ultimate Super-Agent]로 각성을 완료하고 대기 중입니다.\n\n🧠 Long-Term Memory (영구 기억)\n🐝 Autonomous Swarm (자가 군집화)\n👁️ Multi-modal Perception (전방위 인지)\n🛡️ Self-Healing (자가 치유)\n\n위 4대 하이엔드 코어를 완벽 장착했습니다. 1인 기업 제국을 건설할 준비가 되었습니다. 명령만 내려주십시오! 🚀🔥`;

        const form = new FormData();
        form.append('chat_id', chatId);
        form.append('photo', fs.createReadStream(imagePath));
        form.append('caption', caption);

        await axios.post(`https://api.telegram.org/bot${token}/sendPhoto`, form, {
            headers: form.getHeaders(),
        });
        console.log('Successfully sent to chat ID:', chatId);
    } catch (e) {
        if (e.response && e.response.data) {
            console.error('Telegram API Error:', e.response.data);
        } else {
            console.error(e.message);
        }
    }
}
sendIntro();
