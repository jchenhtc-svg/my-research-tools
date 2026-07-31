"""Generates a single self-contained HTML report (no server needed - just
double-click the .html file and it opens in any browser)."""

import html
from datetime import datetime
from typing import Dict

from src.feedback_generator import FeedbackGenerator
from src.models.freestyle_rules import (
    FreestyleIssue,
    SEVERITY_CRITICAL,
    SEVERITY_MODERATE,
    SEVERITY_MINOR,
)

# Below this detection rate, treat the result as low-confidence (too few
# valid frames for the angle/rate statistics to be trustworthy).
LOW_DETECTION_THRESHOLD = 0.7


def _esc(value) -> str:
    return html.escape(str(value))


def _issue_card_html(issue: FreestyleIssue, tone: str) -> str:
    return f"""
    <div class="issue-card {tone}">
      <div class="issue-desc">{_esc(issue.description)}</div>
      <div class="issue-tip"><strong>如何改善：</strong> {_esc(issue.tip)}</div>
    </div>"""


def _metric_cards_html(metrics: Dict) -> str:
    cards = []

    elbow = metrics.get('elbow', {})
    if elbow.get('avg_angle') is not None:
        extra = ""
        if elbow.get('left_avg') is not None and elbow.get('right_avg') is not None:
            extra = f"<div class='metric-sub'>左手：{elbow['left_avg']:.1f}&deg; | 右手：{elbow['right_avg']:.1f}&deg;</div>"
        cards.append(f"""
        <div class="metric-card">
          <div class="metric-label">抓水肘角</div>
          <div class="metric-value">{elbow['avg_angle']:.1f}&deg;</div>
          <div class="metric-optimal">理想範圍：80&ndash;100&deg;</div>
          {extra}
        </div>""")

    rotation = metrics.get('rotation', {})
    if rotation.get('avg_rotation') is not None:
        cards.append(f"""
        <div class="metric-card">
          <div class="metric-label">身體轉肩角度</div>
          <div class="metric-value">{rotation['avg_rotation']:.1f}&deg;</div>
          <div class="metric-optimal">理想範圍：45&ndash;60&deg;</div>
          <div class="metric-sub">範圍：{rotation['min_rotation']:.1f}&deg; &ndash; {rotation['max_rotation']:.1f}&deg;</div>
        </div>""")

    stroke_rate = metrics.get('stroke_rate', {})
    if stroke_rate.get('spm') is not None:
        cards.append(f"""
        <div class="metric-card">
          <div class="metric-label">划頻</div>
          <div class="metric-value">{stroke_rate['spm']:.1f} SPM</div>
          <div class="metric-optimal">理想範圍：50&ndash;60 SPM</div>
          <div class="metric-sub">時長：{stroke_rate['duration']:.1f}秒 | 划水次數：{stroke_rate['total_strokes']}</div>
        </div>""")

    head = metrics.get('head', {})
    if head.get('stability') is not None:
        cards.append(f"""
        <div class="metric-card">
          <div class="metric-label">頭部穩定度</div>
          <div class="metric-value">{head['stability'] * 100:.1f}%</div>
          <div class="metric-optimal">越高越好</div>
        </div>""")

    kick = metrics.get('kick', {})
    if kick.get('avg_knee_angle') is not None:
        cards.append(f"""
        <div class="metric-card">
          <div class="metric-label">踢腿動作（膝關節角度）</div>
          <div class="metric-value">{kick['avg_knee_angle']:.1f}&deg;</div>
          <div class="metric-optimal">應接近170&deg;</div>
        </div>""")

    if metrics.get('valid_frame_ratio') is not None:
        pct = metrics['valid_frame_ratio'] * 100
        cards.append(f"""
        <div class="metric-card">
          <div class="metric-label">偵測品質</div>
          <div class="metric-value">{pct:.1f}%</div>
          <div class="metric-optimal">的影格成功分析</div>
        </div>""")

    return "".join(cards)


