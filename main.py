# MATRIX ICT - V28 - V21 BASE + REAL JAR + BARCODE CLOSE FIX - 5 POINTS
import sqlite3, os, traceback, random, sys
from datetime import datetime

def get_app_folder_safe():
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

def log_to_file(msg):
    try:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")
    except:
        pass

def handle_exception(exc_type, exc_value, exc_tb):
    try:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(f"\n=== CRASH {datetime.now()} ===\n")
            f.write(''.join(traceback.format_exception(exc_type, exc_value, exc_tb)))
            f.write("\n")
    except:
        pass
    sys.__excepthook__(exc_type, exc_value, exc_tb)

sys.excepthook = handle_exception

try:
    os.makedirs(APP_FOLDER, exist_ok=True)
    with open(LOG_PATH, 'w', encoding='utf-8') as f:
        f.write(f"=== V28 Started REAL JAR {datetime.now()} ===\n")
        f.write(f"Folder: {APP_FOLDER}\n")
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
    return BoxLayout(orientation='vertical', padding=12, spacing=6, size_hint_y=None)

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

class UHFManager_G2_Real:
    def __init__(self):
        self.client = None
        self.has_g2 = False
        self.is_inventorying = False
        self.is_open = False
        self.sdk_version = "unknown"
        try:
            from jnius import autoclass
            possible_classes = [
                'com.rscja.deviceapi.RFIDWithUHFUART',
                'com.rscja.deviceapi.RFIDWithUHF',
                'com.rscja.deviceapi.RFIDWithUHFUHF',
                'com.rscja.deviceapi.RFIDWithUHFUHFUART'
            ]
            for cls_name in possible_classes:
                try:
                    Clz = autoclass(cls_name)
                    self.client = Clz.getInstance()
                    self.has_g2 = True
                    self.sdk_version = cls_name
                    log_to_file(f"UHF SDK FOUND: {cls_name} - REAL JAR")
                    break
                except Exception as e:
                    log_to_file(f"UHF try {cls_name} fail: {e}")
                    continue
            if not self.has_g2:
                log_to_file("UHF SDK NOT FOUND - will use fake mode - CHECK reader.jar in APK")
        except Exception as e:
            log_to_file(f"UHF init crash: {e} {traceback.format_exc()}")
            self.has_g2 = False

    def open(self):
        if not self.has_g2:
            log_to_file("UHF open: no G2 SDK, fake mode")
            return False
        try:
            try:
                self.client.init()
                log_to_file("UHF init() OK")
            except Exception as e1:
                log_to_file(f"UHF init() fail: {e1}, trying init(activity)")
                try:
                    from jnius import autoclass
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    activity = PythonActivity.mActivity
                    self.client.init(activity)
                    log_to_file("UHF init(activity) OK")
                except Exception as e2:
                    log_to_file(f"UHF init(activity) fail: {e2}")
            try:
                self.client.setPower(30)
                log_to_file("UHF setPower 30 OK")
            except Exception as e:
                log_to_file(f"UHF setPower fail (normal): {e}")
            try:
                self.client.setFrequencyMode(0)
                log_to_file("UHF setFrequencyMode OK")
            except Exception as e:
                log_to_file(f"UHF setFrequency fail (normal): {e}")
            self.is_open = True
            log_to_file("UHF opened SUCCESS REAL")
            return True
        except Exception as e:
            log_to_file(f"UHF open fail: {e} {traceback.format_exc()}")
            return False

    def start_inventory(self):
        if not self.has_g2:
            log_to_file("UHF start: no G2, fake")
            return False
        try:
            self.client.startInventoryTag()
            self.is_inventorying=True
            log_to_file("UHF inventory START OK REAL")
            return True
        except Exception as e:
            log_to_file(f"UHF start fail: {e} {traceback.format_exc()}")
            return False

    def stop_inventory(self):
        try:
            if self.has_g2 and self.client:
                self.client.stopInventory()
            self.is_inventorying=False
            log_to_file("UHF inventory STOP")
            return True
        except Exception as e:
            log_to_file(f"UHF stop fail: {e}")
            self.is_inventorying=False
            return False

    def free(self):
        try:
            if self.is_inventorying and self.has_g2 and self.client:
                try:
                    self.client.stopInventory()
                except:
                    pass
                self.is_inventorying=False
            if self.has_g2 and self.client:
                try:
                    self.client.free()
                except:
                    pass
            self.is_open=False
            log_to_file("UHF freed")
            return True
        except Exception as e:
            log_to_file(f"UHF free fail: {e}")
            self.is_open=False
            return False

    def read_tags(self):
        tags=[]
        if not self.has_g2:
            return tags
        try:
            result = self.client.readTagFromBuffer()
            if result:
                for tag in result:
                    try:
                        epc = None
                        if hasattr(tag,'getEPC'):
                            epc = tag.getEPC()
                        elif hasattr(tag,'getEpc'):
                            epc = tag.getEpc()
                        else:
                            epc = str(tag)
                        if epc:
                            epc = str(epc).strip().upper().replace(" ", "")
                            if epc and len(epc) >= 8:
                                tags.append(epc)
                    except Exception as te:
                        log_to_file(f"UHF parse tag fail: {te}")
                        pass
                if tags:
                    log_to_file(f"UHF read {len(tags)} tags REAL: {tags[:3]}")
        except Exception as e:
            log_to_file(f"UHF readTagFromBuffer fail: {e}")
        return tags

