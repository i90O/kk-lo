"use client";

import { useEffect, useRef } from "react";
import { getWSUrl } from "./api";
import { useAppStore } from "./store";

export function useWebSocket() {
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimer = useRef<ReturnType<typeof setTimeout>>(undefined);

    useEffect(() => {
        const addToast = useAppStore.getState().addToast;

        function connect() {
            try {
                const ws = new WebSocket(getWSUrl());
                wsRef.current = ws;

                ws.onopen = () => {
                    console.log("[WS] Connected to alerts");
                };

                ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        if (data.alert) {
                            addToast(
                                "warning",
                                `🔔 ${data.alert.ticker}: ${data.alert.type} - ${data.alert.interpretation}`
                            );
                        }
                    } catch {
                        // Non-JSON message
                    }
                };

                ws.onerror = () => {
                    // Silently handle - backend may not be running
                };

                ws.onclose = () => {
                    // Reconnect after 30 seconds
                    reconnectTimer.current = setTimeout(() => {
                        connect();
                    }, 30000);
                };
            } catch {
                // WebSocket connection failed
            }
        }

        connect();

        return () => {
            if (wsRef.current) wsRef.current.close();
            if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
        };
    }, []);

    return wsRef;
}
