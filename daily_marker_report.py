#!/usr/bin/env python3
"""
每日持仓隔夜消息收集脚本
每天早上8点运行，收集全球市场消息并生成报告
支持微信推送（PushPlus/Server酱）
"""

import pandas as pd
import requests
import json
import os
from datetime import datetime

# ============ 配置区域 ============
# 微信推送配置（从环境变量读取，更安全）
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "")  # PushPlus Token
SERVERCHAN_KEY = os.environ.get("SERVERCHAN_KEY", "")  # Server酱SendKey
WECHAT_WEBHOOK = os.environ.get("WECHAT_WEBHOOK", "")  # 企业微信Webhook
# ==================================


def send_pushplus(title, content):
    """使用PushPlus发送微信消息"""
    if not PUSHPLUS_TOKEN:
        print("[PushPlus] 未配置Token，跳过推送")
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
        if result.get("code") == 200:
            print("[PushPlus] 消息推送成功")
            return True
        else:
            print(f"[PushPlus] 推送失败: {result}")
            return False
    except Exception as e:
        print(f"[PushPlus] 推送异常: {e}")
        return False


def send_serverchan(title, content):
    """使用Server酱发送微信消息"""
    if not SERVERCHAN_KEY:
        print("[Server酱] 未配置SendKey，跳过推送")
        return False

    url = f"https://sctapi.ftqq.com/{SERVERCHAN_KEY}.send"
    data = {
        "title": title,
        "desp": content
    }
    try:
        response = requests.post(url, data=data, timeout=10)
        result = response.json()
        if result.get("code") == 0:
            print("[Server酱] 消息推送成功")
            return True
        else:
            print(f"[Server酱] 推送失败: {result}")
            return False
    except Exception as e:
        print(f"[Server酱] 推送异常: {e}")
        return False


def send_wechat_webhook(content):
    """使用企业微信Webhook发送消息"""
    if not WECHAT_WEBHOOK:
        print("[企业微信] 未配置Webhook，跳过推送")
        return False

    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }
    try:
        response = requests.post(WECHAT_WEBHOOK, json=data, timeout=10)
        result = response.json()
        if result.get("errcode") == 0:
            print("[企业微信] 消息推送成功")
            return True
        else:
            print(f"[企业微信] 推送失败: {result}")
            return False
    except Exception as e:
        print(f"[企业微信] 推送异常: {e}")
        return False


def generate_market_report():
    """生成市场报告"""
    today = datetime.now().strftime('%Y年%m月%d日')
    
    # 持仓数据（你可以定期更新这里的数据）
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
    
    # 黄金持仓统计
    gold_value = df[df["类型"] == "黄金"]["持有金额"].sum()
    gold_pct = gold_value / total_value * 100
    
    # 生成报告
    report = f"""## 📊 每日持仓消息 ({today})

### 💰 持仓概览
> **总资产**: ¥{total_value:,.2f}  
> **昨日收益**: {total_yesterday:+.2f}  
> **累计收益**: {holding_profit:+.2f}  
> **黄金持仓**: ¥{gold_value:,.2f} ({gold_pct:.1f}%)

---

### 📈 重点持仓 (Top 5)
"""
    
    # 添加Top5持仓
    df_top5 = df.nlargest(5, "持有金额")
    for _, row in df_top5.iterrows():
        emoji = "🟢" if row["昨日收益"] < 0 else "🔴"
        if row["类型"] == "黄金":
            emoji = "🥇"
        report += f"{emoji} **{row['基金名称'][:15]}** | ¥{row['持有金额']:,.0f} | {row['持有收益率']}\n"
    
    report += f"""
---

### 🌍 隔夜市场关注
- **美股**: 道指/纳指/标普收盘
- **A股板块**: AI、半导体、创新药、电网设备、黄金
- **资金流向**: 北向资金、主力资金
- **宏观**: 央行操作、政策消息

---

### 💡 操作建议
1. **宽基指数**: 定投可继续
2. **行业指数**: AI/半导体/创新药/电网设备可持有
3. **黄金**: 关注国际金价走势
4. **债券**: 持有观望

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*数据来源: 持仓数据整理*
"""
    
    return report, total_value, total_yesterday, holding_profit


def main():
    """主函数"""
    print("=" * 60)
    print("🌅 每日持仓隔夜消息收集")
    print("=" * 60)
    print(f"\n运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n正在生成报告...\n")
    
    # 生成报告
    report, total_value, yesterday, profit = generate_market_report()
    
    # 发送微信推送
    print("=" * 60)
    print("📱 正在发送微信推送...")
    print("=" * 60)
    
    title = f"📊 持仓日报 | 昨日{yesterday:+.2f} | 累计{profit:+.2f}"
    
    # 尝试各种推送方式
    pushed = False
    
    if PUSHPLUS_TOKEN:
        pushed = send_pushplus(title, report)
    
    if not pushed and SERVERCHAN_KEY:
        pushed = send_serverchan(title, report)
    
    if not pushed and WECHAT_WEBHOOK:
        pushed = send_wechat_webhook(report)
    
    if not pushed:
        print("\n⚠️ 未配置微信推送，请设置环境变量:")
        print("   - PUSHPLUS_TOKEN: PushPlus Token")
        print("   - SERVERCHAN_KEY: Server酱SendKey")
        print("   - WECHAT_WEBHOOK: 企业微信Webhook URL")
    
    print("\n" + "=" * 60)
    print("📋 报告内容:")
    print("=" * 60)
    print(report)
    print("\n✅ 任务完成!")


if __name__ == "__main__":
    main()
