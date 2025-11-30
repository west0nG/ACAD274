import csv

# 读取 CSV 文件
csv_file = 'btc_data.csv'  # 改成你的文件路径
sql_file = 'import.sql'

with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    
    with open(sql_file, 'w', encoding='utf-8') as out:
        # 写入清空表的命令
        out.write("TRUNCATE TABLE bitcoin_price_dataset;\n\n")
        out.write("INSERT INTO bitcoin_price_dataset (Date, Close, High, Low, Open, Volume) VALUES\n")
        
        rows = []
        for row in reader:
            date = row['Date']
            close = row['Close']
            high = row['High']
            low = row['Low']
            open_price = row['Open']
            volume = row['Volume']
            
            rows.append(f"('{date}', {close}, {high}, {low}, {open_price}, {volume})")
        
        # 每行用逗号连接
        out.write(',\n'.join(rows))
        out.write(';\n')

print(f"✅ SQL 文件已生成: {sql_file}")
print("现在复制 import.sql 的内容到 phpMyAdmin 执行！")
