import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import os
import re

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Языковой процессор - Текстовый редактор")
        self.root.geometry("1000x700")
        
        self.current_file = None
        self.text_changed = False
        self.tooltip = None
        
        # Привязка события изменения текста
        self.setup_ui()
        self.bind_events()
        
    def bind_events(self):
        self.text_editor.bind('<<Modified>>', self.on_text_modified)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def on_text_modified(self, event=None):
        if self.text_editor.edit_modified():
            self.text_changed = True
            self.text_editor.edit_modified(False)
            
    def on_closing(self):
        if self.text_changed:
            result = messagebox.askyesnocancel("Выход", 
                                              "Сохранить изменения перед выходом?")
            if result is None:  # Отмена
                return
            elif result:  # Да
                self.save_file()
        self.root.destroy()
        
    def setup_ui(self):
        self.create_menu()
        self.create_toolbar()
        
        # Основная панель с возможностью изменения размеров
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.create_editor_area()
        self.create_result_area()
        
        # Строка состояния
        self.create_status_bar()
        
        self.root.minsize(600, 400)
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Создать", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Открыть", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Сохранить", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Сохранить как", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.on_closing, accelerator="Ctrl+Q")
        
        # Меню Правка
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        edit_menu.add_command(label="Отменить", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Повторить", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Вырезать", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Копировать", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Вставить", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_command(label="Удалить", command=self.delete, accelerator="Del")
        edit_menu.add_separator()
        edit_menu.add_command(label="Выделить все", command=self.select_all, accelerator="Ctrl+A")
        
        # Меню Текст (заглушки для будущей реализации)
        text_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Текст", menu=text_menu)
        text_menu.add_command(label="Постановка задачи", 
                            command=lambda: self.show_text_info("Постановка задачи"))
        text_menu.add_command(label="Грамматика", 
                            command=lambda: self.show_text_info("Грамматика"))
        text_menu.add_command(label="Классификация грамматики", 
                            command=lambda: self.show_text_info("Классификация грамматики"))
        text_menu.add_command(label="Метод анализа", 
                            command=lambda: self.show_text_info("Метод анализа"))
        text_menu.add_command(label="Тестовый пример", 
                            command=lambda: self.show_text_info("Тестовый пример"))
        text_menu.add_command(label="Список литературы", 
                            command=lambda: self.show_text_info("Список литературы"))
        text_menu.add_command(label="Исходный код программы", 
                            command=lambda: self.show_text_info("Исходный код программы"))
        
        # Меню Пуск
        menubar.add_command(label="Пуск", command=self.analyze_text)
        
        # Меню Справка
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="Вызов справки", command=self.show_help, accelerator="F1")
        help_menu.add_command(label="О программе", command=self.show_about)
        
        # Горячие клавиши
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-Shift-S>', lambda e: self.save_as_file())
        self.root.bind('<Control-q>', lambda e: self.on_closing())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-x>', lambda e: self.cut())
        self.root.bind('<Control-c>', lambda e: self.copy())
        self.root.bind('<Control-v>', lambda e: self.paste())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.root.bind('<F1>', lambda e: self.show_help())
        
    def create_toolbar(self):
        toolbar = ttk.Frame(self.root, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Кнопки панели инструментов (только иконки)
        buttons = [
            ("📄", self.new_file, "Создать новый файл"),
            ("📂", self.open_file, "Открыть файл"),
            ("💾", self.save_file, "Сохранить файл"),
            (None, None, None),  # Разделитель
            ("↶", self.undo, "Отменить"),
            ("↷", self.redo, "Повторить"),
            (None, None, None),  # Разделитель
            ("📋", self.copy, "Копировать"),
            ("✂", self.cut, "Вырезать"),
            ("📝", self.paste, "Вставить"),
            (None, None, None),  # Разделитель
            ("▶", self.analyze_text, "Запуск анализатора"),
            (None, None, None),  # Разделитель
            ("❓", self.show_help, "Справка"),
            ("ℹ", self.show_about, "О программе")
        ]
        
        for icon, command, tooltip in buttons:
            if icon is None:
                # Разделитель
                ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=2, fill=tk.Y)
            else:
                # Кнопка с иконкой
                btn = ttk.Button(toolbar, text=icon, command=command, width=3)
                btn.pack(side=tk.LEFT, padx=1, pady=2)
                
                # Всплывающая подсказка
                self.create_tooltip(btn, tooltip)
    
    def create_tooltip(self, widget, text):
        """Создание всплывающей подсказки для виджета"""
        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            
            # Создание окна подсказки
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            label = ttk.Label(self.tooltip, text=text, background="#ffffe0", 
                             relief="solid", borderwidth=1, padding=(5, 2))
            label.pack()
            
        def leave(event):
            if hasattr(self, 'tooltip') and self.tooltip:
                self.tooltip.destroy()
                self.tooltip = None
        
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)
    
    def create_editor_area(self):
        editor_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(editor_frame, weight=2)
        
        # Заголовок
        header_frame = ttk.Frame(editor_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(header_frame, text="Редактор:", 
                 font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        # Индикатор изменения
        self.modified_label = ttk.Label(header_frame, text="", foreground="red")
        self.modified_label.pack(side=tk.LEFT, padx=10)
        
        # Область редактирования с подсветкой синтаксиса
        self.text_editor = scrolledtext.ScrolledText(
            editor_frame, 
            wrap=tk.WORD,
            font=("Courier New", 12),
            undo=True,
            maxundo=100,
            autoseparators=True,
            background='white',
            foreground='black',
            insertbackground='black',
            selectbackground='lightblue'
        )
        self.text_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Настройка тегов для подсветки синтаксиса
        self.setup_syntax_highlighting()
        
        # Привязка события для подсветки при вводе
        self.text_editor.bind('<KeyRelease>', self.highlight_syntax)
        
    def setup_syntax_highlighting(self):
        # Определение тегов для подсветки
        self.text_editor.tag_configure("keyword", foreground="blue", font=("Courier New", 12, "bold"))
        self.text_editor.tag_configure("string", foreground="green")
        self.text_editor.tag_configure("comment", foreground="gray")
        self.text_editor.tag_configure("number", foreground="purple")
        
        # Ключевые слова
        self.keywords = [
            'if', 'else', 'while', 'for', 'return', 'break', 'continue',
            'int', 'float', 'char', 'void', 'double', 'string', 'bool',
            'true', 'false', 'null', 'class', 'public', 'private', 'protected',
            'static', 'final', 'abstract', 'interface', 'extends', 'implements',
            'import', 'package', 'try', 'catch', 'finally', 'throw', 'throws',
            'new', 'this', 'super', 'instanceof', 'enum', 'switch', 'case',
            'default', 'do', 'while', 'var', 'const', 'let', 'function'
        ]
        
    def highlight_syntax(self, event=None):
        # Удаление существующих тегов
        for tag in ["keyword", "string", "comment", "number"]:
            self.text_editor.tag_remove(tag, "1.0", tk.END)
        
        # Подсветка ключевых слов
        for keyword in self.keywords:
            start_pos = "1.0"
            while True:
                start_pos = self.text_editor.search(r'\y' + keyword + r'\y', start_pos, tk.END, 
                                                   regexp=True, nocase=False)
                if not start_pos:
                    break
                end_pos = f"{start_pos}+{len(keyword)}c"
                self.text_editor.tag_add("keyword", start_pos, end_pos)
                start_pos = end_pos
        
        # Подсветка комментариев
        for comment_marker in ['#', '//']:
            start_pos = "1.0"
            while True:
                start_pos = self.text_editor.search(comment_marker, start_pos, tk.END)
                if not start_pos:
                    break
                line_end = f"{start_pos} lineend"
                self.text_editor.tag_add("comment", start_pos, line_end)
                start_pos = line_end
        
        # Подсветка строк в кавычках
        start_pos = "1.0"
        while True:
            start_pos = self.text_editor.search('"', start_pos, tk.END)
            if not start_pos:
                break
            end_pos = self.text_editor.search('"', f"{start_pos}+1c", tk.END)
            if end_pos:
                self.text_editor.tag_add("string", start_pos, f"{end_pos}+1c")
                start_pos = f"{end_pos}+1c"
            else:
                break
        
        # Подсветка чисел
        start_pos = "1.0"
        while True:
            start_pos = self.text_editor.search(r'\y\d+\y', start_pos, tk.END, regexp=True)
            if not start_pos:
                break
            self.text_editor.tag_add("number", start_pos, f"{start_pos} wordend")
            start_pos = f"{start_pos}+1c"
    
    def create_result_area(self):
        result_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(result_frame, weight=1)
        
        # Заголовок
        ttk.Label(result_frame, text="Результаты работы языкового процессора:", 
                 font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=5, pady=2)
        
        # Область результатов
        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            wrap=tk.WORD,
            font=("Courier New", 10),
            state='normal',
            height=8,
            background='#f0f0f0'
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Настройка тега для ошибок
        self.result_text.tag_configure("error", foreground="red")
        self.result_text.tag_bind("error", "<Button-1>", self.on_error_click)
        
    def create_status_bar(self):
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Информация о позиции курсора
        self.cursor_pos_label = ttk.Label(self.status_bar, text="Стр: 1  Стлб: 1")
        self.cursor_pos_label.pack(side=tk.LEFT, padx=5)
        
        # Информация о размере файла
        self.file_info_label = ttk.Label(self.status_bar, text="")
        self.file_info_label.pack(side=tk.LEFT, padx=20)
        
        # Индикатор изменений
        self.status_label = ttk.Label(self.status_bar, text="Готов")
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # Обновление позиции курсора
        self.text_editor.bind('<KeyRelease>', self.update_cursor_position)
        self.text_editor.bind('<ButtonRelease-1>', self.update_cursor_position)
        
    def update_cursor_position(self, event=None):
        try:
            cursor_pos = self.text_editor.index(tk.INSERT)
            line, col = cursor_pos.split('.')
            self.cursor_pos_label.config(text=f"Стр: {line}  Стлб: {int(col)+1}")
            
            # Обновление информации о файле
            content = self.text_editor.get("1.0", tk.END)
            lines = content.count('\n')
            chars = len(content) - 1  # минус последний \n
            self.file_info_label.config(text=f"Строк: {lines}  Символов: {chars}")
            
            if self.text_changed:
                self.modified_label.config(text="*")
                self.status_label.config(text="Изменено")
            else:
                self.modified_label.config(text="")
                self.status_label.config(text="Готов")
        except:
            pass
    
    # Команды меню Правка
    def undo(self):
        try:
            self.text_editor.edit_undo()
        except:
            pass
    
    def redo(self):
        try:
            self.text_editor.edit_redo()
        except:
            pass
    
    def copy(self):
        self.text_editor.event_generate("<<Copy>>")
    
    def cut(self):
        self.text_editor.event_generate("<<Cut>>")
    
    def paste(self):
        self.text_editor.event_generate("<<Paste>>")
    
    def delete(self):
        try:
            if self.text_editor.tag_ranges(tk.SEL):
                self.text_editor.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            pass
    
    def select_all(self):
        self.text_editor.tag_add(tk.SEL, "1.0", tk.END)
        self.text_editor.mark_set(tk.INSERT, "1.0")
        self.text_editor.see(tk.INSERT)
        return "break"
    
    # Команды меню Файл
    def new_file(self):
        if self.text_changed:
            result = messagebox.askyesnocancel("Создание файла", 
                                              "Сохранить изменения?")
            if result is None:  # Отмена
                return
            elif result:  # Да
                if not self.save_file():
                    return
        
        self.text_editor.delete("1.0", tk.END)
        self.current_file = None
        self.text_changed = False
        self.root.title("Языковой процессор - Новый файл")
        self.clear_results()
        self.status_label.config(text="Новый файл создан")
        self.update_cursor_position()
    
    def open_file(self):
        if self.text_changed:
            result = messagebox.askyesnocancel("Открытие файла", 
                                              "Сохранить изменения?")
            if result is None:  # Отмена
                return
            elif result:  # Да
                if not self.save_file():
                    return
        
        file_path = filedialog.askopenfilename(
            filetypes=[("Текстовые файлы", "*.txt"), 
                      ("Python файлы", "*.py"),
                      ("Все файлы", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text_editor.delete("1.0", tk.END)
                    self.text_editor.insert("1.0", content)
                
                self.current_file = file_path
                self.text_changed = False
                self.root.title(f"Языковой процессор - {os.path.basename(file_path)}")
                self.status_label.config(text=f"Открыт файл: {os.path.basename(file_path)}")
                self.highlight_syntax()
                self.update_cursor_position()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{str(e)}")
    
    def save_file(self):
        if self.current_file:
            return self._save_to_file(self.current_file)
        else:
            return self.save_as_file()
    
    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), 
                      ("Python файлы", "*.py"),
                      ("Все файлы", "*.*")]
        )
        
        if file_path:
            self.current_file = file_path
            result = self._save_to_file(file_path)
            if result:
                self.root.title(f"Языковой процессор - {os.path.basename(file_path)}")
            return result
        return False
    
    def _save_to_file(self, file_path):
        try:
            content = self.text_editor.get("1.0", tk.END)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            self.text_changed = False
            self.status_label.config(text=f"Файл сохранен: {os.path.basename(file_path)}")
            self.update_cursor_position()
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
            return False
    
    # Функции для меню Текст
    def show_text_info(self, title):
        info_window = tk.Toplevel(self.root)
        info_window.title(title)
        info_window.geometry("600x400")
        info_window.minsize(400, 300)
        
        text_area = scrolledtext.ScrolledText(info_window, wrap=tk.WORD, font=("Arial", 11))
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        info_text = f"Информация по разделу: {title}\n\n"
        info_text += "Этот раздел будет реализован в следующих лабораторных работах.\n\n"
        info_text += "Содержание:\n"
        info_text += "1. Теоретические основы\n"
        info_text += "2. Практическая реализация\n"
        info_text += "3. Примеры использования\n"
        info_text += "4. Дополнительные материалы\n"
        
        if title == "Постановка задачи":
            info_text += "\nЗдесь будет описана постановка задачи для языкового процессора."
        elif title == "Грамматика":
            info_text += "\nЗдесь будет представлена грамматика языка."
        elif title == "Классификация грамматики":
            info_text += "\nЗдесь будет приведена классификация используемой грамматики."
        elif title == "Метод анализа":
            info_text += "\nЗдесь будет описан метод синтаксического анализа."
        elif title == "Тестовый пример":
            info_text += "\nЗдесь будут представлены тестовые примеры."
        elif title == "Список литературы":
            info_text += "\n1. Ахо А., Сети Р., Ульман Д. Компиляторы: принципы, технологии и инструменты.\n"
            info_text += "2. Моженков А.В. Технологии разработки программного обеспечения.\n"
            info_text += "3. Документация Python.\n"
        elif title == "Исходный код программы":
            info_text += "\nИсходный код программы доступен в файле text_editor.py"
        
        text_area.insert("1.0", info_text)
        text_area.config(state='disabled')
        
        ttk.Button(info_window, text="Закрыть", command=info_window.destroy).pack(pady=5)
    
    # Функция анализа текста (Пуск)
    def analyze_text(self):
        text = self.text_editor.get("1.0", tk.END).strip()
        self.clear_results()
        
        if not text:
            self.add_result("Текст отсутствует. Введите текст для анализа.")
            return
        
        self.add_result("=" * 50)
        self.add_result("РЕЗУЛЬТАТЫ АНАЛИЗА ТЕКСТА")
        self.add_result("=" * 50)
        self.add_result(f"Всего символов: {len(text)}")
        self.add_result(f"Всего строк: {text.count(chr(10)) + 1}")
        
        lines = text.split('\n')
        errors_found = False
        
        self.add_result("\n" + "-" * 30)
        self.add_result("ПРОВЕРКА СИНТАКСИСА:")
        self.add_result("-" * 30)
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            # Проверка на точки с запятой
            if '=' in line and ';' not in line and not line.startswith('#'):
                error_msg = f"Ошибка в строке {i}: Отсутствует точка с запятой"
                self.add_result(error_msg, is_error=True, line=i)
                errors_found = True
            
            # Проверка на незакрытые скобки
            if line.count('(') != line.count(')'):
                error_msg = f"Ошибка в строке {i}: Несбалансированные скобки"
                self.add_result(error_msg, is_error=True, line=i)
                errors_found = True
            
            # Проверка ключевых слов
            words = line.split()
            for word in words:
                if word in ['print', 'input', 'len', 'range', 'open']:
                    if '(' not in line:
                        error_msg = f"Предупреждение в строке {i}: Функция '{word}' должна вызываться со скобками"
                        self.add_result(error_msg, is_error=False, line=i)
        
        if not errors_found:
            self.add_result("Синтаксических ошибок не обнаружено.")
        
        self.add_result("\n" + "-" * 30)
        self.add_result("СТАТИСТИКА:")
        self.add_result("-" * 30)
        
        words = text.split()
        self.add_result(f"Количество слов: {len(words)}")
        
        unique_words = len(set(w.lower().strip('.,!?;:()[]{}"\'') for w in words))
        self.add_result(f"Уникальных слов: {unique_words}")
        
        self.add_result("\n" + "=" * 50)
        self.status_label.config(text="Анализ завершен")
        
    def add_result(self, message, is_error=False, line=None):
        self.result_text.config(state='normal')
        
        if is_error:
            start = self.result_text.index(tk.END)
            self.result_text.insert(tk.END, f"{message}\n")
            end = self.result_text.index(tk.END)
            self.result_text.tag_add("error", start, end)
            if line:
                # Сохраняем информацию о строке
                self.result_text.tag_bind("error", "<Button-1>", 
                                        lambda e, l=line: self.go_to_error_line(l))
        else:
            self.result_text.insert(tk.END, f"{message}\n")
        
        self.result_text.config(state='disabled')
        self.result_text.see(tk.END)
    
    def clear_results(self):
        self.result_text.config(state='normal')
        self.result_text.delete("1.0", tk.END)
        self.result_text.config(state='disabled')
    
    def on_error_click(self, event):
        index = self.result_text.index(f"@{event.x},{event.y}")
        line_text = self.result_text.get(index, f"{index} lineend")
        
        match = re.search(r'строке (\d+)', line_text, re.IGNORECASE)
        if match:
            line_num = int(match.group(1))
            self.go_to_error_line(line_num)
    
    def go_to_error_line(self, line_num):
        position = f"{line_num}.0"
        self.text_editor.mark_set(tk.INSERT, position)
        self.text_editor.see(position)
        self.text_editor.focus_set()
        
        self.text_editor.tag_remove("error_line", "1.0", tk.END)
        self.text_editor.tag_add("error_line", f"{line_num}.0", f"{line_num}.0 lineend")
        self.text_editor.tag_config("error_line", background="yellow")
    
    # Команды меню Справка
    def show_help(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("Справка - Руководство пользователя")
        help_window.geometry("700x500")
        help_window.minsize(500, 400)
        
        notebook = ttk.Notebook(help_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка "Общая информация"
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="Общая информация")
        
        general_text = scrolledtext.ScrolledText(general_frame, wrap=tk.WORD, font=("Arial", 10))
        general_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        general_info = """
        ТЕКСТОВЫЙ РЕДАКТОР С ФУНКЦИЯМИ ЯЗЫКОВОГО ПРОЦЕССОРА
        
        Версия: 1.0
        
        Программа представляет собой текстовый редактор с расширенными 
        возможностями для анализа текста и подсветкой синтаксиса.
        
        Основные возможности:
        • Создание, открытие и сохранение текстовых файлов
        • Редактирование текста с поддержкой операций отмены/повтора
        • Подсветка синтаксиса для различных языков программирования
        • Анализ текста с выводом результатов
        • Навигация по ошибкам
        • Настраиваемый интерфейс с изменяемыми областями
        """
        general_text.insert("1.0", general_info)
        general_text.config(state='disabled')
        
        # Вкладка "Меню Файл"
        file_frame = ttk.Frame(notebook)
        notebook.add(file_frame, text="Меню Файл")
        
        file_text = scrolledtext.ScrolledText(file_frame, wrap=tk.WORD, font=("Arial", 10))
        file_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        file_info = """
        МЕНЮ "ФАЙЛ"
        
        Создать (Ctrl+N)
            Создает новый файл. Если текущий файл содержит несохраненные изменения,
            программа предложит сохранить их.
            
        Открыть (Ctrl+O)
            Открывает существующий файл. Поддерживаются форматы .txt и .py.
            
        Сохранить (Ctrl+S)
            Сохраняет изменения в текущем файле. Если файл не был сохранен ранее,
            программа предложит выбрать имя и расположение файла.
            
        Сохранить как (Ctrl+Shift+S)
            Сохраняет текущее содержимое в новый файл, позволяя выбрать имя
            и расположение.
            
        Выход (Ctrl+Q)
            Завершает работу программы. При наличии несохраненных изменений
            программа предложит сохранить их.
        """
        file_text.insert("1.0", file_info)
        file_text.config(state='disabled')
        
        # Вкладка "Меню Правка"
        edit_frame = ttk.Frame(notebook)
        notebook.add(edit_frame, text="Меню Правка")
        
        edit_text = scrolledtext.ScrolledText(edit_frame, wrap=tk.WORD, font=("Arial", 10))
        edit_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        edit_info = """
        МЕНЮ "ПРАВКА"
        
        Отменить (Ctrl+Z)
            Отменяет последнее действие.
            
        Повторить (Ctrl+Y)
            Повторяет отмененное действие.
            
        Вырезать (Ctrl+X)
            Вырезает выделенный текст в буфер обмена.
            
        Копировать (Ctrl+C)
            Копирует выделенный текст в буфер обмена.
            
        Вставить (Ctrl+V)
            Вставляет текст из буфера обмена.
            
        Удалить (Del)
            Удаляет выделенный текст.
            
        Выделить все (Ctrl+A)
            Выделяет весь текст в редакторе.
        """
        edit_text.insert("1.0", edit_info)
        edit_text.config(state='disabled')
        
        # Вкладка "Пуск - Анализ текста"
        analyze_frame = ttk.Frame(notebook)
        notebook.add(analyze_frame, text="Пуск - Анализ текста")
        
        analyze_text_widget = scrolledtext.ScrolledText(analyze_frame, wrap=tk.WORD, font=("Arial", 10))
        analyze_text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        analyze_info = """
        ПУСК - АНАЛИЗ ТЕКСТА
        
        Функция анализа текста (меню "Пуск" или кнопка на панели инструментов)
        выполняет следующие проверки:
        
        1. Синтаксический анализ:
           • Проверка наличия точек с запятой после присваиваний
           • Проверка баланса скобок
           • Проверка корректности вызова функций
           
        2. Статистический анализ:
           • Подсчет количества символов
           • Подсчет количества строк
           • Подсчет количества слов
           • Подсчет уникальных слов
        
        Навигация по ошибкам:
        • Клик на сообщении об ошибке в области результатов автоматически
          перемещает курсор в соответствующую строку в редакторе
        • Ошибочная строка подсвечивается желтым цветом
        """
        analyze_text_widget.insert("1.0", analyze_info)
        analyze_text_widget.config(state='disabled')
        
        ttk.Button(help_window, text="Закрыть", command=help_window.destroy).pack(pady=5)
    
    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("О программе")
        about_window.geometry("400x300")
        about_window.resizable(False, False)
        
        frame = ttk.Frame(about_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Языковой процессор", 
                 font=("Arial", 16, "bold")).pack(pady=10)
        
        ttk.Label(frame, text="Версия 1.0", 
                 font=("Arial", 10)).pack()
        
        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        description = """Текстовый редактор с функциями 
языкового процессора
        
Разработан в рамках лабораторной работы
по дисциплине "Системное программирование"
        
© 2026 Все права защищены"""
        
        ttk.Label(frame, text=description, 
                 font=("Arial", 10), justify=tk.CENTER).pack(pady=10)
        
        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        ttk.Button(frame, text="Закрыть", command=about_window.destroy).pack()

def main():
    root = tk.Tk()
    
    # Установка стиля
    style = ttk.Style()
    style.theme_use('clam')
    
    app = TextEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
