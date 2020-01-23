import shop

product_market = shop.Shop_db('db.sqlite3')
product_market.db_init()
product_market.get_csv()
product_market.make_some_data(1000)
product_market.low_active_customer()
product_market.monthly_sales('2019-01')