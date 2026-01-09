#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys

def install_if_missing(import_name, pip_name=None):
    if pip_name is None:
        pip_name = import_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"Inštalujem {pip_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])

# externé balíky
install_if_missing("serial", "pyserial")
install_if_missing("tk")


import serial, threading, time, random, json
import tkinter as tk
from tkinter import ttk, filedialog
import serial.tools.list_ports


BAUD_OPTIONS = [600,1200,2400,4800,9600,19200,38400,57600,115200,230400,460800,921600]

LANGS = {
    "SK":{
        "choose_test_file":"Zvoliť test súbor","log_file":"LOG súbor:",
        "choose_log_file":"Zvoliť LOG súbor","refresh_ports":"Nacítat COM porty",
        "save_log":"Ukladať LOG","stop_on_error":"Zastaviť pri chybe",
        "min_block_size":"Min. veľkosť pren. blok v byte:","max_block_size":"Max. veľkosť pren. blok v byte:",
        "min_swap_dir":"Min. počet bytov pre zmenu smeru:","max_swap_dir":"Max. počet bytov pre zmenu smeru:",
        "min_swap_baud":"Min. počet bytov pre zmenu baudrate:","max_swap_baud":"Max. počet bytov pre zmenu baudrate:",
        "load_settings":"Načítať nastavenia","save_settings":"Uložiť nastavenia",
        "start_test":"Spustiť test","stop_test":"Zastaviť test",
        "cycle_label":"Cyklus: {cycle}  Chyby: {errors}",
        "direction_label":"Smer: {dir}",
        "error":"Chyba! {dir}, Tx:{tx}, Rx:{rx}, TxCharTime:{TxChar_Time}ms, TxCharDelay:{TxChar_Delay}ms, Timeout Rx bloku {RxBlock_Timeout}ms",
        "exception":"? Výnimka na byte {index}: {e}",
        "cycle_header":"--- Cyklus {cycle} ---",
        "direction_changed":"--- Smer zmenený {dir} ---",
        "baud_changed":"--- Zmena baudrate na {baud} ---",
        "select_file":"? Zvoliť súbor",
        "com_error":"? COM chyba: {e}",
        "file_error":"? Chyba súboru: {e}",
        "stat_a2b":"A->B: {bytes} b",
        "stat_b2a":"B->A: {bytes} b",
        "stat_bad":"[{bad}]",
        "stat_total":"Spolu: {bytes} bytov",
        "summary_header":"--- CELKOVÉ ŠTATISTIKY ---",
        "summary_line":"{label}: {bytes} b [{bad} zlých]",
        "byte_delay_label":"Časová medzera medzi znakmi [ms]:",
        "Baud_delay_label":"Oneskorenie vysielania po zmene baudrate [ms]:"
    },
    "EN":{
        "choose_test_file":"Select test file","log_file":"LOG file:",
        "choose_log_file":"Select LOG file","refresh_ports":"Refresh COM ports",
        "save_log":"Save LOG","stop_on_error":"Stop on error",
        "min_block_size":"Min. size of the transferred block [bytes]:","max_block_size":"Max. size of the transferred block [bytes]:",
        "min_swap_dir":"Min bytes swap direction:","max_swap_dir":"Max bytes swap direction:",
        "min_swap_baud":"Min bytes swap baudrate:","max_swap_baud":"Max bytes swap baudrate:",
        "load_settings":"Load settings","save_settings":"Save settings",
        "start_test":"Start test","stop_test":"Stop test",
        "cycle_label":"Cycle: {cycle}  Errors: {errors}",
        "direction_label":"Direction: {dir}",
        "error":"Error! {dir}, Tx:{tx}, Rx:{rx}, TxCharTime:{TxChar_Time}ms, TxCharDelay:{TxChar_Delay}ms, Rx Block Timeout: {RxBlock_Timeout}ms",
        "exception":"? Exception at byte {index}: {e}",
        "cycle_header":"--- Cycle {cycle} ---",
        "direction_changed":"--- Direction changed {dir} ---",
        "baud_changed":"--- Baudrate changed to {baud} ---",
        "select_file":"? Select file",
        "com_error":"? COM error: {e}",
        "file_error":"? File error: {e}",
        "stat_a2b":"A->B: {bytes} b",
        "stat_b2a":"B->A: {bytes} b",
        "stat_bad":"[{bad}]",
        "stat_total":"Total: {bytes} bytes",
        "summary_header":"--- TOTAL STATISTICS ---",
        "summary_line":"{label}: {bytes} b [{bad} bad]",
        "byte_delay_label":"Time Delay between characters [ms]:",
        "Baud_delay_label":"Transmission delay after baud rate change [ms]:"      
    }
}

