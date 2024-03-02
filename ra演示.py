# -*- coding: UTF-8 -*-    
import tkinter as tk
from tkinter import ttk, Text
from itertools import cycle
import pyautogui
import openai
from pynput import keyboard
from concurrent.futures import ThreadPoolExecutor



openai.api_key = "your-api-key-here"
openai.proxy = "your-proxy-here"

# Function to retrieve system prompts in cyclic manner
def get_system_prompts(option):
    prompts = [
        "接下来你要扮演",
        "你是",
        "你要扮演:",
        "你喜欢阅读、写作、旅行、摄影",
        "扮演....",
    ]
    return cycle(prompts[:int(option)])


# Fetch the response from GPT model
def fetch_response(content, system_prompt, text_box):
    print("Sending content to OpenAI: " + content)
    print("System prompt: " + system_prompt)

    completion = openai.ChatCompletion.create(
        # model="gpt-3.5-turbo",
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ]
    )

    response = completion.choices[0].message['content']
    print("Response from OpenAI: " + response)

    text_box.delete('1.0', 'end')
    text_box.insert('end', response)

# Function to copy to clipboard
def copy_to_clipboard(text):
    root.clipboard_clear()
    root.clipboard_append(text)

# Create the text boxes and buttons
def create_text_and_button(parent, system_prompt):
    text_box = Text(parent, height=5)
    text_box.pack(fill='x', expand=True)
    
    copy_button = ttk.Button(parent, 
                             text="复制", 
                             command=lambda: copy_to_clipboard(text_box.get("1.0", 'end-1c')))
    copy_button.pack()

    return text_box

def selection_changed(frame):
    for widget in frame.winfo_children():
        widget.destroy()
        
    prompts = get_system_prompts(selected_option.get())
    
    for _ in range(int(selected_option.get())):
        text_box = create_text_and_button(frame, next(prompts))

# Fetch and update each text box
def fetch_and_update(text_box, system_prompt):
    content = root.clipboard_get()
    print("Content from clipboard: ", content)
    
    executor.submit(fetch_response, content, system_prompt, text_box)
        
# When F2 is pressed
def on_press(key):
    print("Pressed: ", str(key))
    if key == keyboard.Key.f2:
        pyautogui.hotkey('ctrl', 'c')
        
        prompts_cycle = get_system_prompts(selected_option.get())
        
        for i, child in enumerate(entry_frame.winfo_children()):
            if isinstance(child, tk.Text):
                fetch_and_update(child, next(prompts_cycle))


root = tk.Tk()
root.geometry('500x800')
root.title("Chat Assistant")

ttk.Label(root, text="请选择数量:").pack()

options_frame = ttk.Frame(root)
options_frame.pack()

selected_option = tk.StringVar()
for i in range(5):
    ttk.Radiobutton(options_frame, 
                    text=str(i+1), 
                    value=str(i+1), 
                    variable=selected_option, 
                    command=lambda: selection_changed(entry_frame)).pack(side="left")

entry_frame = ttk.Frame(root)
entry_frame.pack(fill='both', expand=True)

executor = ThreadPoolExecutor(max_workers=5)
listener = keyboard.Listener(on_press=on_press)
listener.start()

root.mainloop()
