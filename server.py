"""Mindful wellness API. Runs with Python's standard library; optional CV/ML packages enhance frame analysis."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path
from datetime import datetime, timezone
import json, math, random, threading, uuid, base64
try:
    from ai_engine import FatigueEngine
    AI = FatigueEngine()
except Exception as exc:
    AI = None

ROOT = Path(__file__).parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
DB = DATA / "sessions.json"
lock = threading.Lock()

def read_sessions():
    if not DB.exists(): return []
    try: return json.loads(DB.read_text())
    except (OSError, json.JSONDecodeError): return []

def save_sessions(items): DB.write_text(json.dumps(items[-100:], indent=2))

def fatigue_score(s):
    """Transparent baseline model; replace with trained LightGBM in production."""
    blink = max(0, min(1, (18 - float(s.get('blink_rate', 17))) / 12))
    posture = max(0, min(1, float(s.get('posture_deviation', 0.1))))
    typing = max(0, min(1, float(s.get('typing_drop', 0.1))))
    mouse = max(0, min(1, float(s.get('inactivity', 0.1))))
    screen = max(0, min(1, float(s.get('screen_minutes', 0)) / 180))
    return round(max(0, min(100, 14 + 27*blink + 24*posture + 18*typing + 12*mouse + 15*screen)))

def recommendation(score):
    if score >= 70: return {"type":"recovery", "title":"Take a longer reset", "body":"Your fatigue signals are elevated. Step away for 5 minutes and hydrate.", "duration":300}
    if score >= 45: return {"type":"posture", "title":"Reset your posture", "body":"Roll your shoulders back, relax your jaw, and look 20 feet away.", "duration":60}
    return {"type":"breathing", "title":"Box breathing", "body":"Inhale, hold, exhale, and hold for four counts each.", "duration":60}

class Handler(SimpleHTTPRequestHandler):
    def end_json(self, status, payload):
        raw = json.dumps(payload).encode()
        self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(raw))); self.send_header('Access-Control-Allow-Origin','*'); self.end_headers(); self.wfile.write(raw)
    def do_OPTIONS(self): self.send_response(204); self.send_header('Access-Control-Allow-Origin','*'); self.send_header('Access-Control-Allow-Headers','Content-Type'); self.end_headers()
    def body(self):
        n=int(self.headers.get('Content-Length','0')); return json.loads(self.rfile.read(n) or b'{}')
    def do_GET(self):
        path=urlparse(self.path).path
        if path == '/api/health': return self.end_json(200, {'ok':True,'service':'mindful-api','time':datetime.now(timezone.utc).isoformat()})
        if path == '/api/history': return self.end_json(200, {'sessions':read_sessions()})
        return super().do_GET()
    def do_POST(self):
        path=urlparse(self.path).path
        try: payload=self.body()
        except Exception: return self.end_json(400, {'error':'Invalid JSON'})
        if path == '/api/session/start':
            sid=uuid.uuid4().hex; now=datetime.now(timezone.utc).isoformat()
            session={'id':sid,'started_at':now,'ended_at':None,'metrics':[],'breaks':0}
            with lock:
                sessions=read_sessions(); sessions.append(session); save_sessions(sessions)
            return self.end_json(201, {'session_id':sid,'started_at':now})
        if path == '/api/frame':
            if not AI: return self.end_json(503, {'available':False,'reason':'AI engine unavailable; install requirements.txt'})
            result=AI.analyze(payload.get('image',''))
            sid=payload.get('session_id')
            if sid and result.get('available') and result.get('face_detected'):
                signals={'blink_rate':17,'posture_deviation':result.get('posture_deviation',0.1),'typing_drop':0.1,'inactivity':0.1,'screen_minutes':0}
                result['fatigue_score']=fatigue_score(signals) if 'fatigue_score' not in result else result['fatigue_score']
            return self.end_json(200,result)
        if path == '/api/session/metric':
            sid=payload.get('session_id'); signals=payload.get('signals',payload); score=payload.get('fatigue_score',fatigue_score(signals))
            with lock:
                sessions=read_sessions(); item=next((x for x in sessions if x['id']==sid),None)
                if not item: return self.end_json(404, {'error':'Session not found'})
                item['metrics'].append({'at':datetime.now(timezone.utc).isoformat(),'signals':signals,'fatigue_score':score}); save_sessions(sessions)
            return self.end_json(200, {'fatigue_score':score,'recommendation':recommendation(score)})
        if path == '/api/session/end':
            with lock:
                sessions=read_sessions(); item=next((x for x in sessions if x['id']==payload.get('session_id')),None)
                if not item: return self.end_json(404, {'error':'Session not found'})
                item['ended_at']=datetime.now(timezone.utc).isoformat(); save_sessions(sessions)
            return self.end_json(200, {'ok':True})
        if path == '/api/intervention':
            with lock:
                sessions=read_sessions(); item=next((x for x in sessions if x['id']==payload.get('session_id')),None)
                if item: item['breaks'] += 1; save_sessions(sessions)
            return self.end_json(200, {'ok':True,'message':'Intervention recorded'})
        return self.end_json(404, {'error':'Unknown endpoint'})
    def log_message(self, fmt, *args):
        if not self.path.startswith('/api'): super().log_message(fmt,*args)

if __name__ == '__main__':
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--port',type=int,default=4173); args=p.parse_args()
    print(f'Mindful API running at http://0.0.0.0:{args.port}')
    ThreadingHTTPServer(('0.0.0.0',args.port),Handler).serve_forever()
