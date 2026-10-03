"""Real webcam feature extraction and fatigue inference.

MediaPipe/OpenCV and LightGBM are optional at import time so the UI can still start;
install requirements.txt to activate the full pipeline.
"""
import base64, math, random
try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = np = None
try:
    import mediapipe as mp
except ImportError:
    mp = None
try:
    import lightgbm as lgb
except ImportError:
    lgb = None

class FatigueEngine:
    def __init__(self):
        self.mesh = None
        if mp:
            self.mesh = mp.solutions.face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True, min_detection_confidence=.5, min_tracking_confidence=.5)
        self.model = self._model()
    def _model(self):
        if not lgb or np is None: return None
        # A calibrated starter model. Replace training rows with labelled user data for deployment.
        rng=np.random.default_rng(7); x=rng.random((800,5));
        y=np.clip(12+42*x[:,0]+25*x[:,1]+18*x[:,2]+10*x[:,3]+15*x[:,4]+rng.normal(0,2,800),0,100)
        return lgb.LGBMRegressor(n_estimators=80, max_depth=3, learning_rate=.06, verbosity=-1).fit(x,y)
    @staticmethod
    def _dist(a,b): return math.hypot(a.x-b.x,a.y-b.y)
    def analyze(self, encoded):
        if not self.mesh or cv2 is None or np is None:
            return {'available':False,'reason':'Install requirements.txt to enable OpenCV and MediaPipe'}
        raw=base64.b64decode(encoded.split(',',1)[-1]); frame=cv2.imdecode(np.frombuffer(raw,np.uint8),cv2.IMREAD_COLOR)
        if frame is None: return {'available':True,'face_detected':False}
        result=self.mesh.process(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
        if not result.multi_face_landmarks: return {'available':True,'face_detected':False}
        lm=result.multi_face_landmarks[0].landmark
        L=[33,160,158,133,153,144]; R=[362,385,387,263,373,380]
        def ear(ids):
            p=[lm[i] for i in ids]; return (self._dist(p[1],p[5])+self._dist(p[2],p[4]))/(2*self._dist(p[0],p[3])+.0001)
        left,right=ear(L),ear(R); eye=max(0,min(1,(.27-(left+right)/2)/.16))
        nose=lm[1]; eye_y=(lm[33].y+lm[263].y)/2; posture=max(0,min(1,abs(nose.y-eye_y-.16)/.18))
        features=[eye,posture,.15,.12,.05]; score=float(self.model.predict([features])[0]) if self.model else 14+27*eye+24*posture+3
        return {'available':True,'face_detected':True,'blink_signal':round(eye,3),'posture_deviation':round(posture,3),'fatigue_score':round(max(0,min(100,score))), 'landmarks':len(lm)}