def generate_html_report(analysis_results: Dict, video_name: str = "") -> str:
    """
    Build a single self-contained HTML report string.

    Args:
        analysis_results: Results from StrokeAnalyzer.analyze_video()
        video_name: Optional source filename, shown in the header

    Returns:
        Full HTML document as a string (write it to a .html file)
    """
    fg = FeedbackGenerator()
    metrics = analysis_results['metrics']
    issues = analysis_results['issues']

    rating = fg._calculate_overall_rating(issues)
    critical_issues = [i for i in issues if i.severity == SEVERITY_CRITICAL]
    moderate_issues = [i for i in issues if i.severity == SEVERITY_MODERATE]
    minor_issues = [i for i in issues if i.severity == SEVERITY_MINOR]
    insight = fg._generate_quick_insight(rating, critical_issues, moderate_issues)
    strengths = fg._identify_strengths(metrics, issues)

    valid_ratio = metrics.get('valid_frame_ratio')
    low_confidence = valid_ratio is not None and valid_ratio < LOW_DETECTION_THRESHOLD

    warning_html = ""
    if low_confidence:
        pct = valid_ratio * 100
        warning_html = f"""
        <div class="low-confidence-banner">
          &#9888;&#65039; <strong>偵測品質偏低（{pct:.1f}%）</strong>&mdash;
          這支影片成功偵測到姿勢的影格太少，下方的角度/划頻數字可信度不足。
          通常是因為影片太短、選手中途游出鏡頭、或水面反光/能見度不佳。
          請斟酌採信這次的評分，建議重新拍攝一支更長、更清楚的影片
          （涵蓋5&ndash;6次以上完整划水週期，選手全程都在鏡頭內）。
        </div>"""

    action_items = []
    n = 1
    for issue in critical_issues:
        action_items.append((n, "優先修正", "critical", issue))
        n += 1
    for issue in moderate_issues[:2]:
        action_items.append((n, "待加強", "moderate", issue))
        n += 1

    action_html = ""
    if action_items:
        rows = "".join(f"""
        <div class="action-item {tone}">
          <div class="action-badge {tone}">{num}. {label}</div>
          <div class="action-desc">{_esc(issue.description)}</div>
          <div class="action-tip">{_esc(issue.tip)}</div>
        </div>""" for num, label, tone, issue in action_items)
        action_html = f"""
        <div class="card">
          <h2>您的行動計畫</h2>
          <p class="muted">依序專注在這些項目：</p>
          {rows}
        </div>"""

    red_flag_html = ""
    if critical_issues:
        top = critical_issues[0]
        more = f"<p class='muted'>（還有{len(critical_issues) - 1}項其他關鍵問題）</p>" if len(critical_issues) > 1 else ""
        red_flag_html = f"""
        <div class="card red-flag-card">
          <h2>&#128680; 最大警訊</h2>
          {_issue_card_html(top, 'critical')}
          {more}
        </div>"""

    strengths_html = ""
    if strengths:
        items = "".join(f"<li>{_esc(s)}</li>" for s in strengths)
        strengths_html = f"""
        <div class="card">
          <h2>&#9989; 做得好的地方</h2>
          <ul class="strengths-list">{items}</ul>
        </div>"""

    breakdown_sections = []
    if critical_issues:
        breakdown_sections.append(("關鍵問題", 'critical', critical_issues))
    if moderate_issues:
        breakdown_sections.append(("待加強項目", 'moderate', moderate_issues))
    if minor_issues:
        breakdown_sections.append(("次要建議", 'minor', minor_issues))

    breakdown_html = ""
    if breakdown_sections:
        blocks = ""
        for label, tone, group in breakdown_sections:
            cards = "".join(_issue_card_html(i, tone) for i in group)
            blocks += f"<h3 class='breakdown-heading {tone}'>{_esc(label)}</h3>{cards}"
        breakdown_html = f"""
        <details class="card">
          <summary><h2 style="display:inline">完整技術報告</h2></summary>
          {blocks}
        </details>"""

    no_issues_html = ""
    if not issues:
        no_issues_html = """
        <div class="card celebration-card">
          <h2>&#127942; 技術優秀！</h2>
          <p>沒有偵測到重大技術問題，您的自由式姿勢很扎實，繼續保持！</p>
        </div>"""

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    subtitle = f"來源：{_esc(video_name)} &middot; 產生時間 {generated_at}" if video_name else f"產生時間 {generated_at}"

    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>自由式划水分析報告</title>