def switch_to_rfid_mode():
    try:
        app = App.get_running_app()
        log_to_file("Switch -> RFID mode V28")
        if hasattr(app, 'barcode_mgr'):
            app.barcode_mgr.force_disable()
            app.barcode_mgr.close()
        def do_open(dt):
            try: app.uhf_mgr.open()
            except: pass
        Clock.schedule_once(do_open, 0.2)
    except Exception as e:
        log_to_file(f"switch_to_rfid err: {e}")

def switch_to_barcode_mode():
    try:
        app = App.get_running_app()
        log_to_file("Switch -> Barcode mode V28")
        if hasattr(app, 'uhf_mgr'):
            if app.uhf_mgr.is_inventorying:
                app.uhf_mgr.stop_inventory()
            if app.uhf_mgr.is_open:
                app.uhf_mgr.free()
        def do_open(dt):
            try: 
                app.barcode_mgr.force_enable()
                app.barcode_mgr.open()
            except: pass
        Clock.schedule_once(do_open, 0.2)
    except Exception as e:
        log_to_file(f"switch_to_barcode err: {e}")

class BarcodeManager:
    def __init__(self):
        self.activity = None
        self.barcode_util = None
        self.module_2d = None
        self.has_sdk = False
        self.is_open = False
        self.disabled = False
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            self.activity = PythonActivity.mActivity
            BarcodeUtility = autoclass('com.rscja.deviceapi.BarcodeUtility')
            self.barcode_util = BarcodeUtility.getInstance()
            ModuleType = autoclass('com.rscja.deviceapi.BarcodeUtility$ModuleType')
            self.module_2d = ModuleType.BARCODE_2D
            self.has_sdk = True
            log_to_file("Barcode SDK OK REAL")
        except Exception as e:
            log_to_file(f"Barcode SDK fail (normal in Pydroid3): {e}")
            self.has_sdk = False

    def open(self):
        if self.disabled:
            log_to_file("Barcode open blocked - disabled for UHF V28")
            return False
        if not self.has_sdk:
            self.is_open = True
            return True
        try:
            self.barcode_util.open(self.activity, self.module_2d)
            self.is_open = True
            self.disabled = False
            log_to_file("Barcode opened V28")
            return True
        except Exception as e:
            log_to_file(f"Barcode open fail: {e}")
            return False

    def close(self):
        self.disabled = True
        if not self.has_sdk:
            self.is_open = False
            log_to_file("V28 Barcode closed fake disabled")
            return True
        for i in range(3):
            try:
                self.barcode_util.close()
                log_to_file(f"V28 Barcode close {i+1} OK")
                break
            except Exception as e:
                log_to_file(f"V28 close {i+1} fail: {e}")
        self.is_open = False
        log_to_file("V28 Barcode closed FINAL disabled")
        return True

    def force_disable(self):
        self.disabled = True
        self.is_open = False
        try:
            if self.has_sdk and self.barcode_util:
                self.barcode_util.close()
        except:
            pass
        log_to_file("V28 Barcode force_disable")

    def force_enable(self):
        self.disabled = False
        log_to_file("V28 Barcode force_enable")

class BarcodeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._timer=None
        try:
            self.build_ui()
            log_to_file("BarcodeScreen UI built")
        except Exception as e:
            log_to_file(f"BarcodeScreen build FAIL: {e} {traceback.format_exc()}")

    def build_ui(self):
        root = BoxLayout(orientation='vertical', padding=0, spacing=0)
        
        # HEADER - SAFE LOGO LOAD
        header = BoxLayout(size_hint_y=None, height=70, padding=6, spacing=8)
        logo_path = find_logo()
        if logo_path:
            try:
                from kivy.uix.image import Image
                # Safe load with small size
                img = Image(source=logo_path, size_hint_x=0.65, allow_stretch=True, keep_ratio=True)
                header.add_widget(img)
                header.add_widget(Label(text='[b][color=FF8C00]V28[/color][/b]', markup=True, font_size=14, size_hint_x=0.35))
                log_to_file(f"Logo loaded: {logo_path}")
            except Exception as e:
                log_to_file(f"Logo load fail {logo_path}: {e}")
                header.add_widget(Label(text='[b][color=2B2E33]MATRIX[/color][color=FF8C00] ICT[/color] V17[/b]', markup=True, font_size=18))
        else:
            header.add_widget(Label(text='[b][color=2B2E33]MATRIX[/color][color=FF8C00] ICT[/color] V17[/b]', markup=True, font_size=18))
        
        root.add_widget(header)
        
        body = BoxLayout(orientation='vertical', padding=8, spacing=5)
        body.add_widget(Label(text='SCAN BARCODE - Blue Button', size_hint_y=None, height=28, bold=True, color=get_color_from_hex(PRIMARY), font_size=16))
        
        self.box_bc = TextInput(hint_text='Scan here...', multiline=False, size_hint_y=None, height=75, font_size=28)
        self.box_bc.bind(text=self.on_text_change)
        self.box_bc.bind(on_text_validate=self.do_scan)
        body.add_widget(self.box_bc)
        
        # CARD - SAFE, NO CANVAS
        self.card = make_safe_card()
        self.card.size_hint_y = 1
        self.card.height = 300
        
        self.lbl_lookup = Label(text='Code: -', size_hint_y=None, height=60, color=(0,0,0,1), font_size=32, bold=True, halign='left')
        self.lbl_lookup.bind(size=self.lbl_lookup.setter('text_size'))
        self.lbl_desc = Label(text='Description: -', size_hint_y=None, height=60, color=(0.15,0.15,0.15,1), font_size=22, bold=True, halign='left')
        self.lbl_desc.bind(size=self.lbl_desc.setter('text_size'))
        self.lbl_sub1 = Label(text='Sub1: -', size_hint_y=None, height=40, color=(0.3,0.3,0.3,1), font_size=18, halign='left')
        self.lbl_sub1.bind(size=self.lbl_sub1.setter('text_size'))
        self.lbl_sub2 = Label(text='Sub2: -', size_hint_y=None, height=40, color=(0.3,0.3,0.3,1), font_size=18, halign='left')
        self.lbl_sub2.bind(size=self.lbl_sub2.setter('text_size'))
        self.lbl_sub3 = Label(text='Sub3: -', size_hint_y=None, height=40, color=(0.3,0.3,0.3,1), font_size=18, halign='left')
        self.lbl_sub3.bind(size=self.lbl_sub3.setter('text_size'))
        
        for w in [self.lbl_lookup, self.lbl_desc, self.lbl_sub1, self.lbl_sub2, self.lbl_sub3]:
            self.card.add_widget(w)
        
        body.add_widget(self.card)
        
        self.lbl_status = Label(text=f'Folder: {APP_FOLDER[-30:]}', size_hint_y=None, height=30, color=(0,0.5,0,1), font_size=10)
        body.add_widget(self.lbl_status)
        self.lbl_count = Label(text='Ready', size_hint_y=None, height=30, color=(0,0.5,0,1), font_size=14)
        body.add_widget(self.lbl_count)
        
        self.btn_go_rfid = Button(text='Scan item first', size_hint_y=None, height=75, background_color=(0.6,0.6,0.6,1), background_normal='', bold=True, font_size=22, disabled=True)
        self.btn_go_rfid.bind(on_press=self.go_to_rfid)
        body.add_widget(self.btn_go_rfid)
        
        row = BoxLayout(size_hint_y=None, height=60, spacing=6)
        b1 = Button(text='Import', background_color=(0,0.6,0,1), background_normal='', font_size=16, bold=True)
        b2 = Button(text='Export', background_color=get_color_from_hex(SECONDARY), background_normal='', font_size=16, bold=True)
        b3 = Button(text='Log', background_color=(0.5,0.5,0.5,1), background_normal='', font_size=12)
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
            try:
                app.barcode_mgr.force_enable()
                if app.uhf_mgr.is_inventorying:
                    app.uhf_mgr.stop_inventory()
                if app.uhf_mgr.is_open:
                    app.uhf_mgr.free()
                log_to_file("V28 Barcode enter: UHF closed, Barcode enabled")
            except Exception as e:
                log_to_file(f"V28 Barcode enter UHF close fail: {e}")
            def _setup(dt):
                try:
                    app.uhf_mgr.free()
                    app.barcode_mgr.force_enable()
                    app.barcode_mgr.open()
                    log_to_file("V28 BarcodeScreen on_enter OK - Barcode opened")
                except Exception as e:
                    log_to_file(f"V28 on_enter fail: {e}")
            try:
                app.barcode_mgr.force_enable()
                app.barcode_mgr.open()
            except:
                pass
            Clock.schedule_once(_setup, 0.2)
            Clock.schedule_once(lambda dt: setattr(self.box_bc, 'focus', True), 0.4)
            self.lbl_count.text=f'Items: {app.db_count} | V28 REAL JAR'
            self.update_btn()
        except Exception as e:
            log_to_file(f"V28 on_enter crash: {e} {traceback.format_exc()}")
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
                log_to_file(f"Found {row[1]}")
                self.update_btn()
            else:
                self.lbl_count.text=f'Not found: {code}'
                self.lbl_count.color=(1,0,0,1)
                log_to_file(f"Not found {code}")
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
            log_to_file(f"Go RFID {app.curr_code}")
            self.manager.transition=SlideTransition(direction='left')
            self.manager.current='rfid'
        except Exception as e:
            log_to_file(f"go_to_rfid crash: {e} {traceback.format_exc()}")

    def import_csv(self, inst):
        app = App.get_running_app()
        csv_path = find_csv()
        log_to_file(f"Import {csv_path}")
        if not csv_path:
            self.lbl_count.text=f'No CSV'
            return
        try:
            conn=sqlite3.connect(app.DB)
            c=conn.cursor()
            bc=0
            with open(csv_path,'r',encoding='utf-8',errors='ignore') as f:
                import csv
                reader=csv.DictReader(f)
                for row in reader:
                    bcode=row.get('barcode') or row.get('Barcode') or ''
                    bcode=str(bcode).strip()
                    if not bcode: continue
                    try: item_id=int(row['ItemID'] or row['ItemId'])
                    except: continue
                    c.execute('INSERT OR IGNORE INTO Items VALUES (?,?,?,?,?,?)',(item_id,row.get('ItemLookupCode',''),row.get('Description',''),row.get('Subdescription1',''),row.get('Subdescription2',''),row.get('Subdescription3','')))
                    c.execute('INSERT OR IGNORE INTO Barcod VALUES (NULL,?,?)',(item_id,bcode))
                    bc+=1
            conn.commit()
            c.execute('SELECT count(*) FROM Items')
            app.db_count=c.fetchone()[0]
            conn.close()
            self.lbl_count.text=f'Imported {bc} | Total {app.db_count}'
            log_to_file(f"Imported {bc}")
        except Exception as e:
            self.lbl_count.text=f'Err {e}'
            log_to_file(f"Import crash: {e} {traceback.format_exc()}")

    def export_txt(self, inst):
        try:
            app = App.get_running_app()
            conn=sqlite3.connect(app.DB)
            c=conn.cursor()
            c.execute("SELECT i.ItemLookupCode, i.Description, r.RFID_CODE FROM RFID r JOIN Items i ON r.ItemID=i.ItemID")
            rows=c.fetchall()
            conn.close()
            if not rows:
                self.lbl_count.text='No RFID'
                return
            fn=f"RFID_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            path=os.path.join(APP_FOLDER, fn)
            with open(path,'w',encoding='utf-8') as f:
                f.write("Itemcode | Description | RFID\n")
                for r in rows: f.write(f"{r[0]} | {r[1]} | {r[2]}\n")
            self.lbl_count.text=f'Exported {len(rows)}'
        except Exception as e:
            log_to_file(f"Export crash: {e}")

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
        header=BoxLayout(size_hint_y=None,height=70,padding=6)
        logo_path = find_logo()
        if logo_path:
            try:
                from kivy.uix.image import Image
                header.add_widget(Image(source=logo_path, size_hint_x=0.65, allow_stretch=True, keep_ratio=True))
                header.add_widget(Label(text='[b][color=FF8C00]V16[/color][/b]', markup=True, font_size=14, size_hint_x=0.35))
            except:
                header.add_widget(Label(text='[b]MATRIX ICT V28[/b]', markup=True, font_size=16))
        else:
            header.add_widget(Label(text='[b]MATRIX ICT V28[/b]', markup=True, font_size=16))
        root.add_widget(header)
        body=BoxLayout(orientation='vertical',padding=8,spacing=5)
        self.lbl_item=Label(text='Item: -', size_hint_y=None,height=60,bold=True,color=get_color_from_hex(PRIMARY), font_size=28)
        body.add_widget(self.lbl_item)
        self.lbl_desc=Label(text='Desc: -', size_hint_y=None,height=35,color=(0.2,0.2,0.2,1), font_size=18)
        body.add_widget(self.lbl_desc)
        self.counter=Label(text='Count: 0', size_hint_y=None,height=45,bold=True,color=(0,0.5,0,1), font_size=22)
        body.add_widget(self.counter)
        scroll=ScrollView(size_hint_y=1)
        self.rfid_grid=GridLayout(cols=1,size_hint_y=None,spacing=6, padding=4)
        self.rfid_grid.bind(minimum_height=self.rfid_grid.setter('height'))
        scroll.add_widget(self.rfid_grid)
        body.add_widget(scroll)
        self.box_rfid=TextInput(hint_text='RFID manual', multiline=False,size_hint_y=None,height=55, font_size=20)
        self.box_rfid.bind(on_text_validate=self.add_manual)
        body.add_widget(self.box_rfid)
        self.lbl_status=Label(text='Blue = START/STOP', size_hint_y=None,height=35,color=(0,0.7,0,1), font_size=13)
        body.add_widget(self.lbl_status)
        row1=BoxLayout(size_hint_y=None,height=65,spacing=6)
        self.btn_scan=Button(text='START UHF (Blue)', background_color=(0.15,0.5,0.9,1), background_normal='', bold=True, font_size=20)
        self.btn_clear=Button(text='Clear', background_color=(0.7,0.7,0.7,1), background_normal='', color=(0,0,0,1), font_size=16, bold=True)
        self.btn_scan.bind(on_press=self.toggle_scan)
        self.btn_clear.bind(on_press=self.clear_tags)
        row1.add_widget(self.btn_scan)
        row1.add_widget(self.btn_clear)
        body.add_widget(row1)
        row2=BoxLayout(size_hint_y=None,height=70,spacing=6)
        self.btn_back=Button(text='< Back', background_color=get_color_from_hex(SECONDARY), background_normal='', font_size=16, bold=True)
        self.btn_save=Button(text='SAVE (0)', background_color=get_color_from_hex(PRIMARY), background_normal='', bold=True, font_size=20)
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
            log_to_file(f"V28 RFID enter {app.curr_code} - FORCE CLOSE Barcode REAL")
            try:
                app.barcode_mgr.force_disable()
                app.barcode_mgr.close()
                app.barcode_mgr.force_disable()
                log_to_file("V28 RFID enter: Barcode force_disable x2 REAL")
            except Exception as e:
                log_to_file(f"V28 RFID enter Barcode fail: {e}")
            try:
                app.root.get_screen('barcode').box_bc.focus = False
            except:
                pass
            def _open(dt):
                try:
                    app.barcode_mgr.force_disable()
                    app.barcode_mgr.close()
                    if app.uhf_mgr.has_g2:
                        app.uhf_mgr.open()
                        log_to_file("V28 RFID _open: UHF opened REAL, Barcode closed")
                    else:
                        log_to_file(f"V28 RFID _open: No UHF SDK {app.uhf_mgr.sdk_version} - CHECK reader.jar!")
                except Exception as e:
                    log_to_file(f"V28 RFID _open err {e}")
            try:
                app.barcode_mgr.force_disable()
                if app.uhf_mgr.has_g2:
                    app.uhf_mgr.open()
            except:
                pass
            Clock.schedule_once(_open, 0.1)
            Clock.schedule_once(_open, 0.5)
        except Exception as e:
            log_to_file(f"RFID on_enter crash: {e} {traceback.format_exc()}")

    def on_leave(self):
        try:
            app=App.get_running_app()
            Clock.unschedule(self.poll)
            app.uhf_mgr.stop_inventory()
            app.uhf_mgr.free()
            app.barcode_mgr.open()
            app.current_screen_name = 'barcode'
        except: pass

    def refresh(self):
        try:
            app=App.get_running_app()
            self.rfid_grid.clear_widgets()
            self.btn_save.text=f'SAVE ({len(app.rfid_list)})'
            if not app.rfid_list:
                self.rfid_grid.add_widget(Label(text='No tags - Blue=UHF', size_hint_y=None,height=60,color=(0.6,0.6,0.6,1), font_size=18))
                return
            for rf in app.rfid_list:
                row=BoxLayout(size_hint_y=None,height=60,spacing=5)
                lbl=Label(text=rf,size_hint_x=0.78,color=(0,0,0,1),font_size=18)
                bx=Button(text='X',size_hint_x=0.22,background_color=(1,0.25,0.25,1),background_normal='', font_size=18)
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
            if not app.uhf_mgr.has_g2:
                log_to_file(f"V28 UHF has_g2=False, SDK={app.uhf_mgr.sdk_version} - FAKE mode REAL JAR MISSING")
                self.lbl_status.text = f"No UHF SDK ({app.uhf_mgr.sdk_version}) - Fake"
                fake = f"E28011{random.randint(0,999):03d}{datetime.now().strftime('%H%M%S')}{random.randint(10,99)}"
                if self.add_tag_unique(fake):
                    self.refresh()
                    self.counter.text=f'Count: {len(app.rfid_list)} (Fake - No SDK REAL JAR MISSING)'
                return
            log_to_file(f"V28 UHF toggle: has_g2=True {app.uhf_mgr.sdk_version} is_open={app.uhf_mgr.is_open}")
            if app.uhf_mgr.is_inventorying:
                app.uhf_mgr.stop_inventory()
                Clock.unschedule(self.poll)
                self.btn_scan.text='START UHF (Blue)'
                self.btn_scan.background_color=(0.15,0.5,0.9,1)
                self.lbl_status.text = 'UHF Stopped REAL'
                log_to_file("V28 UHF STOP")
            else:
                if not app.uhf_mgr.is_open:
                    app.uhf_mgr.open()
                if app.uhf_mgr.start_inventory():
                    Clock.schedule_interval(self.poll, 0.25)
                    self.btn_scan.text='STOP UHF'
                    self.btn_scan.background_color=(0.9,0.2,0.2,1)
                    self.lbl_status.text = 'UHF Scanning REAL...'
                    log_to_file("V28 UHF START OK REAL")
                else:
                    self.lbl_status.text = 'UHF Start Failed'
                    log_to_file("V28 UHF start failed")
        except Exception as e:
            log_to_file(f"V28 toggle crash {e} {traceback.format_exc()}")

    def poll(self, dt):
        try:
            tags=App.get_running_app().uhf_mgr.read_tags()
            added=0
            for t in tags:
                if self.add_tag_unique(t): added+=1
            if added>0:
                self.refresh()
                self.counter.text=f'Count: {len(App.get_running_app().rfid_list)} Real'
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
            switch_to_barcode_mode()
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

    def on_hardware_key(self, window, key, scancode, codepoint, modifier):
        try:
            log_to_file(f"V28 KEY {key} sc={scancode} screen={self.current_screen_name}")
            if self.current_screen_name == 'rfid':
                try:
                    self.barcode_mgr.force_disable()
                    self.barcode_mgr.close()
                except:
                    pass
                try:
                    if self.barcode_mgr.is_open:
                        log_to_file("V28 WARNING Barcode still open in RFID! Closing")
                        self.barcode_mgr.force_disable()
                except:
                    pass
                if key not in [4, 3]:
                    try:
                        self.root.get_screen('rfid').toggle_scan(None)
                        log_to_file(f"V28 RFID key {key} -> UHF (Barcode blocked REAL)")
                    except Exception as e:
                        log_to_file(f"V28 toggle fail {e}")
                    return True
            if self.current_screen_name == 'barcode':
                try:
                    if self.barcode_mgr.disabled:
                        self.barcode_mgr.force_enable()
                    if not self.barcode_mgr.is_open:
                        self.barcode_mgr.open()
                    if self.uhf_mgr.is_inventorying:
                        self.uhf_mgr.stop_inventory()
                    if self.uhf_mgr.is_open:
                        self.uhf_mgr.free()
                except:
                    pass
                return False
            return False
        except Exception as e:
            log_to_file(f"V28 key crash {e} {traceback.format_exc()}")
            return False
        except Exception as e:
            log_to_file(f"key crash {e}")
            return False
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
