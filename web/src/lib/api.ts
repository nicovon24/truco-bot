import type { components } from "./api-types";

export type Agent = components["schemas"]["AgentOut"];
export type Game = components["schemas"]["GameOut"];
export type GameEvent = components["schemas"]["EventOut"];
export type ActionResult = components["schemas"]["ActionResultOut"];
export type LegalAction = components["schemas"]["LegalActionOut"];
export type Card = components["schemas"]["CardOut"];

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export function apiBaseUrl(): string {
  return (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/+$/, "");
}

export function buildUrl(path: string, base: string = apiBaseUrl()): string {
  return `${base.replace(/\/+$/, "")}/${path.replace(/^\/+/, "")}`;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(buildUrl(path), {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
    cache: "no-store",
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = (await res.json()) as { detail?: unknown };
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      // cuerpo no JSON
    }
    throw new ApiError(res.status, detail);
  }
  return (await res.json()) as T;
}

export const api = {
  agents: () => request<Agent[]>("/agents"),
  createGame: (agentId: string, seed?: number) =>
    request<Game>("/games", {
      method: "POST",
      body: JSON.stringify({ agent_id: agentId, seed: seed ?? null }),
    }),
  game: (id: string) => request<Game>(`/games/${id}`),
  play: (id: string, action: number) =>
    request<ActionResult>(`/games/${id}/actions`, {
      method: "POST",
      body: JSON.stringify({ action }),
    }),
  nextHand: (id: string) => request<ActionResult>(`/games/${id}/next-hand`, { method: "POST" }),
};