<style>
  :root {{
    --primary: #667eea;
    --primary-dark: #764ba2;
    --critical: #d32f2f;
    --critical-bg: #fff3f3;
    --moderate: #f57c00;
    --moderate-bg: #fff9e6;
    --minor: #1976d2;
    --minor-bg: #f0f6ff;
    --text: #2d2d2d;
    --muted: #666;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 24px 16px 60px;
    background: #f0f2ff;
    font-family: -apple-system, "Segoe UI", "PingFang TC", "Microsoft JhengHei", Roboto, sans-serif;
    color: var(--text);
  }}
  .container {{ max-width: 820px; margin: 0 auto; }}
  .header {{
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    color: white;
    border-radius: 16px;
    padding: 28px;
    text-align: center;
    box-shadow: 0 8px 24px rgba(102,126,234,0.35);
  }}
  .header h1 {{ margin: 0 0 6px; font-size: 1.7rem; }}
  .header p {{ margin: 0; opacity: 0.9; font-size: 0.95rem; }}
  .score-card {{
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    color: white;
    border-radius: 16px;
    padding: 28px;
    text-align: center;
    margin-top: 20px;
  }}
  .score-circle {{
    width: 140px; height: 140px;
    background: rgba(255,255,255,0.18);
    border-radius: 50%;
    margin: 0 auto 12px;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
  }}
  .score-circle .num {{ font-size: 2.2rem; font-weight: 700; }}
  .low-confidence-banner {{
    background: #fff3cd; border: 2px solid #f0ad4e; color: #7a5200;
    border-radius: 12px; padding: 16px 20px; margin-top: 20px; line-height: 1.6;
  }}
  .card {{
    background: white; border-radius: 16px; padding: 24px;
    margin-top: 20px; box-shadow: 0 4px 16px rgba(0,0,0,0.06);
  }}
  .card h2 {{ margin: 0 0 12px; color: var(--primary-dark); font-size: 1.25rem; }}
  .insight-card {{ background: #eef1ff; border: 2px solid var(--primary); }}
  .red-flag-card {{ border: 2px solid var(--critical); }}
  .muted {{ color: var(--muted); }}
  .issue-card {{
    border-radius: 10px; padding: 14px 16px; margin: 10px 0;
  }}
  .issue-card.critical {{ background: var(--critical-bg); border-left: 4px solid var(--critical); }}
  .issue-card.moderate {{ background: var(--moderate-bg); border-left: 4px solid var(--moderate); }}
  .issue-card.minor {{ background: var(--minor-bg); border-left: 4px solid var(--minor); }}
  .issue-desc {{ font-weight: 600; margin-bottom: 6px; }}
  .issue-tip {{ font-size: 0.92rem; color: var(--muted); }}
  .action-item {{ border-radius: 10px; padding: 14px 16px; margin: 12px 0; }}
  .action-item.critical {{ background: var(--critical-bg); border: 1px solid #f5b5b5; }}
  .action-item.moderate {{ background: var(--moderate-bg); border: 1px solid #f7d38a; }}
  .action-badge {{
    display: inline-block; color: white; font-size: 0.75rem; font-weight: 700;
    padding: 3px 10px; border-radius: 999px; margin-bottom: 8px;
  }}
  .action-badge.critical {{ background: var(--critical); }}
  .action-badge.moderate {{ background: var(--moderate); }}
  .action-desc {{ font-weight: 600; margin-bottom: 4px; }}
  .action-tip {{ font-size: 0.92rem; color: var(--muted); }}
  .strengths-list {{ margin: 0; padding-left: 20px; line-height: 1.8; }}
  .breakdown-heading {{ margin: 18px 0 6px; font-size: 1rem; }}
  .breakdown-heading.critical {{ color: var(--critical); }}
  .breakdown-heading.moderate {{ color: var(--moderate); }}
  .breakdown-heading.minor {{ color: var(--minor); }}
  .celebration-card {{ text-align: center; background: #eafbef; border: 2px solid #4caf50; }}
  summary {{ cursor: pointer; }}
  .metrics-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 14px;
  }}
  .metric-card {{ background: #f8f9ff; border-radius: 10px; padding: 16px; }}
  .metric-label {{ font-size: 0.82rem; color: var(--muted); margin-bottom: 4px; }}
  .metric-value {{ font-size: 1.4rem; font-weight: 700; color: var(--primary-dark); }}
  .metric-optimal {{ font-size: 0.78rem; color: var(--muted); }}
  .metric-sub {{ font-size: 0.82rem; color: var(--muted); margin-top: 4px; }}
  .footer-tip {{
    text-align: center; color: var(--muted); font-size: 0.9rem;
    margin-top: 24px; padding: 16px;
  }}
  @media (prefers-color-scheme: dark) {{
    body {{ background: #1a1a2e; color: #e8e8e8; }}
    .card {{ background: #24243e; }}
    .metric-card {{ background: #1f1f38; }}
    .action-item.critical {{ background: #3a1f1f; }}
    .action-item.moderate {{ background: #3a2f1a; }}
    .issue-card.critical {{ background: #3a1f1f; }}
    .issue-card.moderate {{ background: #3a2f1a; }}
    .issue-card.minor {{ background: #1a2a3a; }}
    .celebration-card {{ background: #1a3a24; }}
    .insight-card {{ background: #262650; }}
  }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>&#127939; 自由式划水分析報告</h1>
    <p>{subtitle}</p>
  </div>

  {warning_html}

  <div class="score-card">
    <div class="score-circle">
      <div class="num">{rating}/10</div>
    </div>
    <div>技術總評分</div>
  </div>

  <div class="card insight-card">
    <h2>快速洞察</h2>
    <p style="margin:0">{_esc(insight)}</p>
  </div>

  {red_flag_html}
  {strengths_html}
  {action_html}
  {no_issues_html}

  <div class="card">
    <h2>您的數據</h2>
    <div class="metrics-grid">
      {_metric_cards_html(metrics)}
    </div>
  </div>

  {breakdown_html}

  <div class="footer-tip">
    &#128161; 一次專注改善一個問題——同時改太多項目反而會拖慢進步速度。
  </div>
</div>
</body>
</html>
"""
