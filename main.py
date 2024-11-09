import json
import pandas as pd
from googleapiclient.discovery import build
import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Ваш API ключ
API_KEY = 'тут апи из гугла'

# Создаем объект для работы с YouTube API без использования кэширования
youtube = build('youtube', 'v3', developerKey=API_KEY, cache_discovery=False)

def search_videos(query, max_results=10, min_likes=0, channel_id=None):
    try:
        search_request = youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            maxResults=max_results,
            channelId=channel_id
        )
        search_response = search_request.execute()
        
        video_ids = [item['id']['videoId'] for item in search_response['items']]
        
        video_request = youtube.videos().list(
            part='snippet,statistics',
            id=','.join(video_ids)
        )
        video_response = video_request.execute()
        
        results = []
        for item in video_response['items']:
            video_id = item['id']
            title = item['snippet']['title']
            description = item['snippet']['description']
            channel_title = item['snippet']['channelTitle']
            like_count = int(item['statistics'].get('likeCount', 0))
            dislike_count = int(item['statistics'].get('dislikeCount', 0))
            comment_count = int(item['statistics'].get('commentCount', 0))
            
            if min_likes == 0 or like_count >= min_likes:
                results.append({
                    'Video ID': video_id,
                    'Title': title,
                    'Description': description,
                    'Channel Title': channel_title,
                    'Likes': like_count,
                    'Dislikes': dislike_count,
                    'Comments': comment_count
                })
        
        if not results:
            messagebox.showinfo("No Results", "No videos found with the specified criteria.")
            return
        
        # Save results to a chosen file location
        file_types = [("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("JSON files", "*.json")]
        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=file_types)
        
        if save_path:
            if save_path.endswith('.json'):
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=4)
            elif save_path.endswith('.csv'):
                df = pd.DataFrame(results)
                df.to_csv(save_path, index=False, encoding='utf-8')
            elif save_path.endswith('.xlsx'):
                df = pd.DataFrame(results)
                df.to_excel(save_path, index=False, engine='openpyxl')
            
            logging.info(f"Results saved to '{save_path}'.")
            messagebox.showinfo("Success", f"Results saved to '{save_path}'.")
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

def on_search_click():
    query = query_entry.get()
    max_results = int(max_results_entry.get())
    min_likes = int(min_likes_entry.get())
    channel_id = channel_id_entry.get() if channel_var.get() else None
    search_videos(query, max_results, min_likes, channel_id)

def on_channel_check():
    if channel_var.get():
        channel_id_entry.config(state='normal')
    else:
        channel_id_entry.config(state='disabled')

# Создание GUI
root = tk.Tk()
root.title("YouTube Video Search")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Метки и поля ввода
query_label = ttk.Label(frame, text="Search Query:")
query_label.grid(row=0, column=0, sticky=tk.W)
query_entry = ttk.Entry(frame, width=50)
query_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

max_results_label = ttk.Label(frame, text="Max Results:")
max_results_label.grid(row=1, column=0, sticky=tk.W)
max_results_entry = ttk.Entry(frame, width=10)
max_results_entry.grid(row=1, column=1, sticky=tk.W)

min_likes_label = ttk.Label(frame, text="Min Likes (0 for no limit):")
min_likes_label.grid(row=2, column=0, sticky=tk.W)
min_likes_entry = ttk.Entry(frame, width=10)
min_likes_entry.grid(row=2, column=1, sticky=tk.W)
min_likes_entry.insert(0, "0")

# Поле для ввода имени канала и галочка
channel_var = tk.BooleanVar()
channel_check = ttk.Checkbutton(frame, text="Search by Channel ID", variable=channel_var, command=on_channel_check)
channel_check.grid(row=3, column=0, sticky=tk.W)

channel_id_label = ttk.Label(frame, text="Channel ID:")
channel_id_label.grid(row=4, column=0, sticky=tk.W)
channel_id_entry = ttk.Entry(frame, width=50, state='disabled')
channel_id_entry.grid(row=4, column=1, sticky=(tk.W, tk.E))

# Кнопка поиска
search_button = ttk.Button(frame, text="Search", command=on_search_click)
search_button.grid(row=5, column=0, columnspan=2)

# Настройка заполнения
frame.columnconfigure(1, weight=1)
frame.rowconfigure(5, weight=1)

# Запуск основного цикла
root.mainloop()
