const { spawn } = require('child_process');
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
            console.log('Calendar Tools:', JSON.stringify(calendarTools, null, 2));

            const listEventsTool = calendarTools.find(t => t.name.includes('events.list') || t.name.includes('listEvents') || t.name.includes('events'));
            if (listEventsTool) {
                send({ jsonrpc: '2.0', id: 3, method: 'tools/call', params: { name: listEventsTool.name, arguments: {} } });
            }
        } catch (e) { console.error(e); }
    }
}, 3000);

setTimeout(() => {
    const rsStr = buffer.split('\n').find(l => l.includes('"id":3'));
    if (rsStr) {
        console.log('Result:', rsStr);
    }
    server.kill();
}, 6000);
