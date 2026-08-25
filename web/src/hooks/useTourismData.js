import { useContext } from "react";
import { TourismDataContext } from "../context/tourismDataContext";

export function useTourismData() {
  const context = useContext(TourismDataContext);
  if (context === undefined) {
    throw new Error("useTourismData must be used within a TourismDataProvider");
  }
  return context;
}
