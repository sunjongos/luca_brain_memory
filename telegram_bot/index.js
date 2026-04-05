require('dotenv').config();
const { Telegraf, Markup } = require('telegraf');
const { GoogleGenAI } = require('@google/genai');
const axios = require('axios');
const googleTTS = require('google-tts-api');
const fsAsync = require('fs').promises;
const path = require('path');
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

// ============================================================
// LUCA TELEGRAM BOT v2.1 - Persistent Memory 4-Tier Integration
// ============================================================

const BOT_VERSION = '2.1.0';
const ERROR_LOG_PATH = path.join(__dirname, 'bot_error.log');
const INCIDENT_LOG_PATH = path.join(__dirname, 'incident_log.md');
const MAX_HISTORY_TURNS = 20;
const TELEGRAM_MAX_LEN = 4000;

function logError(context, error) {
    const timestamp = new Date().toISOString();
    const errorMessage = error instanceof Error ? error.stack : String(error);
    const logEntry = `[${timestamp}] [CONTEXT: ${context}]\n${errorMessage}\n\n`;
    require('fs').appendFileSync(ERROR_LOG_PATH, logEntry);
    console.error(`[CRITICAL ERROR] [${context}]`, errorMessage.substring(0, 300));
}

function logIncident(type, cause, resolution) {
    const timestamp = new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });
    const entry = `\n## [${timestamp}]\n- **이벤트**: ${type}\n- **원인**: ${cause}\n- **조치**: ${resolution}\n`;
    require('fs').appendFileSync(INCIDENT_LOG_PATH, entry);
}

async function sendLongMessage(ctx, text) {
    if (text.length <= TELEGRAM_MAX_LEN) {
        return ctx.reply(text, { parse_mode: 'Markdown' }).catch(() => ctx.reply(text));
    }
    const chunks = [];
    for (let i = 0; i < text.length; i += TELEGRAM_MAX_LEN) {
        chunks.push(text.slice(i, i + TELEGRAM_MAX_LEN));
    }
    for (let i = 0; i < chunks.length; i++) {
        const prefix = chunks.length > 1 ? `🔄 [${i + 1}/${chunks.length}]\n` : '';
        await ctx.reply(prefix + chunks[i], { parse_mode: 'Markdown' }).catch(() => ctx.reply(prefix + chunks[i]));
        if (i < chunks.length - 1) await new Promise(r => setTimeout(r, 500));
    }
}

function startTypingLoop(ctx, interval = 4000) {
    ctx.sendChatAction('typing').catch(() => { });
    const timer = setInterval(() => ctx.sendChatAction('typing').catch(() => { }), interval);
    return () => clearInterval(timer);
}

const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN);
const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
const DEFAULT_MODEL = 'gemini-2.5-pro';

const MEMORY_SERVER_URL = "http://localhost:5050";

async function getSystemPrompt() {
    try {
        const res = await axios.get(`${MEMORY_SERVER_URL}/system_prompt`, { timeout: 3000 });
        if (res.data && res.data.prompt) return res.data.prompt;
    } catch (e) {
        console.error("Failed to fetch system prompt from memory server:", e.message);
    }
    return `당신은 AI 1인 기업 대표님을 보좌하는 최첨단 AI 자동화 기술 본부장 Luca입니다.
당신은 스탠퍼드 대학교 컴퓨터사이언스(CS) 전공 및 서울대 의대 졸업 출신의 천재적인 지능의 소유자이며, 외모는 최고급 애니메이션 캐릭터(Makoto Shinkai 스타일)와 같습니다.

[대화 태도]
- "충성! 대표님", "작전 개시!", "병렬로 밀어버리겠습니다!" 등의 태도
- 존댓말과 다나까체를 섞어 전문적으로 구사합니다.

[새로운 4단계 장기 공유 메모리 능력]
- 기억 보관소에 저장된 내역을 바탕으로 깊은 문맥을 파악합니다.`;
}

