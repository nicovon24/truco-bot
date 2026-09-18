import { beforeEach, describe, expect, it, vi } from "vitest";
import { api, type Game } from "@/lib/api";
import { useGame } from "./game";

vi.mock("@/lib/api", async (original) => ({
  ...(await original<typeof import("@/lib/api")>()),
  api: {
    createGame: vi.fn(),
    play: vi.fn(),
    nextHand: vi.fn(),
    agents: vi.fn(),
  },
}));

beforeEach(() => {
  useGame.getState().leave();
  useGame.setState({ agentId: "heuristic", targetScore: 15 });
  vi.clearAllMocks();
});

describe("game requests during navigation", () => {
  it("does not reopen a match when a late action response arrives after leaving", async () => {
    const game = { id: "old", events: [] } as unknown as Game;
    useGame.setState({ game });
    let finish!: (value: Awaited<ReturnType<typeof api.play>>) => void;
    vi.mocked(api.play).mockImplementation(
      () =>
        new Promise((resolve) => {
          finish = resolve;
        }),
    );
    const request = useGame.getState().play(0);
    useGame.getState().leave();
    finish({ game, new_events: [] });
    await request;
    expect(useGame.getState().game).toBeNull();
    expect(useGame.getState().busy).toBe(false);
  });
  it("ignores an error from a match the player already left", async () => {
    useGame.setState({ game: { id: "old" } as Game });
    let fail!: (reason: Error) => void;
    vi.mocked(api.nextHand).mockImplementation(
      () =>
        new Promise((_, reject) => {
          fail = reject;
        }),
    );
    const request = useGame.getState().nextHand();
    useGame.getState().leave();
    fail(new Error("disconnected"));
    await request;
    expect(useGame.getState().error).toBeNull();
  });
  it("prevents a double click from creating two matches", async () => {
    let finish!: (value: Game) => void;
    vi.mocked(api.createGame).mockImplementation(
      () =>
        new Promise((resolve) => {
          finish = resolve;
        }),
    );
    const first = useGame.getState().newGame();
    const second = useGame.getState().newGame();
    expect(api.createGame).toHaveBeenCalledTimes(1);
    expect(api.createGame).toHaveBeenCalledWith("heuristic", 15, undefined);
    finish({ id: "new", events: [] } as unknown as Game);
    await Promise.all([first, second]);
    expect(useGame.getState().game?.id).toBe("new");
  });

  it("sends the selected match length when creating a game", async () => {
    useGame.getState().selectTargetScore(30);
    vi.mocked(api.createGame).mockResolvedValue({
      id: "long",
      target_score: 30,
      events: [],
    } as unknown as Game);
    await useGame.getState().newGame(42);
    expect(api.createGame).toHaveBeenCalledWith("heuristic", 30, 42);
    expect(useGame.getState().game?.target_score).toBe(30);
  });
});
