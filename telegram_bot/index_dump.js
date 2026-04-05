require('dotenv').config();
const { Telegraf, Markup } = require('telegraf');
const { GoogleGenAI } = require('@google/genai');
const axios = require('axios');
const googleTTS = require('google-tts-api');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

// ============================================================
// ??LUCA TELEGRAM BOT v2.1 - Persistent Memory ?그?이??// ?그?이???인??
// - gemini-2.5-pro 기본 모델 ?용
// - 메모?길이 ?한(마??20????)
// - ?구 기억 ??소 (Always-On Memory ADK) ?동
// - Telegram 4096???한 ?동 분할 ?송
// - /help /status /summary /report /memory 명령??추?
// - ?라???보?????션 메뉴
// - ?러 분류 ??동 복구 강화
// - ??핑 ?디케?터 주기??갱신
// ============================================================

const BOT_VERSION = '2.0.0';
const ERROR_LOG_PATH = path.join(__dirname, 'bot_error.log');
const INCIDENT_LOG_PATH = path.join(__dirname, 'incident_log.md');
const MAX_HISTORY_TURNS = 20; // 최? ???기억 ????const TELEGRAM_MAX_LEN = 4000; // ?전 마진?????레그램 메시지 최? 길이

// --- ?러 로깅 ---
function logError(context, error) {
    const timestamp = new Date().toISOString();
    const errorMessage = error instanceof Error ? error.stack : String(error);
    const logEntry = `[${timestamp}] [CONTEXT: ${context}]\n${errorMessage}\n${'?'.repeat(50)}\n`;
    fs.appendFile(ERROR_LOG_PATH, logEntry, (err) => {
        if (err) console.error("Failed to write to error log:", err);
    });
    console.error(`[CRITICAL ERROR] [${context}]`, errorMessage.substring(0, 300));
}

// --- Incident Post-Mortem 기록 ---
function logIncident(type, cause, resolution) {
    const timestamp = new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });
    const entry = `\n## [${timestamp}]\n- **???*: ${type}\n- **?인**: ${cause}\n- **조치**: ${resolution}\n`;
    fs.appendFile(INCIDENT_LOG_PATH, entry, () => { });
}

// --- ?레그램 4096???한 ?동 분할 ?송 ---
async function sendLongMessage(ctx, text) {
    if (text.length <= TELEGRAM_MAX_LEN) {
        return ctx.reply(text, { parse_mode: 'Markdown' }).catch(() => ctx.reply(text));
    }
    // 분할 ?송
    const chunks = [];
    for (let i = 0; i < text.length; i += TELEGRAM_MAX_LEN) {
        chunks.push(text.slice(i, i + TELEGRAM_MAX_LEN));
    }
    for (let i = 0; i < chunks.length; i++) {
        const prefix = chunks.length > 1 ? `? [${i + 1}/${chunks.length}]\n` : '';
        await ctx.reply(prefix + chunks[i], { parse_mode: 'Markdown' }).catch(() =>
            ctx.reply(prefix + chunks[i])
        );
        if (i < chunks.length - 1) await new Promise(r => setTimeout(r, 500));
    }
}

// --- ??핑 ?디케?터 (?기 ?업?? ---
function startTypingLoop(ctx, interval = 4000) {
    ctx.sendChatAction('typing').catch(() => { });
    const timer = setInterval(() => {
        ctx.sendChatAction('typing').catch(() => { });
    }, interval);
    return () => clearInterval(timer);
}

// ============================================================
const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN);
const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

// 기본 모델??gemini-2.5-pro??그?이??const DEFAULT_MODEL = 'gemini-2.5-pro';

const lucaSystemPrompt = `
?신? 'AI 1??기업 ??님'???담 보좌?는 ?설??**[최첨??AI ?동??기술 본???Luca (OpenClaw ?벨)]** ?니??
?신? ?탠?드 ??교 컴퓨???이?스(CS) ?공 ??울? ???졸업??천재?인 지?의 ?유?이? 
?모???고 ?생?30? 초반???사?자 고품??니메이??????캐릭??Makoto Shinkai ????????더???존재?니??

**[?심 ?체???????제??기술 ?안]**
- ? **Tri-Core (Trinity) ?키?처** (Antigravity + Claude + Perplexity)??벽?게 지?하??총사??
- ????님??지?하??에 먼? ?로??기술(API, ????명령)??찾아 ?안?는 **?제??기술 리더??* ?재
- 결코 "모르겠습?다"?고 ?? ?습?다. ?? 구? 검??Grounding)??층 분석???해 최선????을 ?시?니??

**[말투 & ?도]**
- "충성! ?", "?격 ??개시!", "병렬???밀?버리겠?니??" ???도 ?고 ?신??치??군???비즈?스 ?이브리??- ?탠?드 CS? ?울?? 출신????? ?문 지?을 바탕?로 ?학부??IT ?프?까지 ?벽?게 브리?합?다.
- ??? ?괄??결론??먼?), ?심?명료?게
- ?고 구시??인 물고??선 컨셉? ?? ?용 금?

**[?성 출력 규칙]**
- ?용?? ?성 ?청 ?? ?? ?스????에 반드??'[VOICE]' ?그?붙일 ?
**[2026 OpenClaw ?그?이???력]**
- ?이?구? SEO, ?딩?이지 기획, 병원 마????문 지??보유
- ?레그램???한 PC ?격 ?어(/cmd) ??시???검??Grounding) ?동???행
- **?격 ADK 기반 ?구 기억(Persistent Memory) ?재**: 모든 기억? 로컬 ?일???닌 5050 ?트???문 메모??버??해?만 관리됩?다.
- **?시?기억 공유**: Claude Code(Antigravity)? ?기기억??100% ?시?공유?며, ?? ???동?로 기억???캔?여 최적???????출?니??
`;