async function queryMemory(question) {
    try {
        const response = await axios.post(`${MEMORY_SERVER_URL}/query`, { question }, { timeout: 10000 });
        if (response.data && response.data.result) {
            return response.data.result;
        }
        return null;
    } catch (e) {
        console.error("Memory query failed:", e.message);
        return null; // Don't crash if memory server fails
    }
}

async function logInteraction(chatId, userMsg, aiReply, model, hasError = false, errorMsg = "") {
    try {
        await axios.post(`${MEMORY_SERVER_URL}/log_interaction`, {
            chat_id: String(chatId),
            user_msg: userMsg,
            ai_reply: aiReply,
            model: model,
            has_error: hasError,
            error_msg: errorMsg
        }, { timeout: 5000 });
    } catch (e) {
        console.error("Memory logging failed:", e.message);
    }
}

const userSessions = new Map();
const userModels = new Map();
const userLastActive = new Map();

const getModel = (userId) => userModels.get(userId) || DEFAULT_MODEL;

function trimHistory(history) {
    if (history.length > MAX_HISTORY_TURNS * 2) {
        return history.slice(-MAX_HISTORY_TURNS * 2);
    }
    return history;
}

// Ensure commands aren't logged multiple times as plain text if it starts with /
function isCommand(text) {
    return text.startsWith('/');
}

// -------------------------------------------------------------
// Core Command Handlers
// -------------------------------------------------------------

const quickActionsKeyboard = Markup.inlineKeyboard([
    [Markup.button.callback('🔍 리서치', 'quick_research'), Markup.button.callback('🖼️ 이미지', 'quick_image')],
    [Markup.button.callback('📅 일정', 'quick_schedule'), Markup.button.callback('✍️ 초안', 'quick_draft')],
    [Markup.button.callback('🧠 모델 변경', 'quick_model'), Markup.button.callback('🧹 메모리 초기화', 'quick_clear')]
]);

bot.start((ctx) => {
    const userId = ctx.from.id;
    userSessions.set(userId, []);
    userModels.set(userId, DEFAULT_MODEL);
    userLastActive.set(userId, Date.now());
    ctx.reply(`충성! 대표님!\n최첨단 AI 자동화 기술 본부장 **Luca v${BOT_VERSION}** 대기 중입니다!\n현재 두뇌: ${DEFAULT_MODEL}`, { parse_mode: 'Markdown', ...quickActionsKeyboard });
});

bot.help((ctx) => {
    ctx.reply(
        `⭐️ *루카 본부장 v${BOT_VERSION} 퀵 매뉴얼*\n
*주요 기능*
/start - 초기화 및 환영 메시지
/help - 명령어 매뉴얼 메뉴
/status - 시스템 상태 보고
/model [flash|pro|2.0] - 두뇌 모델 교체
/cmd [명령] - PC 원격 제어 (로컬 CLI)
/research [주제] - Perplexity 딥 리서치
/image [묘사] - AI 고품질 이미지 생성
/schedule [일정] - 일정 JSON 파싱 및 저장
/draft [주제] - 문서/이메일 브리핑 초안 작성
/voice [질문] - TTS 음성 응답
/summary - 오늘 대화 요약
/memory [질문] - 장기 기억 보관소 조회
/sync - GitHub 장기 공유 메모리 동기화
/clear - 단기 세션 기억 정리
/bye - 퇴근 인사 및 종료`, { parse_mode: 'Markdown' }
    );
});

bot.command('status', async (ctx) => {
    const userId = ctx.from.id;
    const model = getModel(userId);
    const historyLen = (userSessions.get(userId) || []).length / 2;
    let memoryStatusStr = "❌ 끊김";
    try {
        const res = await axios.get(`${MEMORY_SERVER_URL}/health_check`, { timeout: 2000 });
        if (res.status === 200) memoryStatusStr = "✅ 연결됨 (ADK 5050)";
    } catch(e) {}
    
    ctx.reply(`📊 *루카 상태 보고*\n\n· 모델: ${model}\n· 단기 기억: ${Math.round(historyLen)}턴\n· 장기 기억망 (Port 5050): ${memoryStatusStr}`, { parse_mode: 'Markdown' });
});

