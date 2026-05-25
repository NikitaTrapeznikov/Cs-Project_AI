import customtkinter as ctk
import threading
from body import ask_custom_question, fetch_relevant_news_via_google
from body.auth import login_user, register_user, login_user


class App(ctk.CTk):
    """Главное окно приложения (открывается после успешного входа)"""

    def __init__(self):
        super().__init__()
        self.title("CS2 AI Assistant")
        self.geometry("900x700")
        ctk.set_appearance_mode("dark")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Верхняя панель (Главные новости CS2) ---
        self.news_button = ctk.CTkButton(self, text="Загрузить главные новости CS2", command=self.start_news_thread)
        self.news_button.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        # --- Центр (Вывод текста) ---
        self.textbox = ctk.CTkTextbox(self, font=("Arial", 14))
        self.textbox.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # --- Нижняя панель (Чат) ---
        self.chat_frame = ctk.CTkFrame(self)
        self.chat_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        self.chat_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(self.chat_frame,
                                  placeholder_text="Спроси про cs (например: Что нового у Spirit?)...")
        self.entry.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ew")
        self.entry.bind("<Return>", lambda event: self.start_chat_thread())

        self.ask_button = ctk.CTkButton(self.chat_frame, text="Спросить", width=100, command=self.start_chat_thread)
        self.ask_button.grid(row=0, column=1, pady=10)

    def start_news_thread(self):
        self.news_button.configure(state="disabled", text="Запрашиваю сводку")
        threading.Thread(target=self.run_news_logic).start()

    def run_news_logic(self):
        # Вместо упавшего RSS ищем в индексе Google главные актуальные страницы по запросу 'cs2'
        report = fetch_relevant_news_via_google("cs2")

        # Добавляем красивый заголовок в интерфейс
        formatted_report = f"🔥 АКТУАЛЬНЫЙ ТОП-5 НОВОСТЕЙ С HLTV.ORG:\n\n{report}"
        self.update_ui(formatted_report, self.news_button, "Обновить главные новости CS2")

    def start_chat_thread(self):
        query = self.entry.get()
        if not query: return
        self.ask_button.configure(state="disabled", text="Думаю...")
        threading.Thread(target=self.run_chat_logic, args=(query,)).start()

    def run_chat_logic(self, query):
        answer = ask_custom_question(query)
        self.entry.delete(0, 'end')
        self.update_ui(f"ВЫ: {query}\n\nОТВЕТ AI:\n{answer}", self.ask_button, "Спросить")

    def update_ui(self, text, button, original_text):
        self.textbox.delete("0.0", "end")
        self.textbox.insert("0.0", text)
        button.configure(state="normal", text=original_text)


class LoginWindow(ctk.CTk):
    """Стартовое окно авторизации через Supabase"""

    def __init__(self):
        super().__init__()
        self.title("Вход в систему")
        self.geometry("400x390")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")

        self.label = ctk.CTkLabel(self, text="Вход через Supabase", font=("Arial", 18, "bold"))
        self.label.pack(pady=20)

        self.email_entry = ctk.CTkEntry(self, placeholder_text="Email", width=250)
        self.email_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Пароль", show="*", width=250)
        self.password_entry.pack(pady=10)

        self.login_button = ctk.CTkButton(self, text="Войти", width=250, command=self.try_login)
        self.login_button.pack(pady=10)

        self.register_button = ctk.CTkButton(self, text="Зарегистрироваться", width=250,
                                             fg_color="transparent", border_width=1,
                                             command=self.try_register)
        self.register_button.pack(pady=5)

        self.status_label = ctk.CTkLabel(self, text="", text_color="red")
        self.status_label.pack(pady=10)

    def try_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        result = login_user(email, password)
        if result["success"]:
            self.destroy()
            app = App()
            app.mainloop()
        else:
            self.status_label.configure(text_color="red", text="Неверная почта или пароль!")

    def try_register(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        result = register_user(email, password)
        if result["success"]:
            self.status_label.configure(text_color="green", text="Аккаунт создан! Теперь нажмите 'Войти'")
        else:
            self.status_label.configure(text_color="red", text="Ошибка при регистрации")


if __name__ == "__main__":
    login_window = LoginWindow()
    login_window.mainloop()