import { describe, expect, it } from "vitest";

import { buildUrl } from "./api";

describe("buildUrl", () => {
  it("une base y ruta sin barras duplicadas", () => {
    expect(buildUrl("/games", "http://api.test/")).toBe("http://api.test/games");
    expect(buildUrl("agents", "http://api.test")).toBe("http://api.test/agents");
  });
});