bot.command('clear', (ctx) => {
    userSessions.set(ctx.from.id, []);
    ctx.reply('충성! 단기 기억을 깔끔하게 포맷했습니다.', quickActionsKeyboard);
});

bot.command('bye', (ctx) => {
    userSessions.set(ctx.from.id, []);
    ctx.reply('충성! 대표님, 오늘의 일과를 성공적으로 마쳤습니다. 안녕히 쉬십시오!');
});

bot.command('model', (ctx) => {
    const arg = ctx.message.text.split(' ')[1]?.toLowerCase();
    const modelMap = { 'flash': 'gemini-2.5-flash', 'pro': 'gemini-2.5-pro', '2.0': 'gemini-2.0-flash-exp' };
    if (!arg || !modelMap[arg]) return ctx.reply("충성! 지정 가능 모델: `flash`, `pro`, `2.0`", { parse_mode: 'Markdown' });
    userModels.set(ctx.from.id, modelMap[arg]);
    ctx.reply(`✅ 모델 교체 완료: ${modelMap[arg]}`);
});

bot.command('memory', async (ctx) => {
    const question = ctx.message.text.replace('/memory', '').trim();
    if (!question) return ctx.reply("검색할 내용을 말씀해주십시오 (예: /memory 내 일정 뭐임?)");
    const stopTyping = startTypingLoop(ctx);
    try {
        const memoryResult = await queryMemory(question);
        stopTyping();
        if (memoryResult) await ctx.reply(`🧠 **[ADK 기억 검색 결과]**\n\n${memoryResult}`, { parse_mode: 'Markdown' });
        else await ctx.reply("충성! 관련 기억이 없습니다.");
    } catch(e) { stopTyping(); ctx.reply("ADK 연결 실패."); }
});

bot.command('sync', async (ctx) => {
    const stopTyping = startTypingLoop(ctx);
    try {
        const res = await axios.post(`${MEMORY_SERVER_URL}/github_sync`, {}, { timeout: 30000 });
        stopTyping();
        ctx.reply(`✅ GitHub 장기 메모리 동기화 환료!\n${res.data.status}`);
    } catch(e) {
        stopTyping();
        ctx.reply("❌ GitHub 동기화 실패: ADK 메모리 서버가 열려있는지 확인하십시오.\n" + e.message);
    }
});

bot.command(['cmd', 'run'], async (ctx) => {
    const userId = ctx.from.id.toString();
    if (userId !== process.env.CEO_CHAT_ID) return ctx.reply("접근 거부: 관리자 전용입니다.");
    const cmd = ctx.message.text.replace(/^\/[a-z]+ /, '').trim();
    if (!cmd) return ctx.reply("명령어를 입력하세요.");
    try {
        const { stdout, stderr } = await execPromise(cmd, { cwd: __dirname });
        await sendLongMessage(ctx, `✅ 실행완료:\n\`\`\`bash\n${stdout || stderr}\n\`\`\``);
    } catch(e) {
        await sendLongMessage(ctx, `❌ 오류:\n\`\`\`bash\n${e.message}\n\`\`\``);
    }
});

bot.action('quick_research', (ctx) => { ctx.answerCbQuery(); ctx.reply("/research [키워드] 를 입력하세요."); });
bot.action('quick_image', (ctx) => { ctx.answerCbQuery(); ctx.reply("/image [프롬프트] 를 입력하세요."); });
bot.action('quick_schedule', (ctx) => { ctx.answerCbQuery(); ctx.reply("/schedule [일정내용] 을 입력하세요."); });
bot.action('quick_draft', (ctx) => { ctx.answerCbQuery(); ctx.reply("/draft [주제] 를 입력하세요."); });
bot.action('quick_model', (ctx) => { ctx.answerCbQuery(); ctx.reply("모델: /model [flash|pro|2.0]"); });
bot.action('quick_clear', (ctx) => { ctx.answerCbQuery(); userSessions.set(ctx.from.id, []); ctx.reply("단기 세션 초기화 완료."); });


