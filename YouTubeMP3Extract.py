import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import yt_dlp
import os
import re
import threading

class mediaExtract:
    def __init__(self, root):
        self.root = root
        self.root.title("可可牌YouTube media轉換器")

        self.root.minsize(500, 150)
        self.root.maxsize(500, 150)

        self.frame = tk.Frame(root)
        self.frame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

        tk.Label(self.frame, text="YouTube URL:").grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        self.url_entry = tk.Entry(self.frame, width=50)
        self.url_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        # tk.Label(frame, text="選擇格式:").grid(row=1, column=0, padx=5, pady=5, sticky='ew')
        self.format_var = tk.StringVar(value='mp3')
        # format_menu = ttk.OptionMenu(frame, format_var, 'mp3', 'mp3', 'mp4')
        # format_menu.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        self.download_button = tk.Button(root, text="下載", command=self.on_download)
        self.download_button.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky='ew')

        # result_label = tk.Label(app, text="")
        # result_label.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky='ew')

        self.progress_bar = ttk.Progressbar(root, orient='horizontal', mode='determinate', maximum=100)
        self.progress_bar.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

    def download_youtube_video(self, url, download_path, progress_callback):
        try:
            ydl_opts = {
                'format': 'bestaudio/best', # 取得高品質的音訊檔案
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'), # 設定輸出檔案的名稱和路徑。插入影片的標題（從影片的元數據提取）、插入檔案的副檔名（擴展名），例如 mp4, webm, m4a 等。
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio', # 從影片中提取音訊，並將其轉換為 MP3 格式
                    'preferredcodec': 'mp3',
                    'preferredquality': '192', # 音訊品質
                }],
                'ffmpeg_location': 'C:/ffmpeg/ffmpeg-7.0.2-full_build/bin', # 讓 yt-dlp 能調用 ffmpeg 處理音訊
                'postprocessor_args': [
                    '-vn', # 強制去除視訊軌
                    '-acodec', 'libmp3lame',
                    '-ab', '192k',
                ],
                'progress_hooks': [progress_callback]  # 設置進度回調
            }
            # with 語句確保在操作結束後，自動釋放內部資源，下載過程中發生錯誤或中斷，也能正確地清理環境，避免資源洩露
            with yt_dlp.YoutubeDL(ydl_opts) as ydl: # ydl_opts 是一個字典，定義了 yt-dlp 的參數配置
                info_dict = ydl.extract_info(url, download=True) # 用於解析並下載指定的 YouTube 影片
                video_file = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            return video_file
        except Exception as e:
            messagebox.showerror("下載錯誤", f"下載過程中發生錯誤：{str(e)}")
            return None

    def validate_url(self, url):
        # 檢查 URL 是否正確
        regex = re.compile(r'(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+')

        if not regex.match(url):
            return False

        return True

    def on_download(self):
        url = self.url_entry.get().strip()
        file_format = self.format_var.get()

        if not url:
            messagebox.showerror("輸入錯誤", "請輸入 YouTube 影片的 URL")
            return
        if not self.validate_url(url):
            messagebox.showerror("輸入錯誤", "無效的 YouTube 影片 URL")
            return

        if 'list=' in url:
            import re
            url = re.sub(r'&list=[^&]*', '', url)

        download_path = filedialog.askdirectory(title="選擇下載位置")
        if not download_path:
            return

        if file_format not in ['mp3', 'mp4']:
            messagebox.showerror("通知", "格式錯誤，請檢察下載格式 !")

        # 重置進度條
        self.progress_bar['value'] = 0
        self.root.update_idletasks()

        # 禁用輸入框和按鈕，防呆機制
        self.url_entry.config(state='disabled')
        self.download_button.config(state='disabled')

        def download_thread():
            # 定義進度回調函數
            def progress_callback(d):
                if d['status'] == 'downloading':
                    percent = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100  # 計算當前下載進度的百分比
                    self.progress_bar['value'] = percent  # 更新進度條的值
                    self.root.update_idletasks()

            try:
                video_file = self.download_youtube_video(url, download_path, progress_callback)
                if video_file:
                    messagebox.showwarning(title="通知", message=f"下載成功 ! \n請至{video_file}，查看")
                    self.url_entry.delete(0, tk.END)  # 清空 URL 輸入框
                    # result_label.config(text=f"音檔保存至: {video_file}")
                else:
                    # result_label.config(test="下載失敗")
                    messagebox.showerror(title="通知", message="下載失敗 ! 請重新嘗試並確認網路狀態")
            except Exception as e:
                messagebox.showerror("下載錯誤", f"下載過程中發生錯誤：{str(e)}")
            finally: # 不論下載成功、失敗，還是發生例外，最終都會執行 finally 區塊中的程式碼。
                # 重新啟用輸入框和按鈕
                self.url_entry.config(state='normal')
                self.download_button.config(state='normal')

                self.url_entry.delete(0, tk.END)  # 清空 URL 輸入框

        # 啟動下載的線程
        threading.Thread(target=download_thread).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = mediaExtract(root)
    root.mainloop()
