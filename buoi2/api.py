import tkinter as tk
from tkinter import ttk
from openai import OpenAI

class TextTranslatorApp:
    def __init__(self, root):
        self.root = root
        root.title("Text Translator (ChatGPT)")

        # Khởi tạo client OpenAI
        self.client = OpenAI(api_key="...")  # <- thay bằng API key của bạn

        self.create_widgets()

    def create_widgets(self):
        label1 = tk.Label(self.root, text="Enter text to translate:")
        self.entry = tk.Entry(self.root, width=50)

        label2 = tk.Label(self.root, text="Choose source language:")
        self.source_lang = ttk.Combobox(self.root, values=['en', 'es', 'vi', 'ja', 'zh'])
        self.source_lang.set('en')

        label3 = tk.Label(self.root, text="Choose target language:")
        self.target_lang = ttk.Combobox(self.root, values=['en', 'es', 'vi', 'ja', 'zh'])
        self.target_lang.set('vi')

        translate_button = tk.Button(self.root, text="Translate", command=self.translate_text)

        self.result_label = tk.Label(self.root, text="Translated text will appear here.", wraplength=400, justify="left")

        label1.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry.grid(row=0, column=1, padx=10, pady=10)
        label2.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.source_lang.grid(row=1, column=1, padx=10, pady=10)
        label3.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.target_lang.grid(row=2, column=1, padx=10, pady=10)
        translate_button.grid(row=3, column=0, columnspan=2, pady=10)
        self.result_label.grid(row=4, column=0, columnspan=2, pady=10)

    def translate_text(self):
        text_to_translate = self.entry.get()
        source = self.source_lang.get()
        target = self.target_lang.get()

        prompt = f"Translate the following text from {source} to {target}:\n\n{text_to_translate}"

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a translation assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            translated_text = response.choices[0].message.content.strip()
            self.result_label.config(text=translated_text)
        except Exception as e:
            self.result_label.config(text=f"Error: {e}")

if __name__ == '__main__':
    root = tk.Tk()
    app = TextTranslatorApp(root)
    root.mainloop()