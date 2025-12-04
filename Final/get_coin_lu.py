#!/usr/bin/env python3
"""
LunarCrush API 脚本 - 获取币种时间序列数据
获取11月份所有endpoints的小时数据并导出为CSV
"""

import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import json

# LunarCrush API配置
API_BASE_URL = "https://lunarcrush.com/api4/public/coins"
API_TOKEN = "4uy7j29xeogorj49hl7monksblmim9l83i4ko38"

# 币种列表 - coin_id 和对应的 LunarCrush 符号
COINS = [
    ("doge", "DOGE"),
    ("shib", "SHIB"),
    ("pepe", "PEPE"),
    ("bonk", "BONK"),
    ("floki", "FLOKI"),
    ("bome", "BOME"),
    ("mog", "MOG"),
    ("wif", "WIF"),
    ("popcat", "POPCAT"),
    ("brett", "BRETT"),
]

# 输出文件
OUTPUT_CSV = "social_mentions_lunarcrush.csv"

def get_headers():
    """获取API请求头"""
    return {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }

def get_coin_time_series(symbol, start_timestamp, end_timestamp):
    """
    获取指定币种的时间序列数据
    
    Args:
        symbol (str): LunarCrush币种符号 (如 "DOGE")
        start_timestamp (int): 开始时间戳 (Unix秒)
        end_timestamp (int): 结束时间戳 (Unix秒)
    
    Returns:
        list: 时间序列数据列表
    """
    url = f"{API_BASE_URL}/{symbol}/time-series/v2"
    
    params = {
        'bucket': 'hour',  # 小时数据
        'start': start_timestamp,
        'end': end_timestamp,
    }
    
    headers = get_headers()
    
    try:
        print(f"正在获取币种 {symbol} 的数据...")
        print(f"  URL: {url}")
        print(f"  时间范围: {datetime.fromtimestamp(start_timestamp)} 到 {datetime.fromtimestamp(end_timestamp)}")
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"  HTTP状态码: {response.status_code}")
        
        response.raise_for_status()
        
        data = response.json()
        
        # 调试：打印响应结构（仅第一个币种）
        if symbol == COINS[0][1]:  # 只对第一个币种打印调试信息
            print(f"  [DEBUG] 响应类型: {type(data)}")
            if isinstance(data, dict):
                print(f"  [DEBUG] 响应键: {list(data.keys())}")
                if 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
                    print(f"  [DEBUG] 第一条数据键: {list(data['data'][0].keys())}")
        
        # 解析响应结构
        ts_list = []
        if isinstance(data, dict):
            container = data.get("data") or data.get("result") or data.get("values")
            if isinstance(container, list):
                if container and isinstance(container[0], dict):
                    # 检查第一层是否有 'time' 字段
                    if "time" in container[0] or "timestamp" in container[0]:
                        ts_list = container
                    else:
                        # 从第一个元素里找 time series 列表
                        first = container[0]
                        ts_list = (
                            first.get("timeSeries")
                            or first.get("time_series")
                            or first.get("timeseries")
                            or first.get("values")
                            or []
                        )
            elif isinstance(container, dict):
                ts_list = (
                    container.get("timeSeries")
                    or container.get("time_series")
                    or container.get("timeseries")
                    or container.get("values")
                    or []
                )
        elif isinstance(data, list):
            ts_list = data
        
        print(f"  成功获取 {len(ts_list)} 条记录")
        return ts_list
        
    except requests.exceptions.RequestException as e:
        print(f"  API请求失败 (币种: {symbol}): {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  响应内容: {e.response.text[:500]}")
        return None
    except json.JSONDecodeError as e:
        print(f"  JSON解析失败 (币种: {symbol}): {e}")
        return None
    except Exception as e:
        print(f"  未知错误 (币种: {symbol}): {e}")
        return None

