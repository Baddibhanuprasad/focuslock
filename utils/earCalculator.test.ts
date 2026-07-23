import { describe, it, expect } from 'vitest';
import { calculateSingleEyeEAR, calculateAverageEAR, LandmarkPoint } from './earCalculator';

describe('EAR Calculator Unit Tests', () => {
  it('calculates high EAR for fully open eye coordinates', () => {
    // Simulated open eye landmark points (wide distance between top & bottom)
    const openEye: LandmarkPoint[] = [
      { x: 0.1, y: 0.5 }, // p1 (left corner)
      { x: 0.2, y: 0.4 }, // p2 (top-left)
      { x: 0.3, y: 0.4 }, // p3 (top-right)
      { x: 0.4, y: 0.5 }, // p4 (right corner)
      { x: 0.3, y: 0.6 }, // p5 (bottom-right)
      { x: 0.2, y: 0.6 }  // p6 (bottom-left)
    ];

    const ear = calculateSingleEyeEAR(openEye);
    expect(ear).toBeGreaterThan(0.25);
    expect(ear).toBeCloseTo(0.667, 2);
  });

  it('calculates low EAR for closed/squinted eye coordinates', () => {
    // Simulated closed eye (top and bottom points near zero vertical distance)
    const closedEye: LandmarkPoint[] = [
      { x: 0.1, y: 0.5 }, // p1
      { x: 0.2, y: 0.501 }, // p2
      { x: 0.3, y: 0.501 }, // p3
      { x: 0.4, y: 0.5 }, // p4
      { x: 0.3, y: 0.499 }, // p5
      { x: 0.2, y: 0.499 }  // p6
    ];

    const ear = calculateSingleEyeEAR(closedEye);
    expect(ear).toBeLessThan(0.1);
  });

  it('correctly averages left and right eye EAR values', () => {
    const leftEye: LandmarkPoint[] = [
      { x: 0.1, y: 0.5 }, { x: 0.2, y: 0.4 }, { x: 0.3, y: 0.4 },
      { x: 0.4, y: 0.5 }, { x: 0.3, y: 0.6 }, { x: 0.2, y: 0.6 }
    ];
    const rightEye: LandmarkPoint[] = [
      { x: 0.5, y: 0.5 }, { x: 0.6, y: 0.4 }, { x: 0.7, y: 0.4 },
      { x: 0.8, y: 0.5 }, { x: 0.7, y: 0.6 }, { x: 0.6, y: 0.6 }
    ];

    const avg = calculateAverageEAR(leftEye, rightEye);
    expect(avg).toBeGreaterThan(0.25);
  });
});
