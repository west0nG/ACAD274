#!/usr/bin/env python3
"""
准备social_final.csv用于phpMyAdmin导入
将CSV表头修改为与price_data表一致的格式
"""

import csv

INPUT_CSV = "social_final.csv"
OUTPUT_CSV = "social_final_for_import.csv"

# 字段映射：CSV原字段名 -> 新字段名（匹配price表格式）
FIELD_MAPPING = {
    'coin_symbol': 'coin_id',
    'datetime': 'ts',
    'open': 'open_price',
    'high': 'high_price',
    'low': 'low_price',
    'close': 'close_price',
    'volume_24h': 'volume_usd',
    # 其他字段保持不变
}

def main():
    print(f"读取文件: {INPUT_CSV}")
    
    with open(INPUT_CSV, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        
        # 创建新的字段名列表
        new_fieldnames = []
        for field in fieldnames:
            new_field = FIELD_MAPPING.get(field, field)
            new_fieldnames.append(new_field)
        
        print(f"\n字段映射:")
        print("-" * 60)
        for old, new in zip(fieldnames, new_fieldnames):
            if old != new:
                print(f"  {old:25s} -> {new}")
            else:
                print(f"  {old:25s} -> (保持不变)")
        
        # 写入新文件
        print(f"\n写入文件: {OUTPUT_CSV}")
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=new_fieldnames)
            writer.writeheader()
            
            row_count = 0
            for row in reader:
                # 创建新行，使用新字段名
                new_row = {}
                for old_field, new_field in zip(fieldnames, new_fieldnames):
                    new_row[new_field] = row[old_field]
                writer.writerow(new_row)
                row_count += 1
        
        print(f"✅ 完成！共处理 {row_count} 行数据")
        print(f"\n新CSV文件字段名（匹配price表格式）:")
        print(", ".join(new_fieldnames[:8]))  # 显示前8个字段
        print("...")
        print(f"\n现在可以使用 phpMyAdmin 导入 {OUTPUT_CSV}")
        print("导入时表名建议使用: social_data 或 social_final")

if __name__ == "__main__":
    main()

