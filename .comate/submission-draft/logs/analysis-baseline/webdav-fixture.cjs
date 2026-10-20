const http = require('http');
const fs = require('fs');
const path = require('path');
const logFile = path.join(__dirname, 'webdav-requests.jsonl');
const objects = new Map();
let sequence = 0;
function log(record) { fs.appendFileSync(logFile, JSON.stringify({ utc: new Date().toISOString(), run: process.argv[2] || 'initial', ...record }) + '\n'); }
const server = http.createServer((req, res) => {
  const id = ++sequence;
  let body = '';
  req.on('data', chunk => { body += chunk; });
  req.on('end', () => {
    log({ event: 'request', id, method: req.method, path: req.url, bodyBytes: Buffer.byteLength(body), authPresent: Boolean(req.headers.authorization) });
    const delay = id === 1 ? 12000 : 0;
    setTimeout(() => {
      let status = 200;
      let response = '';
      if (req.method === 'PUT') { objects.set(req.url, body); status = 201; }
      else if (req.method === 'DELETE') { objects.delete(req.url); status = 204; }
      else if (req.method === 'MKCOL') { status = 201; }
      else if (req.method === 'GET') {
        if (objects.has(req.url)) response = objects.get(req.url);
        else status = 404;
      } else if (req.method === 'HEAD') {
        status = req.url.includes('.') && !objects.has(req.url) ? 404 : 200;
      } else if (req.method === 'PROPFIND') {
        status = 207;
        response = '<?xml version="1.0"?><d:multistatus xmlns:d="DAV:"></d:multistatus>';
      } else if (req.method !== 'OPTIONS') { status = 405; }
      res.writeHead(status, { 'Content-Type': req.method === 'PROPFIND' ? 'application/xml' : 'application/octet-stream', 'DAV': '1, 2' });
      res.end(req.method === 'HEAD' ? undefined : response);
      log({ event: 'response', id, method: req.method, path: req.url, status, delayMs: delay });
    }, delay);
  });
});
server.listen(18164, '127.0.0.1', () => { log({ event: 'listening', address: '127.0.0.1', port: 18164 }); });
process.on('SIGTERM', () => server.close(() => process.exit(0)));
