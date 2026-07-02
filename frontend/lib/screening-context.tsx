"use client";

import { createContext, useContext, useState, ReactNode } from "react";
import type { ScreenResponse } from "@/lib/api";

interface ScreeningContextValue {
  result: ScreenResponse | null;
  setResult: (result: ScreenResponse | null) => void;
}

const ScreeningContext = createContext<ScreeningContextValue | undefined>(undefined);

export function ScreeningProvider({ children }: { children: ReactNode }) {
  const [result, setResult] = useState<ScreenResponse | null>(null);
  return (
    <ScreeningContext.Provider value={{ result, setResult }}>
      {children}
    </ScreeningContext.Provider>
  );
}

export function useScreening() {
  const context = useContext(ScreeningContext);
  if (!context) {
    throw new Error("useScreening must be used within a ScreeningProvider");
  }
  return context;
}
