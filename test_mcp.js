const { spawn } = require('child_process');

const npxCmd = process.platform === 'win32' ? 'npx.cmd' : 'npx';
const server = spawn(npxCmd, ['-y', '@presto-ai/google-workspace-mcp'], {
    env: { ...process.env, GOOGLE_APPLICATION_CREDENTIALS: 'c:\\Users\\USER\\OneDrive\\바탕 화면\\luca연구에이전트\\credentials.json' },
    shell: true
});

server.stdout.on('data', data => {
    console.log(`STDOUT: ${data}`);
});

server.stderr.on('data', data => {
    console.error(`STDERR: ${data}`);
});

const send = (msg) => {
    console.log(`Sending: ${JSON.stringify(msg)}`);
    server.stdin.write(JSON.stringify(msg) + '\n');
};

server.on('error', err => console.error('Spawn error:', err));
server.on('exit', code => console.log('Exited with code:', code));

send({
    jsonrpc: '2.0',
    id: 1,
    method: 'initialize',
    params: { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'test', version: '1.0' } }
});

setTimeout(() => {
    send({ jsonrpc: '2.0', id: 2, method: 'tools/list', params: {} });
}, 2000);

setTimeout(() => {
    send({
        jsonrpc: '2.0',
        id: 3,
        method: 'tools/call',
        params: { name: 'google_workspace_calendar_events_list', arguments: {} }
    });
}, 4000);

setTimeout(() => {
    server.kill();
}, 8000);
