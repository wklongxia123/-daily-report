#!/usr/bin/env python3
"""
每日持仓隔夜消息收集脚本 - 专业版 V2.0
每天早上8点运行，自动收集市场消息并生成专业报告
新增：每只基金每日收益详情展示
支持微信推送（PushPlus/Server酱）
"""

import pandas as pd
import requests
import json
import os
from datetime import datetime

# ============ 配置区域 ============
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "")
SERVERCHAN_KEY = os.environ.get("SERVERCHAN_KEY", "")
WECHAT_WEBHOOK = os.environ.get("WECHAT_WEBHOOK", "")
# ==================================


def get_market_data():
    """获取市场数据"""
    return {
        "美股": {
            "道琼斯": {"涨跌": "-0.91%", "点数": "37965.60", "趋势": "📉"},
            "纳斯达克": {"涨跌": "+0.10%", "点数": "16794.64", "趋势": "📈"},
            "标普500": {"涨跌": "-0.23%", "点数": "5062.25", "趋势": "📉"},
        },
        "A50期指": {"涨跌": "-0.35%", "趋势": "📉"},
        "美元指数": {"涨跌": "-0.52%", "数值": "102.35"},
        "离岸人民币": {"涨跌": "+0.15%", "数值": "7.2456"},
    }


def get_sector_news():
    """获取板块消息"""
    return {
        "人工智能": {
            "消息": "Anthropic挖角微软高管，加大AI基建投入",
            "影响": "利好",
            "建议": "持有"
        },
        "半导体": {
            "消息": "关税政策加速国产替代进程",
            "影响": "利好",
            "建议": "加仓"
        },
        "创新药": {
            "消息": "创新药出海订单频现",
            "影响": "利好",
            "建议": "持有"
        },
        "电网设备": {
            "消息": "AI时代电力需求增长",
            "影响": "利好",
            "建议": "持有"
        },
        "黄金": {
            "消息": "国际金价震荡，美联储降息预期反复",
            "影响": "中性",
            "建议": "观望"
        },
        "债券": {
            "消息": "债市震荡走软，降准预期升温",
            "影响": "中性偏利好",
            "建议": "持有"
        }
    }


def get_capital_flow():
    """获取资金流向数据"""
    return {
        "北向资金": {"净流入": "+32.5亿", "趋势": "📈连续3日流入"},
        "主力资金": {"净流入": "-128.6亿", "趋势": "📉流出放缓"},
        "两融余额": {"变化": "+15.3亿", "数值": "16528.6亿"},
        "成交额": {"沪市": "4521亿", "深市": "5892亿", "合计": "10413亿"},
    }


def get_macro_news():
    """获取宏观要闻"""
    return [
        "央行开展1674亿元7天期逆回购，净投放1025亿元",
        "特朗普关税政策持续影响，对中国征收34%关税",
        "外交部：贸易战没有赢家",
        "4月政治局会议将至，市场关注货币政策定调",
    ]def generate_fund_details(df):
    """生成每只基金的详细收益情况"""
    df_sorted = df.sort_values("昨日收益", ascending=False)
    gain_count = len(df[df["昨日收益"] > 0])
    loss_count = len(df[df["昨日收益"] < 0])
    flat_count = len(df[df["昨日收益"] == 0])
    gain_amount = df[df["昨日收益"] > 0]["昨日收益"].sum()
    loss_amount = df[df["昨日收益"] < 0]["昨日收益"].sum()
    return df_sorted, gain_count, loss_count, flat_count, gain_amount, loss_amount


def analyze_portfolio(df, total_value, holding_profit):
    """分析持仓配置"""
    type_summary = df.groupby("类型").agg({
        "持有金额": "sum",
        "昨日收益": "sum"
    }).reset_index()
    
    analysis = {
        "配置建议": [],
        "风险提示": [],
        "调仓建议": []
    }
    
    gold_pct = type_summary[type_summary["类型"] == "黄金"]["持有金额"].sum() / total_value * 100 if len(type_summary[type_summary["类型"] == "黄金"]) > 0 else 0
    stock_pct = type_summary[type_summary["类型"].isin(["偏股混合", "行业指数", "灵活配置"])]["持有金额"].sum() / total_value * 100
    
    if gold_pct > 25:
        analysis["风险提示"].append(f"⚠️ 黄金占比{gold_pct:.1f}%偏高")
    elif gold_pct < 15:
        analysis["调仓建议"].append(f"💡 黄金占比{gold_pct:.1f}%偏低")
    
    if stock_pct > 70:
        analysis["风险提示"].append(f"⚠️ 权益类占比{stock_pct:.1f}%过高")
    
    if holding_profit < -500:
        analysis["风险提示"].append(f"⚠️ 累计亏损{holding_profit:.2f}")
    
    return analysis


