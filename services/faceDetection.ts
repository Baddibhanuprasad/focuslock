import { FaceMesh } from '@mediapipe/face_mesh';
import { calculateAverageEAR, LandmarkPoint } from '../utils/earCalculator';
import { PresenceStatus } from '../../../shared/src/types';

// MediaPipe 6-point landmark indices for left and right eyes
const LEFT_EYE_INDICES = [33, 160, 158, 133, 153, 144];
const RIGHT_EYE_INDICES = [362, 385, 387, 263, 373, 380];

export class FaceDetectionService {
  private videoElement: HTMLVideoElement | null = null;
  private faceMesh: FaceMesh | null = null;
  private isRunning: boolean = false;
  private animFrameId: number | null = null;
  private lowEARStartTimestamp: number | null = null;
  private lastPresenceStatus: PresenceStatus = 'UNKNOWN';
  private noFaceTimer: number = 0;

  constructor(
    private onEARCalculated?: (ear: number) => void,
    private onDrowsinessDetected?: (ear: number) => void,
    private onPresenceChanged?: (presence: PresenceStatus) => void
  ) {}

  public async start(
    videoEl: HTMLVideoElement,
    threshold: number = 0.21,
    sensitivityDurationMs: number = 2000
  ) {
    if (this.isRunning) return;
    this.videoElement = videoEl;
    this.isRunning = true;

    try {
      // Initialize webcam stream
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, frameRate: 15 }
      });
      this.videoElement.srcObject = stream;
      await this.videoElement.play();

      // Initialize MediaPipe FaceMesh
      this.faceMesh = new FaceMesh({
        locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`
      });

      this.faceMesh.setOptions({
        maxNumFaces: 1,
        refineLandmarks: true,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5
      });

      this.faceMesh.onResults((results) => {
        this.processMeshResults(results, threshold, sensitivityDurationMs);
      });

      this.processVideoFrames();
      console.log('[FocusLock FaceDetection] Webcam face monitoring started');
    } catch (e) {
      console.error('[FocusLock FaceDetection] Failed to access webcam:', e);
      if (this.onPresenceChanged) {
        this.onPresenceChanged('UNKNOWN');
      }
    }
  }

  private processVideoFrames = async () => {
    if (!this.isRunning || !this.videoElement || !this.faceMesh) return;
    if (this.videoElement.readyState >= 2) {
      await this.faceMesh.send({ image: this.videoElement });
    }
    // Frequency throttling: check frame every ~150ms for low CPU usage
    setTimeout(() => {
      if (this.isRunning) {
        this.animFrameId = requestAnimationFrame(this.processVideoFrames);
      }
    }, 150);
  };

  private processMeshResults(results: any, threshold: number, sensitivityDurationMs: number) {
    if (results.multiFaceLandmarks && results.multiFaceLandmarks.length > 0) {
      this.noFaceTimer = 0;
      this.updatePresence('USER_PRESENT');

      const landmarks = results.multiFaceLandmarks[0];
      const leftEye: LandmarkPoint[] = LEFT_EYE_INDICES.map(idx => landmarks[idx]);
      const rightEye: LandmarkPoint[] = RIGHT_EYE_INDICES.map(idx => landmarks[idx]);

      const ear = calculateAverageEAR(leftEye, rightEye);

      if (this.onEARCalculated) {
        this.onEARCalculated(ear);
      }

      // Check Drowsiness threshold
      if (ear < threshold) {
        if (!this.lowEARStartTimestamp) {
          this.lowEARStartTimestamp = Date.now();
        } else if (Date.now() - this.lowEARStartTimestamp >= sensitivityDurationMs) {
          console.warn(`[FocusLock Drowsiness] Drowsiness triggered! EAR=${ear.toFixed(3)} for ${sensitivityDurationMs}ms`);
          if (this.onDrowsinessDetected) {
            this.onDrowsinessDetected(ear);
          }
          this.lowEARStartTimestamp = null; // reset until next trigger
        }
      } else {
        this.lowEARStartTimestamp = null;
      }
    } else {
      // No face detected
      this.noFaceTimer += 150;
      if (this.noFaceTimer >= 3000) { // 3 seconds without face = USER_AWAY
        this.updatePresence('USER_AWAY');
      }
    }
  }

  private updatePresence(status: PresenceStatus) {
    if (this.lastPresenceStatus !== status) {
      this.lastPresenceStatus = status;
      if (this.onPresenceChanged) {
        this.onPresenceChanged(status);
      }
    }
  }

  public stop() {
    this.isRunning = false;
    if (this.animFrameId) {
      cancelAnimationFrame(this.animFrameId);
      this.animFrameId = null;
    }
    if (this.videoElement && this.videoElement.srcObject) {
      const stream = this.videoElement.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      this.videoElement.srcObject = null;
    }
    if (this.faceMesh) {
      this.faceMesh.close();
      this.faceMesh = null;
    }
    console.log('[FocusLock FaceDetection] Webcam face monitoring stopped');
  }
}
