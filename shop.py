import pandas as pd
import numpy as np
import os
import sqlite3
import re
import random
import calendar
from matplotlib import pyplot as plt
from sqlite3 import Error
import csv

def email_check(email):

    pattern = re.compile(r'(^|\s)[-a-z0-9_.]+@([-a-z0-9]+\.)+[a-z]{2,6}(\s|$)')
    if pattern.match(email):
        return True
    else:
        return False

def str_check(string):
    
    if re.search(r'\d+', string) is not None:
        return False
    else:
        return True

def validation(df):
    
    df.dropna(inplace=True)
    df.drop_duplicates(keep='last', inplace=True)
    df.first_name = df.first_name.str.capitalize()
    df.last_name = df.last_name.str.capitalize()
    df = df[df.email.apply(email_check) & df.last_name.apply(str_check) & df.first_name.apply(str_check)]
    
    return df

class Shop_db():

    """ 
    Store Database Class 
    Takes a database path
    """
    def __init__(self, db):
        self.db = db
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()

    def db_init(self):

        """
        Database initialization function creates tables, triggers, vievs and other SQL object

        """
        with self.conn:
            try:
                sql_script = """CREATE TABLE IF NOT EXISTS Customers (
                                                                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                                                        first_name TEXT NOT NULL,
                                                                        last_name TEXT NOT NULL,
                                                                        gender TEXT NOT NULL,
                                                                        delFlg INTEGER NOT NULL DEFAULT 0,
                                                                        UNIQUE(last_name,first_name)
                                                                    );
                                                                    """
                self.conn.execute(sql_script)

                sql_script = """CREATE TABLE IF NOT EXISTS Locators (
                                                                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                                                        email TEXT NOT NULL UNIQUE,
                                                                        phone TEXT UNIQUE
                                                                    );
                                                                    """
                self.conn.execute(sql_script)
                
                sql_script = """CREATE TABLE IF NOT EXISTS Customers_locators (
                                                                                customer_id INTEGER NOT NULL,
                                                                                locator_id  INTEGER NOT NULL,
                                                                                FOREIGN KEY(customer_id) REFERENCES Customers(id),
                                                                                FOREIGN KEY(locator_id) REFERENCES Locators(id)
                                                                            );                                                                                                   
                                                                            """
                self.conn.execute(sql_script)

                sql_script = """CREATE TABLE IF NOT EXISTS Customer_sales (
                                                                            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                                                            customer_id INTEGER NOT NULL,
                                                                            value INTEGER NOT NULL,
                                                                            effictive_from_dttm NUMERIC NOT NULL DEFAULT (datetime('now')),
                                                                            effictive_to_dttm NUMERIC NOT NULL DEFAULT '5999-12-31',
                                                                            FOREIGN KEY(customer_id) REFERENCES Customers(id)
                                                                    );                                                                                                   
                                                                    """
                self.conn.execute(sql_script)

                sql_script = """CREATE TABLE IF NOT EXISTS Transactions (
                                                                            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                                                            customer_id INTEGER NOT NULL,
                                                                            warehouse_id  INTEGER NOT NULL,
                                                                            create_at NUMERIC NOT NULL DEFAULT (datetime('now')),
                                                                            type TEXT NOT NULL, 
                                                                            FOREIGN KEY(customer_id) REFERENCES Customers(id),
                                                                            FOREIGN KEY(warehouse_id) REFERENCES Warehouse(id)
                                                                    );                                                                                                   
                                                                    """
                self.conn.execute(sql_script)

                sql_script = """CREATE TABLE IF NOT EXISTS Goods (
                                                                    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                                                    title TEXT NOT NULL,
                                                                    category_id INTEGER NOT NULL,
                                                                    price INTEGER NOT NULL,
                                                                    create_at NUMERIC NOT NULL DEFAULT (datetime('now')),
                                                                    delFlg INTEGER NOT NULL DEFAULT 0,
                                                                    FOREIGN KEY(category_id) REFERENCES Categoris(id),
                                                                    UNIQUE(title)
                                                                );                                                                                                   
                                                                """
                self.conn.execute(sql_script)

                sql_script = """CREATE TABLE IF NOT EXISTS Warehouse (
                                                                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                                                        good_id INTEGER NOT NULL,
                                                                        create_at NUMERIC NOT NULL DEFAULT (datetime('now')),
                                                                        delFlg INTEGER NOT NULL DEFAULT 0,
                                                                        saleFlg INTEGER NOT NULL DEFAULT 0,
                                                                        FOREIGN KEY(good_id) REFERENCES Goods(id)
                                                                    );                                                                                                   
                                                                    """
                self.conn.execute(sql_script)

                sql_script = """CREATE TABLE IF NOT EXISTS Deliveries (
                                                                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                                                        good_id INTEGER NOT NULL,
                                                                        count INTEGER NOT NULL,
                                                                        price INTEGER NOT NULL,
                                                                        create_at NUMERIC NOT NULL DEFAULT (datetime('now')),
                                                                        FOREIGN KEY(good_id) REFERENCES Goods(id)
                                                                    );                                                                                                   
                                                                    """
                self.conn.execute(sql_script)

                sql_script = """CREATE TABLE IF NOT EXISTS Categoris (
                                                                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                                                        title TEXT NOT NULL,
                                                                        description TEXT
                                                                    );                                                                                                   
                                                                    """
                self.conn.execute(sql_script)

                sql_script = """CREATE TABLE IF NOT EXISTS Category_sales (
                                                                            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                                                            category_id INTEGER NOT NULL,
                                                                            value INTEGER NOT NULL,
                                                                            effictive_from_dttm NUMERIC NOT NULL DEFAULT (datetime('now')),
                                                                            effictive_to_dttm NUMERIC NOT NULL DEFAULT '5999-12-31',
                                                                            FOREIGN KEY(category_id) REFERENCES Categoris(id)
                                                                        );                                                                                                   
                                                                    """
                self.conn.execute(sql_script)
                
                sql_script = """CREATE TRIGGER trigger_insert_category_sale BEFORE INSERT 
                                ON Category_sales
                                BEGIN
                                    UPDATE Category_sales SET effictive_to_dttm = datetime(NEW.effictive_from_dttm, '-1 seconds')
                                    WHERE category_id = NEW.category_id  AND (datetime('now')) BETWEEN effictive_from_dttm AND effictive_to_dttm; 
                                END;
                    """
                self.conn.execute(sql_script)

                sql_script = """CREATE TRIGGER trigger_insert_customer_sale BEFORE INSERT 
                                ON Customer_sales
                                BEGIN
                                    UPDATE Customer_sales SET effictive_to_dttm = datetime(NEW.effictive_from_dttm, '-1 seconds')
                                    WHERE customer_id = NEW.customer_id  AND (datetime('now')) BETWEEN effictive_from_dttm AND effictive_to_dttm; 
                                END;
                    """
                self.conn.execute(sql_script)


                sql_script = """CREATE VIEW view_customer_sale 
                                AS 
                                SELECT 
                                    customer_id,
                                    value as customer_sale
                                FROM Customer_sales
                                WHERE (datetime('now')) BETWEEN effictive_from_dttm AND effictive_to_dttm;
                    """
                self.conn.execute(sql_script)

                sql_script = """CREATE VIEW view_category_sale 
                                AS 
                                SELECT 
                                    category_id,
                                    value as category_sale
                                FROM Category_sales
                                WHERE (datetime('now')) BETWEEN effictive_from_dttm AND effictive_to_dttm;
                    """
                self.conn.execute(sql_script)

                sql_script = """CREATE VIEW view_customer_sale_count
                                AS 
                                SELECT
                                    c.id, 
                                    COUNT(customer_id) as count
                                FROM Customers as c
                                LEFT JOIN Transactions as t ON c.id = t.customer_id
                                GROUP BY c.id
                    """
                self.conn.execute(sql_script)

                sql_script = """CREATE VIEW view_purchase
                                AS 
                                SELECT
                                    ROUND(SUM(d.price * d.count), 2) as purchase_price,
                                    strftime('%Y-%m-%d', d.create_at) as datetime
                                FROM Deliveries as d
                                GROUP BY datetime
                    """
                self.conn.execute(sql_script)

                self.conn.commit()

                print('Database initialized')
            except Error as e:
                print(e)
                
    def get_csv(self):

        """
        The function of loading data from dns from the 'Data' folder

        It is advisable to run the function immediately after initializing the database
        """
        with self.conn:

            #Persons table load
            df = pd.read_csv(os.getcwd()+'\\Data\\Persons_table.csv',
                            index_col='id',
                            dtype = {'gender': 'category'})

            df.gender = df.gender.map({'Female':'F', 'Male':'M'})
            df = validation(df)
            df['customer_id'] = df.index
            df['locator_id'] = df.index
            df["phone"] = df.email.str.split(n=1, expand=True)[1].str.replace(' ', '')
            df["email"] = df.email.str.split(n=1, expand=True)[0]
            df[['first_name', 'last_name', 'gender']].to_sql('Customers', con=self.conn, if_exists='append', index = True)
            df[['email', 'phone']].to_sql('Locators', con=self.conn, if_exists='append', index = True)
            df[['customer_id', 'locator_id']].to_sql('Customers_locators', con=self.conn, if_exists='append', index = False)

            #Categoris table load
            df = pd.read_csv(os.getcwd()+'\\Data\\categoris_table.csv',
                                sep=';',
                            index_col='id')

            df[['title', 'description']].to_sql('Categoris', con=self.conn, if_exists='append', index = False)

            #Goods table load
            df = pd.read_csv(os.getcwd()+'\\Data\\goods_table.csv')
            df.rename(columns={'categoryId': 'category_id'}, inplace=True)
            df.drop_duplicates('title', keep='first', inplace=True)
            df[['title',	'price', 'category_id']].to_sql('Goods', con=self.conn, if_exists='append', index = False)
            df.rename(columns={'id': 'good_id'}, inplace=True)

            print('Data added from csv')

    def add_customer(self, name, last, gender):

        """
        Add Customer function

        Parametrs:

            name: str
                The name of customer
            last: str
                The lastname of customer
            gender: str ('M', 'F')
                The gender of customer
        """
        with self.conn:     
            sql = ''' INSERT INTO Customers(first_name, last_name, gender)
                      VALUES(?,?,?) '''
            self.cur.execute(sql, [name, last, gender])
            print(f"Customer {last} {name} added") 

    def sale(self, customed_id, warehouse_id, **kwargs):

        """
        Sale goods function

        Parametrs:

            customed_id: int
                The id of customer
            warehouse_id: int
                The id of good in warehouse

        Kwargs parametrs:

            date: str (example: '2019-01-01 00:00:00')
                The datetime, when good was sold

        """
        customed_id = str(customed_id)
        warehouse_id = str(warehouse_id)
        with self.conn:
            try:
                sql_script = 'SELECT * FROM Warehouse WHERE id= ?'
                test = self.conn.execute(sql_script, [warehouse_id])
                count = test.fetchall()
                #print(count)
                if (count) and (1 not in (count[0][-2:])):
                
                    sql_script = "UPDATE Warehouse SET saleFlg = 1 WHERE id =?"
                    self.conn.execute(sql_script, [str(warehouse_id)])     

                    if kwargs:
                        sql_script = """INSERT INTO Transactions (customer_id, warehouse_id, type, create_at) VALUES (?,?,?,?) """
                        self.conn.execute(sql_script, [customed_id, str(warehouse_id), 'sale', kwargs['date']])       
                        print('Customer ' + str(customed_id) +' bought good ' + str(warehouse_id))

                    else:
                        sql_script = """INSERT INTO Transactions (customer_id, warehouse_id, type) VALUES (?,?,?) """
                        self.conn.execute(sql_script, [customed_id, str(warehouse_id), 'sale'])       
                        print('Customer ' + str(customed_id) +' bought good ' + str(warehouse_id))

                    self.conn.commit()
                elif count[0][-2] == 1:
                    print('Good removed')  
                else:
                    print('Good already sold')
            except Error as e:
                print(e)

    def refund(self, warehouse_id, **kwargs):

        """
        Refund goods function

        Parametrs:

            warehouse_id: int
                The id of good in warehouse

        Kwargs parametrs:

            date: str (example: '2019-01-01 00:00:00')
                The datetime, when good was refunded

        """

        warehouse_id = str(warehouse_id)
        with self.conn:
            try:
                sql_script = 'SELECT * FROM Transactions WHERE warehouse_id= ?'
                test = self.conn.execute(sql_script, [warehouse_id])
                count = test.fetchall()
                #print(count)
                if count[-1][-1] == 'sale':
                
                    sql_script = "UPDATE Warehouse SET saleFlg = 0 WHERE id =?"
                    self.conn.execute(sql_script, [count[-1][2]]) 

                    if kwargs:
                        sql_script = """INSERT INTO Transactions (customer_id, warehouse_id, type, create_at) VALUES (?,?,?, ?) """
                        self.conn.execute(sql_script, [count[-1][1], count[-1][2], 'refund', kwargs['date']]) 

                    else:
                        sql_script = """INSERT INTO Transactions (customer_id, warehouse_id, type) VALUES (?,?,?) """
                        self.conn.execute(sql_script, [count[-1][1], count[-1][2], 'refund'])       
                    print('Customer ' + str(count[-1][1]) +' refund good ' + str(count[0][2]))

                    self.conn.commit()
                else:
                    print('Good not sold')
            except Error as e:
                print(e)

    def delivery(self, goods_id, count, value, **kwargs):
                
        """
        Delivery goods function

        Parametrs:

            goods_id: int
                The id of good
            count: int
                Number of products per batch
            value: int
                Price per batch
        Kwargs parametrs:

            date: str (example: '2019-01-01 00:00:00')
                The datetime, when batch was delivered

        """
        goods_id = str(goods_id)
        value = str(value)
        with self.conn:
            try:
                sql_script = 'SELECT * FROM Goods WHERE id=?'
                test = self.conn.execute(sql_script, [goods_id])
                select = test.fetchall()
                if select:                        
                    sql_script = """INSERT INTO Deliveries (good_id, count, price, create_at) VALUES (?,?,?,?) """
                    self.conn.execute(sql_script, [goods_id, str(count), value, kwargs['date']])
                    tmp = 0
                    while tmp < count:
                        sql_script = """INSERT INTO Warehouse (good_id, create_at) VALUES (?, ?) """
                        self.conn.execute(sql_script, [goods_id, kwargs['date']])
                        tmp +=1
                    self.conn.commit()
                else:
                    print('This good has not been added to the Goods list.')
            except Error as e:
                print(e)
            print('Good ' + goods_id + ' delivered in volume ' + str(count))

    def sales_set(self, id_, value, sale_type, **kwargs):

        """
        Discount setting function

        Parametrs:

            id_: int
                The id of good or customer
            value: int
                Value of discount in procent
            sale_type: str ('customer', 'category)
                What is the discount for
        Kwargs parametrs:

            ef_from: str (example: '2019-01-01 00:00:00')
                The datetime, when discount start
            ef_to: str (example: '2019-01-01 00:00:00')
                The datetime, when discount end

        """
        id_ = str(id_)
        value = str(value)

        if sale_type == 'customer':
            with self.conn:
                if kwargs:
                    try:
                        sql_script = """INSERT INTO Customer_sales (customer_id, value, effictive_from_dttm, effictive_to_dttm) VALUES (?,?,?,?) """
                        self.conn.execute(sql_script, [id_, value, kwargs['ef_from'], kwargs['ef_to']])       
                        print('Customer', id_, value, 'discount added', sep=' ')
                    except Error as e:
                        print(e)
                else:
                    try:
                        sql_script = """INSERT INTO Customer_sales (customer_id, value) VALUES (?,?) """
                        self.conn.execute(sql_script, [id_, value])       
                        print('Customer', id_, value, 'discount added', sep=' ')
                    except Error as e:
                        print(e)
                    
        elif sale_type == 'category':
            with self.conn:
                if kwargs:
                    try:
                        sql_script = """INSERT INTO Category_sales (category_id, value, effictive_from_dttm, effictive_to_dttm) VALUES (?,?,?,?) """
                        self.conn.execute(sql_script, [id_, value, kwargs['ef_from'], kwargs['ef_to']])       
                        print('Category', id_, value, 'discount added', sep=' ')
                    except Error as e:
                        print(e)
                else:
                    try:
                        sql_script = """INSERT INTO Category_sales (category_id, value) VALUES (?,?) """
                        self.conn.execute(sql_script, [id_, value])       
                        print('Category', id_, value, 'discount added', sep=' ')
                    except Error as e:
                        print(e)
        else:
            raise AttributeError 
        
        self.conn.commit()

    def make_some_data(self, rand_iter):
        
        """
        This function generates synthetic data for the store.
        So far, data is only for '2019-01'
        Parametrs:

            rand_iter: int
                Number of transactions

        """
 
        day_list = ['0' + (str(i)) if len(str(i)) == 1 else (str(i)) for i in range(1, 32)] 
        time_list = ['2019-01-' + i + ' 07:00:00' for i in day_list] #СОЗДАЕМ СПИСОК ДНЕЙ В ДЕКАБРЕ 2019 ГОДА
        count_list = [10, 20 ,30] # СПИОСК ШТУК ТОВАРОВ В ПАРТИИ
        with self.conn:     
            self.cur.execute("SELECT * FROM Goods")
            goods_list = self.cur.fetchall() # СЛОВАРЬ ТОВАРОВ
    #################################################            ДОСТАВЛЯЕМ ТОВАРЫ        ########################################################################
        tmp = 0
        while tmp < rand_iter:
            good = random.choice(goods_list)
            count = random.choice(count_list)
            time = random.choice(time_list)
            self.delivery(good[0], count, good[3] * 0.4, date=time)
            tmp += 1
    #################################################            ПРОДАЕМ ТОВАРЫ        ########################################################################
        with self.conn:     
            self.cur.execute("SELECT * FROM Customers")
            customers_list = self.cur.fetchall() #СПИСОК ПОЛЬЗОВАТЕЛЕЙ

            self.cur.execute("SELECT * FROM Warehouse")
            warehouse_list = self.cur.fetchall() #СПИСОК ТОВАРОВ НА СКЛАДЕ       
        tmp = 0
        sale_list = []
        while tmp < rand_iter * 10:
            warehouse = random.choice(warehouse_list)
            warehouse_list.remove(warehouse)
            sale_list.append(warehouse) # CПИСОК ПРОДАННЫХ ТОВАРОВ
            customer = random.choice(customers_list)
            time = random.choice(time_list)
            self.sale(customer[0], warehouse[0], date=time)
            tmp += 1
    ############################################               СДАЕМ ТОВАРЫ           ##########################################################################
        tmp = 0
        while tmp < round(rand_iter * 0.15):
            refund = random.choice(sale_list)
            sale_list.remove(refund)
            time = random.choice(time_list)
            self.refund(refund[0], date=time)
            tmp += 1
    #############################################        СОЗДАЕМ СКИДКИ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ          ######################################################################
        sale_customer_list = [5, 7.5, 10] #СПИСОК СКИДОВ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ

        #CОЗДАЕМ СКИДКИ ДЛЯ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ С 1 ЯНВАРЯ
        for customer in customers_list:
            sale_customer = random.choice(sale_customer_list)
            self.sales_set(customer[0], sale_customer, sale_type='customer', ef_from='2019-01-01 07:00:00', ef_to='5999-12-31')

        #CОЗДАЕМ СКИДКИ ДЛЯ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ С 15 ЯНВАРЯ
        for customer in customers_list:
            sale_customer = random.choice(sale_customer_list)
            self.sales_set(customer[0], sale_customer, sale_type='customer', ef_from='2019-01-15 07:00:00', ef_to='5999-12-31')
    ###############################################      СОЗДАЕМ СКИДКИ ДЛЯ КАТЕГОРИЙ          ##############################################################
        with self.conn:     
            self.cur.execute("SELECT * FROM Categoris")
            category_list = self.cur.fetchall() #СПИСОК ВСЕХ КАТЕГОРИЙ
        sale_category_list = [5, 10, 15] #СПИСОК СКИДОК ДЛЯ КАТЕГОРИЙ

        #CОЗДАЕМ СКИДКИ ДЛЯ ВСЕХ КАТЕГОРИЙ С 1 ЯНВАРЯ
        for category in category_list:
            sale_category = random.choice(sale_category_list)
            self.sales_set(category[0], sale_category, sale_type='category', ef_from='2019-01-01 07:00:00', ef_to='5999-12-31')

        #CОЗДАЕМ СКИДКИ ДЛЯ ВСЕХ КАТЕГОРИЙ С 15 ЯНВАРЯ
        for category in category_list:
            sale_category = random.choice(sale_category_list)
            self.sales_set(category[0], sale_category, sale_type='category', ef_from='2019-01-15 07:00:00', ef_to='5999-12-31')
    ###############################################      СОЗДАЕМ НЕ АКТИВНЫХ ПОЛЬЗОВАТЕЛЕЙ          ##############################################################
        self.add_customer('Mark', 'Khubbatulin', 'M')
        self.add_customer('Hayk', 'Inants', 'M')
        print('Сreated a lot of data')

    def low_active_customer(self):

        """
        Function shows low active users

        """
        with self.conn:    
            self.cur.execute("""SELECT 
                                    c.id,
                                    c.last_name,
                                    c.first_name,
                                    v.count,
                                    l.email,
                                    l.phone
                                FROM view_customer_sale_count as v
                                JOIN Customers as c ON c.id = v.id
                                LEFT JOIN Customers_locators as cl ON v.id = cl.customer_id
                                LEFT JOIN Locators as l ON l.id = cl.locator_id
                                WHERE count < (SELECT ROUND(AVG(count)) * 0.2
                                                FROM view_customer_sale_count)
                            """)
            df = pd.DataFrame(self.cur.fetchall(), columns=['id', 'last_name', 'first_name', 'count', 'email', 'phone_number'])
            df.set_index('id', inplace=True)
            print('------------Low Active Users-----------')
            print(df[:])

    def monthly_sales(self, date):
                
                
        """
        The function shows a report for the month of sale.
        So far, data is only for '2019-01'
        Parametrs:

            date: str (example: '2019-01)
                Date of month

        """
        with self.conn:    
            self.cur.execute("""SELECT
                                    SUM(g.price * (1 - (cu_s.value + ca_s.value) / 100)),
                                    strftime('%Y-%m-%d', t.create_at) as datetime
                                FROM Warehouse as w
                                LEFT JOIN Transactions as t ON t.warehouse_id = w.id
                                LEFT JOIN Goods as g ON g.id = w.good_id
                                JOIN Category_sales as ca_s ON ca_s.category_id = g.category_id
                                JOIN Customer_sales as cu_s ON cu_s.customer_id = t.customer_id
                                WHERE w.saleFlg = 1 
                                    AND t.create_at BETWEEN ca_s.effictive_from_dttm AND ca_s.effictive_to_dttm
                                    AND t.create_at BETWEEN cu_s.effictive_from_dttm AND cu_s.effictive_to_dttm
                                    AND strftime('%Y-%m', datetime) =?
                                GROUP BY datetime
                            """, (date,))
            df2 = pd.DataFrame(self.cur.fetchall(), columns=['Income', 'Date'])

            self.cur.execute("""SELECT
                                    *
                                FROM view_purchase
                                WHERE strftime('%Y-%m', datetime) =?
                                GROUP BY datetime
                            """, (date,))

            df3 = pd.DataFrame(self.cur.fetchall(), columns=['Purchase', 'Date'])

            day = calendar.monthrange(2019, 1)[1]
            day_list = ['0' + (str(i)) if len(str(i)) == 1 else (str(i)) for i in range(1, day + 1)]
            d = {'Date': ['2019-01-' + i for i in day_list]}
            df1= pd.DataFrame(data=d)
            df = df1.merge(df2)
            df = df.merge(df3)
            print('------------Monthly report-----------')
            print(df)

            width = 0.5
            y1 = df.Income
            y2 = df.Purchase
            x = [i[-2:] for i in df.Date]
            plt.figure(figsize=(16,9))
            plt.bar(x, y1, width, label='Income')
            plt.bar(x, y2, width, label='Purchase')
            plt.xlabel(f'Days in {date}')
            plt.ylabel('Ruble')
            plt.title('Monthly report')
            plt.legend(loc='best')
            plt.show()
