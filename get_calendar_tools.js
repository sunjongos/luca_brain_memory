const { spawn } = require('child_process');
const fs = require('fs');
const npxCmd = process.platform === 'win32' ? 'npx.cmd' : 'npx';
const server = spawn(npxCmd, ['-y', '@presto-ai/google-workspace-mcp'], {
    env: { ...process.env, GOOGLE_APPLICATION_CREDENTIALS: 'c:\\Users\\USER\\OneDrive\\바탕 화면\\luca연구에이전트\\credentials.json' },
    shell: true
});

let buffer = '';
server.stdout.on('data', data => { buffer += data.toString(); });
server.stderr.on('data', data => { });

const send = (msg) => server.stdin.write(JSON.stringify(msg) + '\n');

send({
    jsonrpc: '2.0', id: 1, method: 'initialize',
    params: { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'test', version: '1.0' } }
});

setTimeout(() => {
    send({ jsonrpc: '2.0', id: 2, method: 'tools/list', params: {} });
}, 1000);

setTimeout(() => {
    const toolsMsgStr = buffer.split('\n').find(l => l.includes('"id":2'));
    if (toolsMsgStr) {
        try {
            const toolsObj = JSON.parse(toolsMsgStr);
            const calendarTools = toolsObj.result.tools.filter(t => t.name.includes('calendar'));
            fs.writeFileSync('calendar_tools.json', JSON.stringify(calendarTools, null, 2));
        } catch (e) { console.error(e); }
    }
    server.kill();
}, 4000);
