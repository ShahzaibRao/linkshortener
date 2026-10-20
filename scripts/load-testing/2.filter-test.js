import http from 'k6/http';
import { check } from 'k6';

const BASE = 'http://127.0.0.1:8080';

function randomCode() {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
  let s = '';
  for (let i = 0; i < 8; i++) s += chars[Math.floor(Math.random() * chars.length)];
  return s;
}

function randomSeedCode() {
  return 'seed' + String(Math.floor(Math.random() * 100000)).padStart(6, '0');
}

export default function () {
  // 90% miss (random code), 10% hit (seed code — sab filters mein hai)
  const isHit = Math.random() < 0.1;
  const code = isHit ? randomSeedCode() : randomCode();
  const res = http.get(`${BASE}/${code}`, { redirects: 0 });
  if (isHit) {
    check(res, { 'hit -> 307': (r) => r.status === 307 });
  } else {
    check(res, { 'miss -> 404': (r) => r.status === 404 });
  }
}