def normalize_timestamp(raw_ts):
    """规范化时间戳为Unix秒级"""
    if raw_ts is None:
        return None
    if isinstance(raw_ts, str):
        raw_ts = float(raw_ts)
    elif not isinstance(raw_ts, (int, float)):
        raw_ts = float(raw_ts)
    # 如果是毫秒级（大于 10^12），除以 1000
    if raw_ts > 10**12:
        raw_ts = raw_ts / 1000.0
    return int(raw_ts)

def process_time_series_data(coin_symbol, ts_list):
    """
    处理时间序列数据，动态提取所有可用的endpoints
    
    Args:
        coin_symbol (str): 币种符号
        ts_list (list): 时间序列数据列表
    
    Returns:
        list: 处理后的数据行列表
    """
    if not ts_list:
        return []
    
    rows = []
    
    # 收集所有可能的字段名（从第一条记录中获取）
    all_fields = set()
    for record in ts_list:
        if isinstance(record, dict):
            all_fields.update(record.keys())
    
    for record in ts_list:
        if not isinstance(record, dict):
            continue
            
        # 基础信息 - 尝试多种可能的时间字段名
        raw_timestamp = record.get('time') or record.get('timestamp') or record.get('t')
        timestamp = normalize_timestamp(raw_timestamp)
        
        if timestamp:
            dt = datetime.fromtimestamp(timestamp)
            date_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        else:
            date_str = None
            continue  # 如果没有时间戳，跳过这条记录
        
        # 创建行数据，包含所有API返回的字段
        row = {
            'coin_symbol': coin_symbol,
            'timestamp': timestamp,
            'datetime': date_str,
        }
        
        # 动态添加所有API返回的字段（排除已添加的基础字段）
        excluded_fields = {'time', 'timestamp', 't'}  # 时间字段已处理
        for field in all_fields:
            if field not in excluded_fields:
                row[field] = record.get(field)
        
        rows.append(row)
    
    return rows

def main():
    """主函数"""
    print("开始获取LunarCrush币种时间序列数据...")
    print(f"目标时间段: 2024年11月 (小时数据)")
    print(f"币种数量: {len(COINS)}")
    
    # 设置11月的时间范围 (2024-11-01 00:00:00 UTC 到 2024-11-30 23:59:59 UTC)
    start_dt = datetime(2024, 11, 1, 0, 0, 0)
    end_dt = datetime(2024, 11, 30, 23, 59, 59)
    start_timestamp = int(start_dt.timestamp())
    end_timestamp = int(end_dt.timestamp())
    
    print(f"时间范围: {start_dt} 到 {end_dt}")
    print(f"时间戳: {start_timestamp} 到 {end_timestamp}\n")
    
    all_rows = []
    
    for coin_id, symbol in COINS:
        print(f"\n{'='*60}")
        print(f"处理币种: {coin_id} (LunarCrush符号: {symbol})")
        print(f"{'='*60}")
        
        # 获取时间序列数据
        ts_list = get_coin_time_series(symbol, start_timestamp, end_timestamp)
        
        if ts_list:
            # 处理数据
            rows = process_time_series_data(coin_id, ts_list)
            all_rows.extend(rows)
            print(f"已处理 {len(rows)} 条记录")
        else:
            print(f"未获取到数据，跳过...")
        
        # 添加延迟避免API限制
        time.sleep(1)
    
    # 导出到CSV
    if all_rows:
        df = pd.DataFrame(all_rows)
        df = df.sort_values(['coin_symbol', 'timestamp'])
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"\n✅ 成功导出 {len(df)} 条记录到 {OUTPUT_CSV}")
        
        # 显示数据概览
        print(f"\n数据概览:")
        print(f"币种数量: {df['coin_symbol'].nunique()}")
        print(f"时间范围: {df['datetime'].min()} 到 {df['datetime'].max()}")
        print(f"总记录数: {len(df)}")
        
        # 显示每个币种的记录数
        coin_counts = df['coin_symbol'].value_counts()
        print(f"\n各币种记录数:")
        for coin, count in coin_counts.items():
            print(f"  {coin}: {count} 条")
            
    else:
        print("❌ 没有获取到任何数据")

if __name__ == "__main__":
    main()
