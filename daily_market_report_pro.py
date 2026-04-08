#!/usr/bin/env python3
"""
每日持仓报告 - V2.0 简化版
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
        data = {
            "token": PUSHPLUS_TOKEN,
            "title": title,
            "content": content,
            "template": "markdown"
        }
        response = requests.post(url, json=data, timeout=10)
        return response.json().get("code") == 200
    except:
        return False

def generate_report():
    today = datetime.now().strftime('%Y年%m月%d日')
    
    # 持仓数据
    holdings = [
        {"基金名称": "京东黄金·积存金", "持有金额": 5643.36, "昨日收益": 0.00, "持有收益": -356.58, "类型": "黄金"},
        {"基金名称": "国金中证A500指数增强C", "持有金额": 4235.63, "昨日收益": -4.69, "持有收益": -14.37, "类型": "宽基指数"},
        {"基金名称": "博道沪深300指数增强C", "持有金额": 3851.78, "昨日收益": 4.04, "持有收益": -148.22, "类型": "宽基指数"},
        {"基金名称": "东方阿尔法瑞享混合C", "持有金额": 3198.28, "昨日收益": -17.32, "持有收益": 183.13, "类型": "偏股混合"},
        {"基金名称": "永赢双利债券C", "持有金额": 2941.31, "昨日收益": 13.94, "持有收益": -58.69, "类型": "债券型"},
        {"基金名称": "民生加银增强收益债券C", "持有金额": 2779.32, "昨日收益": 17.74, "持有收益": -220.68, "类型": "债券型"},
        {"基金名称": "天弘沪深港创新药50ETF联接C", "持有金额": 2419.81, "昨日收益": -6.88, "持有收益": -80.19, "类型": "行业指数"},
        {"基金名称": "景顺长城中证沪港深红利成长", "持有金额": 1975.54, "昨日收益": -9.41, "持有收益": -24.46, "类型": "宽基指数"},
        {"基金名称": "中欧红利优享灵活配置混合C", "持有金额": 1907.84, "昨日收益": -3.41, "持有收益": -92.16, "类型": "灵活配置"},
        {"基金名称": "天弘中证电网设备主题指数C", "持有金额": 1498.19, "昨日收益": -10.91, "持有收益": -101.81, "类型": "行业指数"},
        {"基金名称": "国泰黄金ETF联接C", "持有金额": 1353.70, "昨日收益": -8.26, "持有收益": 139.81, "类型": "黄金"},
        {"基金名称": "嘉实低碳精选混合C", "持有金额": 944.20, "昨日收益": -2.79, "持有收益": -55.80, "类型": "偏股混合"},
        {"基金名称": "永赢资源慧选混合C", "持有金额": 879.51, "昨日收益": 18.30, "持有收益": 2.88, "类型": "偏股混合"},
        {"基金名称": "天弘中证人工智能主题指数C", "持有金额": 755.71, "昨日收益": 7.56, "持有收益": -44.29, "类型": "行业指数"},
        {"基金名称": "天弘半导体材料设备指数C", "持有金额": 732.29, "昨日收益": 3.55, "持有收益": -67.71, "类型": "行业指数"},
        {"基金名称": "博时黄金(ETF)I", "持有金额": 68.36, "昨日收益": -0.43, "持有收益": 68.36, "类型": "黄金"},
    ]
    
    df = pd.DataFrame(holdings)
    total_value = df["持有金额"].sum()
    total_yesterday = df["昨日收益"].sum()
    holding_profit = df["持有收益"].sum()
    
    # 统计涨跌
    gain_funds = df[df["昨日收益"] > 0].sort_values("昨日收益", ascending=False)
    loss_funds = df[df["昨日收益"] < 0].sort_values("昨日收益", ascending=True)
    flat_funds = df[df["昨日收益"] == 0]
    
    # 生成报告
    report = f"""# 📊 每日持仓报告 | {today}

## 💰 持仓概览
- **总资产**：¥{total_value:,.2f}
- **昨日收益**：{total_yesterday:+.2f}元
- **累计收益**：{holding_profit:+.2f}元
- **涨跌统计**：📈{len(gain_funds)}只 / 📉{len(loss_funds)}只 / ➖{len(flat_funds)}只

---

## 📋 每只基金每日收益详情

### 🔴 上涨基金 ({len(gain_funds)}只)
"""
    
    for _, row in gain_funds.iterrows():
        report += f"""- **{row['基金名称']}**
  - 持有金额：¥{row['持有金额']:,.2f}
  - 昨日收益：📈 +{row['昨日收益']:.2f}元
  - 持有收益：{row['持有收益']:+.2f}元
  - 类型：{row['类型']}

"""
    
    if len(loss_funds) > 0:
        report += f"""### 🟢 下跌基金 ({len(loss_funds)}只)
"""
        for _, row in loss_funds.iterrows():
            report += f"""- **{row['基金名称']}**
  - 持有金额：¥{row['持有金额']:,.2f}
  - 昨日收益：📉 {row['昨日收益']:.2f}元
  - 持有收益：{row['持有收益']:+.2f}元
  - 类型：{row['类型']}

"""
    
    report += """---

## 🌍 市场关注
- **美股**：道琼斯 📉-0.91% / 纳斯达克 📈+0.10%
- **北向资金**：+32.5亿 📈连续流入
- **主力资金**：-128.6亿

## 💡 操作建议
1. 宽基指数：定投可继续
2. 行业指数：AI、半导体、创新药可持有
3. 黄金：短期观望
4. 债券：持有等待降准

---

*报告生成时间：""" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """*
"""
    
    return report, total_yesterday, holding_profit

def main():
    print("开始生成报告...")
    report, yesterday, profit = generate_report()
    
    title = f"📊 持仓日报 | 昨日{yesterday:+.2f} | 累计{profit:+.2f}"
    
    if send_pushplus(title, report):
        print("✅ 微信推送成功！")
    else:
        print("⚠️ 推送失败，请检查Token配置")
    
    print("\n报告内容预览：")
    print(report[:500] + "...")

if __name__ == "__main__":
    main()
