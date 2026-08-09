"""Generates human-readable feedback reports from analysis results."""

from typing import Dict, List
from src.models.freestyle_rules import (
    FreestyleIssue,
    get_severity_emoji,
    get_severity_label,
    SEVERITY_CRITICAL,
    SEVERITY_MODERATE,
    SEVERITY_MINOR,
    get_thresholds,
    DEFAULT_PROFILE,
    PROFILE_LABELS,
    VIEW_SIDE,
    VIEW_LABELS,
    METRIC_LABELS,
)


class FeedbackGenerator:
    """Generates structured feedback reports for swimmers."""

    def generate_report(self, analysis_results: Dict) -> str:
        """
        Generate comprehensive text report.

        Args:
            analysis_results: Results from stroke analyzer

        Returns:
            Formatted text report
        """
        metrics = analysis_results['metrics']
        issues = analysis_results['issues']

        report = []

        # Overall rating
        rating = self._calculate_overall_rating(issues)

        # Group issues by severity
        critical_issues = [i for i in issues if i.severity == SEVERITY_CRITICAL]
        moderate_issues = [i for i in issues if i.severity == SEVERITY_MODERATE]
        minor_issues = [i for i in issues if i.severity == SEVERITY_MINOR]

        # ====== HEADER WITH SCORE ======
        measured, total = self._coverage(metrics)
        report.append("🏊‍♂️ 您的游泳分析")
        report.append("")
        report.append(f"技術總評分：{rating}/10")
        if measured < total:
            # 沒量到的項目不會扣分，分數因此偏高。不講清楚的話，
            # 使用者會把「沒量到」誤讀成「沒問題」。
            report.append(f"（本次只量測到 {measured}/{total} 項指標，"
                          f"未量測的項目不列入評分，分數僅供參考）")
        report.append("")

        # ====== QUICK INSIGHT (THE HOOK) ======
        insight = self._generate_quick_insight(rating, critical_issues, moderate_issues,
                                               measured, total)
        report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        report.append("📊 快速洞察")
        report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        report.append(insight)
        report.append("")

        # ====== BIGGEST RED FLAG (if any) ======
        if critical_issues:
            report.append("🚨 最大警訊")
            report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            top_issue = critical_issues[0]
            report.append(f"⚠️  {top_issue.description}")
            report.append("")
            report.append(f"💡 如何改善：")
            report.append(f"   {top_issue.tip}")
            report.append("")
            if len(critical_issues) > 1:
                report.append(f"   （還有{len(critical_issues) - 1}項其他關鍵問題）")
            report.append("")

        # ====== WHAT'S WORKING ======
        strengths = self._identify_strengths(metrics, issues)
        if strengths:
            report.append("✅ 做得好的地方")
            report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            for strength in strengths:
                report.append(f"• {strength}")
            report.append("")

        # ====== ACTION PLAN ======
        if critical_issues or moderate_issues:
            report.append("🎯 您的行動計畫")
            report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            report.append("依序專注在這些項目：")
            report.append("")

            # Add critical issues
            for i, issue in enumerate(critical_issues, 1):
                report.append(f"{i}. 🚨 優先修正：{issue.description}")
                report.append(f"   → {issue.tip}")
                report.append("")

            # Add top moderate issues
            start_num = len(critical_issues) + 1
            for i, issue in enumerate(moderate_issues[:2], start_num):  # Only top 2 moderate
                report.append(f"{i}. ⚠️ 待加強：{issue.description}")
                report.append(f"   → {issue.tip}")
                report.append("")

        # ====== DETAILED BREAKDOWN (Collapsed by default in UI) ======
        if critical_issues or moderate_issues or minor_issues:
            report.append("📋 詳細分析")
            report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

            # Critical issues
            if critical_issues:
                report.append(f"{get_severity_emoji(SEVERITY_CRITICAL)} {get_severity_label(SEVERITY_CRITICAL)}:")
                for issue in critical_issues:
                    report.append(f"  • {issue.description}")
                    report.append(f"    → {issue.tip}")
                report.append("")

            # Moderate issues
            if moderate_issues:
                report.append(f"{get_severity_emoji(SEVERITY_MODERATE)} {get_severity_label(SEVERITY_MODERATE)}:")
                for issue in moderate_issues:
                    report.append(f"  • {issue.description}")
                    report.append(f"    → {issue.tip}")
                report.append("")

            # Minor issues
            if minor_issues:
                report.append(f"{get_severity_emoji(SEVERITY_MINOR)} {get_severity_label(SEVERITY_MINOR)}:")
                for issue in minor_issues:
                    report.append(f"  • {issue.description}")
                    report.append(f"    → {issue.tip}")
                report.append("")

        # ====== METRICS ======
        report.append("📊 您的數據")
        report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        report.append(self._format_metrics(metrics))
        report.append("")

        # ====== NO ISSUES CELEBRATION ======
        if not issues:
            report.append("🏆 本次未發現問題")
            report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            if measured < total:
                report.append(f"已量測的 {measured} 項指標都沒有問題。")
                report.append(f"但有 {total - measured} 項這個視角量不到（見上方數據區），")
                report.append("補拍另一個角度才能確認整體技術。")
            else:
                report.append("六項指標全數通過，自由式姿勢很扎實。")
                report.append("繼續保持這個水準！")
            report.append("")

        # ====== FOOTER WITH TIP ======
        report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        report.append("💡 小提醒：一次專注改善一個問題。")
        report.append("   同時改太多項目反而會拖慢進步速度！")
        report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        return "\n".join(report)

    def generate_summary(self, analysis_results: Dict) -> str:
        """
        Generate brief summary.

        Args:
            analysis_results: Results from stroke analyzer

        Returns:
            Brief text summary
        """
        issues = analysis_results['issues']
        rating = self._calculate_overall_rating(issues)

        critical_count = len([i for i in issues if i.severity == SEVERITY_CRITICAL])
        moderate_count = len([i for i in issues if i.severity == SEVERITY_MODERATE])

        summary = [
            f"評分：{rating}/10",
            f"關鍵問題：{critical_count}項",
            f"待加強項目：{moderate_count}項"
        ]

        return " | ".join(summary)

    def _calculate_overall_rating(self, issues: List[FreestyleIssue]) -> int:
        """
        Calculate overall technique rating (1-10).

        Args:
            issues: List of detected issues

        Returns:
            Rating from 1-10
        """
        # Start with perfect score
        score = 10

        # Deduct points based on severity
        for issue in issues:
            if issue.severity == SEVERITY_CRITICAL:
                score -= 2
            elif issue.severity == SEVERITY_MODERATE:
                score -= 1
            elif issue.severity == SEVERITY_MINOR:
                score -= 0.5

        return max(1, min(10, int(round(score))))

    @staticmethod
    def _coverage(metrics: Dict) -> tuple:
        """回傳 (實際量到的指標數, 指標總數)。

        視角不對而跳過的指標不會產生問題、也就不會扣分，
        評分因此偏高。呼叫端要據此提醒使用者。
        """
        names = ('elbow', 'rotation', 'entry', 'head', 'stroke_rate', 'kick')
        measured = sum(1 for n in names if metrics.get(n, {}).get('available'))
        return measured, len(names)

    def _generate_quick_insight(self, rating: int, critical_issues: List, moderate_issues: List,
                                measured: int = 6, total: int = 6) -> str:
        """一句話講重點。

        高分時要看涵蓋率：只量到一半指標卻說「技術優秀」是誤導，
        因為沒量到的那些可能正是問題所在。
        """
        from src.models.freestyle_rules import ISSUE_TYPES

        def issue_name(issue):
            return ISSUE_TYPES.get(issue.issue_type, {}).get('name', issue.issue_type)

        partial = measured < total

        if rating >= 9:
            if partial:
                return (f"👍 已量測的 {measured} 項指標都在理想範圍內。"
                        f"但還有 {total - measured} 項因拍攝視角不足沒量到，"
                        f"補拍另一個角度才能看到完整狀況。")
            return "🏆 六項指標全數落在理想範圍，技術相當扎實！維持這個狀態，專注在穩定性上。"
        elif rating >= 7:
            if critical_issues:
                return f"💪 基礎很扎實，但「{issue_name(critical_issues[0])}」正在拖慢您的速度/效率。修正這點會有明顯進步！"
            else:
                return "👍 整體技術不錯！稍微調整幾個地方就能更接近職業水準。"
        elif rating >= 5:
            if critical_issues:
                return f"⚠️  您最大的問題是：「{issue_name(critical_issues[0])}」。這是最耗費體力、拖慢速度的原因，優先處理這項！"
            else:
                return "🔧 有幾個地方需要加強，但都是可以改善的！請照下面的行動計畫執行。"
        else:
            if critical_issues:
                return f"🚨 警訊：「{issue_name(critical_issues[0])}」正嚴重影響您的游泳表現，讓我們一步一步修正！"
            else:
                return "📚 您才剛起步！照著行動計畫執行，很快就能看到進步。"

    def _identify_strengths(self, metrics: Dict, issues: List[FreestyleIssue]) -> List[str]:
        """找出做得好的地方。只看視角允許、且真的算出值的指標。"""
        strengths = []
        th = get_thresholds(metrics.get('profile', DEFAULT_PROFILE))

        def ok(name):
            d = metrics.get(name, {})
            return d if d.get('available') else {}

        e = ok('elbow')
        if e.get('catch_angle') is not None:
            if th['elbow_optimal_min'] <= e['catch_angle'] <= th['elbow_optimal_max']:
                strengths.append("抓水肘角掌握得很好——有正確運用背闊肌發力！")
        if e.get('asymmetry') is not None and e['asymmetry'] < 8:
            strengths.append(f"左右手抓水角度對稱（差 {e['asymmetry']:.0f}°）——動作很平均！")

        r = ok('rotation')
        if r.get('avg_rotation') is not None:
            if th['rotation_optimal_min'] <= r['avg_rotation'] <= th['rotation_optimal_max']:
                strengths.append("身體滾轉幅度很棒——核心運用得很有效率！")

        h = ok('head')
        if h.get('lift_ratio') is not None and h['lift_ratio'] <= th['head_lift'] * 0.6:
            strengths.append("換氣時頭部很穩定——沒有多餘的抬頭動作！")

        s = ok('stroke_rate')
        if s.get('spm') is not None:
            if th['stroke_rate_min'] <= s['spm'] <= th['stroke_rate_max']:
                strengths.append("划頻在此族群的參考範圍內——節奏感很好！")

        k = ok('kick')
        if k.get('peak_flexion') is not None and k['peak_flexion'] >= th['knee_optimal'] - 10:
            strengths.append("踢腿時膝蓋保持得很直——是從髖部發力的正確打水！")

        if not strengths and len(issues) <= 2:
            strengths.append("整支影片的動作維持得很一致！")

        return strengths

    def _format_metrics(self, metrics: Dict) -> str:
        """列出各項數據。視角量不到的指標會明講原因，而不是靜靜消失。"""
        profile = metrics.get('profile', DEFAULT_PROFILE)
        view = metrics.get('view', VIEW_SIDE)
        th = get_thresholds(profile)
        lines = []

        lines.append(f"拍攝視角：{VIEW_LABELS.get(view, view)}"
                     f" ｜ 對照族群：{PROFILE_LABELS.get(profile, profile)}")
        if metrics.get('cycle_count') is not None:
            lines.append(f"偵測到劃臂週期：{metrics['cycle_count']} 個")
        lines.append("")

        unavailable = []

        def emit(name, render):
            d = metrics.get(name, {})
            if not d.get('available'):
                if d.get('reason'):
                    unavailable.append(f"   • {METRIC_LABELS.get(name, name)}：{d['reason']}")
                return
            render(d)

        def elbow(d):
            if d.get('catch_angle') is None:
                return
            lines.append("🔸 抓水肘角（水下期最大屈曲）：")
            lines.append(f"   {d['catch_angle']:.1f}°"
                         f"（理想 {th['elbow_optimal_min']}-{th['elbow_optimal_max']}°）")
            if d.get('left_avg') and d.get('right_avg'):
                lines.append(f"   左手 {d['left_avg']:.1f}° ｜ 右手 {d['right_avg']:.1f}°")
            lines.append(f"   採計 {d.get('cycles_used', 0)} 個週期")
            lines.append("")

        def rotation(d):
            if d.get('avg_rotation') is None:
                return
            lines.append("🔸 身體滾轉角度：")
            lines.append(f"   平均 {d['avg_rotation']:.1f}°"
                         f"（理想 {th['rotation_optimal_min']}-{th['rotation_optimal_max']}°）")
            if d.get('peak_rotation') is not None:
                lines.append(f"   最大 {d['peak_rotation']:.1f}°")
            lines.append("   註：以全片最平的姿勢為基準推估，若全程都沒趴平會低估")
            lines.append("")

        def entry(d):
            if d.get('max_crossing') is None:
                return
            v = d['max_crossing']
            lines.append("🔸 入水點左右偏移（以肩寬為單位）：")
            if v < 0:
                lines.append(f"   越過中線 {abs(v)*100:.0f}%"
                             f"（容許 {abs(th['entry_crossing'])*100:.0f}%）")
            else:
                lines.append(f"   維持在身體外側 {v*100:.0f}%，沒有越線")
            lines.append("")

        def stroke_rate(d):
            if d.get('spm') is None:
                if d.get('note'):
                    lines.append(f"🔸 划頻：無法估計（{d['note']}）")
                    lines.append("")
                return
            lines.append("🔸 划頻：")
            lines.append(f"   每分鐘 {d['spm']:.0f} 次划手"
                         f"（此族群參考 {th['stroke_rate_min']}-{th['stroke_rate_max']}）")
            lines.append(f"   = 每分鐘 {d['cycles_per_min']:.1f} 個完整週期"
                         f" ｜ 分析時長 {d['duration']:.1f} 秒")
            lines.append("")

        def head(d):
            if d.get('lift_ratio') is None:
                return
            lines.append("🔸 換氣抬頭幅度：")
            lines.append(f"   垂直位移為軀幹長的 {d['lift_ratio']*100:.0f}%"
                         f"（建議低於 {th['head_lift']*100:.0f}%）")
            lines.append("")

        def kick(d):
            if d.get('peak_flexion') is None:
                return
            lines.append("🔸 踢腿膝關節角度：")
            lines.append(f"   最大屈曲 {d['peak_flexion']:.1f}°"
                         f"（建議不低於 {th['knee_excessive_bend']}°，180°=完全打直）")
            if d.get('median_angle') is not None:
                lines.append(f"   中位數 {d['median_angle']:.1f}°")
            lines.append("")

        emit('elbow', elbow)
        emit('rotation', rotation)
        emit('entry', entry)
        emit('stroke_rate', stroke_rate)
        emit('head', head)
        emit('kick', kick)

        if unavailable:
            lines.append("⛔ 這個視角量不到的項目：")
            lines.extend(unavailable)
            lines.append("")

        if metrics.get('valid_frame_ratio') is not None:
            lines.append(f"🔸 偵測品質：{metrics['valid_frame_ratio']*100:.1f}% 的影格成功分析")

        return "\n".join(lines)