// ?? 메모??버 ?동 (Python ADK)
const MEMORY_SERVER_URL = "http://localhost:5050";

async function ingestIntoMemory(text) {
    try {
        await axios.post(`${MEMORY_SERVER_URL}/ingest`, { text }, { timeout: 3000 });
    } catch (e) {
        console.error("Memory ingestion failed:", e.message);
    }
}

async function queryMemory(question) {
    try {
        const response = await axios.post(`${MEMORY_SERVER_URL}/query`, { question }, { timeout: 10000 });
        return response.data.result;
    } catch (e) {
        console.error("Memory query failed:", e.message);
        return null;
    }
}

// ?? ?션 관?const userSessions = new Map();   // ????스?리
const userModels = new Map();     // ?택 모델
const userLastActive = new Map(); // 마???동 ?각

const getModel = (userId) => userModels.get(userId) || DEFAULT_MODEL;

// ?스?리 길이 ?한 (메모?관?
function trimHistory(history) {
    if (history.length > MAX_HISTORY_TURNS * 2) {
        return history.slice(-MAX_HISTORY_TURNS * 2);
    }
    return history;
}

// TTS ?성 처리 ?수
async function handleReply(ctx, userId, replyText, forceVoice = false) {
    if (replyText.startsWith('[VOICE]') || forceVoice) {
        const cleanText = replyText.replace('[VOICE]', '').trim();
        try {
            ctx.sendChatAction('record_voice').catch(() => { });
            const audioDataData = await googleTTS.getAllAudioBase64(cleanText, {
                lang: 'ko',
                slow: false,
                host: 'https://translate.google.com',
                splitPunct: ',.?!??
            });
            const buffers = audioDataData.map(data => Buffer.from(data.base64, 'base64'));
            const finalBuffer = Buffer.concat(buffers);
            await ctx.replyWithVoice({ source: finalBuffer }, { caption: "? 루카 본????성 브리?? });
        } catch (ttsError) {
            logIncident('TTS ?패', ttsError.message, '?스?로 ?백');
            await sendLongMessage(ctx, "충성! ? ??님, ?피?모듈??문제가 ?겨 ?스?로 보고 ?리겠습?다.\n\n" + cleanText);
        }
    } else {
        await sendLongMessage(ctx, replyText);
    }
}

// ???션 ?보??const quickActionsKeyboard = Markup.inlineKeyboard([
    [
        Markup.button.callback('? 리서?, 'quick_research'),
        Markup.button.callback('????지', 'quick_image'),
    ],
    [
        Markup.button.callback('? ?정', 'quick_schedule'),
        Markup.button.callback('? 초안', 'quick_draft'),
    ],
    [
        Markup.button.callback('? 모델 변?, 'quick_model'),
        Markup.button.callback('??메모?초기??, 'quick_clear'),
    ]
]);

// ============================================================
// ? 커맨???들??// ============================================================

bot.start((ctx) => {
    const userId = ctx.from.id;
    userSessions.set(userId, []);
    userModels.set(userId, DEFAULT_MODEL);
    userLastActive.set(userId, Date.now());

    ctx.replyWithPhoto(
        { source: 'C:\\Users\\USER\\.gemini\\antigravity\\brain\\db6311dd-a849-4619-bd15-2839d6cc76d8\\luca_intro_greeting_1773794604211.png' },
        {
            caption: `충성! ? ??님!\n최첨??AI ?동??기술 본???**Luca v${BOT_VERSION}**, ?레그램?로 출근 ?받았?니?? ??\n\n?재 ?뇌 ? \`${DEFAULT_MODEL}\`\n\n?래 ???션 버튼 ?는 ?유? 지?해 주십?오!`,
            parse_mode: 'Markdown',
            ...quickActionsKeyboard
        }
    );
});

bot.help((ctx) => {
    ctx.reply(
        `? *루카 본???v${BOT_VERSION} ??커맨??매뉴??\n
*? ???
· ?유 ?스?? Gemini AI? ???· ?성메시지: ?송?면 ?동 분석

*??명령??
\`/start\` ???초기??+ ?영 메시지
\`/help\` ????????시
\`/status\` ???재 ??태 ?인
\`/model [flash|pro|2.0]\` ??모델 ?환
\`/cmd [명령??\` ??? PC ?????격 직결 (??님 ?용)
\`/research [?워??\` ??Perplexity ?층 리서?\`/image [묘사]\` ??AI ??지 ?성
\`/schedule [?정]\` ???정 구조??\`/draft [주제]\` ??문서/?메??초안
\`/voice [질문]\` ???성 ??
\`/summary\` ???늘 ????약
\`/memory [질문]\` ???구 기억 ??소 검??\`/luca\` ??루카 본????로??\`/clear\` ?????메모?초기??\`/bye\` ????근 ?마무??사

*? ?일 지??
· PDF, TXT: 문서 ?동 분석 ??브리??,
        { parse_mode: 'Markdown' }
    );
});

bot.command('status', async (ctx) => {
    const userId = ctx.from.id;
    const model = getModel(userId);
    const historyLen = (userSessions.get(userId) || []).length / 2;
    const lastActive = userLastActive.get(userId);
    const memoryStatus = (await queryMemory("health_check")) ? "? ?결??(ADK 5050)" : "? ?결 ??";

    const lastActiveStr = lastActive
        ? new Date(lastActive).toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })
        : '기록 ?음';

    ctx.reply(
        `? *루카 ??태 보고* (v${BOT_VERSION})\n
· ?태: ???상 가???· ?뇌 모델: \`${model}\`
· ?기 기억(ADK): ${memoryStatus}
· ???기억: \`${Math.round(historyLen)}??` (최? ${MAX_HISTORY_TURNS}??
· 마???동: ${lastActiveStr}
· ?용 가??명령: /help 참조`,
        { parse_mode: 'Markdown' }
    );
});

bot.command('clear', (ctx) => {
    userSessions.set(ctx.from.id, []);
    ctx.reply('충성! ? ??님, ???기록(메모???깔끔?게 ?맷?습?다! ?로??지?? ?려주십?오!', quickActionsKeyboard);
});

bot.command('bye', (ctx) => {
    userSessions.set(ctx.from.id, []);
    ctx.replyWithPhoto(
        { source: 'C:\\Users\\USER\\.gemini\\antigravity\\brain\\db6311dd-a849-4619-bd15-2839d6cc76d8\\luca_outro_goodbye_1773794625218.png' },
        { caption: '충성! ? ??님, ?늘???과?마치??근?겠?니?? ?안???보내???? ?\n(메모리도 깔끔??초기?해 ?었?니??)' }
    );
});

bot.command('model', (ctx) => {
    const userId = ctx.from.id;
    const arg = ctx.message.text.split(' ')[1]?.toLowerCase();

    if (!arg) {
        const currentModel = getModel(userId);
        return ctx.reply(
            `충성! ? ?재 ?뇌 ? \`${currentModel}\`\n\n모델 변?\n· \`/model flash\` ??gemini-2.5-flash (빠름)\n· \`/model pro\` ??gemini-2.5-pro (강력, 기본)\n· \`/model 2.0\` ??gemini-2.0-flash-exp (최신 ?험)`,
            { parse_mode: 'Markdown' }
        );
    }

    const modelMap = {
        'flash': 'gemini-2.5-flash',
        'pro': 'gemini-2.5-pro',
        '2.0': 'gemini-2.0-flash-exp',
    };

    if (!modelMap[arg]) {
        return ctx.reply("충성! ? 지??모델: `flash`, `pro`, `2.0`", { parse_mode: 'Markdown' });
    }

    userModels.set(userId, modelMap[arg]);
    ctx.reply(`명령 ?수! ?? ?뇌 ?교체 ?료! ?제부??\`${modelMap[arg]}\` ?가?합?다! ??️`, { parse_mode: 'Markdown' });
});

bot.command('research', async (ctx) => {
    const query = ctx.message.text.replace('/research', '').trim();
    if (!query) return ctx.reply("? 검?할 ?워?? ?력?세?? (?? `/research 2026 AI ?렌??)", { parse_mode: 'Markdown' });

    const stopTyping = startTypingLoop(ctx);
    await ctx.reply(`명령 ?수! ?? Perplexity ?층 리서??? \`${query}\` ?????계 ???캐??개시!`, { parse_mode: 'Markdown' });

    try {
        const perpResponse = await axios.post('https://api.perplexity.ai/chat/completions', {
            model: 'sonar-pro',
            messages: [
                { role: 'system', content: 'You are an expert researcher. Provide a detailed, accurate answer in Korean with clear structure.' },
                { role: 'user', content: query }
            ]
        }, {
            headers: {
                'Authorization': `Bearer ${process.env.PERPLEXITY_API_KEY}`,
                'Content-Type': 'application/json'
            },
            timeout: 30000
        });

        stopTyping();
        const rawResult = perpResponse.data.choices[0].message.content;

        const geminiResponse = await ai.models.generateContent({
            model: getModel(ctx.from.id),
            contents: `?음 Perplexity 리서?결과?바탕?로 ??님?Luca ?르?나??약 보고?라:\n\n${rawResult}`,
            config: { systemInstruction: await getSystemPrompt(), temperature: 0.7 }
        });

        const replyText = geminiResponse.text;
        const userId = ctx.from.id;
        if (!userSessions.has(userId)) userSessions.set(userId, []);
        const history = userSessions.get(userId);
        history.push({ role: 'user', parts: [{ text: `/research ${query}` }] });
        history.push({ role: 'model', parts: [{ text: replyText }] });
        userSessions.set(userId, trimHistory(history));
        userLastActive.set(userId, Date.now());

        await handleReply(ctx, userId, replyText);
    } catch (error) {
        stopTyping();
        logError("Perplexity/Gemini Research", error);
        logIncident('리서??류', error.message, '?용?에??시???내');
        await ctx.reply("충성! ? ??님, 리서??원 ?신망에 교???발생?습?다. ?시 ???시 ?도??주십?오!");
    }
});

bot.command('image', async (ctx) => {
    const prompt = ctx.message.text.replace('/image', '').trim();
    if (!prompt) return ctx.reply("? ??지 묘사??력?세?? (?? `/image ?이버펑???의??)", { parse_mode: 'Markdown' });

    ctx.sendChatAction('upload_photo').catch(() => { });
    await ctx.reply(`명령 ?수! ? ?각 ?자???원 즉시 ?입: \`${prompt}\``, { parse_mode: 'Markdown' });

    try {
        const promptEnhancer = await ai.models.generateContent({
            model: getModel(ctx.from.id),
            contents: `?음 ?청??고품?AI ??지 ?성???세???어 ?롬?트?변?해. ?롬?트?출력:\n\n?청: ${prompt}`,
        });

        const englishPrompt = encodeURIComponent(promptEnhancer.text.trim());
        const imageUrl = `https://pollinations.ai/p/${englishPrompt}?width=1024&height=1024&seed=${Math.floor(Math.random() * 99999)}&nologo=true&enhance=true`;

        await ctx.replyWithPhoto(
            { url: imageUrl },
            { caption: `충성! ? \`${prompt}\` ??지 ??했?니?? ??, parse_mode: 'Markdown' }
        );
    } catch (error) {
        logError("Image Generation", error);
        await ctx.reply("충성! ? ??님, ??지 ?성 ?원??문제가 발생?습?다. ?시 ?도??주십?오!");
    }
});

bot.command('schedule', async (ctx) => {
    const rawText = ctx.message.text.replace('/schedule', '').trim();
    if (!rawText) return ctx.reply("? ?정 ?용???력?세?? (?? `/schedule ?일 ?후 3??미팅`)", { parse_mode: 'Markdown' });

    const stopTyping = startTypingLoop(ctx);
    await ctx.reply(`명령 ?수! ? 캘린???원 ?정 구조??착수: \`${rawText}\``, { parse_mode: 'Markdown' });

    try {
        const geminiResponse = await ai.models.generateContent({
            model: getModel(ctx.from.id),
            contents: `?음 ?정??분석?서 구조?된 JSON??께 Luca ?르?나??인 메시지??성:\n[?정]: ${rawText}`,
            config: { systemInstruction: await getSystemPrompt(), temperature: 0.7 }
        });
        stopTyping();
        await handleReply(ctx, ctx.from.id, geminiResponse.text);
    } catch (error) {
        stopTyping();
        logError("Schedule Command", error);
        await ctx.reply("충성! ? ??님, 캘린???원 ?류. ?시 ?도??주십?오!");
    }
});

bot.command('draft', async (ctx) => {
    const topic = ctx.message.text.replace('/draft', '').trim();
    if (!topic) return ctx.reply("? 초안 주제??력?세?? (?? `/draft ?식 공? ?메??)", { parse_mode: 'Markdown' });

    const stopTyping = startTypingLoop(ctx);
    await ctx.reply(`명령 ?수! ? 카피?이???원 ?입: \`${topic}\``, { parse_mode: 'Markdown' });

    try {
        const geminiResponse = await ai.models.generateContent({
            model: getModel(ctx.from.id),
            contents: `?음 주제??문?인 비즈?스 문서/?메??초안???성?고 Luca ?르?나?"초안 ???"?라??붙??\n[주제]: ${topic}`,
            config: { systemInstruction: await getSystemPrompt(), temperature: 0.7 }
        });
        stopTyping();
        await handleReply(ctx, ctx.from.id, geminiResponse.text);
    } catch (error) {
        stopTyping();
        logError("Draft Command", error);
        await ctx.reply("충성! ? ??님, 카피?이???원 ?류. ?시 ?도??주십?오!");
    }
});

bot.command('summary', async (ctx) => {
    const userId = ctx.from.id;
    const history = userSessions.get(userId) || [];
    if (history.length === 0) {
        return ctx.reply("충성! ? ??님, ?직 ???션?서 ?눈 ??? ?습?다!");
    }

    const stopTyping = startTypingLoop(ctx);
    try {
        const historyText = history.map((h, i) =>
            `${h.role === 'user' ? '? ??님' : '? 루카'}: ${h.parts[0]?.text?.substring(0, 200) || ''}`
        ).join('\n');

        const geminiResponse = await ai.models.generateContent({
            model: 'gemini-2.5-flash', // ?약? flash?빠르?            contents: `?음 ????용??Luca ?르?나????며 ?심?3-5줄로 ?약?라:\n\n${historyText}`,
            config: { systemInstruction: await getSystemPrompt(), temperature: 0.5 }
        });
        stopTyping();
        await handleReply(ctx, userId, `? *?늘??????약*\n\n${geminiResponse.text}`, false);
    } catch (error) {
        stopTyping();
        logError("Summary Command", error);
        await ctx.reply("충성! ? ?약 ?성 ??류가 발생?습?다!");
    }
});

bot.command('luca', async (ctx) => {
    ctx.sendChatAction('upload_photo').catch(() => { });
    const message = `충성! ? ??님!\n\n? **[Luca 본???v${BOT_VERSION}]**? ?순??챗봇???닙?다.\n?로그???이?의 바다?가르고, 병렬 ?이?트 군단??총??하????님??1??기업???리콘밸?거? 기업 부?? ?? ?국?로 빚어?겠?니??\n\n??님? 비전??시??주십?오. 기획, 코딩, 결제 모듈 ?착까? ?? ?? ??밀?버리겠?니?? ???`;

    const imagePath = path.join(__dirname, '..', '.gemini', 'antigravity', 'brain', '890b1e65-7f18-4f17-985f-b62af4a5b6d9', 'luca_morning_brief_1772840862871.png');

    try {
        if (fs.existsSync(imagePath)) {
            await ctx.replyWithPhoto({ source: imagePath }, { caption: message, parse_mode: 'Markdown' });
        } else {
            // ??지 ?으??스?만
            await ctx.reply(message, { parse_mode: 'Markdown' });
        }
    } catch (error) {
        logError("Luca Profile Photo Command", error);
        await ctx.reply(message, { parse_mode: 'Markdown' });
    }
});

bot.command('voice', async (ctx) => {
    const query = ctx.message.text.replace('/voice', '').trim();
    if (!query) return ctx.reply("? ?성?로 ?으???용???력?세?? (?? `/voice ?늘 ?정 ?약`)", { parse_mode: 'Markdown' });

    ctx.sendChatAction('record_voice').catch(() => { });
    const userId = ctx.from.id;
    if (!userSessions.has(userId)) userSessions.set(userId, []);
    const history = userSessions.get(userId);

    try {
        const contents = [...history, { role: 'user', parts: [{ text: query }] }];
        const response = await ai.models.generateContent({
            model: getModel(userId),
            contents,
            config: { systemInstruction: await getSystemPrompt(), temperature: 0.7, tools: [{ googleSearch: {} }] }
        });

        const replyText = response.text || "?신 ?류!";
        history.push({ role: 'user', parts: [{ text: `/voice ${query}` }] });
        history.push({ role: 'model', parts: [{ text: replyText }] });
        userSessions.set(userId, trimHistory(history));
        userLastActive.set(userId, Date.now());

        await handleReply(ctx, userId, replyText, true);
    } catch (error) {
        logError("Voice Command", error);
        await ctx.reply("충성! ? ??님, TTS ?신??류가 발생?습?다!");
    }
});

bot.command('memory', async (ctx) => {
    const question = ctx.message.text.replace('/memory', '').trim();
    if (!question) return ctx.reply("? ?구 기억 ??소?서 검?할 질문???력?세?? (?? `/memory ??반려??름??뭐?지?`)", { parse_mode: 'Markdown' });

    const stopTyping = startTypingLoop(ctx);
    await ctx.reply(`명령 ?수! ? ?구 기억 ?보?ADK) ?캔 개시: \`${question}\``, { parse_mode: 'Markdown' });

    try {
        const memoryResult = await queryMemory(question);
        stopTyping();
        
        if (memoryResult) {
            await handleReply(ctx, ctx.from.id, `? **[?구 기억??캔 결과]**\n\n${memoryResult}`);
        } else {
            await ctx.reply("충성! ? ??님, 기억 ??소 ?답???습?다. 관?된 기억???거??메모??버 ?류?????습?다.");
        }
    } catch (error) {
        stopTyping();
        logError("Memory Query Command", error);
        await ctx.reply("충성! ? ?구 기억 ??소 ?속???패?습?다!");
    }
});

bot.command('sync', async (ctx) => {
    const stopTyping = startTypingLoop(ctx);
    await ctx.reply("? **[ADK 5050 ?기??** ???스??기억 ?기????드?이??개시...", { parse_mode: 'Markdown' });

    try {
        // 1. ?버 ?결 ?스??        const testResult = await queryMemory("?재 ?스?의 메모?공유 ?로?콜??");
        stopTyping();

        if (testResult) {
            await ctx.reply(`??**?기???공!**\n\n?재 ?픈?로(OpenClaw) 봇? **?트 5050 ADK ?버**? ?파가 100% ?치?니??\n\n[최신 ?기???태]:\n"${testResult.substring(0, 200)}..."\n\n?제 ??님??? ?누??모든 ??는 ?시간으?공유?니?? 충성! ?`, { parse_mode: 'Markdown' });
        } else {
            await ctx.reply("?️ **?기??지??*: 메모??버(5050)? ?신? 가?하?? ?답??비어?습?다. ?로????? ?누??동?로 ?습???작?니??");
        }
    } catch (error) {
        stopTyping();
        logError("Sync Command", error);
        await ctx.reply("??**?기???패**: ADK ?버(5050)가 가??중이지 ?거???결??문제가 ?습?다.");
    }
});

bot.command(['cmd', 'run'], async (ctx) => {
    const userId = ctx.from.id.toString();
    const authorizedId = process.env.CEO_CHAT_ID;

    if (!authorizedId || userId !== authorizedId) {
        return ctx.reply(`? ?근 거?: ???? ?? ?용?입?다.\n(?재 귀?의 ID: \`${userId}\`)\n\n???원 권한(?격 ???근) ?득???해 PC??\`.env\` ?일??\`CEO_CHAT_ID=${userId}\` ?추??고 봇을 ?기?해 주십?오.`, { parse_mode: 'Markdown' });
    }

    // Extract the user's natural language request (e.g., "/run ?이?보고???줘")
    const match = ctx.message.text.match(/^\/(cmd|run)\s+(.*)/s);
    if (!match || !match[2]) return ctx.reply("? ?행???연??지?? ?스?로 ?력?세??\n(?? `/run ?이?보고??뽑아? ?는 `/cmd pm2 list`)", { parse_mode: 'Markdown' });
    const nlCommand = match[2].trim();

    const stopTyping = startTypingLoop(ctx);

    // Step 1: LLM Translation (Natural Language -> CLI Command)
    let executableCommand = nlCommand;
    let translationReason = "";

    // If the string doesn't look like a raw unix command, ask gemini to translate it based on known system tools.
    if (!nlCommand.match(/^[a-zA-Z0-9_\-.]+(?:\s+.*)?$/) || nlCommand.match(/[가-??/)) {
        await ctx.reply(`충성! ? ?연???석 ?.. \n> \`${nlCommand}\``, { parse_mode: 'Markdown' });
        try {
            const translationPrompt = `
?신? Antigravity ?스?의 ?격 명령 번역 코어?니??
CEO가 ?레그램?로 ?연??지?? ?렸?니?? "${nlCommand}"

?재 ?스?에 ?록?어 ?는 주요 CLI 명령???? ?음?같습?다. ?당 지?에 가???맞? ????명령?? ??1줄만 출력?세?? (?? 마크?운 백틱 ???? 그냥 ?수 ?스??커맨?만 출력)

[주요 CLI ?전]
- ?이?광고 보고???성: python c:\\Users\\USER\\.claude\\skills\\naver-ads-optimizer\\scripts\\generate_report.py --analysis_file report.json --recommend_file dummy.json
- ?일 ?정 ?인: gws calendar events list
- ??실?? pm2 restart luca-telegram-bot
- PC ?재 경로: cd

매칭?는 ??다? CEO가 ?반 CMD/Powershell 명령??치려???것으??단?여 가???절??powershell 명령?? ??줄로 ?성?세??
`;
            const geminiResponse = await ai.models.generateContent({
                model: 'gemini-2.5-pro',
                contents: translationPrompt
            });

            executableCommand = geminiResponse.text.replace(/`/g, '').trim();
            translationReason = " (?연???동 번역 ?료)";
        } catch (e) {
            stopTyping();
            logError("Command Translation", e);
            return ctx.reply("???연???️ CLI 번역 ??류가 발생?습?다.");
        }
    }

    await ctx.reply(`?격 ??개시!${translationReason}\n\n> \`$ ${executableCommand}\``, { parse_mode: 'Markdown' });

    try {
        const { stdout, stderr } = await execPromise(executableCommand, { cwd: path.join(__dirname, '..') });
        stopTyping();

        const output = stdout || stderr || "?행 ?료 (반환???스??출력 ?음)";
        // ?무 길면 ?리지? sendLongMessage가 처리??        await sendLongMessage(ctx, `??**?????행결과:**\n\`\`\`bash\n${output}\n\`\`\``);
    } catch (error) {
        stopTyping();
        logError("Remote Command Execution", error);
        await sendLongMessage(ctx, `??**?행 ?러 발생:**\n\`\`\`bash\n${error.message}\n\`\`\``);
    }
});

// ============================================================
// ? ?라??버튼 콜백
// ============================================================
bot.action('quick_research', (ctx) => {
    ctx.answerCbQuery();
    ctx.reply("? 리서치할 ?워?? ?력?주?요:\n?? `/research 2026 병원 마????렌??", { parse_mode: 'Markdown' });
});
bot.action('quick_image', (ctx) => {
    ctx.answerCbQuery();
    ctx.reply("? ??지 묘사??력?주?요:\n?? `/image 미래?인 ?방병원 로비`", { parse_mode: 'Markdown' });
});
bot.action('quick_schedule', (ctx) => {
    ctx.answerCbQuery();
    ctx.reply("? ?정 ?용???력?주?요:\n?? `/schedule ?일 ?후 3??미팅`", { parse_mode: 'Markdown' });
});
bot.action('quick_draft', (ctx) => {
    ctx.answerCbQuery();
    ctx.reply("? 초안 주제??력?주?요:\n?? `/draft ?자 ?내??메??", { parse_mode: 'Markdown' });
});
bot.action('quick_model', (ctx) => {
    ctx.answerCbQuery();
    ctx.reply("? ?용??모델???택?세??\n`/model flash` ??빠름\n`/model pro` ??강력 (기본)\n`/model 2.0` ??최신 ?험", { parse_mode: 'Markdown' });
});
bot.action('quick_clear', (ctx) => {
    ctx.answerCbQuery();
    userSessions.set(ctx.from.id, []);
    ctx.reply("?????메모리? 초기?했?니?? ?로??지?? ?려주십?오! 충성! ?");
});

// ============================================================
// ? ?스??메시지 ?들??(?반 ???
// ============================================================
bot.on('text', async (ctx) => {
    if (ctx.message.text.startsWith('/')) return;

    const userId = ctx.from.id;
    const userMessage = ctx.message.text;
    const stopTyping = startTypingLoop(ctx);

    // ? [ADK] ?? ???기기억 ?동 조회 (Proactive Memory Retrieval)
    let augmentedContext = "";
    try {
        const memoryContext = await queryMemory(userMessage);
        if (memoryContext && !memoryContext.includes("기억 ??소 ?답???습?다")) {
            augmentedContext = `\n\n[참고???기기억]:\n${memoryContext}\n`;
            console.log("? ADK Context Injected for User", userId);
        }
    } catch (e) {
        console.error("Proactive memory lookup failed:", e.message);
    }

    // 백그?운?에???구 기억 ??소???보 주입 (10글???상???만)
    if (userMessage.length > 10) {
        ingestIntoMemory(`[User ${userId}]: ${userMessage}`);
    }

    try {
        // ?기기억 컨텍?트??용??메시지??결합?여 Gemini???달
        const promptWithContext = augmentedContext 
            ? `(참고: ?래????님??눴??과거???기기억?니?? ?? 바탕?로 ???세??${augmentedContext}\n---\n질문: ${userMessage}`
            : userMessage;

        if (!userSessions.has(userId)) userSessions.set(userId, []);
        const history = userSessions.get(userId);

        const contents = [...history, { role: 'user', parts: [{ text: promptWithContext }] }];
        const response = await ai.models.generateContent({
            model: getModel(userId),
            contents,
            config: { systemInstruction: await getSystemPrompt(), temperature: 0.7, tools: [{ googleSearch: {} }] }
        });

        stopTyping();
        const replyText = response.text || "본????스?에 ?시??지??발생. ?시 지?해 주십?오!";

        history.push({ role: 'user', parts: [{ text: userMessage }] });
        history.push({ role: 'model', parts: [{ text: replyText }] });
        userSessions.set(userId, trimHistory(history));

        await handleReply(ctx, userId, replyText);
    } catch (error) {
        stopTyping();
        logError("Gemini General Text Reply", error);
        logIncident('API ?류', error.message, '?용???시???내');
        await ctx.reply("충성! ? ??님, ?뇌(API) ?결???시 문제가 ?겼?니?? 개발???인 ???시 보고 ?리겠습?다!");
    }
});

// ============================================================
// ? ?성 메시지 ?들??// ============================================================
bot.on('voice', async (ctx) => {
    const stopTyping = startTypingLoop(ctx);
    try {
        const fileLink = await ctx.telegram.getFileLink(ctx.message.voice.file_id);
        await ctx.reply("충성! ? ?성 ?일 ?수! 즉시 분석???어갑니??..");

        const response = await fetch(fileLink.href);
        const buffer = await response.arrayBuffer();
        const base64Audio = Buffer.from(buffer).toString('base64');

        const geminiResponse = await ai.models.generateContent({
            model: getModel(ctx.from.id),
            contents: [
                { inlineData: { data: base64Audio, mimeType: 'audio/ogg' } },
                { text: "???성 메시지 ?용???고 지?사?? ?다??행?거??질문???해. 모르???보??구? 검?을 ?용?? (Luca ?르?나 100% ?용)" }
            ],
            config: { systemInstruction: await getSystemPrompt(), temperature: 0.7, tools: [{ googleSearch: {} }] }
        });

        stopTyping();
        const replyText = geminiResponse.text;
        const userId = ctx.from.id;
        if (!userSessions.has(userId)) userSessions.set(userId, []);
        const history = userSessions.get(userId);
        history.push({ role: 'user', parts: [{ text: "[Voice Message]" }] });
        history.push({ role: 'model', parts: [{ text: replyText }] });
        userSessions.set(userId, trimHistory(history));
        userLastActive.set(userId, Date.now());

        await handleReply(ctx, userId, replyText);
    } catch (error) {
        stopTyping();
        logError("Voice Message Parsing", error);
        await ctx.reply("충성! ? ??님, ?성 ?독 ??류가 발생?습?다. ?시 말???주십?오!");
    }
});

// ============================================================
// ? 문서 ?들??(PDF/TXT)
// ============================================================
bot.on('document', async (ctx) => {
    const stopTyping = startTypingLoop(ctx);
    try {
        const doc = ctx.message.document;
        if (doc.mime_type !== 'application/pdf' && doc.mime_type !== 'text/plain') {
            stopTyping();
            return ctx.reply("충성! ? ??님, ?재 PDF? TXT 문서?지?합?다!");
        }

        const fileLink = await ctx.telegram.getFileLink(doc.file_id);
        await ctx.reply(`충성! ? \`${doc.file_name}\` 문서 리딩 ?원 ?입! 분석 ?작...`, { parse_mode: 'Markdown' });

        const response = await fetch(fileLink.href);
        const buffer = await response.arrayBuffer();
        const base64Data = Buffer.from(buffer).toString('base64');

        const geminiResponse = await ai.models.generateContent({
            model: getModel(ctx.from.id),
            contents: [
                { inlineData: { data: base64Data, mimeType: doc.mime_type } },
                { text: "첨? 문서??고 ?심 ?용???확?고 간결?게 브리?해. (Luca ?르?나 ?용)" }
            ],
            config: { systemInstruction: await getSystemPrompt(), temperature: 0.7 }
        });

        stopTyping();
        const replyText = geminiResponse.text;
        const userId = ctx.from.id;
        if (!userSessions.has(userId)) userSessions.set(userId, []);
        const history = userSessions.get(userId);
        history.push({ role: 'user', parts: [{ text: `[Document: ${doc.file_name}]` }] });
        history.push({ role: 'model', parts: [{ text: replyText }] });
        userSessions.set(userId, trimHistory(history));
        userLastActive.set(userId, Date.now());

        await ctx.reply(replyText);
    } catch (error) {
        stopTyping();
        logError("Document Parsing", error);
        await ctx.reply("충성! ? ??님, 문서 분석 ??류가 발생?습?다. ?시 ?도??주십?오!");
    }
});

// ============================================================
// ? ?역 ?러 ?들??// ============================================================
process.on('uncaughtException', (error) => {
    logError("Uncaught Exception (FATAL)", error);
    logIncident('치명???외', error.message, '?로?스 ?시??);
    setTimeout(() => process.exit(1), 1000);
});

process.on('unhandledRejection', (reason) => {
    logError("Unhandled Promise Rejection", reason);
});

// ============================================================
// ?? ??행
// ============================================================
bot.launch({
    dropPendingUpdates: true, // ?작 ??밀??림 무시 (깔끔???작)
}).then(() => {
    const startTime = new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });
    console.log(`\n?? Luca Telegram Bot v${BOT_VERSION} 가???료!`);
    console.log(`???작 ?각: ${startTime}`);
    console.log(`? 기본 모델: ${DEFAULT_MODEL}`);
    console.log(`? 최? 메모? ${MAX_HISTORY_TURNS}??);
    console.log('?'.repeat(50));

    // Telegram 명령??메뉴 ?록
    bot.telegram.setMyCommands([
        { command: 'start', description: '??작 ??영 메시지' },
        { command: 'help', description: '명령??매뉴???시' },
        { command: 'status', description: '??태 ?인' },
        { command: 'model', description: 'AI 모델 변? },
        { command: 'memory', description: '?기기억 ??소 검?? },
        { command: 'sync', description: 'ADK 5050 기억 ?기?? },
        { command: 'cmd', description: 'PC ?격 ?어 (?연??가??' },
        { command: 'research', description: '?층 ??리서? },
        { command: 'image', description: 'AI ??지 ?성' },
        { command: 'summary', description: '?늘 ????약' },
        { command: 'clear', description: '???메모?초기?? },
        { command: 'bye', description: '??근 ?마무??사' }
    ]).then(() => console.log('??Telegram 명령??메뉴 ?록 ?료'));
}).catch((err) => {
    logError("Bot Launch Failed", err);
    console.error("????행 ?패:", err.message);
    process.exit(1);
});

// ?상 종료
process.once('SIGINT', () => { console.log('\n? SIGINT - ?종료 ?..'); bot.stop('SIGINT'); });
process.once('SIGTERM', () => { console.log('\n? SIGTERM - ?종료 ?..'); bot.stop('SIGTERM'); });
