package com.matrixict.uhf;

import com.gg.reader.api.dal.GClient;
import com.gg.reader.api.dal.HandlerTagEpcLog;
import com.gg.reader.api.protocol.gx.EnumG;
import com.gg.reader.api.protocol.gx.LogBaseEpcInfo;
import com.gg.reader.api.protocol.gx.MsgBaseInventoryEpc;
import com.gg.reader.api.protocol.gx.MsgBaseStop;
import java.util.concurrent.ConcurrentLinkedQueue;

/**
 * All reader SDK calls live here in Java. Python only calls these simple methods
 * (String / int / boolean), so pyjnius never has to look up SDK classes from a
 * background thread (that fails with ClassNotFoundException and aborts the app).
 */
public class UhfBridge implements HandlerTagEpcLog {
    private final ConcurrentLinkedQueue<String> queue = new ConcurrentLinkedQueue<String>();
    private final GClient client;
    private String lastError = "";
    private boolean opened = false;

    public UhfBridge() {
        client = new GClient();
        client.onTagEpcLog = this;
    }

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

    /** param like "/dev/ttyS3:115200". Returns true when the reader answers a Stop command. */
    public boolean open(String param, int timeout) {
        try {
            if (!client.openAndroidSerial(param, timeout)) {
                lastError = "openAndroidSerial(" + param + ") returned false";
                return false;
            }
            MsgBaseStop stop = new MsgBaseStop();
            client.sendSynMsg(stop);
            if (stop.getRtCode() == 0) {
                opened = true;
                lastError = "";
                return true;
            }
            lastError = "Stop rtCode=" + stop.getRtCode() + " " + stop.getRtMsg() + " at " + param;
        } catch (Throwable t) {
            lastError = "open " + param + ": " + t;
        }
        try { client.close(); } catch (Throwable ignored) { }
        return false;
    }

    /** Returns "" on success, otherwise the error text. */
    public String startInventory() {
        try {
            queue.clear();
            MsgBaseInventoryEpc msg = new MsgBaseInventoryEpc();
            msg.setAntennaEnable(Long.valueOf(EnumG.AntennaNo_1));
            msg.setInventoryMode(EnumG.InventoryMode_Inventory);
            client.sendSynMsg(msg);
            if (msg.getRtCode() == 0) return "";
            lastError = "Inventory rtCode=" + msg.getRtCode() + " " + msg.getRtMsg();
        } catch (Throwable t) {
            lastError = "startInventory: " + t;
        }
        return lastError;
    }

    public void stopInventory() {
        try { client.sendUnsynMsg(new MsgBaseStop()); } catch (Throwable t) { lastError = "stop: " + t; }
    }

    public void close() {
        try { client.close(); } catch (Throwable ignored) { }
        opened = false;
    }

    public boolean isOpened() { return opened; }

    public String getLastError() { return lastError; }

    public String poll() { return queue.poll(); }

    public void clear() { queue.clear(); }
}
