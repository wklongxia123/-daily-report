#!/usr/bin/env python3
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

def get_market_data():
    return {"美股": {"道琼斯": {"涨跌": "-0.91%", "点数": "37965.60", "趋势": "📉"}, "纳斯达克": {"涨跌": "+0.10%", "点数": "16794.64", "趋势": "📈"}, "标普500": {"涨跌": "-0.23%", "点数": "5062.25", "趋势": "📉"}}}

def get_sector_news():
    return {"人工智能": {"消息": "Anthropic挖角微软高管", "影响": "利好", "建议": "持有"}, "半导体": {"消息": "关税加速国产替代", "影响": "利好", "建议": "加仓"}}

def get_capital_flow():
    return {"北向资金": {"净流入": "+32.5亿", "趋势": "📈"}, "主力资金": {"净流入": "-128.6亿", "趋势": "📉"}}

def analyze_portfolio(df, total_value, holding_profit):
    analysis = {"风险提示": [], "调仓建议": []}
    gold_pct = df[df["类型"] == "黄金"]["持有金额"].sum() / total_value * 100 if len(df[df["类型"] == "黄金"]) > 0 else 0
    if gold_pct > 25:
        analysis["风险提示"].append(f"⚠️ 黄金占比{gold_pct:.1f}%偏高")
    if holding_profit < -500:
        analysis["风险提示"].append(f"⚠️ 累计亏损{holding_profit:.2f}")
    return analysis

