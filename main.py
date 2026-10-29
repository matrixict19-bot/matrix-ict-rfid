
# MATRIX ICT - V27 - V21 BASE + IMPORT/EXPORT ANYWHERE + UHF PHYSICAL BUTTON FIX - 5 POINTS
import sqlite3, os, traceback, random, sys, time, threading, collections
from datetime import datetime

# Global crash catcher - writes even on Python crash
def get_app_folder_safe():
    # V25 - V21 BASE FIX 5 POINTS - private folder only, NO Download to avoid Permission Denied
    try:
        from android.storage import app_storage_path
        p = app_storage_path()
        if p:
            return p
    except:
        pass
    try:
        folder = os.path.dirname(os.path.abspath(__file__))
    except:
        folder = os.getcwd()
    return folder

APP_FOLDER = get_app_folder_safe()
DB_PATH = os.path.join(APP_FOLDER, "rfid.db")
LOG_PATH = os.path.join(APP_FOLDER, "rfid_crash_log.txt")

EXT_LOG_DIR = "/storage/emulated/0/Android/data/com.matrixict.rfid.matrixictrfid/files"
EXT_LOG_PATH = os.path.join(EXT_LOG_DIR, "rfid_crash_log.txt")

def _ext_log(text):
    try:
        os.makedirs(EXT_LOG_DIR, exist_ok=True)
        with open(EXT_LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(text)
    except:
        pass

def log_to_file(msg):
    line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n"
    try:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(line)
    except:
        pass
    _ext_log(line)

def handle_exception(exc_type, exc_value, exc_tb):
    _ext_log(f"\n=== CRASH {datetime.now()} ===\n" + ''.join(traceback.format_exception(exc_type, exc_value, exc_tb)) + "\n")
    try:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(f"\n=== CRASH {datetime.now()} ===\n")
            f.write(''.join(traceback.format_exception(exc_type, exc_value, exc_tb)))
            f.write("\n")
    except:
        pass
    # Call original
    sys.__excepthook__(exc_type, exc_value, exc_tb)

sys.excepthook = handle_exception

try:
    import faulthandler
    os.makedirs(EXT_LOG_DIR, exist_ok=True)
    _fh = open(os.path.join(EXT_LOG_DIR, "rfid_native_crash.txt"), 'a')
    faulthandler.enable(file=_fh, all_threads=True)
except Exception:
    pass
_ext_log(f"=== process start {datetime.now()} ===\n")

try:
    os.makedirs(APP_FOLDER, exist_ok=True)
    with open(LOG_PATH, 'w', encoding='utf-8') as f:
        f.write(f"=== V17 Started - Fixed bold TextInput {datetime.now()} ===\n")
        f.write(f"Folder: {APP_FOLDER}\n")
        f.write(f"Files: {os.listdir(APP_FOLDER)[:15]}\n")
except Exception as e:
    print(f"Log init fail: {e}")

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup

BG = "#F5F5F5"
PRIMARY = "#FF8C00"
SECONDARY = "#2B2E33"

def find_logo():
    # V25 - V21 BASE - search only private folder and cwd, NO Download
    for d in [APP_FOLDER, os.getcwd()]:
        if not d:
            continue
        try:
            if not os.path.exists(d):
                continue
        except:
            continue
        for name in ["logo.png", "logo_header.png", "icon.png"]:
            p = os.path.join(d, name)
            try:
                if os.path.exists(p):
                    return p
            except:
                continue
    return None

def make_safe_card():
    # FIX BLANK SCREEN - was missing in V18, caused NameError in Pydroid3 and APK
    return BoxLayout(orientation='vertical', padding=12, spacing=6, size_hint_y=None)

APP_VERSION = "v0.30"

def wrap_label(text='', font_size=24, color=(0,0,0,1), bold=False, halign='left', min_height=0):
    """Label that wraps to its width and grows in height to show ALL its text (never cut)."""
    lbl = Label(text=text, size_hint_y=None, font_size=font_size, color=color, bold=bold,
                halign=halign, valign='middle')
    def _w(w, width):
        w.text_size = (width, None)
    def _h(w, ts):
        w.height = max(min_height, ts[1] + 6)
    lbl.bind(width=_w, texture_size=_h)
    return lbl

def make_header():
    """Big logo + version, same on every screen."""
    header = BoxLayout(size_hint_y=None, height=120, padding=(10, 6), spacing=8)
    logo_path = find_logo()
    if logo_path:
        try:
            from kivy.uix.image import Image
            header.add_widget(Image(source=logo_path, size_hint_x=0.8, allow_stretch=True, keep_ratio=True))
        except Exception:
            header.add_widget(Label(text='[b][color=2B2E33]MATRIX[/color][color=FF8C00] ICT[/color][/b]', markup=True, font_size=34, size_hint_x=0.8))
    else:
        header.add_widget(Label(text='[b][color=2B2E33]MATRIX[/color][color=FF8C00] ICT[/color][/b]', markup=True, font_size=34, size_hint_x=0.8))
    header.add_widget(Label(text=f'[b][color=FF8C00]{APP_VERSION}[/color][/b]', markup=True, font_size=20, size_hint_x=0.2))
    return header

def init_db(db_path):
    try:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        log_to_file(f"init_db: {db_path}")
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS Items (ItemID INTEGER PRIMARY KEY, ItemLookupCode TEXT, Description TEXT, Subdescription1 TEXT, Subdescription2 TEXT, Subdescription3 TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS Barcod (BarcodID INTEGER PRIMARY KEY AUTOINCREMENT, ItemID INTEGER, Barcode TEXT UNIQUE)")
        c.execute("CREATE TABLE IF NOT EXISTS RFID (AutoID INTEGER PRIMARY KEY AUTOINCREMENT, ItemID INTEGER, RFID_CODE TEXT UNIQUE)")
        c.execute("SELECT count(*) FROM Items")
        cnt = c.fetchone()[0]
        conn.commit()
        conn.close()
        log_to_file(f"DB OK: {cnt}")
        return cnt
    except Exception as e:
        log_to_file(f"DB ERROR: {e} {traceback.format_exc()}")
        return 0

def find_csv():
    # V25 - 5 POINTS - DO NOT look at Download folder, only private + Download
    for d in [APP_FOLDER, "/storage/emulated/0/Download", "/sdcard/Download", os.getcwd()]:
        if not d:
            continue
        try:
            if not os.path.exists(d):
                continue
        except:
            continue
        for name in ["Matrix_Items.csv", "MATRIX_Items.csv", "matrix_items.csv", "items.csv"]:
            p = os.path.join(d, name)
            try:
                if os.path.exists(p):
                    return p
            except:
                continue
    return None

def _make_epc_handler(callback):
    """Java HandlerTagEpcLog implemented in Python (called from the SDK's reader thread)."""
    from jnius import PythonJavaClass, java_method

    class EpcHandler(PythonJavaClass):
        __javainterfaces__ = ['com/gg/reader/api/dal/HandlerTagEpcLog']
        __javacontext__ = 'app'

        @java_method('(Ljava/lang/String;Lcom/gg/reader/api/protocol/gx/LogBaseEpcInfo;)V')
        def log(self, reader_name, info):
            try:
                callback(info)
            except Exception as e:
                log_to_file(f"EpcHandler err: {e}")

    return EpcHandler()


class UHFManager_G2_Real:
    """GXWL GClient reader. Every SDK call is done in Java (com.matrixict.uhf.UhfBridge).
    Python only: (1) creates the bridge on the MAIN thread (preload), (2) writes the power
    file, (3) calls simple bridge methods (String/int/bool) from a worker thread.
    Sequence = G2_UHFReaderDemo: power 1 -> openAndroidSerial('/dev/ttyS3:baud') -> Stop ack
    -> MsgBaseInventoryEpc; tags arrive in the Java onTagEpcLog callback and are polled."""
    UHF_POWER_PATH = "/proc/gpiocontrol/set_uhf"
    SERIAL_PORT = "/dev/ttyS3"
    BAUDS = (460800, 115200)  # same order as the G2 demo app

    def __init__(self):
        self.bridge = None
        self.has_g2 = True
        self.is_inventorying = False
        self.is_open = False
        self.sdk_version = "GClient via UhfBridge"
        self.last_error = ""
        self._open_lock = threading.Lock()

    def preload(self):
        """MUST run on the main (Kivy) thread: app classes can only be found there."""
        if self.bridge is not None:
            return True
        try:
            from jnius import autoclass
            Bridge = autoclass('com.matrixict.uhf.UhfBridge')
            self.bridge = Bridge()
            log_to_file("UHF preload OK: UhfBridge created (main thread)")
            return True
        except Exception as e:
            self.has_g2 = False
            self.last_error = f"UhfBridge load: {e}"[:300]
            log_to_file(f"UHF preload FAIL: {e} {traceback.format_exc()}")
            return False

    def _activity(self):
        from jnius import autoclass
        return autoclass('org.kivy.android.PythonActivity').mActivity

    def enable_trigger(self):
        """Main thread. The system scan service stops grabbing the trigger key and we hook
        keycode 619 in Java (SDL/Kivy cannot see it)."""
        if self.bridge is None:
            return
        try:
            from jnius import autoclass
            B = autoclass('com.matrixict.uhf.UhfBridge')
            act = self._activity()
            err = B.setScannerHandleKey(act, False)
            if err:
                log_to_file(f"UHF trigger: {err}")
            B.takeKeyPresses()
            B.installKeyHook(act)
            log_to_file("UHF trigger hook installed")
        except Exception as e:
            log_to_file(f"UHF enable_trigger fail: {e} {traceback.format_exc()}")

    def disable_trigger(self):
        if self.bridge is None:
            return
        try:
            from jnius import autoclass
            B = autoclass('com.matrixict.uhf.UhfBridge')
            act = self._activity()
            B.removeKeyHook(act)
            B.setScannerHandleKey(act, True)
            log_to_file("UHF trigger hook removed, scanner gets the key again")
        except Exception as e:
            log_to_file(f"UHF disable_trigger fail: {e}")

    def take_trigger_presses(self):
        if self.bridge is None:
            return 0
        try:
            from jnius import autoclass
            return int(autoclass('com.matrixict.uhf.UhfBridge').takeKeyPresses())
        except Exception:
            return 0

    def _write_power(self, value):
        try:
            with open(self.UHF_POWER_PATH, 'w') as f:
                f.write(value)
            log_to_file(f"UHF power {value} written to {self.UHF_POWER_PATH}")
            return True
        except Exception as e:
            log_to_file(f"UHF power write fail ({self.UHF_POWER_PATH}): {e}")
            return False

    def open(self):
        """Blocking (~2-6 s): call from a worker thread, after preload() on the main thread."""
        with self._open_lock:
            if self.is_open:
                return True
            if self.bridge is None:
                if not self.last_error:
                    self.last_error = "UhfBridge not created (preload not run)"
                return False
            try:
                power_ok = self._write_power("1")
                time.sleep(1.5)
                errors = []
                for baud in self.BAUDS:
                    param = f"{self.SERIAL_PORT}:{baud}"
                    ok = self.bridge.open(param, 10)
                    log_to_file(f"UHF open {param} -> {ok} {self.bridge.getLastError()}")
                    if ok:
                        self.is_open = True
                        self.last_error = ""
                        log_to_file(f"UHF opened SUCCESS at {baud}")
                        return True
                    errors.append(str(self.bridge.getLastError()))
                self.last_error = (("" if power_ok else "power write failed; ") + (errors[0] if errors else "open failed"))[:300]
                log_to_file("UHF open FAILED at all bauds: " + " | ".join(errors))
                return False
            except Exception as e:
                self.last_error = f"open: {e}"[:300]
                log_to_file(f"UHF open fail: {e} {traceback.format_exc()}")
                return False

    def start_inventory(self):
        if not self.is_open or self.bridge is None:
            log_to_file("UHF start: not open")
            return False
        try:
            err = self.bridge.startInventory()
            if err:
                self.last_error = str(err)[:300]
                log_to_file(f"UHF inventory fail: {err}")
                return False
            self.is_inventorying = True
            log_to_file("UHF inventory START OK")
            return True
        except Exception as e:
            self.last_error = f"start: {e}"[:300]
            log_to_file(f"UHF start fail: {e} {traceback.format_exc()}")
            return False

    def stop_inventory(self):
        try:
            if self.bridge is not None and self.is_inventorying:
                self.bridge.stopInventory()
            self.is_inventorying = False
            log_to_file("UHF inventory STOP")
            return True
        except Exception as e:
            log_to_file(f"UHF stop fail: {e}")
            self.is_inventorying = False
            return False

    def free(self):
        try:
            if self.is_inventorying:
                self.stop_inventory()
            if self.is_open and self.bridge is not None:
                self.bridge.close()
                self._write_power("0")
            self.is_open = False
            log_to_file("UHF freed")
            return True
        except Exception as e:
            log_to_file(f"UHF free fail: {e}")
            self.is_open = False
            return False

    def read_tags(self):
        out = []
        try:
            if self.bridge is not None:
                while True:
                    e = self.bridge.poll()
                    if e is None:
                        break
                    e = str(e).strip().upper().replace(" ", "")
                    if len(e) >= 8:
                        out.append(e)
        except Exception as ex:
            log_to_file(f"UHF read_tags err: {ex}")
        if out:
            log_to_file(f"UHF read {len(out)} tags: {out[:3]}")
        return out


class BarcodeManager:
    def __init__(self):
        self.activity = None
        self.barcode_util = None
        self.module_2d = None
        self.has_sdk = False
        self.is_open = False
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            self.activity = PythonActivity.mActivity
            BarcodeUtility = autoclass('com.rscja.deviceapi.BarcodeUtility')
            self.barcode_util = BarcodeUtility.getInstance()
            ModuleType = autoclass('com.rscja.deviceapi.BarcodeUtility$ModuleType')
            self.module_2d = ModuleType.BARCODE_2D
            self.has_sdk = True
            log_to_file("Barcode SDK OK")
        except Exception as e:
            log_to_file(f"Barcode SDK fail (normal in Pydroid3): {e}")
            self.has_sdk = False
    def open(self):
        if not self.has_sdk: 
            self.is_open = True
            return True
        try: 
            self.barcode_util.open(self.activity, self.module_2d)
            self.is_open = True
            log_to_file("Barcode opened")
            return True
        except Exception as e: 
            log_to_file(f"Barcode open fail: {e}")
            return False
    def close(self):
        if not self.has_sdk: 
            self.is_open = False
            return True
        try: 
            self.barcode_util.close()
            self.is_open = False
            log_to_file("Barcode closed")
            return True
        except Exception as e: 
            log_to_file(f"Barcode close fail: {e}")
            self.is_open = False
            return False



class BarcodeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._timer=None
        try:
            self.build_ui()
            log_to_file("BarcodeScreen V25 built - V21 base + Import/Export anywhere")
        except Exception as e:
            log_to_file(f"BarcodeScreen build FAIL: {e} {traceback.format_exc()}")

    def build_ui(self):
        root = BoxLayout(orientation='vertical', padding=0, spacing=0)
        root.add_widget(make_header())
        body = BoxLayout(orientation='vertical', padding=(12, 6), spacing=8)
        body.add_widget(Label(text='SCAN BARCODE', size_hint_y=None, height=40, bold=True,
                              color=get_color_from_hex(PRIMARY), font_size=26))
        self.box_bc = TextInput(hint_text='Scan here...', multiline=False, size_hint_y=None, height=95, font_size=34,
                                padding=(14, 22))
        self.box_bc.bind(text=self.on_text_change)
        self.box_bc.bind(on_text_validate=self.do_scan)
        body.add_widget(self.box_bc)

        # Item info: each value under its own title, wraps to show the full text.
        self.card = make_safe_card()
        self.card.padding = (8, 6)
        self.card.spacing = 2
        self.card.bind(minimum_height=self.card.setter('height'))
        def field(title, value_size, value_bold=False):
            self.card.add_widget(wrap_label(title, font_size=19, color=get_color_from_hex(PRIMARY), bold=True))
            v = wrap_label('-', font_size=value_size, color=(0.1,0.1,0.1,1), bold=value_bold, min_height=40)
            self.card.add_widget(v)
            return v
        self.lbl_lookup = field('Item Code', 34, True)
        self.lbl_desc = field('Description', 28, True)
        self.lbl_sub1 = field('Sub Description 1', 26)
        self.lbl_sub2 = field('Sub Description 2', 26)
        self.lbl_sub3 = field('Sub Description 3', 26)
        from kivy.graphics import Color, RoundedRectangle
        with self.card.canvas.before:
            Color(1, 1, 1, 1)
            _bg = RoundedRectangle(radius=[12])
        self.card.bind(pos=lambda w, v: setattr(_bg, 'pos', v), size=lambda w, v: setattr(_bg, 'size', v))
        info_scroll = ScrollView(size_hint_y=1, do_scroll_x=False)
        info_scroll.add_widget(self.card)
        body.add_widget(info_scroll)

        self.lbl_status = wrap_label('Folder: ' + APP_FOLDER[-30:], font_size=16, color=(0,0.5,0,1), halign='center')
        body.add_widget(self.lbl_status)
        self.lbl_count = wrap_label('Ready', font_size=22, color=(0,0.5,0,1), bold=True, halign='center')
        body.add_widget(self.lbl_count)
        self.btn_go_rfid = Button(text='Scan item first', size_hint_y=None, height=110, background_color=(0.6,0.6,0.6,1),
                                  background_normal='', bold=True, font_size=28, disabled=True)
        self.btn_go_rfid.bind(on_press=self.go_to_rfid)
        body.add_widget(self.btn_go_rfid)
        row = BoxLayout(size_hint_y=None, height=95, spacing=8)
        b1 = Button(text='Import', background_color=(0,0.6,0,1), background_normal='', font_size=24, bold=True)
        b2 = Button(text='Export', background_color=get_color_from_hex(SECONDARY), background_normal='', font_size=24, bold=True)
        b3 = Button(text='Log', background_color=(0.5,0.5,0.5,1), background_normal='', font_size=22, bold=True)
        b1.bind(on_press=self.import_csv)
        b2.bind(on_press=self.export_txt)
        b3.bind(on_press=self.show_log)
        row.add_widget(b1)
        row.add_widget(b2)
        row.add_widget(b3)
        body.add_widget(row)
        root.add_widget(body)
        self.add_widget(root)

    def on_enter(self):
        try:
            app = App.get_running_app()
            app.current_screen_name = 'barcode'
            # V27 - 5 POINTS - Immediately close UHF and open Barcode - no delay for C72 switch
            try:
                if app.uhf_mgr.is_inventorying:
                    app.uhf_mgr.stop_inventory()
                if app.uhf_mgr.is_open:
                    app.uhf_mgr.free()
                log_to_file("V27 Barcode enter: UHF closed")
            except Exception as e:
                log_to_file(f"V27 Barcode enter UHF close fail: {e}")
            
            def _setup(dt):
                try:
                    app.uhf_mgr.free()
                    app.barcode_mgr.open()
                    log_to_file("V27 BarcodeScreen on_enter OK - Barcode opened")
                except Exception as e:
                    log_to_file(f"V27 on_enter fail: {e}")
            # Open immediately + delayed backup
            try:
                app.barcode_mgr.open()
            except:
                pass
            Clock.schedule_once(_setup, 0.3)
            Clock.schedule_once(lambda dt: setattr(self.box_bc, 'focus', True), 0.5)
            self.lbl_count.text=f'Items in DB: {app.db_count}'
            self.update_btn()
        except Exception as e:
            log_to_file(f"V27 on_enter crash: {e} {traceback.format_exc()}")
        except Exception as e:
            log_to_file(f"on_enter crash: {e} {traceback.format_exc()}")

    def on_leave(self):
        try: self.box_bc.focus = False
        except: pass

    def on_text_change(self, inst, text):
        try:
            if self._timer: Clock.unschedule(self._timer)
            app = App.get_running_app()
            if app.current_screen_name != 'barcode':
                inst.text = ''
                return
            if len(text.strip())>=3:
                self._timer = Clock.schedule_once(lambda dt: self.do_scan(inst), 0.4)
        except Exception as e:
            log_to_file(f"text_change err: {e}")

    def do_scan(self, inst):
        try:
            if self._timer:
                Clock.unschedule(self._timer)
                self._timer=None
            app = App.get_running_app()
            if app.current_screen_name != 'barcode':
                inst.text=''
                return
            code = inst.text.strip()
            log_to_file(f"Scan: {code}")
            if not code or len(code)<3: return
            conn = sqlite3.connect(app.DB)
            c = conn.cursor()
            c.execute("SELECT i.ItemID, i.ItemLookupCode, i.Description, i.Subdescription1, i.Subdescription2, i.Subdescription3 FROM Items i JOIN Barcod b ON i.ItemID=b.ItemID WHERE b.Barcode=?", (code,))
            row = c.fetchone()
            conn.close()
            if row:
                app.curr_id=row[0]
                app.curr_code=row[1]
                app.curr_desc=row[2]
                self.lbl_lookup.text=f'{row[1]}'
                self.lbl_desc.text=f'{row[2]}'
                self.lbl_sub1.text=f'{row[3]}'
                self.lbl_sub2.text=f'{row[4]}'
                self.lbl_sub3.text=f'{row[5]}'
                inst.text=''
                self.lbl_count.text=f'Found: {row[1]}'
                self.lbl_count.color=(0,0.6,0,1)
                self.update_btn()
            else:
                self.lbl_count.text=f'Not found: {code}'
                self.lbl_count.color=(1,0,0,1)
                inst.text=''
        except Exception as e:
            self.lbl_count.text=f'Error: {e}'
            log_to_file(f"do_scan crash: {e} {traceback.format_exc()}")

    def update_btn(self):
        try:
            app=App.get_running_app()
            if app.curr_id:
                self.btn_go_rfid.disabled=False
                self.btn_go_rfid.text=f'Link RFID ({len(app.rfid_list)}) -> {app.curr_code}'
                self.btn_go_rfid.background_color=get_color_from_hex(PRIMARY)
            else:
                self.btn_go_rfid.disabled=True
                self.btn_go_rfid.text='Scan item first'
                self.btn_go_rfid.background_color=(0.6,0.6,0.6,1)
        except Exception as e:
            log_to_file(f"update_btn err: {e}")

    def go_to_rfid(self, inst):
        try:
            app=App.get_running_app()
            if not app.curr_id: return
            app.barcode_mgr.close()
            self.box_bc.focus=False
            self.manager.transition=SlideTransition(direction='left')
            self.manager.current='rfid'
        except Exception as e:
            log_to_file(f"go_to_rfid crash: {e} {traceback.format_exc()}")

    def import_csv(self, inst):
        # V25 - V21 BASE - 5 POINTS - Import from anywhere
        self.open_csv_chooser_anywhere()

    def request_all_files_permission(self):
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            Intent = autoclass('android.content.Intent')
            Settings = autoclass('android.provider.Settings')
            Uri = autoclass('android.net.Uri')
            intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
            uri = Uri.parse("package:" + activity.getPackageName())
            intent.setData(uri)
            activity.startActivity(intent)
            self.lbl_count.text = 'Grant All files access'
            return True
        except Exception as e:
            log_to_file(f"request permission fail: {e}")
            return False

    def open_csv_chooser_anywhere(self):
        # V25 - Import: Choose CSV from ANYWHERE - V21 base stable
        try:
            start_path = "/storage/emulated/0"
            try:
                if not os.path.exists(start_path):
                    start_path = "/storage/emulated/0/Download"
            except:
                start_path = APP_FOLDER
            if not os.path.exists(start_path):
                start_path = APP_FOLDER
            box = BoxLayout(orientation='vertical', spacing=5, padding=5)
            chooser = FileChooserListView(path=start_path, filters=['*.csv', '*.CSV'], size_hint_y=0.85)
            box.add_widget(chooser)
            path_label = Label(text='Current: ' + start_path, size_hint_y=None, height=30, font_size=11)
            def update_path_label(instance, value):
                path_label.text = 'Current: ' + value
            chooser.bind(path=update_path_label)
            box.add_widget(path_label)
            btn_row = BoxLayout(size_hint_y=None, height=60, spacing=8, padding=5)
            btn_cancel = Button(text='Cancel', background_color=(0.6,0.6,0.6,1), background_normal='', font_size=16)
            btn_perm = Button(text='Grant Access', background_color=(0.2,0.6,1,1), background_normal='', font_size=11)
            btn_select = Button(text='Select CSV', background_color=get_color_from_hex(PRIMARY), background_normal='', bold=True, font_size=16)
            btn_row.add_widget(btn_cancel)
            btn_row.add_widget(btn_perm)
            btn_row.add_widget(btn_select)
            box.add_widget(btn_row)
            popup = Popup(title='Import: Choose CSV from ANYWHERE', content=box, size_hint=(0.95, 0.92), auto_dismiss=False)
            def do_cancel(instance):
                popup.dismiss()
            def do_perm(instance):
                self.request_all_files_permission()
                popup.dismiss()
            def do_select(instance):
                try:
                    if chooser.selection:
                        selected = chooser.selection[0]
                        popup.dismiss()
                        self.do_import_file_anywhere(selected)
                    else:
                        self.lbl_count.text = 'Select a file first'
                except Exception as e:
                    log_to_file(f"Select error: {e}")
                    popup.dismiss()
            btn_cancel.bind(on_press=do_cancel)
            btn_perm.bind(on_press=do_perm)
            btn_select.bind(on_press=do_select)
            chooser.bind(on_submit=lambda instance, selection, touch: do_select(None) if selection else None)
            popup.open()
        except Exception as e:
            log_to_file(f"Chooser import crash: {e} {traceback.format_exc()}")
            self.lbl_count.text = 'Chooser error'

    def do_import_file_anywhere(self, csv_path):
        # V25 - 5 POINTS isolated, no side effects
        app = App.get_running_app()
        log_to_file(f"Importing anywhere: {csv_path}")
        if not csv_path:
            self.lbl_count.text = 'No file selected'
            return
        try:
            exists = os.path.exists(csv_path)
        except PermissionError:
            self.lbl_count.text = 'Permission denied'
            self.open_csv_chooser_anywhere()
            return
        except Exception:
            self.lbl_count.text = 'File error'
            return
        if not exists:
            self.lbl_count.text = 'File not found'
            return
        try:
            import shutil
            private_copy = os.path.join(APP_FOLDER, "Matrix_Items_imported.csv")
            csv_path_to_read = csv_path
            try:
                shutil.copy2(csv_path, private_copy)
                csv_path_to_read = private_copy
            except:
                csv_path_to_read = csv_path
            conn=sqlite3.connect(app.DB)
            c=conn.cursor()
            bc=0
            with open(csv_path_to_read,'r',encoding='utf-8',errors='ignore') as f:
                import csv
                reader=csv.DictReader(f)
                for row in reader:
                    bcode=row.get('barcode') or row.get('Barcode') or row.get('BARCODE') or ''
                    bcode=str(bcode).strip()
                    if not bcode:
                        for k in row.keys():
                            if 'barcode' in k.lower() or 'barcod' in k.lower():
                                bcode = str(row[k]).strip()
                                break
                    if not bcode: continue
                    try:
                        raw_id = row.get('ItemID') or row.get('ItemId') or row.get('ID') or 0
                        item_id=int(float(str(raw_id).strip() or 0))
                        if item_id == 0:
                            continue
                    except: continue
                    try:
                        c.execute('INSERT OR IGNORE INTO Items VALUES (?,?,?,?,?,?)',(item_id,row.get('ItemLookupCode','') or '',row.get('Description',''),row.get('Subdescription1',''),row.get('Subdescription2',''),row.get('Subdescription3','')))
                        c.execute('INSERT OR IGNORE INTO Barcod VALUES (NULL,?,?)',(item_id,bcode))
                        bc+=1
                    except:
                        continue
            conn.commit()
            c.execute('SELECT count(*) FROM Items')
            app.db_count=c.fetchone()[0]
            conn.close()
            self.lbl_count.text=f'Imported {bc} | Total {app.db_count}'
            self.lbl_status.text='File: ' + os.path.basename(csv_path)
        except PermissionError:
            self.lbl_count.text = 'Permission denied'
            self.open_csv_chooser_anywhere()
        except Exception as e:
            self.lbl_count.text='Err ' + str(e)[:30]
            log_to_file(f"Import crash: {e} {traceback.format_exc()}")

    def export_txt(self, inst):
        # V25 - Export: Choose save location anywhere
        self.open_export_chooser_anywhere()

    def open_export_chooser_anywhere(self):
        # V25 - Export chooser - V21 base + anywhere
        try:
            start_path = "/storage/emulated/0/Download"
            try:
                if not os.path.exists(start_path):
                    start_path = "/storage/emulated/0"
            except:
                start_path = APP_FOLDER
            if not os.path.exists(start_path):
                start_path = APP_FOLDER
            box = BoxLayout(orientation='vertical', spacing=5, padding=5)
            chooser = FileChooserListView(path=start_path, size_hint_y=0.80)
            chooser.filters = []
            box.add_widget(chooser)
            path_label = Label(text='Save to: ' + start_path, size_hint_y=None, height=30, font_size=11)
            def update_path_label(instance, value):
                path_label.text = 'Save to: ' + value
            chooser.bind(path=update_path_label)
            box.add_widget(path_label)
            info = Label(text='Select FOLDER then Save', size_hint_y=None, height=25, font_size=10, color=(0,0.6,0,1))
            box.add_widget(info)
            btn_row = BoxLayout(size_hint_y=None, height=60, spacing=8, padding=5)
            btn_cancel = Button(text='Cancel', background_color=(0.6,0.6,0.6,1), background_normal='', font_size=16)
            btn_perm = Button(text='Grant Access', background_color=(0.2,0.6,1,1), background_normal='', font_size=11)
            btn_save = Button(text='Save Here', background_color=get_color_from_hex(PRIMARY), background_normal='', bold=True, font_size=16)
            btn_row.add_widget(btn_cancel)
            btn_row.add_widget(btn_perm)
            btn_row.add_widget(btn_save)
            box.add_widget(btn_row)
            popup = Popup(title='Export: Choose Folder to Save', content=box, size_hint=(0.95, 0.92), auto_dismiss=False)
            def do_cancel(instance):
                popup.dismiss()
            def do_perm(instance):
                self.request_all_files_permission()
                popup.dismiss()
            def do_save(instance):
                try:
                    save_dir = chooser.path
                    if chooser.selection and os.path.isdir(chooser.selection[0]):
                        save_dir = chooser.selection[0]
                    elif chooser.selection and os.path.isfile(chooser.selection[0]):
                        save_dir = os.path.dirname(chooser.selection[0])
                    popup.dismiss()
                    self.do_export_anywhere(save_dir)
                except Exception as e:
                    log_to_file(f"Export chooser error: {e}")
                    popup.dismiss()
            btn_cancel.bind(on_press=do_cancel)
            btn_perm.bind(on_press=do_perm)
            btn_save.bind(on_press=do_save)
            popup.open()
        except Exception as e:
            log_to_file(f"Export chooser crash: {e} {traceback.format_exc()}")
            self.lbl_count.text = 'Export chooser error'

    def do_export_anywhere(self, save_dir):
        # V25 - 5 POINTS isolated
        try:
            app = App.get_running_app()
            conn=sqlite3.connect(app.DB)
            c=conn.cursor()
            c.execute("SELECT i.ItemLookupCode, i.Description, r.RFID_CODE FROM RFID r JOIN Items i ON r.ItemID=i.ItemID")
            rows=c.fetchall()
            conn.close()
            if not rows:
                self.lbl_count.text='No RFID to export'
                return
            try:
                if not os.path.exists(save_dir):
                    save_dir = APP_FOLDER
            except:
                save_dir = APP_FOLDER
            fn="RFID_Export_" + datetime.now().strftime('%Y%m%d_%H%M%S') + ".txt"
            path=os.path.join(save_dir, fn)
            try:
                with open(path,'w',encoding='utf-8') as f:
                    f.write("Itemcode | Description | RFID" + chr(10))
                    for r in rows:
                        f.write(f"{r[0]} | {r[1]} | {r[2]}" + chr(10))
                self.lbl_count.text=f'Exported {len(rows)}'
                self.lbl_status.text='Saved: ' + path[-40:]
            except PermissionError:
                fallback_path=os.path.join(APP_FOLDER, fn)
                with open(fallback_path,'w',encoding='utf-8') as f:
                    f.write("Itemcode | Description | RFID" + chr(10))
                    for r in rows:
                        f.write(f"{r[0]} | {r[1]} | {r[2]}" + chr(10))
                self.lbl_count.text=f'Exported {len(rows)} to private'
                self.lbl_status.text='Permission denied, saved privately'
                try:
                    import shutil
                    dl_path=os.path.join("/storage/emulated/0/Download", fn)
                    shutil.copy2(fallback_path, dl_path)
                    self.lbl_status.text='Saved to Download: ' + fn
                except:
                    pass
        except Exception as e:
            self.lbl_count.text='Export Err ' + str(e)[:20]
            log_to_file(f"Export crash: {e} {traceback.format_exc()}")

    def show_log(self, inst):
        try:
            if os.path.exists(LOG_PATH):
                with open(LOG_PATH, 'r', encoding='utf-8') as f:
                    content = f.read()[-300:]
                self.lbl_status.text = content[-60:]
        except: pass


class RFIDScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.seen_set = set()
        try:
            self.build_ui()
        except Exception as e:
            log_to_file(f"RFID build fail: {e} {traceback.format_exc()}")

    def build_ui(self):
        root=BoxLayout(orientation='vertical',padding=0,spacing=0)
        root.add_widget(make_header())
        body=BoxLayout(orientation='vertical',padding=(12, 6),spacing=8)
        self.lbl_item=wrap_label('Item: -', font_size=34, bold=True, color=get_color_from_hex(PRIMARY), halign='center')
        body.add_widget(self.lbl_item)
        self.lbl_desc=wrap_label('Desc: -', font_size=26, color=(0.15,0.15,0.15,1), halign='center')
        body.add_widget(self.lbl_desc)
        self.counter=Label(text='Count: 0', size_hint_y=None,height=55,bold=True,color=(0,0.5,0,1), font_size=30)
        body.add_widget(self.counter)
        scroll=ScrollView(size_hint_y=1, do_scroll_x=False)
        self.rfid_grid=GridLayout(cols=1,size_hint_y=None,spacing=6, padding=4)
        self.rfid_grid.bind(minimum_height=self.rfid_grid.setter('height'))
        scroll.add_widget(self.rfid_grid)
        body.add_widget(scroll)
        # Manual RFID entry removed (not needed). Kept as None so older checks stay safe.
        self.box_rfid=None
        self.lbl_status=wrap_label('Blue = START/STOP', font_size=20, color=(0,0.6,0,1), bold=True, halign='center', min_height=50)
        body.add_widget(self.lbl_status)
        row1=BoxLayout(size_hint_y=None,height=110,spacing=8)
        self.btn_scan=Button(text='START UHF', background_color=(0.15,0.5,0.9,1), background_normal='', bold=True, font_size=30, size_hint_x=0.65)
        self.btn_clear=Button(text='Clear', background_color=(0.7,0.7,0.7,1), background_normal='', color=(0,0,0,1), font_size=26, bold=True, size_hint_x=0.35)
        self.btn_scan.bind(on_press=self.toggle_scan)
        self.btn_clear.bind(on_press=self.clear_tags)
        row1.add_widget(self.btn_scan)
        row1.add_widget(self.btn_clear)
        body.add_widget(row1)
        row2=BoxLayout(size_hint_y=None,height=100,spacing=8)
        self.btn_back=Button(text='< Back', background_color=get_color_from_hex(SECONDARY), background_normal='', font_size=26, bold=True, size_hint_x=0.35)
        self.btn_save=Button(text='SAVE (0)', background_color=get_color_from_hex(PRIMARY), background_normal='', bold=True, font_size=30, size_hint_x=0.65)
        self.btn_back.bind(on_press=self.go_back)
        self.btn_save.bind(on_press=self.save_tags)
        row2.add_widget(self.btn_back)
        row2.add_widget(self.btn_save)
        body.add_widget(row2)
        root.add_widget(body)
        self.add_widget(root)

    def on_enter(self):
        try:
            app=App.get_running_app()
            app.current_screen_name = 'rfid'
            self.lbl_item.text=f'{app.curr_code}'
            self.lbl_desc.text=f'{app.curr_desc}'
            self.seen_set = set([t.upper().strip() for t in app.rfid_list])
            self.refresh()
            log_to_file(f"V27 RFID enter {app.curr_code} - CLOSING Barcode, OPENING UHF")
            
            # V27 - IMMEDIATELY close Barcode - C72 cannot have both
            try:
                app.barcode_mgr.close()
                log_to_file("V27 RFID enter: Barcode closed immediately")
            except Exception as e:
                log_to_file(f"V27 RFID enter Barcode close fail: {e}")
            
            def _open(dt):
                try:
                    if app.uhf_mgr.has_g2:
                        self.lbl_status.text = 'Starting UHF...'
                        app.uhf_mgr.preload()
                        app.uhf_mgr.enable_trigger()
                        Clock.unschedule(self.poll_trigger)
                        Clock.schedule_interval(self.poll_trigger, 0.1)
                        def _work():
                            ok = app.uhf_mgr.open()
                            Clock.schedule_once(lambda d: setattr(self.lbl_status, 'text',
                                'UHF ready - press Blue' if ok else ('UHF failed: ' + (app.uhf_mgr.last_error or 'see Log'))[:220]), 0)
                        threading.Thread(target=_work, daemon=True).start()
                    else:
                        self.lbl_status.text = f'No UHF SDK ({app.uhf_mgr.sdk_version})'
                except Exception as e:
                    log_to_file(f"V27 RFID _open err {e}")
            # Single open, after Barcode has released the module
            Clock.schedule_once(_open, 0.5)
        except Exception as e:
            log_to_file(f"V27 RFID on_enter crash: {e} {traceback.format_exc()}")
        except Exception as e:
            log_to_file(f"RFID on_enter crash: {e} {traceback.format_exc()}")

    def on_leave(self):
        try:
            app=App.get_running_app()
            Clock.unschedule(self.poll)
            Clock.unschedule(self.poll_trigger)
            app.uhf_mgr.disable_trigger()
            app.uhf_mgr.stop_inventory()
            app.uhf_mgr.free()
            app.barcode_mgr.open()
            app.current_screen_name = 'barcode'
        except: pass

    def poll_trigger(self, dt):
        """Physical trigger (keycode 619) presses caught in Java -> same as START/STOP button."""
        try:
            n = App.get_running_app().uhf_mgr.take_trigger_presses()
            if n:
                log_to_file(f"UHF physical trigger x{n}")
                self.toggle_scan(None)
        except Exception as e:
            log_to_file(f"poll_trigger err {e}")

    def refresh(self):
        try:
            app=App.get_running_app()
            self.rfid_grid.clear_widgets()
            self.btn_save.text=f'SAVE ({len(app.rfid_list)})'
            self.counter.text=f'Count: {len(app.rfid_list)}'
            if not app.rfid_list:
                self.rfid_grid.add_widget(Label(text='No tags - press trigger or START', size_hint_y=None,height=70,color=(0.55,0.55,0.55,1), font_size=24))
                return
            for rf in app.rfid_list:
                row=BoxLayout(size_hint_y=None,height=75,spacing=6)
                lbl=Label(text=rf,size_hint_x=0.8,color=(0,0,0,1),font_size=24)
                lbl.bind(size=lambda w,s: setattr(w,'text_size',(s[0],None)))
                lbl.halign='center'
                bx=Button(text='X',size_hint_x=0.2,background_color=(1,0.25,0.25,1),background_normal='', font_size=26, bold=True)
                bx.bind(on_press=lambda inst,r=rf: self.remove_tag(r))
                row.add_widget(lbl)
                row.add_widget(bx)
                self.rfid_grid.add_widget(row)
        except Exception as e:
            log_to_file(f"refresh crash: {e}")

    def add_tag_unique(self, code):
        try:
            if not code: return False
            code = str(code).strip().upper()
            if not code or code in self.seen_set: return False
            app=App.get_running_app()
            self.seen_set.add(code)
            app.rfid_list.append(code)
            log_to_file(f"Tag {code}")
            return True
        except Exception as e:
            log_to_file(f"add_tag err {e}")
            return False

    def add_manual(self, inst):
        try:
            if self.add_tag_unique(inst.text.strip()):
                self.refresh()
                self.counter.text=f'Count: {len(App.get_running_app().rfid_list)}'
            inst.text=''
        except Exception as e:
            log_to_file(f"add_manual crash {e}")

    def remove_tag(self, code):
        try:
            app=App.get_running_app()
            if code in app.rfid_list: app.rfid_list.remove(code)
            if code.upper() in self.seen_set: self.seen_set.remove(code.upper())
            self.refresh()
        except: pass

    def clear_tags(self, inst):
        try:
            app=App.get_running_app()
            app.rfid_list=[]
            self.seen_set=set()
            self.refresh()
            log_to_file("Cleared")
        except: pass

    def toggle_scan(self, inst):
        try:
            app=App.get_running_app()
            # V26 - Show UHF SDK status
            if not app.uhf_mgr.has_g2:
                log_to_file(f"UHF has_g2=False, SDK={app.uhf_mgr.sdk_version} - FAKE mode")
                self.lbl_status.text = f"No UHF SDK: {app.uhf_mgr.last_error}"[:200]
                return
            
            log_to_file(f"UHF toggle: has_g2=True, is_open={app.uhf_mgr.is_open}, is_inventorying={app.uhf_mgr.is_inventorying}")
            
            if app.uhf_mgr.is_inventorying:
                app.uhf_mgr.stop_inventory()
                Clock.unschedule(self.poll)
                self.btn_scan.text='START UHF'
                self.btn_scan.background_color=(0.15,0.5,0.9,1)
                self.lbl_status.text = 'UHF Stopped'
                log_to_file("UHF toggled STOP")
            else:
                # Ensure UHF is open
                if not app.uhf_mgr.is_open:
                    log_to_file("UHF not open yet, starting in background...")
                    self.lbl_status.text = 'Starting UHF... press again'
                    app.uhf_mgr.preload()
                    def _work2():
                        ok = app.uhf_mgr.open()
                        Clock.schedule_once(lambda d: setattr(self.lbl_status, 'text',
                            'UHF ready - press Blue' if ok else ('UHF failed: ' + (app.uhf_mgr.last_error or 'see Log'))[:220]), 0)
                    threading.Thread(target=_work2, daemon=True).start()
                    return
                
                if app.uhf_mgr.start_inventory():
                    Clock.schedule_interval(self.poll, 0.25)
                    self.btn_scan.text='STOP UHF'
                    self.btn_scan.background_color=(0.9,0.2,0.2,1)
                    self.lbl_status.text = 'UHF Scanning...'
                    log_to_file("UHF toggled START OK")
                else:
                    self.lbl_status.text = 'UHF Start Failed - Check Log'
                    log_to_file("UHF start_inventory returned False")
        except Exception as e:
            log_to_file(f"toggle crash {e} {traceback.format_exc()}")
            try:
                self.lbl_status.text = f'Error: {e}'[:40]
            except:
                pass


    def poll(self, dt):
        try:
            tags=App.get_running_app().uhf_mgr.read_tags()
            added=0
            for t in tags:
                if self.add_tag_unique(t): added+=1
            if added>0:
                self.refresh()
                self.counter.text=f'Count: {len(App.get_running_app().rfid_list)}'
        except Exception as e:
            log_to_file(f"poll err {e}")

    def save_tags(self, inst):
        try:
            app=App.get_running_app()
            if not app.curr_id or not app.rfid_list: return
            conn=sqlite3.connect(app.DB)
            c=conn.cursor()
            cnt=0
            for rf in app.rfid_list:
                try:
                    c.execute("INSERT INTO RFID (ItemID, RFID_CODE) VALUES (?,?)",(app.curr_id, rf))
                    cnt+=1
                except: pass
            conn.commit()
            conn.close()
            log_to_file(f"Saved {cnt}")
            app.rfid_list=[]
            self.seen_set=set()
            self.refresh()
            self.lbl_status.text=f'Saved {cnt}!'
            Clock.schedule_once(lambda dt: self.go_back(None), 1.0)
        except Exception as e:
            log_to_file(f"save crash {e} {traceback.format_exc()}")

    def go_back(self, inst):
        try:
            App.get_running_app().uhf_mgr.stop_inventory()
            App.get_running_app().uhf_mgr.free()
            self.manager.transition=SlideTransition(direction='right')
            self.manager.current='barcode'
        except Exception as e:
            log_to_file(f"go_back crash {e}")

class RFIDLinkApp(App):
    def build(self):
        try:
            self.DB = DB_PATH
            self.db_count = init_db(self.DB)
            self.barcode_mgr = BarcodeManager()
            self.uhf_mgr = UHFManager_G2_Real()
            self.curr_id=None
            self.curr_code=''
            self.curr_desc=''
            self.rfid_list=[]
            self.current_screen_name='barcode'
            Window.clearcolor=get_color_from_hex(BG)
            Window.bind(on_key_down=self.on_hardware_key)
            sm=ScreenManager()
            sm.add_widget(BarcodeScreen(name='barcode'))
            sm.add_widget(RFIDScreen(name='rfid'))
            log_to_file(f"App built OK db={self.db_count}")
            return sm
        except Exception as e:
            log_to_file(f"BUILD CRASH: {e} {traceback.format_exc()}")
            raise

    def on_pause(self):
        # leaving the app: give the trigger key back to the system barcode scanner
        try:
            if self.current_screen_name == 'rfid':
                self.uhf_mgr.disable_trigger()
        except Exception:
            pass
        return True

    def on_resume(self):
        try:
            if self.current_screen_name == 'rfid':
                self.uhf_mgr.enable_trigger()
        except Exception:
            pass

    def on_hardware_key(self, window, key, scancode, codepoint, modifier):
        try:
            log_to_file(f"V27 KEY {key} scancode={scancode} screen={self.current_screen_name}")
            # V27 - C72 keys: 120-122 F1-F3, 131-137 scan keys, 264-266, 293-296, 1001-1004 custom
            # Blue button is usually 131 or 134 or 120
            SCAN_KEYS = [120,121,122,131,132,133,134,135,136,137,264,265,266,293,294,295,296,1001,1002,1003,1004,66,79,85, 103, 108,  134]
            
            if self.current_screen_name == 'rfid':
                rs = self.root.get_screen('rfid')
                # Don't hijack typing in the manual RFID box, or back/home/menu
                if (rs.box_rfid is not None and rs.box_rfid.focus) or key in (4, 3, 82):
                    return False
                try:
                    if self.barcode_mgr.is_open:
                        self.barcode_mgr.close()
                except:
                    pass
                import time
                now = time.time()
                # Debounce: key auto-repeat was toggling start/stop repeatedly
                if now - getattr(self, '_last_trigger', 0) > 0.6:
                    self._last_trigger = now
                    rs.toggle_scan(None)
                    log_to_file(f"V28 RFID physical button {key} -> toggle_scan UHF")
                return True

            # In Barcode screen, let Barcode SDK handle it - don't consume
            # But ensure Barcode is open and UHF closed
            if self.current_screen_name == 'barcode':
                if key in SCAN_KEYS:
                    log_to_file(f"V27 Barcode physical button {key} -> Barcode")
                    try:
                        if not self.barcode_mgr.is_open:
                            self.barcode_mgr.open()
                    except:
                        pass
                    # Return False to let system/Barcode SDK handle it (focus TextInput)
                    return False
            
            return False
        except Exception as e:
            log_to_file(f"V27 key crash {e} {traceback.format_exc()}")
            return False
        except Exception as e:
            log_to_file(f"key crash {e}")
            return False

if __name__=='__main__':
    try:
        RFIDLinkApp().run()
    except Exception as e:
        try:
            with open(LOG_PATH, 'a', encoding='utf-8') as f:
                f.write(f"\n=== FATAL CRASH {datetime.now()} ===\n")
                f.write(traceback.format_exc())
        except:
            pass
        raise
