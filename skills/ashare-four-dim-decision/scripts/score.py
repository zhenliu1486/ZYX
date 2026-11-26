#!/usr/bin/env python3
"""四维加权打分器（确定性计算，仅用标准库）。

用法：
  python3 score.py --tech 71 --flow 68 --theme 74 --sent 62 --trend up
  python3 score.py --tech 45 --flow 30 --theme 20 --sent 25 --trend down --index-broken
  python3 score.py --tech 80 --flow 70 --theme 85 --sent 78 --trend range --json
"""

import argparse
import json

WEIGHTS = {
    "trend":         {"tech": 0.40, "flow": 0.30, "theme": 0.15, "sent": 0.15},
    "range":         {"tech": 0.35, "flow": 0.30, "theme": 0.20, "sent": 0.15},
    "theme_hot":     {"tech": 0.20, "flow": 0.25, "theme": 0.40, "sent": 0.15},
    "ebb":           {"tech": 0.30, "flow": 0.40, "theme": 0.10, "sent": 0.20},
    "risk_off":      {"tech": 0.00, "flow": 0.00, "theme": 0.00, "sent": 0.00},
}

STATE_CN = {
    "trend": "单边趋势",
    "range": "震荡结构",
    "theme_hot": "题材亢奋",
    "ebb": "退潮冰点",
    "risk_off": "系统性风险（一票否决）",
}

# 综合分 -> (仓位上限%, 动作)
LADDER = [
    (80, "主攻", 70),
    (75, "进攻", 55),
    (70, "进攻偏谨慎", 45),
    (65, "试探", 35),
    (60, "观察性试仓", 25),
    (55, "极小仓观察", 15),
    (0,  "空仓等待", 0),
]


def detect_state(trend, sent, theme, index_broken, index_amp):
    if index_broken:
        return "risk_off", "指数破位一票否决"
    if trend == "down":
        return "risk_off", "指数趋势向下（破 MA60 或放量长阴）"
    if sent >= 75 and theme >= 70:
        return "theme_hot", "情绪亢奋 + 风口强"
    if sent <= 30:
        return "ebb", "情绪冰点"
    if trend == "up":
        return "trend", "指数 MA20 上方且 MA20 上行"
    return "range", "指数横盘 / 上下穿梭 MA20"


def consistency(scores):
    vals = [scores["tech"], scores["flow"], scores["theme"], scores["sent"]]
    low = [k for k in scores if scores[k] < 40]
    high = [k for k in scores if scores[k] >= 60]
    spread = max(vals) - min(vals)
    m = 1.0
    notes = []
    if len(low) >= 2:
        m *= 0.75
        notes.append("两个及以上维度低于 40，短板严重，整体降一档")
    elif len(low) == 1:
        m *= 0.85
        notes.append(f"存在短板维度：{low[0]} < 40，整体打 0.85 折")
    if spread > 35:
        m *= 0.90
        notes.append(f"四维分歧过大（极差 {spread:.0f}），打 0.90 折")
    if len(high) == 4:
        notes.append("四维共振（全部 ≥60），不打折")
    return m, notes


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--tech", type=float, required=True)
    p.add_argument("--flow", type=float, required=True)
    p.add_argument("--theme", type=float, required=True)
    p.add_argument("--sent", type=float, required=True)
    p.add_argument("--trend", choices=["up", "range", "down"], default="range")
    p.add_argument("--index-amp", type=float, default=1.5, help="指数日均振幅百分数")
    p.add_argument("--index-broken", action="store_true")
    p.add_argument("--state", choices=list(WEIGHTS.keys()), default=None)
    p.add_argument("--json", action="store_true")
    p.add_argument("--locked-limit-up", action="store_true",
                   help="闸门6：候选标的前一交易日为一字板（开=高=低=收=涨停价、换手<2%%），本轮作废")
    p.add_argument("--event-driven", action="store_true",
                   help="闸门7：候选标的处于摘帽/复牌/异常波动/近5日两次以上龙虎榜期间，仓位上限 10%%")
    a = p.parse_args()

    scores = {"tech": a.tech, "flow": a.flow, "theme": a.theme, "sent": a.sent}
    for k, v in scores.items():
        if not 0 <= v <= 100:
            raise SystemExit(f"{k} 必须在 0-100")

    state = a.state or detect_state(a.trend, a.sent, a.theme, a.index_broken, a.index_amp)[0]
    reason = detect_state(a.trend, a.sent, a.theme, a.index_broken, a.index_amp)[1] if not a.state else "手动指定"
    w = WEIGHTS[state]

    raw = sum(w[k] * scores[k] for k in scores) if state != "risk_off" else 0.0
    mult, notes = (1.0, ["一票否决：不进入打分"]) if state == "risk_off" else consistency(scores)
    final = round(raw * mult, 1)

    action, cap = "空仓等待", 0
    for th, act, pos in LADDER:
        if final >= th:
            action, cap = act, pos
            break

    gate_notes = []
    if a.event_driven:
        cap = min(cap, 10)
        action = action + "（事件驱动，仓位上限 10%）"
        gate_notes.append("闸门7 事件驱动：仓位上限 10%；1000 元级资金等同不参与")
    if a.locked_limit_up:
        action, cap = "标的本轮作废（前一日一字板，不可买）", 0
        gate_notes.append("闸门6 可买性：一字板买不到，移出本轮候选池，不给买点")

    out = {
        "state": STATE_CN[state],
        "state_key": state,
        "state_reason": reason,
        "scores": scores,
        "weights": {k: f"{v:.0%}" for k, v in w.items()},
        "weighted_raw": round(raw, 1),
        "consistency_multiplier": mult,
        "consistency_notes": notes,
        "final_score": final,
        "action": action,
        "position_cap_pct": cap,
        "gate_notes": gate_notes,
    }

    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    print(f"市场状态：{out['state']}（{reason}）")
    print("权重：技术 {tech} ｜ 资金 {flow} ｜ 风口 {theme} ｜ 情绪 {sent}".format(**out["weights"]))
    print(f"四维分：技术 {scores['tech']:.0f} ｜ 资金 {scores['flow']:.0f} ｜ 风口 {scores['theme']:.0f} ｜ 情绪 {scores['sent']:.0f}")
    print(f"加权原始分：{out['weighted_raw']}｜一致性系数：{mult}")
    for n in notes:
        print(f"  - {n}")
    print(f"综合分 S = {final}")
    print(f"结论：{action}｜总仓位上限 {cap}%")
    for g in gate_notes:
        print(f"  ⚠ {g}")
    print("单票上限 20%，同题材合计上限 40%（与总仓位上限取小）")


if __name__ == "__main__":
    main()
