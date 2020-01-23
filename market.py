import tkinter as tk
from tkinter import ttk
import sqlite3
import shop

class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.init_main()
        self.view_records()

    def init_main(self):
        toolbar = tk.Frame(bg='#d7d8e0', bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        toolbar_2 = tk.Frame(bg='#d7d8e0', bd=2)
        toolbar_2.pack(side=tk.LEFT, fill=tk.Y)

        self.add_img = tk.PhotoImage(file="icon//add.gif")
        btn_open_dialog = tk.Button(toolbar, text='Добавить позицию', command=self.open_dialog, bg='#d7d8e0', bd=0,
                                    compound=tk.TOP, image=self.add_img)
        btn_open_dialog.pack(side=tk.LEFT)

        btn_open_dialog_2 = tk.Button(toolbar_2, text='Добавить позицию', command=self.open_dialog, bg='#d7d8e0', bd=0,
                                    compound=tk.LEFT, image=self.add_img)
        btn_open_dialog_2.pack(side=tk.LEFT)


        self.tree = ttk.Treeview(self, columns=('id', 'title', 'category_id', 'price', 'create_at', 'delFlg', 'saleFlg'),
                                 height=15, show='headings')
        self.tree.column("id", width=0, anchor=tk.CENTER)
        self.tree.column("title", width=365, anchor=tk.CENTER)
        self.tree.column("category_id", width=150, anchor=tk.CENTER)
        self.tree.column("price", width=100, anchor=tk.CENTER)
        self.tree.column("create_at", width=365, anchor=tk.CENTER)
        self.tree.column("delFlg", width=150, anchor=tk.CENTER)
        self.tree.column("saleFlg", width=100, anchor=tk.CENTER)

        self.tree.heading("id", text='ID')
        self.tree.heading("title", text='Наименование')
        self.tree.heading("category_id", text='Категория')
        self.tree.heading("price", text='Цена')
        self.tree.heading("create_at", text='Время добавления')
        self.tree.heading("delFlg", text='Удален')
        self.tree.heading("saleFlg", text='Продан')
 
        self.tree.pack()

    def open_dialog(self):
        Child()

    def view_records(self):
        product_market.c.execute('''SELECT * FROM Goods''')
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in product_market.c.fetchall()]


class Child(tk.Toplevel):
    def __init__(self):
        super().__init__(root)
        self.init_child()

    def init_child(self):
        self.title('Добавить доходы/расходы')
        self.geometry('400x220+400+300')
        self.resizable(False, False)

        label_description = tk.Label(self, text='Наименование:')
        label_description.place(x=50, y=50)
        label_select = tk.Label(self, text='Статья дохода/расхода:')
        label_select.place(x=50, y=80)
        label_sum = tk.Label(self, text='Сумма:')
        label_sum.place(x=50, y=110)

        self.entry_description = ttk.Entry(self)
        self.entry_description.place(x=200, y=50)

        self.entry_money = ttk.Entry(self)
        self.entry_money.place(x=200, y=110)

        self.combobox = ttk.Combobox(self, values=[u"Доход", u"Расход"])
        self.combobox.current(0)
        self.combobox.place(x=200, y=80)

        btn_cancel = ttk.Button(self, text='Закрыть', command=self.destroy)
        btn_cancel.place(x=300, y=170)

        btn_ok = ttk.Button(self, text='Добавить')
        btn_ok.place(x=220, y=170)
        btn_ok.bind('<Button-1>')

if __name__ == "__main__":
    product_market = shop.Shop_db('db.sqlite3')
    product_market.db_init()
    product_market.get_csv()
    root = tk.Tk()
    app = Main(root)
    app.pack()
    root.title("Shop")
    root.geometry("1450x600+300+200")
    root.resizable(False, False)
    root.mainloop()
# product_market = shop.Shop_db('db.sqlite3')

# product_market.db_init()

# product_market.get_csv()

