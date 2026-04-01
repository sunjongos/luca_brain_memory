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
    const d = new Date('2026-02-28T09:00:00+09:00');
    const d_start = new Date(d);
    d_start.setDate(d.getDate() - d.getDay() + 1); // Monday
    d_start.setHours(0, 0, 0, 0);
    const d_end = new Date(d_start);
    d_end.setDate(d_start.getDate() + 7); // Next Monday

    send({
        jsonrpc: '2.0', id: 2, method: 'tools/call',
        params: {
            name: 'calendar.listEvents',
            arguments: { calendarId: 'primary', timeMin: d_start.toISOString(), timeMax: d_end.toISOString() }
        }
    });
}, 1000);

setTimeout(() => {
    const rsStr = buffer.split('\n').find(l => l.includes('"id":2'));
    if (rsStr) {
        try {
            const obj = JSON.parse(rsStr);
            const textResult = obj.result.content[0].text;
            fs.writeFileSync('schedule.json', textResult);
        } catch (e) { console.error(e); }
    }
    server.kill();
}, 6000);
