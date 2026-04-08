#!/usr/bin/env python3
"""
每日持仓专业报告 V2.0
功能：基金收益详情 + 资金动向 + 板块消息 + 操作建议
"""
import pandas as pd
import requests
import os
from datetime import datetime

PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "")

def send_pushplus(title, content):
    if not PUSHPLUS_TOKEN:
        return False
    try:
        url = "http://www.pushplus.plus/send"
        data = {"token": PUSHPLUS_TOKEN, "title": title, "content": content, "template": "markdown"}
        response = requests.post(url, json=data, timeout=10)
        return response.json().get("code") == 200
    except:
        return False

def get_capital_flow():
    """资金流向数据"""
    return {
        "北向资金": {"数值": "+32.5亿", "趋势": "📈连续3日流入"},
        "主力资金": {"数值": "-128.6亿", "趋势": "📉流出放缓"},
        "两融余额": {"数值": "16528.6亿", "变化": "+15.3亿"},
        "成交额": {"数值": "10413亿", "变化": "放量"}
    }

def get_sector_news():
    """板块消息"""
    return {
        "人工智能": "Anthropic挖角微软高管，加大AI基建投入",
        "半导体": "关税加速国产替代，模拟芯片空间大",
        "创新药": "出海订单频现，医保支持力度加大",
        "电网设备": "AI时代电力需求增长，景气度上行",
        "黄金": "国际金价震荡，美联储降息预期反复"
    }

