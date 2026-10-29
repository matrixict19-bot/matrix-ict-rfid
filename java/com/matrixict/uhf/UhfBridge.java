package com.matrixict.uhf;

import com.gg.reader.api.dal.GClient;
import com.gg.reader.api.dal.HandlerTagEpcLog;
import com.gg.reader.api.protocol.gx.EnumG;
import com.gg.reader.api.protocol.gx.LogBaseEpcInfo;
import com.gg.reader.api.protocol.gx.MsgBaseInventoryEpc;
import com.gg.reader.api.protocol.gx.MsgBaseStop;
import android.app.Activity;
import android.content.Context;
import android.view.KeyEvent;
import android.view.View;
import android.view.inputmethod.InputMethodManager;
import android.view.Window;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.atomic.AtomicInteger;

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
            // same as the G2 demo: quick Stop first, in case a previous read is still running
            try { client.sendUnsynMsg(new MsgBaseStop()); } catch (Throwable ignored) { }
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

    // ---------------- physical trigger key (keycode 619 on this PDA) ----------------
    // SDL/Kivy drops key codes it does not know (619), so we catch it here in Java.
    private static final AtomicInteger keyPresses = new AtomicInteger(0);
    private static volatile int lastKeyCode = 0;
    private static Window.Callback originalCallback = null;

    public static void installKeyHook(final Activity activity) {
        activity.runOnUiThread(new Runnable() {
            public void run() {
                try {
                    final Window window = activity.getWindow();
                    if (originalCallback != null) return; // already installed
                    final Window.Callback orig = window.getCallback();
                    originalCallback = orig;
                    Window.Callback hook = (Window.Callback) Proxy.newProxyInstance(
                        Window.Callback.class.getClassLoader(),
                        new Class[]{Window.Callback.class},
                        new InvocationHandler() {
                            public Object invoke(Object proxy, Method m, Object[] args) throws Throwable {
                                if ("dispatchKeyEvent".equals(m.getName()) && args != null && args.length == 1
                                        && args[0] instanceof KeyEvent) {
                                    KeyEvent ev = (KeyEvent) args[0];
                                    int code = ev.getKeyCode();
                                    if (code >= 600) {
                                        lastKeyCode = code;
                                        if (ev.getAction() == KeyEvent.ACTION_DOWN && ev.getRepeatCount() == 0) {
                                            keyPresses.incrementAndGet();
                                        }
                                        return Boolean.TRUE;
                                    }
                                }
                                try {
                                    return m.invoke(orig, args);
                                } catch (java.lang.reflect.InvocationTargetException e) {
                                    throw e.getCause();
                                }
                            }
                        });
                    window.setCallback(hook);
                } catch (Throwable t) {
                    originalCallback = null;
                }
            }
        });
    }

    public static void removeKeyHook(final Activity activity) {
        activity.runOnUiThread(new Runnable() {
            public void run() {
                try {
                    if (originalCallback != null) activity.getWindow().setCallback(originalCallback);
                } catch (Throwable ignored) { }
                originalCallback = null;
            }
        });
    }

    /** Number of trigger presses since the last call (then reset to 0). */
    public static int takeKeyPresses() { return keyPresses.getAndSet(0); }

    public static int getLastKeyCode() { return lastKeyCode; }

    // ---------------- system scan service (android.bld.ScanManager) ----------------
    /** false = the system barcode scanner stops grabbing the trigger key (demo does this). */
    public static String setScannerHandleKey(Context ctx, boolean handle) {
        try {
            Class<?> c = Class.forName("android.bld.ScanManager");
            Object sm = c.getMethod("getDefaultInstance", Context.class).invoke(null, ctx);
            c.getMethod("setHandleKey", boolean.class).invoke(sm, handle);
            return "";
        } catch (Throwable t) {
            return "ScanManager: " + t;
        }
    }

    // ---------------- on-screen keyboard (scan field) ----------------
    /** Hide the soft keyboard but keep the text field focused (scanner input keeps working). */
    public static void hideKeyboard(final Activity activity) {
        activity.runOnUiThread(new Runnable() {
            public void run() {
                try {
                    InputMethodManager imm = (InputMethodManager) activity.getSystemService(Context.INPUT_METHOD_SERVICE);
                    View v = activity.getCurrentFocus();
                    if (v == null) v = activity.getWindow().getDecorView();
                    imm.hideSoftInputFromWindow(v.getWindowToken(), 0);
                } catch (Throwable ignored) { }
            }
        });
    }

    /** Show the soft keyboard (user tapped the scan field). */
    public static void showKeyboard(final Activity activity) {
        activity.runOnUiThread(new Runnable() {
            public void run() {
                try {
                    InputMethodManager imm = (InputMethodManager) activity.getSystemService(Context.INPUT_METHOD_SERVICE);
                    View v = activity.getCurrentFocus();
                    if (v != null) imm.showSoftInput(v, 0);
                } catch (Throwable ignored) { }
            }
        });
    }
}
