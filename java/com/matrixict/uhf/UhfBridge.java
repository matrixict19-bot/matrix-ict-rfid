package com.matrixict.uhf;

import com.gg.reader.api.dal.GClient;
import com.gg.reader.api.dal.HandlerTagEpcLog;
import com.gg.reader.api.protocol.gx.LogBaseEpcInfo;
import java.util.concurrent.ConcurrentLinkedQueue;

/** Receives tag callbacks in Java (no Python proxy needed) and lets Python poll them. */
public class UhfBridge implements HandlerTagEpcLog {
    private final ConcurrentLinkedQueue<String> queue = new ConcurrentLinkedQueue<String>();

    @Override
    public void log(String readerName, LogBaseEpcInfo info) {
        try {
            if (info == null || info.getResult() != 0) return;
            String epc = info.getEpc();
            if (epc != null && epc.length() > 0) queue.add(epc);
        } catch (Throwable t) {
            // never let a callback exception reach the reader thread
        }
    }

    public static UhfBridge attach(GClient client) {
        UhfBridge bridge = new UhfBridge();
        client.onTagEpcLog = bridge;
        return bridge;
    }

    public String poll() { return queue.poll(); }

    public void clear() { queue.clear(); }
}
