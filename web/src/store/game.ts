import { create } from "zustand";

import { type Agent, ApiError, type Game, type GameEvent, api } from "@/lib/api";

type Status = "idle" | "loading" | "ready" | "error";

interface GameStore {
  agents: Agent[];
  agentsStatus: Status;
  agentId: string | null;
  game: Game | null;
  /** Eventos que llegaron con la última respuesta (para animar solo lo nuevo). */
  fresh: GameEvent[];
  busy: boolean;
  error: string | null;
  analysis: boolean;
  loadAgents: () => Promise<void>;
  selectAgent: (id: string) => void;
  newGame: (seed?: number) => Promise<void>;
  play: (action: number) => Promise<void>;
  nextHand: () => Promise<void>;
  leave: () => void;
  toggleAnalysis: () => void;
  clearError: () => void;
}

function describe(err: unknown): string {
  if (err instanceof ApiError) {
    if (err.status === 404) return "La partida ya no existe en el servidor. Empezá otra.";
    return err.message;
  }
  return "No hay conexión con la mesa. Revisá que la API esté levantada y probá de nuevo.";
}

export const useGame = create<GameStore>((set, get) => ({
  agents: [],
  agentsStatus: "idle",
  agentId: null,
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
        agentId: s.agentId ?? agents.find((a) => a.id === "heuristic")?.id ?? agents[0]?.id ?? null,
      }));
    } catch (err) {
      set({ agentsStatus: "error", error: describe(err) });
    }
  },

  selectAgent: (id) => set({ agentId: id }),

  newGame: async (seed) => {
    const { agentId } = get();
    if (!agentId) return;
    set({ busy: true, error: null });
    try {
      const game = await api.createGame(agentId, seed);
      set({ game, fresh: game.events, busy: false });
    } catch (err) {
      set({ busy: false, error: describe(err) });
    }
  },

  play: async (action) => {
    const { game, busy } = get();
    if (!game || busy) return;
    set({ busy: true, error: null });
    try {
      const res = await api.play(game.id, action);
      set({ game: res.game, fresh: res.new_events, busy: false });
    } catch (err) {
      set({ busy: false, error: describe(err) });
    }
  },

  nextHand: async () => {
    const { game, busy } = get();
    if (!game || busy) return;
    set({ busy: true, error: null });
    try {
      const res = await api.nextHand(game.id);
      set({ game: res.game, fresh: res.new_events, busy: false });
    } catch (err) {
      set({ busy: false, error: describe(err) });
    }
  },

  leave: () => set({ game: null, fresh: [], error: null }),
  toggleAnalysis: () => set((s) => ({ analysis: !s.analysis })),
  clearError: () => set({ error: null }),
}));