def generate_market_report():
    today = datetime.now().strftime('%Y年%m月%d日')
    market_data = get_market_data()
    sector_news = get_sector_news()
    capital_flow = get_capital_flow()
    
    holdings = [
        {"基金名称": "京东黄金·积存金", "持有金额": 5643.36, "昨日收益": 0.00, "持有收益": -356.58, "持有收益率": "-5.94%", "类型": "黄金"},
        {"基金名称": "国金中证A500指数增强C", "持有金额": 4235.63, "昨日收益": -4.69, "持有收益": -14.37, "持有收益率": "-0.36%", "类型": "宽基指数"},
        {"基金名称": "博道沪深300指数增强C", "持有金额": 3851.78, "昨日收益": 4.04, "持有收益": -148.22, "持有收益率": "-3.95%", "类型": "宽基指数"},
        {"基金名称": "东方阿尔法瑞享混合C", "持有金额": 3198.28, "昨日收益": -17.32, "持有收益": 183.13, "持有收益率": "+6.07%", "类型": "偏股混合"},
        {"基金名称": "永赢双利债券C", "持有金额": 2941.31, "昨日收益": 13.94, "持有收益": -58.69, "持有收益率": "-1.96%", "类型": "债券型"},
        {"基金名称": "民生加银增强收益债券C", "持有金额": 2779.32, "昨日收益": 17.74, "持有收益": -220.68, "持有收益率": "-7.36%", "类型": "债券型"},
        {"基金名称": "天弘沪深港创新药50ETF联接C", "持有金额": 2419.81, "昨日收益": -6.88, "持有收益": -80.19, "持有收益率": "-3.21%", "类型": "行业指数"},
        {"基金名称": "景顺长城中证沪港深红利成长", "持有金额": 1975.54, "昨日收益": -9.41, "持有收益": -24.46, "持有收益率": "-1.22%", "类型": "宽基指数"},
        {"基金名称": "中欧红利优享灵活配置混合C", "持有金额": 1907.84, "昨日收益": -3.41, "持有收益": -92.16, "持有收益率": "-4.61%", "类型": "灵活配置"},
        {"基金名称": "天弘中证电网设备主题指数C", "持有金额": 1498.19, "昨日收益": -10.91, "持有收益": -101.81, "持有收益率": "-6.36%", "类型": "行业指数"},
        {"基金名称": "国泰黄金ETF联接C", "持有金额": 1353.70, "昨日收益": -8.26, "持有收益": 139.81, "持有收益率": "+11.52%", "类型": "黄金"},
        {"基金名称": "嘉实低碳精选混合C", "持有金额": 944.20, "昨日收益": -2.79, "持有收益": -55.80, "持有收益率": "-5.58%", "类型": "偏股混合"},
        {"基金名称": "永赢资源慧选混合C", "持有金额": 879.51, "昨日收益": 18.30, "持有收益": 2.88, "持有收益率": "+0.33%", "类型": "偏股混合"},
        {"基金名称": "天弘中证人工智能主题指数C", "持有金额": 755.71, "昨日收益": 7.56, "持有收益": -44.29, "持有收益率": "-5.54%", "类型": "行业指数"},
        {"基金名称": "天弘半导体材料设备指数C", "持有金额": 732.29, "昨日收益": 3.55, "持有收益": -67.71, "持有收益率": "-8.46%", "类型": "行业指数"},
        {"基金名称": "博时黄金(ETF)I", "持有金额": 68.36, "昨日收益": -0.43, "持有收益": 68.36, "持有收益率": "0.00%", "类型": "黄金"},
    ]
    
    df = pd.DataFrame(holdings)
    total_value = df["持有金额"].sum()
    total_yesterday = df["昨日收益"].sum()
    holding_profit = sum([h["持有收益"] for h in holdings])
    gold_value = df[df["类型"] == "黄金"]["持有金额"].sum()
    gold_pct = gold_value / total_value * 100
    
    df_sorted = df.sort_values("昨日收益", ascending=False)
    gain_count = len(df[df["昨日收益"] > 0])
    loss_count = len(df[df["昨日收益"] < 0])
    flat_count = len(df[df["昨日收益"] == 0])
    gain_amount = df[df["昨日收益"] > 0]["昨日收益"].sum()
    loss_amount = df[df["昨日收益"] < 0]["昨日收益"].sum()
    
    analysis = analyze_portfolio(df, total_value, holding_profit)
    
    report = f"""# 📊 每日持仓专业报告 | {today}

## 💰 持仓概览
| 指标 | 数值 | 状态 |
|:---:|:---:|:---:|
| **总资产** | ¥{total_value:,.2f} | 📊 |
| **昨日收益** | {total_yesterday:+.2f} | {'📈' if total_yesterday >= 0 else '📉'} |
| **累计收益** | {holding_profit:+.2f} | {'📈' if holding_profit >= 0 else '📉'} |
| **黄金仓位** | ¥{gold_value:,.2f} ({gold_pct:.1f}%) | 🥇 |

### 📊 今日涨跌统计
- 📈 **上涨**：{gain_count}只，合计+{gain_amount:.2f}元
- 📉 **下跌**：{loss_count}只，合计{loss_amount:.2f}元
- ➖ **持平**：{flat_count}只

---

## 📋 每只基金每日收益详情

### 🔴 上涨基金 ({gain_count}只)

"""
    
    gain_funds = df_sorted[df_sorted["昨日收益"] > 0]
    for _, row in gain_funds.iterrows():
        report += f"""- **{row['基金名称']}**
  - 持有金额：¥{row['持有金额']:,.2f}
  - 昨日收益：📈 +{row['昨日收益']:.2f}元
  - 持有收益：{row['持有收益']:+.2f}元
  - 收益率：{row['持有收益率']}
  - 类型：{row['类型']}

"""
    
    loss_funds = df_sorted[df_sorted["昨日收益"] < 0]
    if len(loss_funds) > 0:
        report += f"""### 🟢 下跌基金 ({loss_count}只)

"""
        for _, row in loss_funds.iterrows():
            report += f"""- **{row['基金名称']}**
  - 持有金额：¥{row['持有金额']:,.2f}
  - 昨日收益：📉 {row['昨日收益']:.2f}元
  - 持有收益：{row['持有收益']:+.2f}元
  - 收益率：{row['持有收益率']}
  - 类型：{row['类型']}

"""
    
    flat_funds = df_sorted[df_sorted["昨日收益"] == 0]
    if len(flat_funds) > 0:
        report += f"""### ➖ 持平基金 ({flat_count}只)

"""
        for _, row in flat_funds.iterrows():
            report += f"""- **{row['基金名称']}**
  - 持有金额：¥{row['持有金额']:,.2f}
  - 昨日收益：➖ 0.00元
  - 持有收益：{row['持有收益']:+.2f}元
  - 收益率：{row['持有收益率']}
  - 类型：{row['类型']}

"""
    
    report += f"""---

## 🌍 全球市场

### 美股隔夜
| 指数 | 收盘 | 涨跌 |
|:---:|:---:|:---:|
| **道琼斯** | {market_data['美股']['道琼斯']['点数']} | {market_data['美股']['道琼斯']['趋势']} {market_data['美股']['道琼斯']['涨跌']} |
| **纳斯达克** | {market_data['美股']['纳斯达克']['点数']} | {market_data['美股']['纳斯达克']['趋势']} {market_data['美股']['纳斯达克']['涨跌']} |
| **标普500** | {market_data['美股']['标普500']['点数']} | {market_data['美股']['标普500']['趋势']} {market_data['美股']['标普500']['涨跌']} |

## 💹 资金流向
| 类型 | 数据 | 趋势 |
|:---:|:---:|:---:|
| **北向资金** | {capital_flow['北向资金']['净流入']} | {capital_flow['北向资金']['趋势']} |
| **主力资金** | {capital_flow['主力资金']['净流入']} | {capital_flow['主力资金']['趋势']} |

## 📰 板块消息
"""

    for sector, info in sector_news.items():
        emoji = "✅" if info["影响"] == "利好" else "⚠️"
        report += f"""- {emoji} **{sector}** ({info['影响']})：{info['消息'][:20]}... 建议{info['建议']}

"""
    
    if analysis["风险提示"]:
        report += f"""---

## ⚠️ 风险提示
"""
        for risk in analysis["风险提示"]:
            report += f"- {risk}\n"
    
    report += f"""

---

## 📌 操作建议
1. **宽基指数**：定投可继续
2. **行业指数**：AI、半导体、创新药可持有
3. **黄金**：短期观望
4. **债券**：持有等待降准

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*⚠️ 本报告仅供参考，不构成投资建议*
"""
    
    return report, total_value, total_yesterday, holding_profit

def main():
    print("=" * 70)
    print("🌅 每日持仓隔夜消息收集 - 专业版 V2.0")
    print("=" * 70)
    print(f"\n运行时间: {datet
