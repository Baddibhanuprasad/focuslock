export interface LandmarkPoint {
  x: number;
  y: number;
  z?: number;
}

/**
 * Calculates Euclidean distance between two 2D/3D points.
 */
export function euclideanDistance(p1: LandmarkPoint, p2: LandmarkPoint): number {
  const dx = p1.x - p2.x;
  const dy = p1.y - p2.y;
  const dz = (p1.z || 0) - (p2.z || 0);
  return Math.sqrt(dx * dx + dy * dy + dz * dz);
}

/**
 * Calculates Eye Aspect Ratio (EAR) for a single eye given 6 eye landmarks.
 * Formula: EAR = (|p2 - p6| + |p3 - p5|) / (2 * |p1 - p4|)
 * 
 * Order of landmark points array:
 * [p1: left corner, p2: top-left, p3: top-right, p4: right corner, p5: bottom-right, p6: bottom-left]
 */
export function calculateSingleEyeEAR(eyePoints: LandmarkPoint[]): number {
  if (!eyePoints || eyePoints.length < 6) return 0.3; // default open eye fallback

  const p1 = eyePoints[0];
  const p2 = eyePoints[1];
  const p3 = eyePoints[2];
  const p4 = eyePoints[3];
  const p5 = eyePoints[4];
  const p6 = eyePoints[5];

  const vertical1 = euclideanDistance(p2, p6);
  const vertical2 = euclideanDistance(p3, p5);
  const horizontal = euclideanDistance(p1, p4);

  if (horizontal === 0) return 0;

  return (vertical1 + vertical2) / (2.0 * horizontal);
}

/**
 * Calculates average EAR across both left and right eyes.
 */
export function calculateAverageEAR(leftEyePoints: LandmarkPoint[], rightEyePoints: LandmarkPoint[]): number {
  const leftEAR = calculateSingleEyeEAR(leftEyePoints);
  const rightEAR = calculateSingleEyeEAR(rightEyePoints);
  return (leftEAR + rightEAR) / 2.0;
}
