// Runs the pulse-in-time computation off the main thread: settings in, all frames out.
import { runPulses, type PulseOpts } from "./pulsetime";

self.onmessage = (e: MessageEvent<{ id: number; o: PulseOpts }>) => {
  (self as unknown as Worker).postMessage({ id: e.data.id, out: runPulses(e.data.o) });
};
