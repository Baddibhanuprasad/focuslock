class AlarmSoundService {
  private audioCtx: AudioContext | null = null;
  private osc: OscillatorNode | null = null;
  private gainNode: GainNode | null = null;
  private isPlaying: boolean = false;
  private timerId: any = null;

  public startEscalatingAlarm() {
    if (this.isPlaying) return;
    this.isPlaying = true;

    try {
      const AudioCtxClass = window.AudioContext || (window as any).webkitAudioContext;
      this.audioCtx = new AudioCtxClass();
      
      this.gainNode = this.audioCtx.createGain();
      this.gainNode.gain.setValueAtTime(0.1, this.audioCtx.currentTime); // start at low volume

      this.osc = this.audioCtx.createOscillator();
      this.osc.type = 'sawtooth';
      this.osc.frequency.setValueAtTime(440, this.audioCtx.currentTime); // A4 note

      this.osc.connect(this.gainNode);
      this.gainNode.connect(this.audioCtx.destination);
      this.osc.start();

      // Escalating volume and tone pulses over 15 seconds
      let currentGain = 0.1;
      let pulseDirection = 1;
      this.timerId = setInterval(() => {
        if (!this.audioCtx || !this.gainNode || !this.osc) return;
        
        // Increase gain up to max 0.8
        if (currentGain < 0.8) {
          currentGain += 0.05;
        }

        // Pulse frequency between 440Hz and 880Hz for urgent alarm effect
        const now = this.audioCtx.currentTime;
        const newFreq = pulseDirection > 0 ? 880 : 440;
        pulseDirection *= -1;

        this.gainNode.gain.setValueAtTime(currentGain, now);
        this.osc.frequency.setValueAtTime(newFreq, now);
      }, 500);

    } catch (e) {
      console.error('Failed to initialize AudioContext alarm:', e);
    }
  }

  public stopAlarm() {
    if (this.timerId) {
      clearInterval(this.timerId);
      this.timerId = null;
    }

    if (this.osc) {
      try {
        this.osc.stop();
        this.osc.disconnect();
      } catch {}
      this.osc = null;
    }

    if (this.gainNode) {
      try {
        this.gainNode.disconnect();
      } catch {}
      this.gainNode = null;
    }

    if (this.audioCtx) {
      try {
        this.audioCtx.close();
      } catch {}
      this.audioCtx = null;
    }

    this.isPlaying = false;
  }
}

export const alarmAudio = new AlarmSoundService();
