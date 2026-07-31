"""Swimming technique rules and thresholds for freestyle stroke analysis."""

# Elbow angle thresholds (degrees)
ELBOW_ANGLE_OPTIMAL_MIN = 80
ELBOW_ANGLE_OPTIMAL_MAX = 100
ELBOW_ANGLE_DROPPED = 120  # Above this is considered "dropped elbow"

# Body rotation thresholds (degrees)
BODY_ROTATION_OPTIMAL_MIN = 45
BODY_ROTATION_OPTIMAL_MAX = 60
BODY_ROTATION_TOO_FLAT = 30  # Below this is too flat
BODY_ROTATION_TOO_MUCH = 70  # Above this is over-rotating

# Arm entry - distance from centerline (pixels - will be normalized)
ARM_ENTRY_CENTERLINE_THRESHOLD = 0.15  # 15% of frame width

# Head position - vertical movement threshold
HEAD_LIFT_THRESHOLD = 0.1  # 10% of frame height variation

# Stroke rate thresholds (strokes per minute)
STROKE_RATE_OPTIMAL_MIN = 50
STROKE_RATE_OPTIMAL_MAX = 60

# Knee angle thresholds (degrees) - should be minimal bend
KNEE_ANGLE_OPTIMAL = 170  # Nearly straight
KNEE_ANGLE_EXCESSIVE_BEND = 140  # Too much bending

# Visibility threshold for landmark confidence
MIN_VISIBILITY = 0.5

# Issue severity levels
SEVERITY_CRITICAL = "critical"
SEVERITY_MODERATE = "moderate"
SEVERITY_MINOR = "minor"


class FreestyleIssue:
    """Represents a detected technique issue."""

    def __init__(self, issue_type: str, severity: str, description: str, tip: str, metric_value=None):
        self.issue_type = issue_type
        self.severity = severity
        self.description = description
        self.tip = tip
        self.metric_value = metric_value

    def __repr__(self):
        return f"FreestyleIssue({self.issue_type}, {self.severity})"


# Issue definitions with coaching tips
ISSUE_TYPES = {
    'dropped_elbow': {
        'name': '手肘下垂',
        'tip': '專注於高肘抓水，想像手臂越過一個桶子。抓水階段手肘要比手腕高。',
        'severity': SEVERITY_CRITICAL,
    },
    'flat_body': {
        'name': '身體轉肩不足',
        'tip': '增加身體轉肩幅度（45-60°）。轉肩要從髖部發動，不是肩膀。讓身體像滾木頭一樣轉動。',
        'severity': SEVERITY_CRITICAL,
    },
    'over_rotation': {
        'name': '轉肩過度',
        'tip': '減少身體轉肩幅度，專注於有控制的轉動。肩膀轉動幅度應該大於髖部。',
        'severity': SEVERITY_MODERATE,
    },
    'crossing_centerline': {
        'name': '入水過中線',
        'tip': '入水點要對齊肩膀，避免超過身體中線。手臂要沿直線划回。',
        'severity': SEVERITY_CRITICAL,
    },
    'head_lifting': {
        'name': '換氣時抬頭',
        'tip': '換氣時轉頭而不是抬頭，一邊泳鏡留在水中，眼睛看側邊而不是前方。',
        'severity': SEVERITY_MODERATE,
    },
    'excessive_knee_bend': {
        'name': '踢腿膝蓋彎曲過度',
        'tip': '雙腿保持較直，從髖部發力打水，小幅度快速踢腿、盡量減少膝蓋彎曲。',
        'severity': SEVERITY_MODERATE,
    },
    'slow_stroke_rate': {
        'name': '划頻過慢',
        'tip': '稍微加快節奏（長距離游泳建議抓50-60 SPM），專注於加快手部轉換速度。',
        'severity': SEVERITY_MINOR,
    },
    'fast_stroke_rate': {
        'name': '划頻過快',
        'tip': '放慢速度、拉長划距，每次划水後多一點滑行。划距效率比划頻更重要。',
        'severity': SEVERITY_MINOR,
    },
}


def get_severity_emoji(severity: str) -> str:
    """Get emoji indicator for severity level."""
    if severity == SEVERITY_CRITICAL:
        return "🔴"
    elif severity == SEVERITY_MODERATE:
        return "🟡"
    else:
        return "🔵"


def get_severity_label(severity: str) -> str:
    """Get text label for severity level."""
    if severity == SEVERITY_CRITICAL:
        return "關鍵問題"
    elif severity == SEVERITY_MODERATE:
        return "待加強項目"
    else:
        return "次要建議"
