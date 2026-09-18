"use client";

import { Cartelera } from "@/components/Cartelera";
import { Mesa } from "@/components/Mesa";
import { useGame } from "@/store/game";

export default function Home() {
  const game = useGame((s) => s.game);
  return game ? <Mesa game={game} /> : <Cartelera />;
}