class SerialStressTester(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Serial Stress Tester v1.0")
        self.geometry("1280x750")
        self.minsize(800,600)
        self.running=False
        self.thread=None
        self.cycle=0
        self.errors=0
        self.lang="SK"

        # Premenné
        self.a_port_var=tk.StringVar()
        self.b_port_var=tk.StringVar()
        self.filepath=tk.StringVar()
        self.logfile=tk.StringVar()
        self.save_log=tk.BooleanVar(value=False)
        self.stop_on_error=tk.BooleanVar(value=True)
        self.min_block_size=tk.IntVar(value=10)
        self.max_block_size=tk.IntVar(value=100)
        self.min_swap_dir=tk.IntVar(value=10)
        self.max_swap_dir=tk.IntVar(value=100)
        self.min_swap_baud=tk.IntVar(value=10)
        self.max_swap_baud=tk.IntVar(value=100)
        self.byte_delay = tk.DoubleVar(value=0.0)  # oneskorenie medzi bajtmi v sekundách        
        self.baud_checks={}
        self.hex_log_max_chars=500
        self._prev_stats = {b: {'A->B':0,'B->A':0,'Total':0} for b in BAUD_OPTIONS}  # pre sledovanie zmien
        self.baud_delay = tk.DoubleVar(value=0.05)  # predvolených 50 ms

        # GUI update interval (sekundy)
        self.gui_update_interval=0.05
        self._last_gui_update=time.time()

        # Status
        self.direction_label_var=tk.StringVar(value="")
        self.cycle_label_var=tk.StringVar(value="")
        self.stats_labels={}  # pre štatistiku (teraz mapuje na sub-labely)
        self.make_ui()
        self.detect_com_ports()
        self.update_texts()

    def clear_all(self):
        # Vymaže log
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")

        # Vynuluje štatistiky
        for b in BAUD_OPTIONS:
            if b in self.stats_labels:
                lbls = self.stats_labels[b]
                for key in lbls:
                    if 'ok' in key:
                        lbls[key].config(text=self._t("stat_total", bytes=0), fg="black")
                    else:
                        lbls[key].config(text=self._t("stat_bad", bad=0))
        # Reset číselníkov pre _stats
        self._stats = {b: {'A->B':0,'B->A':0,'Total':0,'A->B_err':0,'B->A_err':0,'Total_err':0} for b in BAUD_OPTIONS}
        self._prev_stats = {b: {'A->B':0,'B->A':0,'Total':0} for b in BAUD_OPTIONS}

        # Reset počítadiel
        self.cycle = 0
        self.errors = 0
        self.direction_label_var.set("")
        self.cycle_label_var.set(self._t("cycle_label", cycle=self.cycle, errors=self.errors))


    def _t(self,key,**kwargs):
        return LANGS[self.lang].get(key,key).format(**kwargs)

    # --------------------------- UI ---------------------------
    def make_ui(self):
        frm = tk.Frame(self, padx=10, pady=10)
        frm.pack(fill="both", expand=True)

        # Jazykove tlacitka
        lang_frame = tk.Frame(frm)
        lang_frame.grid(row=0, column=3, sticky="e")
        for code in LANGS.keys():
            tk.Button(lang_frame, text=code, command=lambda c=code: self.set_lang(c)).pack(side="left", padx=2)

        # Nastavenia a jazyk
        self.load_settings_btn = tk.Button(frm, text="", command=self.load_settings)
        self.load_settings_btn.grid(row=0, column=0)
        self.save_settings_btn = tk.Button(frm, text="", command=self.save_settings)
        self.save_settings_btn.grid(row=1, column=0)


        # Porty
        tk.Label(frm, text="Port A:").grid(row=0, column=0, sticky="e")
        self.a_combo = ttk.Combobox(frm, textvariable=self.a_port_var, width=60)
        self.a_combo.grid(row=0, column=1, sticky="w")
        tk.Label(frm, text="Port B:").grid(row=1, column=0, sticky="e")
        self.b_combo = ttk.Combobox(frm, textvariable=self.b_port_var, width=60)
        self.b_combo.grid(row=1, column=1, sticky="w")
        self.refresh_ports_btn = tk.Button(frm, text="", command=self.detect_com_ports)
        self.refresh_ports_btn.grid(row=1, column=2, sticky="w", padx=5)

        # Súbor
        self.choose_file_btn = tk.Button(frm, text="", command=self.choose_test_file)
        self.choose_file_btn.grid(row=3, column=0, sticky="w")
        tk.Entry(frm, textvariable=self.filepath, width=80).grid(row=3, column=1, columnspan=3, sticky="w")

        
        
        self.min_block_size_label = tk.Label(frm, text="")
        self.min_block_size_label.grid(row=4, column=0, sticky="e")
        tk.Entry(frm, textvariable=self.min_block_size, width=10).grid(row=4, column=1, sticky="w")

        self.max_block_size_label = tk.Label(frm, text="")
        self.max_block_size_label.grid(row=4, column=2, sticky="e")
        tk.Entry(frm, textvariable=self.max_block_size, width=10).grid(row=4, column=3, sticky="w")


        # Swap nastavenia
        self.min_swap_dir_label = tk.Label(frm, text="")
        self.min_swap_dir_label.grid(row=5, column=0, sticky="e")
        tk.Entry(frm, textvariable=self.min_swap_dir, width=10).grid(row=5, column=1, sticky="w")
        
        self.max_swap_dir_label = tk.Label(frm, text="")
        self.max_swap_dir_label.grid(row=5, column=2, sticky="e")
        tk.Entry(frm, textvariable=self.max_swap_dir, width=10).grid(row=5, column=3, sticky="w")

        self.min_swap_baud_label = tk.Label(frm, text="")
        self.min_swap_baud_label.grid(row=6, column=0, sticky="e")
        tk.Entry(frm, textvariable=self.min_swap_baud, width=10).grid(row=6, column=1, sticky="w")
        
        self.max_swap_baud_label = tk.Label(frm, text="")
        self.max_swap_baud_label.grid(row=6, column=2, sticky="e")
        tk.Entry(frm, textvariable=self.max_swap_baud, width=10).grid(row=6, column=3, sticky="w")

        # Byte delay
        tk.Label(frm, text=self._t("byte_delay_label")).grid(row=7, column=0, sticky="e")
        tk.Entry(frm, textvariable=self.byte_delay, width=10).grid(row=7, column=1, sticky="w")

        tk.Label(frm, text=self._t("Baud_delay_label")).grid(row=7, column=2, sticky="e")
        tk.Entry(frm, textvariable=self.baud_delay, width=10).grid(row=7, column=3, sticky="w")

        # LOG nastavenia
        self.save_log_cb = tk.Checkbutton(frm, text="", variable=self.save_log)
        self.save_log_cb.grid(row=8, column=0, sticky="w", padx=2)
        self.choose_log_btn = tk.Button(frm, text="", command=self.choose_logfile)
        self.choose_log_btn.grid(row=8, column=1, sticky="w")
        self.log_file_label = tk.Label(frm, text="")
        self.log_file_label.grid(row=8, column=2, sticky="e")
        self.log_entry = tk.Entry(frm, textvariable=self.logfile, width=80)
        self.log_entry.grid(row=8, column=3, sticky="we")
        
        # Štatistika nad log oknom
        self.stats_frame = tk.Frame(frm)
        self.stats_frame.grid(row=11, column=0, columnspan=4, sticky="we", pady=2)
        # checkboxy pre vybratie aktívnych baudov
        for b in BAUD_OPTIONS:
            var = tk.BooleanVar(value=(b==115200))
            cb = tk.Checkbutton(self.stats_frame, text=str(b), variable=var)
            cb.grid(row=0, column=BAUD_OPTIONS.index(b), sticky="w")
            self.baud_checks[b] = var

        # Labels pre každý baud
        self.stats_labels = {}
        for col, b in enumerate(BAUD_OPTIONS):
            self.stats_labels[b] = {}
            f_ab = tk.Frame(self.stats_frame); f_ab.grid(row=1, column=col, sticky="w")
            lbl_ab_ok = tk.Label(f_ab, text=self._t("stat_a2b", bytes=0), fg="black"); lbl_ab_ok.pack(side="left")
            lbl_ab_bad = tk.Label(f_ab, text=" "+self._t("stat_bad", bad=0), fg="#800000"); lbl_ab_bad.pack(side="left")
            self.stats_labels[b]['A->B_ok'] = lbl_ab_ok; self.stats_labels[b]['A->B_bad'] = lbl_ab_bad

            f_ba = tk.Frame(self.stats_frame); f_ba.grid(row=2, column=col, sticky="w")
            lbl_ba_ok = tk.Label(f_ba, text=self._t("stat_b2a", bytes=0), fg="black"); lbl_ba_ok.pack(side="left")
            lbl_ba_bad = tk.Label(f_ba, text=" "+self._t("stat_bad", bad=0), fg="#800000"); lbl_ba_bad.pack(side="left")
            self.stats_labels[b]['B->A_ok'] = lbl_ba_ok; self.stats_labels[b]['B->A_bad'] = lbl_ba_bad

            f_tot = tk.Frame(self.stats_frame); f_tot.grid(row=3, column=col, sticky="w")
            lbl_tot_ok = tk.Label(f_tot, text=self._t("stat_total", bytes=0), fg="black"); lbl_tot_ok.pack(side="left")
            lbl_tot_bad = tk.Label(f_tot, text=" "+self._t("stat_bad", bad=0), fg="#800000"); lbl_tot_bad.pack(side="left")
            self.stats_labels[b]['Total_ok'] = lbl_tot_ok; self.stats_labels[b]['Total_bad'] = lbl_tot_bad

        # Log
        log_frame = tk.Frame(frm)
        log_frame.grid(row=12, column=0, columnspan=4, sticky="nsew")
        frm.rowconfigure(12, weight=1)
        frm.columnconfigure(1, weight=1)
        self.log = tk.Text(log_frame, height=15, state="disabled", bg="#111", fg="#0f0", wrap="char", insertbackground="#0f0")
        self.scrollbar = tk.Scrollbar(log_frame, command=self.log.yview)
        self.log.configure(yscrollcommand=self.scrollbar.set)
        self.log.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # ------------------- Test Controls -------------------
        self.ctrl_frame = tk.Frame(frm)
        self.ctrl_frame.grid(row=13, column=0, columnspan=4, pady=6, sticky="we")
        self.ctrl_frame.columnconfigure(2, weight=1)  # status sa roztiahne

        # Stop on error checkbox
        self.stop_on_error_cb = tk.Checkbutton(self.ctrl_frame, text=self._t("stop_on_error"), variable=self.stop_on_error)
        self.stop_on_error_cb.grid(row=0, column=0, sticky="w", padx=5)

        # Start button
        self.start_btn = tk.Button(self.ctrl_frame, text=self._t("start_test"), bg="#4CAF50", fg="white", command=self.start_test)
        self.start_btn.grid(row=0, column=1, sticky="w", padx=5)

        # Status label 
        self.status_var = tk.StringVar(value="")
        self.status_label = tk.Label(self.ctrl_frame, textvariable=self.status_var, anchor="w", bg="#eee")
        self.status_label.grid(row=0, column=2, sticky="we", padx=5)
       
        # Stop button
        self.stop_btn = tk.Button(self.ctrl_frame, text=self._t("stop_test"), bg="#f44336", fg="white", command=self.stop_test)
        self.stop_btn.grid(row=0, column=3, sticky="e", padx=5)

        # Clear button
        self.clear_btn = tk.Button(self.ctrl_frame, text="Clear", bg="#2196F3", fg="white", command=self.clear_all)
        self.clear_btn.grid(row=0, column=4, sticky="e", padx=5)



    # --------------------------- jazyk ---------------------------
    def set_lang(self,code):
        self.lang=code
        self.update_texts()
        self.update_stats()

    def update_texts(self):
        self.save_log_cb.config(text=self._t("save_log"))
        self.stop_on_error_cb.config(text=self._t("stop_on_error"))
        self.min_block_size_label.config(text=self._t("min_block_size"))
        self.max_block_size_label.config(text=self._t("max_block_size"))
        self.min_swap_dir_label.config(text=self._t("min_swap_dir"))
        self.max_swap_dir_label.config(text=self._t("max_swap_dir"))
        self.min_swap_baud_label.config(text=self._t("min_swap_baud"))
        self.max_swap_baud_label.config(text=self._t("max_swap_baud"))
        self.log_file_label.config(text=self._t("log_file"))
        self.choose_file_btn.config(text=self._t("choose_test_file"))
        self.choose_log_btn.config(text=self._t("choose_log_file"))
        self.refresh_ports_btn.config(text=self._t("refresh_ports"))
        self.load_settings_btn.config(text=self._t("load_settings"))
        self.save_settings_btn.config(text=self._t("save_settings"))
        self.start_btn.config(text=self._t("start_test"))
        self.stop_btn.config(text=self._t("stop_test"))
        self.cycle_label_var.set(self._t("cycle_label", cycle=self.cycle, errors=self.errors))
        self.direction_label_var.set(self._t("direction_label", dir=""))
        
     # --- Štatistika ---
    def update_stats(self, stats=None):
        """Aktualizuje GUI štatistiky podla self._stats alebo poskytnutého dict."""
        if stats is None:
            stats = getattr(self, "_stats", {})
        for baud, vals in stats.items():
          if baud not in self.stats_labels:
              continue
          lbls = self.stats_labels[baud]

          # A->B
          new_val = vals.get('A->B',0)
          if getattr(lbls['A->B_ok'], "_last_val", None) != new_val:
              lbls['A->B_ok'].config(fg="green")
          else:
              lbls['A->B_ok'].config(fg="black")
          lbls['A->B_ok'].config(text=self._t("stat_a2b", bytes=new_val))
          lbls['A->B_ok']._last_val = new_val

          new_err = vals.get('A->B_err',0)
          lbls['A->B_bad'].config(text=self._t("stat_bad", bad=new_err))

          # B->A
          new_val = vals.get('B->A',0)
          if getattr(lbls['B->A_ok'], "_last_val", None) != new_val:
              lbls['B->A_ok'].config(fg="green")
          else:
              lbls['B->A_ok'].config(fg="black")
          lbls['B->A_ok'].config(text=self._t("stat_b2a", bytes=new_val))
          lbls['B->A_ok']._last_val = new_val

          new_err = vals.get('B->A_err',0)
          lbls['B->A_bad'].config(text=self._t("stat_bad", bad=new_err))

          # Total
          new_val = vals.get('Total',0)
          if getattr(lbls['Total_ok'], "_last_val", None) != new_val:
              lbls['Total_ok'].config(fg="green")
          else:
              lbls['Total_ok'].config(fg="black")
          lbls['Total_ok'].config(text=self._t("stat_total", bytes=new_val))
          lbls['Total_ok']._last_val = new_val

          new_err = vals.get('Total_err',0)
          lbls['Total_bad'].config(text=self._t("stat_bad", bad=new_err))
    
    # --------------------------- COM ---------------------------
    def detect_com_ports(self):
        ports=serial.tools.list_ports.comports()
        port_list=[f"{p.device} - {p.description}" for p in ports]
        self.a_combo['values']=port_list
        self.b_combo['values']=port_list
        if port_list:
            self.a_port_var.set(port_list[0])
            self.b_port_var.set(port_list[0])

    def choose_test_file(self):
        f=filedialog.askopenfilename()
        if f:self.filepath.set(f)

    def choose_logfile(self):
        f=filedialog.asksaveasfilename(defaultextension=".txt")
        if f:self.logfile.set(f)

    # --------------------------- Log ---------------------------
    def log_msg(self,msg, inline=False, stop=False):
        # Ukladame do bufferu a GUI refreshujeme len podla intervalov
        if inline:
            self._log_buffer.append(msg)
        else:
            self._log_buffer.append("\n"+msg)

        # zapis do suboru okamzite
        if self.save_log.get() and self.logfile.get():
            try:
                with open(self.logfile.get(),"a") as f:
                    if inline:
                        f.write(msg)
                    else:
                        f.write("\n"+msg)
            except Exception:
                pass

        # stop flag
        if stop:
            self.running=False

    def _update_gui(self):
        """Flush log buffer a aktualizuje GUI podla _stats a ostatných premenných."""
        for item in self._log_buffer:
            # bezpecné rozbalenie
            if len(item) == 3:
                msg, inline, _ = item
            elif len(item) == 2:
                msg, inline = item
                _ = False
            else:
                msg = str(item)
                inline = False
                _ = False

            self.log.config(state="normal")
            if inline:
                # vložíme medzeru len ak log už nie je prázdny a posledný znak nie je medzera
                if self.log.index("end-1c") != "1.0":  # log nie je prázdny
                    end_char = self.log.get("end-2c", "end-1c")
                    if end_char not in (" ", "\n"):
                        self.log.insert("end", " ")
                self.log.insert("end", msg)
            else:
                self.log.insert("end", "\n" + msg)

            # orezanie dlhého logu
            if len(self.log.get("1.0", "end")) > self.hex_log_max_chars * 3:
                self.log.delete("1.0", f"1.{len(self.log.get('1.0','end'))-self.hex_log_max_chars*3}")
            self.log.see("end")
            self.log.config(state="disabled")

            # zapis do log súboru
            if self.save_log.get() and self.logfile.get():
                try:
                    with open(self.logfile.get(), "a") as f:
                        if inline:
                            f.write(msg + " ")
                        else:
                            f.write("\n" + msg + "\n")
                except Exception:
                    pass

        self._log_buffer.clear()

        # aktualizácia GUI prvkov
        # --- Štatistika ---
        for baud, vals in self._stats.items():
            if baud not in self.stats_labels:
                continue
            lbls = self.stats_labels[baud]

            # A->B
            if vals['A->B'] != self._prev_stats[baud]['A->B']:
                lbls['A->B_ok'].config(text=self._t("stat_a2b", bytes=vals['A->B']), fg="green")
            else:
                lbls['A->B_ok'].config(fg="black")
            lbls['A->B_bad'].config(text=self._t("stat_bad", bad=vals['A->B_err']), fg="black")

            # B->A
            if vals['B->A'] != self._prev_stats[baud]['B->A']:
                lbls['B->A_ok'].config(text=self._t("stat_b2a", bytes=vals['B->A']), fg="green")
            else:
                lbls['B->A_ok'].config(fg="black")
            lbls['B->A_bad'].config(text=self._t("stat_bad", bad=vals['B->A_err']), fg="black")

            # Total
            if vals['Total'] != self._prev_stats[baud]['Total']:
                lbls['Total_ok'].config(text=self._t("stat_total", bytes=vals['Total']), fg="green")
            else:
                lbls['Total_ok'].config(fg="black")
            lbls['Total_bad'].config(text=self._t("stat_bad", bad=vals['Total_err']), fg="black")

            # uloženie hodnoty pre další update
            self._prev_stats[baud]['A->B'] = vals['A->B']
            self._prev_stats[baud]['B->A'] = vals['B->A']
            self._prev_stats[baud]['Total'] = vals['Total']
    
            status_text = f"Cycle: {self.cycle}  Errors: {self.errors}   Block size: {self._current_block_size}   Baudrate: {self._current_baud}  TxChar_Time: {round(self._Char_time*1000, 3)}ms  TxChar_Delay: {round(self._TxInterByteDelay*1000, 3)}ms  RxBlockTimeout: {round(self._RxBlock_Timeout*1000, 3)}ms"
            
            self.status_var.set(status_text)

            # update direction a cycle labels
            self.direction_label_var.set(self._t("direction_label", dir=self._direction_label))
            self.cycle_label_var.set(self._t("cycle_label", cycle=self.cycle, errors=self.errors))

    
    # --------------------------- Settings ---------------------------
    def save_settings(self):
        f=filedialog.asksaveasfilename(defaultextension=".set",filetypes=[("SET files","*.set")])
        if not f:return
        data={
            "a_port":self.a_port_var.get(),
            "b_port":self.b_port_var.get(),
            "filepath":self.filepath.get(),
            "logfile":self.logfile.get(),
            "save_log":self.save_log.get(),
            "stop_on_error":self.stop_on_error.get(),
            "min_block_size":self.min_block_size.get(),
            "max_block_size":self.max_block_size.get(),
            "min_swap_dir":self.min_swap_dir.get(),
            "max_swap_dir":self.max_swap_dir.get(),
            "min_swap_baud":self.min_swap_baud.get(),
            "max_swap_baud":self.max_swap_baud.get(),
            "baud_checks":{str(k):v.get() for k,v in self.baud_checks.items()},
            "lang":self.lang,
            "byte_delay": self.byte_delay.get(),
            "baud_delay": self.baud_delay.get()
        }
        with open(f,"w") as file:
            json.dump(data,file,indent=2)

    def load_settings(self):
        f=filedialog.askopenfilename(filetypes=[("SET files","*.set")])
        if not f:return
        with open(f) as file:
            data=json.load(file)
        self.a_port_var.set(data.get("a_port",""))
        self.b_port_var.set(data.get("b_port",""))
        self.filepath.set(data.get("filepath",""))
        self.logfile.set(data.get("logfile",""))
        self.save_log.set(data.get("save_log",False))
        self.stop_on_error.set(data.get("stop_on_error",True))
        self.min_block_size.set(data.get("min_block_size",0))
        self.max_block_size.set(data.get("max_block_size",100))
        self.min_swap_dir.set(data.get("min_swap_dir",0))
        self.max_swap_dir.set(data.get("max_swap_dir",100))
        self.min_swap_baud.set(data.get("min_swap_baud",0))
        self.max_swap_baud.set(data.get("max_swap_baud",100))
        for k,v in data.get("baud_checks",{}).items():
            if int(k) in self.baud_checks:self.baud_checks[int(k)].set(v)
        self.lang=data.get("lang","SK")
        self.byte_delay.set(data.get("byte_delay", 0.0))
        self.baud_delay.set(data.get("baud_delay", 0.05))
        self.update_texts()

    # --------------------------- Test ---------------------------
    def start_test(self):
        if self.running:return
        if not self.filepath.get():self.log_msg(self._t("select_file"));return
        self.running=True
        self._log_buffer=[]
        self._stats={}
        self._direction_label=""
        self.thread=threading.Thread(target=self.run_loop,daemon=True)
        self.thread.start()
        # GUI refresh loop
        self.after(int(self.gui_update_interval*1000), self._gui_refresh_loop)

    def _gui_refresh_loop(self):
        if self.running:
            self._update_gui()
            self.after(int(self.gui_update_interval*1000), self._gui_refresh_loop)
        else:
            self._update_gui()  # final update

    def run_loop(self):
        try:
            baud_list = [b for b, v in self.baud_checks.items() if v.get()]
            if not baud_list:
                self.log_msg("❌ Žiadny baudrate povolený")
                self.running = False
                return

            current_baud = baud_list[0]  # počiatočný baud z povolených
            last_baud = None

            def Char_time(baud):
                return (10 / baud)  # plati pre 8-bit komunikaciu + 1 start + 1 stop bit

            a_port = serial.Serial(
                self.a_port_var.get().split(" - ")[0],
                current_baud,
            )
            b_port = serial.Serial(
                self.b_port_var.get().split(" - ")[0],
                current_baud,
            )
        except Exception as e:
            self.log_msg(self._t("com_error", e=e))
            self.running = False
            return

        try:
            with open(self.filepath.get(), "rb") as f:
                data = f.read()
        except Exception as e:
            self.log_msg(self._t("file_error", e=e))
            self.running = False
            return

        direction = 0
        next_dir = direction
        stats = {b: {'A->B':0,'B->A':0,'Total':0,'A->B_err':0,'B->A_err':0,'Total_err':0} for b in baud_list}
        self._stats = stats
        self._direction_label = "A→B"

        index = 0
        self._current_block_size = 0
        self._current_baud = current_baud
        next_baud = current_baud
        self._Char_time = 0
        self._TxInterByteDelay = 0
        self._RxBlock_Timeout = 0
        self._RxTimeCounter = 0
        
        # nastavenie velkosti bloku podla nastaveni min a max parametrov
        if self.max_swap_dir.get() > 0 and self.min_swap_dir.get() > 0:
            next_dir = index + random.randint(max(1, self.min_swap_dir.get()), max(self.max_swap_dir.get(), self.min_swap_dir.get()))
            if next_dir == index: 
                next_dir = index + 1
        else: next_dir = 0
        
        if self.min_swap_baud.get() > 0 and self.max_swap_baud.get() > 0:
            next_baud = index + random.randint(max(1, self.min_swap_baud.get()), max(self.max_swap_baud.get(), self.min_swap_baud.get()))
            if next_baud == index: 
                next_baud = index + 1
        else: next_baud = 0                
                
        if next_dir > index and next_baud > index:
            block_size = min(next_dir - index, next_baud - index, len(data) - index)
        else:
            if next_dir > index:
                block_size = next_dir - index
            else:
                if next_baud > index:
                    block_size = next_baud - index
                else:
                    block_size = random.randint(self.min_block_size.get(), self.max_block_size.get())
        
        

        
        stop_flag = 0
        while self.running:
            if index >= len(data):
                index = 0
                self.cycle += 1
                if self.max_swap_dir.get() > 0 and self.min_swap_dir.get() > 0:
                    next_dir = index + random.randint(max(1, self.min_swap_dir.get()), max(self.max_swap_dir.get(), self.min_swap_dir.get()))
                    if next_dir == index: 
                        next_dir = index + 1
                else: next_dir = 0
                if self.min_swap_baud.get() > 0 and self.max_swap_baud.get() > 0:    
                    next_baud = index + random.randint(max(1, self.min_swap_baud.get()), max(self.max_swap_baud.get(), self.min_swap_baud.get()))
                    if next_baud == index: 
                        next_baud = index + 1
                else: next_baud = 0
                
            if next_dir > index and next_baud > index:
                block_size = min(next_dir - index, next_baud - index, len(data) - index)
            else:
                if next_dir > index:
                    block_size = next_dir - index
                else:
                    if next_baud > index:
                        block_size = next_baud - index
                    else:
                        block_size = random.randint(self.min_block_size.get(), self.max_block_size.get())
            
            block = data[index:index+block_size]

            tport, rport = (a_port, b_port) if direction == 0 else (b_port, a_port)

            self._current_block_size = len(block)
            self._current_baud = current_baud
            self._Char_time = Char_time(current_baud)
            
            try:
                tport.flush()
                rport.flush()
                tport.reset_output_buffer()
                rport.reset_input_buffer()
                                        
                self._RxBlock_Timeout = 0
                rx_block = b""
                
                expected = len(block)
                
                self._RxBlock_Timeout = (self._Char_time * (len(block))) + ((self.byte_delay.get()/1000) * len(block))
                self._RxBlock_Timeout += (self._RxBlock_Timeout/100) * 100       # prirataj 100%  
                rport.timeout = None  #self._RxBlock_Timeout
                
                self._TxInterByteDelay = (self.byte_delay.get()/1000)   
                tport.inter_byte_timeout = self._TxInterByteDelay 
                
                
                tport.write(block)
                TimerStart = time.perf_counter_ns()

                timeout_s = self._RxBlock_Timeout
                start_ns = time.perf_counter_ns()
                deadline_ns = start_ns + int(timeout_s * 1e9)
                
                while len(rx_block) < expected:
                    avail = rport.in_waiting
                    if avail > 0:
                        chunk = rport.read(min(avail, expected - len(rx_block)))
                        rx_block += chunk
                    else:
                        # check timeout
                        if time.perf_counter_ns() > deadline_ns:
                            print("TIMEOUT")
                            break
                        time.sleep(0.001)  # 1 ms, aby CPU nebusy-waitoval


                TimerEnd = time.perf_counter_ns()
                
                _RxTimeCounter = TimerEnd - TimerStart
                
                self.log_msg(f"Rx time:{_RxTimeCounter/1000000} msec")
                
                b_stats = stats[current_baud]
                inline_log = []

                for i, b_byte in enumerate(block):
                    rx_byte = rx_block[i] if i < len(rx_block) else None
                    sent_hex = f"{b_byte:02X}"
                    recv_hex = f"{rx_byte:02X}" if rx_byte is not None else "??"
                    err_flag = (rx_byte is None or rx_byte != b_byte)
                    dir_label = "A→B" if direction == 0 else "B→A"

                    if err_flag:
                        self.errors += 1
                        stop_flag = self.stop_on_error.get()
                        sent_block_hex = " ".join(f"{x:02X}" for x in block)
                        recv_block_hex = " ".join(f"{x:02X}" for x in rx_block)
                        self.log_msg(f"Tx:[{len(block)}B]: {sent_block_hex}")
                        self.log_msg(f"Rx:[{len(rx_block)}B]: {recv_block_hex}")
                        self.log_msg(f"Rx time:{_RxTimeCounter/1000000} usec")
                        self.log_msg(f"Rx buffer contains:{rport.in_waiting} bytes")
                        self.log_msg(self._t("error", dir=dir_label, tx=sent_hex, rx=recv_hex, TxChar_Time=round(self._Char_time*1000, 3), TxChar_Delay=round(self._TxInterByteDelay*1000, 3), RxBlock_Timeout=round(self._RxBlock_Timeout*1000, 3)))

                        if direction == 0:
                            b_stats['A->B'] += 1
                            b_stats['A->B_err'] += 1
                        else:
                            b_stats['B->A'] += 1
                            b_stats['B->A_err'] += 1
                        b_stats['Total'] += 1
                        b_stats['Total_err'] += 1

                        if stop_flag:
                            self.running = False
                            break
                    else:
                        inline_log.append(sent_hex)
                        if direction == 0:
                            b_stats['A->B'] += 1
                        else:
                            b_stats['B->A'] += 1
                        b_stats['Total'] += 1

                if inline_log and stop_flag == 0:
                    self.log_msg(" ".join(inline_log), inline=True)

            except Exception as e:
                self.errors += 1
                stop_flag = self.stop_on_error.get()
                self.log_msg(self._t("exception", index=index, e=e), stop=stop_flag)
                if stop_flag:
                    self.running = False
                    break

            index += block_size

            # Zmena smeru
            if index >= next_dir and self.max_swap_dir.get() > 0 and self.min_swap_dir.get() > 0:
                direction = 1 - direction
                self._direction_label = "A→B" if direction == 0 else "B→A"
                self.log_msg(self._t("direction_changed", dir=self._direction_label))
                next_dir = index + random.randint(max(1, self.min_swap_dir.get()), max(self.max_swap_dir.get(), self.min_swap_dir.get()))
                if next_dir == index: 
                    next_dir = index + 1

            # Zmena baudrate
            if index >= next_baud and self.max_swap_baud.get() > 0 and self.min_swap_baud.get() > 0:
                new_bauds = [b for b in baud_list if b != current_baud and b != last_baud] or [b for b in baud_list if b != current_baud]
                if new_bauds:
                    new_baud = random.choice(new_bauds)
                    last_baud = current_baud
                    current_baud = new_baud
                    self._Char_time = Char_time(current_baud)
                    a_port.baudrate = b_port.baudrate = current_baud
                    self.log_msg(self._t("baud_changed", baud=current_baud))
                    time.sleep(self.baud_delay.get() / 1000)
                    self._current_baud = current_baud

                next_baud = index + random.randint(max(1, self.min_swap_baud.get()), max(self.max_swap_baud.get(), self.min_swap_baud.get()))
                if next_baud == index: 
                    next_baud = index + 1


        try:
            a_port.close()
            b_port.close()
        except Exception:
            pass

        # Zhrnutie štatistík
        total_a2b = sum(stats[b]['A->B'] for b in baud_list)
        total_b2a = sum(stats[b]['B->A'] for b in baud_list)
        total_all = sum(stats[b]['Total'] for b in baud_list)
        err_a2b = sum(stats[b]['A->B_err'] for b in baud_list)
        err_b2a = sum(stats[b]['B->A_err'] for b in baud_list)
        err_all = sum(stats[b]['Total_err'] for b in baud_list)

        self.log_msg(self._t("summary_header"))
        self.log_msg(self._t("summary_line", label="A->B", bytes=total_a2b, bad=err_a2b))
        self.log_msg(self._t("summary_line", label="B->A", bytes=total_b2a, bad=err_b2a))
        self.log_msg(self._t("summary_line", label="Total", bytes=total_all, bad=err_all))

        self.running = False



    
    def stop_test(self):
        self.running=False

if __name__=="__main__":
    app=SerialStressTester()
    app.mainloop()