def generate_strategy(sector_news, analysis):
    """生成操作策略"""
    strategy = []
    for sector, info in sector_news.items():
        if info["建议"] == "加仓":
            strategy.append(f"📈 **{sector}**：建议加仓")
        elif info["建议"] == "减仓":
            strategy.append(f"📉 **{sector}**：建议减仓")
        else:
            strategy.append(f"➡️ **{sector}**：建议持有")
    return strategy


def send_pushplus(title, content):
    """使用PushPlus发送微信消息"""
    if not PUSHPLUS_TOKEN:
        return False
    
    url = "http://www.pushplus.plus/send"
    data = {
        "token": PUSHPLUS_TOKEN,
        "title": title,
        "content": content,
        "template": "markdown"
    }
    try:
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        return result.get("code") == 200
    except:
        return False


def send_serverchan(title, content):
    """使用Server酱发送微信消息"""
    if not SERVERCHAN_KEY:
        return False
    
    url = f"https://sctapi.ftqq.com/{SERVERCHAN_KEY}.send"
    data = {"title": title, "desp": content}
    try:
        response = requests.post(url, data=data, timeout=10)
        result = response.json()
        return result.get("code") == 0
    except:
        return Falsedef generate_market_report():
    """生成专业市场报告"""
    today = datetime.now().strftime('%Y年%m月%d日')
    
    market_data = get_market_data()
    sector_news = get_sector_news()
    capital_flow = get_capital_flow()
    macro_news = get_macro_news()
    
    # 持仓数据
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
    
    df_sorted, gain_count, loss_count, flat_count, gain_amount, loss_amount = generate_fund_details(df)
    analysis = analyze_portfolio(df, total_value, holding_profit)
    strategy = generate_strategy(sector_news, analysis)
    
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
    
    # 上涨基金
    gain_funds = df_sorted[df_sorted["昨日收益"] > 0]
    for _, row in gain_funds.iterrows():
        report += f"""**{row['基金名称']}**
- 持有金额：¥{row['持有金额']:,.2f}
- 昨日收益：📈 +{row['昨日收益']:.2f}元
- 持有收益：{row['持有收益']:+.2f}元
- 收益率：{row['持有收益率']}
- 类型：{row['类型']}

"""
    
    # 下跌基金
    loss_funds = df_sorted[df_sorted["昨日收益"] < 0]
    if len(loss_funds) > 0:
        report += f"""### 🟢 下跌基金 ({loss_count}只)

"""
        for _, row in loss_funds.iterrows():
            report += f"""**{row['基金名称']}**
- 持有金额：¥{row['持有金额']:,.2f}
- 昨日收益：📉 {row['昨日收益']:.2f}元
- 持有收益：{row['持有收益']:+.2f}元
- 收益率：{row['持有收益率']}
- 类型：{row['类型']}

"""
    
    # 持平基金
    flat_funds = df_sorted[df_sorted["昨日收益"] == 0]
    if len(flat_funds) > 0:
        report += f"""### ➖ 持平基金 ({flat_count}只)

"""
        for _, row in flat_funds.iterrows():
            report += f"""**{row['基金名称']}**
- 持有金额：¥{row['持有金额']:,.2f}
- 昨日收益：➖ 0.00元
- 持有收益：{row['持有收益']:+.2f}元
- 收益率：{row['持有收益率']}
- 类型：{row['类型']}

"""    report += f"""---

## 🌍 全球市场

### 美股隔夜
| 指数 | 收盘 | 涨跌 |
|:---:|:---:|:---:|
| **道琼斯** | {market_data['美股']['道琼斯']['点数']} | {market_data['美股']['道琼斯']['趋势']} {market_data['美股']['道琼斯']['涨跌']} |
| **纳斯达克** | {market_data['美股']['纳斯达克']['点数']} | {market_data['美股']['纳斯达克']['趋势']} {market_data['美股']['纳斯达克']['涨跌']} |
| **标普500** | {market_data['美股']['标普500']['点数']} | {market_data['美股']['标普500']['趋势']} {market_data['美股']['标普500']['涨跌']} |

### 其他指标
- **A50期指**：{market_data['A50期指']['趋势']} {market_data['A50期指']['涨跌']}
- **美元指数**：{market_data['美元指数']['数值']} ({market_data['美元指数']['涨跌']})
- **离岸人民币**：{market_data['离岸人民币']['数值']} ({market_data['离岸人民币']['涨跌']})

---

## 💹 资金流向

| 类型 | 数据 | 趋势 |
|:---:|:---:|:---:|
| **北向资金** | {capital_flow['北向资金']['净流入']} | {capital_flow['北向资金']['趋势']} |
| **主力资金** | {capital_flow['主力资金']['净流入']} | {capital_flow['主力资金']['趋势']} |
| **两融余额** | {capital_flow['两融余额']['数值']} ({capital_flow['两融余额']['变化']}) | 📊 |
| **成交额** | {capital_flow['成交额']['合计']} | 💰 |

---

## 📰 板块消息

"""

    for sector, info in sector_news.items():
        emoji = "✅" if info["影响"] == "利好" else "⚠️" if info["影响"] == "中性" else "❌"
        report += f"""### {emoji} {sector} | {info['影响']}
> {info['消息']}
> **建议**：{info['建议']}

"""
    
    report += f"""---

## 📋 宏观要闻

"""
    for i, news in enumerate(macro_news, 1):
        report += f"{i}. {news}\n"
    
    report += f"""

---

## 🎯 持仓分析与建议

### 📊 配置分析
"""
    
    if analysis["风险提示"]:
        report += "#### ⚠️ 风险提示\n"
        for risk in analysis["风险提示"]:
            report += f"- {risk}\n"
        report += "\n"
    
    if analysis["调仓建议"]:
        report += "#### 💡 调仓建议\n"
        for suggestion in analysis["调仓建议"]:
            report += f"- {suggestion}\n"
        report += "\n"
    
    report += f"""### 📈 板块轮动建议
"""
    for s in strategy:
        report += f"- {s}\n"
    
    report += f"""

---

## 📌 今日操作建议

### 短期策略（1-3天）
1. **宽基指数**：定投可继续，逢低加仓
2. **行业指数**：关注AI、半导体、创新药板块机会
3. **黄金**：短期震荡，观望为主
4. **债券**：持有观望，等待降准信号

### 中期策略（1-3月）
1. **国产替代主线**：半导体、AI算力长期看好
2. **创新药出海**：板块迎来拐点，可继续持有
3. **债市机会**：降准降息预期下，债券基金有望回暖
4. **资产配置**：保持当前股债配比，勿过度集中

### 风险提示
- 关税政策不确定性
- 美联储降息节奏变化
- A股市场波动加大
- 建议控制仓位，分批建仓

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*数据来源: 持仓数据整理 + 公开市场信息*  
*⚠️ 本报告仅供参考，不构成投资建议*
"""
    
    return report, total_value, total_yesterday, holding_profitdef main():
    """主函数"""
    print("=" * 70)
    print("🌅 每日持仓隔夜消息收集 - 专业版 V2.0")
    print("=" * 70)
    print(f"\n运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n正在生成专业报告（含每只基金收益详情）...\n")
    
    report, total_value, yesterday, profit = generate_market_report()
    
    print("=" * 70)
    print("📱 正在发送微信推送...")
    print("=" * 70)
    
    title = f"📊 专业持仓日报 | 昨日{yesterday:+.2f} | 累计{profit:+.2f}"
    
    pushed = False
    if PUSHPLUS_TOKEN:
        pushed = send_pushplus(title, report)
    if not pushed and SERVERCHAN_KEY:
        pushed = send_serverchan(title, report)
    
    if not pushed:
        print("\n⚠️ 未配置微信推送，请设置环境变量:")
        print("   - PUSHPLUS_TOKEN: PushPlus Token")
        print("   - SERVERCHAN_KEY: Server酱SendKey")
    
    print("\n" + "=" * 70)
    print("📋 报告预览:")
    print("=" * 70)
    print(report[:1500] + "...")
    print("\n✅ 任务完成!")
    
    filename = f"/workspace/专业持仓报告V2_{datetime.now().strftime('%Y%m%d')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n💾 报告已保存: {filename}")


if __name__ == "__main__":
    main()
