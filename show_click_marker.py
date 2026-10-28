import win32gui
import tkinter as tk
import threading

def show_click_marker(hwnd, x, y):
    # 대상 창의 클라이언트 좌표를 화면 좌표로 변환
    screen_x, screen_y = win32gui.ClientToScreen(hwnd, (x, y))

    def show():
        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-transparentcolor", "black")

        size = 60
        root.geometry(
            f"{size}x{size}+{screen_x - size // 2}+{screen_y - size // 2}"
        )

        canvas = tk.Canvas(
            root,
            width=size,
            height=size,
            bg="black",
            highlightthickness=0
        )
        canvas.pack()

        canvas.create_oval(
            5, 5, 55, 55,
            outline="red",
            width=4
        )

        canvas.create_line(30, 15, 30, 45, fill="red", width=2)
        canvas.create_line(15, 30, 45, 30, fill="red", width=2)

        root.after(1500, root.destroy)
        root.mainloop()

    threading.Thread(target=show, daemon=True).start()