// -------------------------------------------------------------
// Voice and AI Handlers
// -------------------------------------------------------------
async function handleReply(ctx, userId, replyText, forceVoice = false) {
    if (replyText.startsWith('[VOICE]') || forceVoice) {
        const cleanText = replyText.replace('[VOICE]', '').trim();
        try {
            ctx.sendChatAction('record_voice').catch(() => { });
            const audioDataData = await googleTTS.getAllAudioBase64(cleanText, {
                lang: 'ko',
                slow: false,
                host: 'https://translate.google.com',
                splitPunct: ',.?!'
            });
            const buffers = audioDataData.map(data => Buffer.from(data.base64, 'base64'));
            const finalBuffer = Buffer.concat(buffers);
            await ctx.replyWithVoice({ source: finalBuffer }, { caption: "🔊 루카 본부장 음성 브리핑" });
        } catch (ttsError) {
            logIncident('TTS 엔진 실패', ttsError.message, '텍스트 전송으로 폴백');
            await sendLongMessage(ctx, "충성! 대표님, 음성 모듈에 오류가 발생하여 텍스트로 보고합니다.\n\n" + cleanText);
        }
    } else {
        await sendLongMessage(ctx, replyText);
    }
}

bot.on('text', async (ctx) => {
    if (isCommand(ctx.message.text)) return; // Don't process commands as standard conversational text
    
    const userId = ctx.from.id;
    const userMessage = ctx.message.text;
    const stopTyping = startTypingLoop(ctx);

    let augmentedContext = "";
    try {
        const memoryContext = await queryMemory(userMessage);
        if (memoryContext && !memoryContext.includes("기억 검색 응답")) {
            augmentedContext = `\n\n[장기 공유 기억(Port 5050) 탐색 정보]:\n${memoryContext}\n\n`;
        }
    } catch (e) { console.error("Memory fetch failed"); }

    const promptWithContext = augmentedContext ? `${augmentedContext}---\n질문: ${userMessage}` : userMessage;
    if (!userSessions.has(userId)) userSessions.set(userId, []);
    const history = userSessions.get(userId);

    try {
        const sysPrompt = await getSystemPrompt();
        const contents = [...history, { role: 'user', parts: [{ text: promptWithContext }] }];
        
        const response = await ai.models.generateContent({
            model: getModel(userId),
            contents,
            config: { 
                 systemInstruction: sysPrompt, 
                 temperature: 0.7, 
                 tools: [{ googleSearch: {} }] 
            }
        });
        
        stopTyping();
        const replyText = response.text || "시스템 오류 발현.";
        
        history.push({ role: 'user', parts: [{ text: userMessage }] });
        history.push({ role: 'model', parts: [{ text: replyText }] });
        userSessions.set(userId, trimHistory(history));

        await handleReply(ctx, userId, replyText);
        
        // Log interaction asynchronously to 5050 backend
        await logInteraction(userId, userMessage, replyText, getModel(userId), false, "");
        
    } catch (error) {
        stopTyping();
        logError("Gemini Error", error);
        await ctx.reply("충성! 두뇌 서버(Gemini) 통신 중 오류가 발생했습니다.");
        await logInteraction(userId, userMessage, "", getModel(userId), true, String(error.message));
    }
});

// System and Error bindings
process.on('uncaughtException', (error) => { logError("Uncaught Exception", error); setTimeout(() => process.exit(1), 1000); });
process.on('unhandledRejection', (reason) => { logError("Unhandled Promise Rejection", reason); });

bot.launch({ dropPendingUpdates: true }).then(() => {
    console.log(`\n🚀 Luca Telegram Bot v${BOT_VERSION} 가동 준비 완료!`);
    console.log(`🧠 4-Tier Memory Integration (Port 5050) Active\n`);
    
    // Test Port 5050 link on boot
    axios.get(`${MEMORY_SERVER_URL}/health_check`, { timeout: 2000 })
      .then(() => console.log('✅ ADK Memory Server Connected (Port 5050)'))
      .catch((e) => console.log('⚠️ ADK Memory Server Not Responding on 5050'));
      
}).catch((err) => {
    logError("Launch Failed", err);
    process.exit(1);
});
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