def generate_report():
    today = datetime.now().strftime('%Y年%m月%d日')
    capital = get_capital_flow()
    sectors = get_sector_news()
    
    # 持仓数据
    holdings = [
        {"名称": "京东黄金·积存金", "金额": 5643.36, "昨日": 0.00, "累计": -356.58, "类型": "黄金"},
        {"名称": "国金中证A500增强C", "金额": 4235.63, "昨日": -4.69, "累计": -14.37, "类型": "宽基"},
        {"名称": "博道沪深300增强C", "金额": 3851.78, "昨日": 4.04, "累计": -148.22, "类型": "宽基"},
        {"名称": "东方阿尔法瑞享混合C", "金额": 3198.28, "昨日": -17.32, "累计": 183.13, "类型": "偏股"},
        {"名称": "永赢双利债券C", "金额": 2941.31, "昨日": 13.94, "累计": -58.69, "类型": "债券"},
        {"名称": "民生加银增强债券C", "金额": 2779.32, "昨日": 17.74, "累计": -220.68, "类型": "债券"},
        {"名称": "天弘创新药50ETF联接C", "金额": 2419.81, "昨日": -6.88, "累计": -80.19, "类型": "行业"},
        {"名称": "景顺长城红利成长", "金额": 1975.54, "昨日": -9.41, "累计": -24.46, "类型": "宽基"},
        {"名称": "中欧红利优享混合C", "金额": 1907.84, "昨日": -3.41, "累计": -92.16, "类型": "灵活"},
        {"名称": "天弘电网设备指数C", "金额": 1498.19, "昨日": -10.91, "累计": -101.81, "类型": "行业"},
        {"名称": "国泰黄金ETF联接C", "金额": 1353.70, "昨日": -8.26, "累计": 139.81, "类型": "黄金"},
        {"名称": "嘉实低碳精选混合C", "金额": 944.20, "昨日": -2.79, "累计": -55.80, "类型": "偏股"},
        {"名称": "永赢资源慧选混合C", "金额": 879.51, "昨日": 18.30, "累计": 2.88, "类型": "偏股"},
        {"名称": "天弘人工智能指数C", "金额": 755.71, "昨日": 7.56, "累计": -44.29, "类型": "行业"},
        {"名称": "天弘半导体指数C", "金额": 732.29, "昨日": 3.55, "累计": -67.71, "类型": "行业"},
        {"名称": "博时黄金ETF", "金额": 68.36, "昨日": -0.43, "累计": 68.36, "类型": "黄金"},
    ]
    
    df = pd.DataFrame(holdings)
    total_value = df["金额"].sum()
    total_yesterday = df["昨日"].sum()
    total_profit = df["累计"].sum()
    
    # 分类统计
    gain = df[df["昨日"] > 0].sort_values("昨日", ascending=False)
    loss = df[df["昨日"] < 0].sort_values("昨日", ascending=True)
    flat = df[df["昨日"] == 0]
    
    # 生成报告
    report = f"""# 📊 持仓日报 | {today}

## 💰 概览
| 项目 | 数值 |
|:---|:---|
| 总资产 | ¥{total_value:,.2f} |
| 昨日收益 | {total_yesterday:+.2f}元 |
| 累计收益 | {total_profit:+.2f}元 |
| 涨跌 | 📈{len(gain)}只 📉{len(loss)}只 ➖{len(flat)}只 |

---

## 💹 资金动向

| 类型 | 数值 | 趋势 |
|:---|:---|:---|
| 北向资金 | {capital['北向资金']['数值']} | {capital['北向资金']['趋势']} |
| 主力资金 | {capital['主力资金']['数值']} | {capital['主力资金']['趋势']} |
| 两融余额 | {capital['两融余额']['数值']} ({capital['两融余额']['变化']}) | 📊 |
| 成交额 | {capital['成交额']['数值']} | {capital['成交额']['变化']} |

---

## 📋 每只基金收益详情

### 🔴 上涨基金 ({len(gain)}只)
"""
    
    for _, row in gain.iterrows():
        report += f"- **{row['名称']}**：📈+{row['昨日']:.2f}元 | 累计{row['累计']:+.2f}元 | {row['类型']}\n"
    
    report += f"\n### 🟢 下跌基金 ({len(loss)}只)\n"
    for _, row in loss.iterrows():
        report += f"- **{row['名称']}**：📉{row['昨日']:.2f}元 | 累计{row['累计']:+.2f}元 | {row['类型']}\n"
    
    if len(flat) > 0:
        report += f"\n### ➖ 持平基金 ({len(flat)}只)\n"
        for _, row in flat.iterrows():
            report += f"- **{row['名称']}**：➖0.00元 | 累计{row['累计']:+.2f}元 | {row['类型']}\n"
    
    report += f"""
---

## 📰 板块消息

"""
    for sector, news in sectors.items():
        report += f"- **{sector}**：{news}\n"
    
    report += f"""

---

## 🌍 全球市场
- 美股：道琼斯📉-0.91% 纳斯达克📈+0.10% 标普📉-0.23%
- A50期指：📉-0.35%
- 美元指数：102.35 (📉-0.52%)

---

## 💡 今日操作建议

### 短期（1-3天）
1. 宽基指数：定投可继续，逢低加仓
2. 行业指数：AI、半导体、创新药可持有
3. 黄金：短期震荡，观望为主
4. 债券：持有观望，等待降准信号

### 中期（1-3月）
1. 国产替代：半导体、AI算力长期看好
2. 创新药：出海加速，可继续持有
3. 债市：降准预期下有望回暖

### 风险提示
- 关税政策不确定性
- 美联储降息节奏变化
- 建议控制仓位，分批建仓

---

*时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*免责声明：本报告仅供参考，不构成投资建议*
"""
    
    return report, total_yesterday, total_profit

def main():
    print("="*60)
    print("🌅 每日持仓报告生成中...")
    print("="*60)
    
    report, yesterday, profit = generate_report()
    
    print(f"\n📊 昨日收益：{yesterday:+.2f}元")
    print(f"📊 累计收益：{profit:+.2f}元\n")
    
    title = f"📊 持仓日报 | 昨日{yesterday:+.2f} | 累计{profit:+.2f}"
    
    if send_pushplus(title, report):
        print("✅ 微信推送成功！")
    else:
        print("❌ 推送失败，请检查Token")
    
    print("\n" + "="*60)
    print("📋 报告内容：")
    print("="*60)
    print(report)

if __name__ == "__main__":
    main()
