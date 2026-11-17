// Runs the Richards–Wolf sums off the main thread: a list of jobs (points and settings) in, the 2CE and 2PE signals out.
import { rwSignals, type RWOpts } from "./rw";

type Job = { x: number[]; z: number[]; o: RWOpts };
self.onmessage = (e: MessageEvent<{ id: number; jobs: Job[] }>) => {
  const { id, jobs } = e.data;
  (self as unknown as Worker).postMessage({ id, out: jobs.map((j) => rwSignals(j.x, j.z, j.o)) });
};
