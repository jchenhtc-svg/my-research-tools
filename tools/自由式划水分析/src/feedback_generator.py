"""Generates human-readable feedback reports from analysis results."""

from typing import Dict, List
from src.models.freestyle_rules import (
    FreestyleIssue,
    get_severity_emoji,
    get_severity_label,
    SEVERITY_CRITICAL,
    SEVERITY_MODERATE,
    SEVERITY_MINOR
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
        report.append("🏊‍♂️ 您的游泳分析")
        report.append("")
        report.append(f"技術總評分：{rating}/10")
        report.append("")

        # ====== QUICK INSIGHT (THE HOOK) ======
        insight = self._generate_quick_insight(rating, critical_issues, moderate_issues)
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
            report.append("🏆 技術優秀！")
            report.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            report.append("沒有偵測到重大技術問題！您的自由式姿勢很扎實。")
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

    def _generate_quick_insight(self, rating: int, critical_issues: List, moderate_issues: List) -> str:
        """Generate a quick, shareable insight about the swim."""
        from src.models.freestyle_rules import ISSUE_TYPES

        def issue_name(issue):
            return ISSUE_TYPES.get(issue.issue_type, {}).get('name', issue.issue_type)

        if rating >= 9:
            return "🏆 您的技術已達奧運等級！維持這個姿勢，專注在穩定性上。"
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
        """Identify what the swimmer is doing well."""
        strengths = []

        # Check elbow angle
        if metrics.get('elbow', {}).get('avg_angle'):
            angle = metrics['elbow']['avg_angle']
            if 80 <= angle <= 100:
                strengths.append("抓水肘角掌握得很好——有正確運用背闊肌發力！")

        # Check body rotation
        if metrics.get('rotation', {}).get('avg_rotation'):
            rotation = metrics['rotation']['avg_rotation']
            if 45 <= rotation <= 60:
                strengths.append("身體轉肩幅度很棒——核心運用得很有效率！")

        # Check head stability
        if metrics.get('head', {}).get('stability'):
            stability = metrics['head']['stability']
            if stability > 0.8:
                strengths.append("頭部位置很穩定——身體對齊維持得不錯！")

        # Check stroke rate
        if metrics.get('stroke_rate', {}).get('spm'):
            spm = metrics['stroke_rate']['spm']
            if 50 <= spm <= 60:
                strengths.append("划頻在理想範圍——節奏感很好！")

        # If no specific strengths but also few issues
        if not strengths and len(issues) <= 2:
            strengths.append("整支影片的動作維持得很一致！")

        return strengths

    def _format_metrics(self, metrics: Dict) -> str:
        """Format metrics section."""
        lines = []

        # Elbow metrics
        if metrics.get('elbow', {}).get('avg_angle') is not None:
            elbow = metrics['elbow']
            lines.append(f"🔸 抓水肘角：")
            lines.append(f"   平均：{elbow['avg_angle']:.1f}°（理想範圍：80-100°）")
            if elbow['left_avg'] and elbow['right_avg']:
                lines.append(f"   左手：{elbow['left_avg']:.1f}° | 右手：{elbow['right_avg']:.1f}°")
            lines.append("")

        # Body rotation
        if metrics.get('rotation', {}).get('avg_rotation') is not None:
            rotation = metrics['rotation']
            lines.append(f"🔸 身體轉肩角度：")
            lines.append(f"   平均：{rotation['avg_rotation']:.1f}°（理想範圍：45-60°）")
            lines.append(f"   範圍：{rotation['min_rotation']:.1f}° - {rotation['max_rotation']:.1f}°")
            lines.append("")

        # Stroke rate
        if metrics.get('stroke_rate', {}).get('spm') is not None:
            sr = metrics['stroke_rate']
            lines.append(f"🔸 划頻：")
            lines.append(f"   每分鐘 {sr['spm']:.1f} 次划水（理想範圍：50-60 SPM）")
            lines.append(f"   時長：{sr['duration']:.1f}秒 | 總划水次數：{sr['total_strokes']}")
            lines.append("")

        # Head stability
        if metrics.get('head', {}).get('stability') is not None:
            head = metrics['head']
            stability_pct = head['stability'] * 100
            lines.append(f"🔸 頭部穩定度：{stability_pct:.1f}%（越高越好）")
            lines.append("")

        # Kick
        if metrics.get('kick', {}).get('avg_knee_angle') is not None:
            kick = metrics['kick']
            lines.append(f"🔸 踢腿動作：")
            lines.append(f"   膝關節角度：{kick['avg_knee_angle']:.1f}°（應接近170°）")
            lines.append("")

        # Video quality
        if metrics.get('valid_frame_ratio') is not None:
            valid_pct = metrics['valid_frame_ratio'] * 100
            lines.append(f"🔸 偵測品質：{valid_pct:.1f}% 的影格成功分析")

        return "\n".join(lines)
