import { useEffect, useState } from "react";
import { ActivityEvent, AnalysisStateResponse, fetchActivity, fetchAnalysisState, getErrorMessage, toWebSocketUrl } from "./api";

export function useBookAnalysisResource(bookId: number, enabled = true) {
  const [analysis, setAnalysis] = useState<AnalysisStateResponse | null>(null);
  const [activity, setActivity] = useState<ActivityEvent[]>([]);
  const [loading, setLoading] = useState(enabled);
  const [error, setError] = useState<string | null>(null);
  const [refreshTick, setRefreshTick] = useState(0);

  useEffect(() => {
    setAnalysis(null);
    setActivity([]);
    setLoading(enabled);
    setError(null);
    setRefreshTick(0);
  }, [bookId, enabled]);

  useEffect(() => {
    if (!enabled || !bookId) {
      return;
    }

    const timer = window.setInterval(() => {
      setRefreshTick((value) => value + 1);
    }, 5000);

    return () => {
      window.clearInterval(timer);
    };
  }, [bookId, enabled]);

  useEffect(() => {
    if (!enabled || !bookId) {
      return;
    }

    const socket = new WebSocket(toWebSocketUrl(`/api/ws/books/${bookId}/analysis`));
    socket.onmessage = () => {
      setRefreshTick((value) => value + 1);
    };
    socket.onerror = () => undefined;

    return () => {
      socket.close();
    };
  }, [bookId, enabled]);

  useEffect(() => {
    if (!enabled || !bookId) {
      return;
    }

    let active = true;

    async function load() {
      try {
        const [nextAnalysis, nextActivity] = await Promise.all([
          fetchAnalysisState(bookId),
          fetchActivity(bookId),
        ]);
        if (!active) {
          return;
        }
        setAnalysis(nextAnalysis);
        setActivity(nextActivity.items);
        setError(null);
      } catch (reason) {
        if (!active) {
          return;
        }
        setError(getErrorMessage(reason));
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    void load();

    return () => {
      active = false;
    };
  }, [bookId, enabled, refreshTick]);

  return {
    analysis,
    activity,
    loading,
    error,
    refresh: () => setRefreshTick((value) => value + 1),
  };
}
