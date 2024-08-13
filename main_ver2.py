import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import pyautogui
import pyperclip
import random
import json
import os

class CopyPasteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Copy Paste App - ver.2.0")
        self.root.attributes('-topmost', True)

        self.config_file = "config.json"
        self.words = self.load_words()
        self.load_config()

        self.label_interval = ttk.Label(root, text="貼り付ける秒数間隔:")
        self.label_interval.grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.interval_var = tk.StringVar(value=self.config.get('interval', '1'))
        self.combo_interval = ttk.Combobox(root, textvariable=self.interval_var, values=[str(i) for i in range(1, 31)], width=3)
        self.combo_interval.grid(row=1, column=1, padx=10, pady=10, sticky='w')
        self.combo_interval.current(0)

        self.custom_button = ttk.Button(root, text="カスタム (C)", command=self.toggle_custom)
        self.custom_button.grid(row=1, column=2, padx=10, pady=10, sticky='w')

        self.start_button = ttk.Button(root, text="開始 (O)", command=self.start)
        self.start_button.grid(row=2, column=0, padx=10, pady=10, sticky='w')

        self.stop_button = ttk.Button(root, text="停止 (T)", command=self.stop)
        self.stop_button.grid(row=2, column=1, padx=10, pady=10, sticky='w')
        self.stop_button.config(state=tk.DISABLED)

        self.word_button = ttk.Button(root, text="単語 (L)", command=self.open_word_window)
        self.word_button.grid(row=3, column=0, padx=10, pady=10, sticky='w')

        self.settings_button = ttk.Button(root, text="設定 (S)", command=self.open_settings_window)
        self.settings_button.grid(row=3, column=1, padx=10, pady=10, sticky='w')

        # 終了ボタンの追加
        self.exit_button = ttk.Button(root, text="終了 (E)", command=self.on_closing)
        self.exit_button.grid(row=3, column=2, padx=10, pady=10, sticky='e')

        self.frame = ttk.Frame(root)
        self.frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky='w')

        self.countdown_label = ttk.Label(self.frame, text="")
        self.countdown_label.grid(row=1, column=0, padx=10, pady=10, sticky='w')

        self.next_word_label = ttk.Label(self.frame, text="")
        self.next_word_label.grid(row=2, column=0, padx=10, pady=10, sticky='w')

        self.paste_count_label = ttk.Label(self.frame, text="")
        self.paste_count_label.grid(row=3, column=0, padx=10, pady=10, sticky='w')

        self.running = False
        self.custom_mode = False
        self.paste_count = 0

        self.always_on_top = tk.BooleanVar(value=self.config.get('always_on_top', True))
        self.clear_words_on_exit = tk.BooleanVar(value=self.config.get('clear_words_on_exit', False))
        self.show_messages = tk.BooleanVar(value=self.config.get('show_messages', True))
        self.allow_empty_words = tk.BooleanVar(value=self.config.get('allow_empty_words', False))
        self.enter_after_paste = tk.BooleanVar(value=self.config.get('enter_after_paste', False))
        self.enter_interval = tk.IntVar(value=self.config.get('enter_interval', 1))

        self.root.bind('<o>', lambda event: self.start())
        self.root.bind('<t>', lambda event: self.stop())
        self.root.bind('<c>', lambda event: self.toggle_custom())
        self.root.bind('<l>', lambda event: self.open_word_window())
        self.root.bind('<s>', lambda event: self.open_settings_window())
        self.root.bind('<b>', lambda event: self.close_word_window())
        self.root.bind('<e>', lambda event: self.on_closing())  # 終了ショートカットキーのバインド

    def load_words(self):
        if os.path.exists("words.json"):
            with open("words.json", "r", encoding="utf-8") as file:
                return json.load(file)
        return []

    def save_words(self):
        with open("words.json", "w", encoding="utf-8") as file:
            json.dump(self.words, file, ensure_ascii=False, indent=4)

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as file:
                self.config = json.load(file)
        else:
            self.config = {}

    def save_config(self):
        self.config['interval'] = self.interval_var.get()
        self.config['always_on_top'] = self.always_on_top.get()
        self.config['clear_words_on_exit'] = self.clear_words_on_exit.get()
        self.config['show_messages'] = self.show_messages.get()
        self.config['allow_empty_words'] = self.allow_empty_words.get()
        self.config['enter_after_paste'] = self.enter_after_paste.get()
        self.config['enter_interval'] = self.enter_interval.get()
        with open(self.config_file, "w", encoding="utf-8") as file:
            json.dump(self.config, file, ensure_ascii=False, indent=4)

    def open_word_window(self):
        self.word_window = tk.Toplevel(self.root)
        self.word_window.title("単語設定")
        self.root.withdraw()

        self.word_window.protocol("WM_DELETE_WINDOW", self.close_word_window)

        self.label_new_word = ttk.Label(self.word_window, text="新しい単語:")
        self.label_new_word.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.entry_new_word = ttk.Entry(self.word_window, width=30)
        self.entry_new_word.grid(row=0, column=1, padx=10, pady=10, sticky='w')
        self.entry_new_word.bind("<Return>", lambda event: self.add_word())

        self.add_button = ttk.Button(self.word_window, text="追加", command=self.add_word)
        self.add_button.grid(row=1, column=0, padx=10, pady=10, sticky='w')

        self.listbox_words = tk.Listbox(self.word_window, width=50, height=10)
        self.listbox_words.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='w')
        self.scrollbar = ttk.Scrollbar(self.word_window, orient="vertical", command=self.listbox_words.yview)
        self.scrollbar.grid(row=2, column=2, sticky='nsw')  # スクロールバー位置の調整
        self.listbox_words.config(yscrollcommand=self.scrollbar.set)
        self.update_word_list()

        self.delete_button = ttk.Button(self.word_window, text="削除", command=self.delete_word)
        self.delete_button.grid(row=3, column=0, padx=10, pady=10, sticky='w')

        self.delete_all_button = ttk.Button(self.word_window, text="全削除", command=self.delete_all_words)
        self.delete_all_button.grid(row=3, column=1, padx=10, pady=10, sticky='w')

        self.back_button = ttk.Button(self.word_window, text="戻る (B)", command=self.close_word_window)
        self.back_button.grid(row=3, column=2, padx=10, pady=10, sticky='e')

        self.entry_new_word.bind("<FocusIn>", lambda event: self.disable_back_shortcut())
        self.entry_new_word.bind("<FocusOut>", lambda event: self.enable_back_shortcut())
        self.word_window.bind('<b>', lambda event: self.close_word_window())  # ショートカットキーの修正

    def close_word_window(self):
        self.root.deiconify()
        self.word_window.destroy()

    def disable_back_shortcut(self):
        self.word_window.unbind('<b>')

    def enable_back_shortcut(self):
        self.word_window.bind('<b>', lambda event: self.close_word_window())

    def add_word(self):
        new_word = self.entry_new_word.get()
        if new_word:
            self.words.insert(0, new_word)
            self.entry_new_word.delete(0, tk.END)
            self.update_word_list()
            self.save_words()

    def delete_word(self):
        selected_word_index = self.listbox_words.curselection()
        if selected_word_index:
            self.words.pop(selected_word_index[0])
            self.update_word_list()
            self.save_words()

    def delete_all_words(self):
        if messagebox.askyesno("確認", "本当に全ての単語を削除しますか？"):
            self.words.clear()
            self.update_word_list()
            self.save_words()

    def update_word_list(self):
        self.listbox_words.delete(0, tk.END)
        for word in self.words:
            self.listbox_words.insert(tk.END, word)

    def toggle_custom(self):
        if self.custom_mode:
            self.custom_mode = False
            self.custom_button.config(text="カスタム (C)")
            self.combo_interval.grid(row=1, column=1, padx=10, pady=10, sticky='w')
            self.entry_custom_interval.grid_forget()
        else:
            self.custom_mode = True
            self.custom_button.config(text="ノーマル (C)")
            self.combo_interval.grid_forget()
            self.entry_custom_interval = ttk.Entry(self.root, textvariable=self.interval_var, width=5)
            self.entry_custom_interval.grid(row=1, column=1, padx=10, pady=10, sticky='w')

    def open_settings_window(self):
        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("設定")
        self.root.withdraw()

        self.settings_window.protocol("WM_DELETE_WINDOW", self.close_settings_window)

        self.topmost_check = ttk.Checkbutton(self.settings_window, text="常にこのAppウィンドウを最前面に配置する", variable=self.always_on_top, command=self.toggle_always_on_top)
        self.topmost_check.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        self.clear_words_check = ttk.Checkbutton(self.settings_window, text="Appを終了するとき単語を全削除する", variable=self.clear_words_on_exit)
        self.clear_words_check.grid(row=1, column=0, padx=10, pady=10, sticky='w')

        self.show_messages_check = ttk.Checkbutton(self.settings_window, text="動作メッセージを表示する", variable=self.show_messages, command=self.toggle_message_display)
        self.show_messages_check.grid(row=2, column=0, padx=10, pady=10, sticky='w')

        self.allow_empty_words_check = ttk.Checkbutton(self.settings_window, text="単語が未設定でも動作を行う", variable=self.allow_empty_words)
        self.allow_empty_words_check.grid(row=3, column=0, padx=10, pady=10, sticky='w')

        self.enter_after_paste_check = ttk.Checkbutton(self.settings_window, text="単語貼り付け後にEnterを実行する", variable=self.enter_after_paste, command=self.toggle_enter_interval)
        self.enter_after_paste_check.grid(row=4, column=0, padx=10, pady=10, sticky='w')

        self.enter_interval_combo = ttk.Combobox(self.settings_window, textvariable=self.enter_interval, values=[str(i) for i in range(1, 101)], width=3)
        self.enter_interval_combo.grid(row=4, column=1, padx=5, pady=10, sticky='w')  # 間隔を詰める
        self.enter_interval_label = ttk.Label(self.settings_window, text="回貼り付け毎にEnter")
        self.enter_interval_label.grid(row=4, column=2, padx=5, pady=10, sticky='w')  # 間隔を詰める

        self.settings_back_button = ttk.Button(self.settings_window, text="戻る (B)", command=self.close_settings_window)
        self.settings_back_button.grid(row=5, column=0, padx=10, pady=10, sticky='w')

        # 終了ボタンの位置変更
        self.exit_button = ttk.Button(self.settings_window, text="終了 (E)", command=self.on_closing)
        self.exit_button.grid(row=5, column=1, padx=10, pady=10, sticky='e')

        self.settings_window.bind('<b>', lambda event: self.close_settings_window())  # ショートカットキーの修正

        # Enterの設定に応じてプルダウンを有効/無効にする
        self.toggle_enter_interval()

    def toggle_enter_interval(self):
        if self.enter_after_paste.get():
            self.enter_interval_combo.config(state='normal')
        else:
            self.enter_interval_combo.config(state='disabled')

    def toggle_message_display(self):
        if self.show_messages.get():
            self.countdown_label.grid()
            self.next_word_label.grid()
            self.paste_count_label.grid()
        else:
            self.countdown_label.grid_remove()
            self.next_word_label.grid_remove()
            self.paste_count_label.grid_remove()

    def close_settings_window(self):
        self.save_config()  # 設定を保存
        self.root.deiconify()
        self.settings_window.destroy()

    def toggle_always_on_top(self):
        # 全ウィンドウを常に最前面に配置するかどうか
        self.root.attributes('-topmost', self.always_on_top.get())
        if hasattr(self, 'word_window'):
            self.word_window.attributes('-topmost', self.always_on_top.get())
        if hasattr(self, 'settings_window'):
            self.settings_window.attributes('-topmost', self.always_on_top.get())

    def start(self):
        if not self.allow_empty_words.get() and not self.words:
            messagebox.showwarning("警告", "単語を設定してください")
            return

        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.custom_button.config(state=tk.DISABLED)
        self.word_button.config(state=tk.DISABLED)
        self.settings_button.config(state=tk.DISABLED)
        self.paste_count = 0
        self.run()

    def stop(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.custom_button.config(state=tk.NORMAL)
        self.word_button.config(state=tk.NORMAL)
        self.settings_button.config(state=tk.NORMAL)
        self.reset_messages()

    def reset_messages(self):
        self.countdown_label.config(text="")
        self.next_word_label.config(text="")
        self.paste_count_label.config(text="")

    def run(self):
        if not self.running:
            return

        interval = int(self.interval_var.get())

        if self.show_messages.get():
            self.countdown_label.config(text=f"{interval}秒後に次の単語を貼り付けます...")

        if self.words:
            next_word = random.choice(self.words)
            self.next_word_label.config(text=f"次の単語: {next_word}")
        else:
            next_word = ""

        def countdown():
            for i in range(interval, 0, -1):
                if self.show_messages.get():
                    self.countdown_label.config(text=f"{i}秒後に次の単語を貼り付けます...")
                time.sleep(1)
                if not self.running:
                    return

            self.paste(next_word)

        threading.Thread(target=countdown).start()

    def paste(self, word):
        if word:
            pyperclip.copy(word)
            pyautogui.hotkey("ctrl", "v")
        self.paste_count += 1
        if self.show_messages.get():
            self.paste_count_label.config(text=f"貼り付けた回数: {self.paste_count}")

        if self.enter_after_paste.get() and self.paste_count % self.enter_interval.get() == 0:
            pyautogui.press("enter")

        if self.running:
            self.run()

    def on_closing(self):
        if self.clear_words_on_exit.get():
            self.words.clear()
            self.save_words()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CopyPasteApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
