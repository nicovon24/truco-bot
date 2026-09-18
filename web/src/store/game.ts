import { create } from "zustand";

import {
  type Agent,
  ApiError,
  type Game,
  type GameEvent,
  api,
} from "@/lib/api";

type Status = "idle" | "loading" | "ready" | "error";
export type TargetScore = 15 | 30;

// Ignore in-flight responses after leaving or starting a different match.
let gameGeneration = 0;

interface GameStore {
  agents: Agent[];
  agentsStatus: Status;
  agentId: string | null;
  targetScore: TargetScore;
  game: Game | null;
  /** Eventos que llegaron con la última respuesta (para animar solo lo nuevo). */
  fresh: GameEvent[];
  busy: boolean;
  error: string | null;
  analysis: boolean;
  loadAgents: () => Promise<void>;
  selectAgent: (id: string) => void;
  selectTargetScore: (score: TargetScore) => void;
  newGame: (seed?: number) => Promise<void>;
  play: (action: number) => Promise<void>;
  nextHand: () => Promise<void>;
  leave: () => void;
  toggleAnalysis: () => void;
  clearError: () => void;
}

function describe(err: unknown): string {
  if (err instanceof ApiError) {
    if (err.status === 404)
      return "La partida ya no existe en el servidor. Empezá otra.";
    return err.message;
  }
  return "No hay conexión con la mesa. Revisá que la API esté levantada y probá de nuevo.";
}

export const useGame = create<GameStore>((set, get) => ({
  agents: [],
  agentsStatus: "idle",
  agentId: null,
  targetScore: 15,
  game: null,
  fresh: [],
  busy: false,
  error: null,
  analysis: false,

  loadAgents: async () => {
    set({ agentsStatus: "loading", error: null });
    try {
      const agents = await api.agents();
      set((s) => ({
        agents,
        agentsStatus: "ready",
        agentId:
          s.agentId ??
          agents.find((a) => a.id === "heuristic")?.id ??
          agents[0]?.id ??
          null,
      }));
    } catch (err) {
      set({ agentsStatus: "error", error: describe(err) });
    }
  },

  selectAgent: (id) => set({ agentId: id }),
  selectTargetScore: (targetScore) => set({ targetScore }),

  newGame: async (seed) => {
    const { agentId, targetScore, busy } = get();
    if (!agentId || busy) return;
    const generation = ++gameGeneration;
    set({ busy: true, error: null });
    try {
      const game = await api.createGame(agentId, targetScore, seed);
      if (generation !== gameGeneration) return;
      set({ game, fresh: game.events, busy: false });
    } catch (err) {
      if (generation !== gameGeneration) return;
      set({ busy: false, error: describe(err) });
    }
  },

  play: async (action) => {
    const { game, busy } = get();
    if (!game || busy) return;
    const generation = gameGeneration;
    set({ busy: true, error: null });
    try {
      const res = await api.play(game.id, action);
      if (generation !== gameGeneration) return;
      set({ game: res.game, fresh: res.new_events, busy: false });
    } catch (err) {
      if (generation !== gameGeneration) return;
      set({ busy: false, error: describe(err) });
    }
  },

  nextHand: async () => {
    const { game, busy } = get();
    if (!game || busy) return;
    const generation = gameGeneration;
    set({ busy: true, error: null });
    try {
      const res = await api.nextHand(game.id);
      if (generation !== gameGeneration) return;
      set({ game: res.game, fresh: res.new_events, busy: false });
    } catch (err) {
      if (generation !== gameGeneration) return;
      set({ busy: false, error: describe(err) });
    }
  },

  leave: () => {
    gameGeneration += 1;
    set({ game: null, fresh: [], error: null, busy: false, analysis: false });
  },
  toggleAnalysis: () => set((s) => ({ analysis: !s.analysis })),
  clearError: () => set({ error: null }),
}));
