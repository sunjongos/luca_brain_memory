const { spawn } = require('child_process');

const npxCmd = process.platform === 'win32' ? 'npx.cmd' : 'npx';
const server = spawn(npxCmd, ['-y', '@presto-ai/google-workspace-mcp'], {
    env: { ...process.env, GOOGLE_APPLICATION_CREDENTIALS: 'c:\\Users\\USER\\OneDrive\\바탕 화면\\luca연구에이전트\\credentials.json' },
    shell: true
});

let buffer = '';
server.stdout.on('data', data => {
    buffer += data.toString();
});

const send = (msg) => {
    server.stdin.write(JSON.stringify(msg) + '\n');
};

send({
    jsonrpc: '2.0',
    id: 1,
    method: 'initialize',
    params: { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'test', version: '1.0' } }
});

setTimeout(() => {
    send({ jsonrpc: '2.0', id: 3, method: 'tools/call', params: { name: 'people.getMe', arguments: {} } });
}, 1000);

setTimeout(() => {
    let lines = buffer.split('\n');
    lines.forEach(l => {
        try {
            const obj = JSON.parse(l);
            if (obj.id === 3) console.log('Response:', JSON.stringify(obj));
        } catch (e) { }
    });
    console.log('Raw Output:', buffer);
    server.kill();
}, 4000);
