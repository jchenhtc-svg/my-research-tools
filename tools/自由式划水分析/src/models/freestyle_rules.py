"""Swimming technique rules and thresholds for freestyle stroke analysis.

門檻的兩層設定
--------------
1. **視角（view）**：不是每個指標從每個角度都量得到。側拍看得到矢狀面的動作
   （手肘、膝、抬頭），但看不到繞著身體長軸的滾轉，也看不到左右方向的偏移；
   那兩項需要俯瞰。強行從側拍計算會得到看似合理、實則無意義的數字。

2. **族群（profile）**：同一個動作對高中一般生和校隊競技選手不該用同一把尺。

門檻值的可信度
--------------
每個門檻都標了 `basis`：
  - `literature` — 有游泳生物力學文獻或教練共識支持
  - `provisional` — 合理的起始值，**需要用你自己的影片驗證後調整**

`provisional` 的值不要當成標準答案。建議先用一批已知技術水準的影片跑一次，
看判定結果跟你的主觀評估差多少，再回來調這裡的數字。
"""

# ---------------------------------------------------------------------------
# 拍攝視角
# ---------------------------------------------------------------------------

VIEW_SIDE = "side"          # 側拍（與泳道平行，從池邊拍）
VIEW_OVERHEAD = "overhead"  # 俯瞰（從岸邊高處或看台往下拍）

VIEW_LABELS = {
    VIEW_SIDE: "側拍",
    VIEW_OVERHEAD: "俯瞰",
}

# 每個指標需要哪些視角才量得準。
# 這張表是整個工具正確性的關鍵：指標不在對應視角就不該輸出判定，
# 因為算出來的數字沒有物理意義。
METRIC_REQUIRED_VIEWS = {
    'elbow':       {VIEW_SIDE},                    # 手肘屈曲在矢狀面
    'kick':        {VIEW_SIDE},                    # 膝屈曲在矢狀面
    'head':        {VIEW_SIDE},                    # 抬頭是垂直方向位移
    'stroke_rate': {VIEW_SIDE, VIEW_OVERHEAD},     # 週期性訊號兩種視角都抓得到
    'rotation':    {VIEW_OVERHEAD},                # 滾轉需俯瞰看肩線橫向收縮
    'entry':       {VIEW_OVERHEAD},                # 左右偏移需俯瞰
}

METRIC_LABELS = {
    'elbow': '手肘抓水角度',
    'kick': '踢腿膝關節角度',
    'head': '換氣抬頭幅度',
    'stroke_rate': '划頻',
    'rotation': '身體滾轉角度',
    'entry': '入水點左右偏移',
}


def metric_is_valid_for_view(metric: str, view: str) -> bool:
    """這個指標在這個視角下量得準嗎？"""
    return view in METRIC_REQUIRED_VIEWS.get(metric, set())


def required_view_label(metric: str) -> str:
    """這個指標需要哪個視角（給使用者看的字串）。"""
    views = METRIC_REQUIRED_VIEWS.get(metric, set())
    return "／".join(VIEW_LABELS[v] for v in sorted(views))


# ---------------------------------------------------------------------------
# 選手族群
# ---------------------------------------------------------------------------

PROFILE_STUDENT = "student"          # 高中一般生、游泳課學生
PROFILE_COMPETITIVE = "competitive"  # 校隊競技選手

PROFILE_LABELS = {
    PROFILE_STUDENT: "高中一般生／游泳課",
    PROFILE_COMPETITIVE: "校隊競技選手",
}

DEFAULT_PROFILE = PROFILE_STUDENT


# ---------------------------------------------------------------------------
# 門檻定義
# ---------------------------------------------------------------------------
#
# 尺度說明：所有長度類指標都以「身體尺度」正規化，不用影格尺寸。
# 影格尺寸會隨拍攝距離與變焦改變，同一個動作拍近拍遠會得到不同數字；
# 用軀幹長或肩寬當分母才有可比性。

THRESHOLDS = {
    PROFILE_STUDENT: {
        # 抓水期手肘角度（肩-肘-腕夾角，度）
        # 取水下期各週期的最小值平均，代表抓水時的屈曲程度
        'elbow_optimal_min': 85,
        'elbow_optimal_max': 115,
        'elbow_dropped': 130,        # 高於此視為手肘下垂（沒有高肘）
        'elbow_basis': 'provisional',

        # 身體滾轉（度，0=完全趴平，90=側轉到底）— 需俯瞰
        'rotation_optimal_min': 30,
        'rotation_optimal_max': 60,
        'rotation_too_flat': 20,
        'rotation_too_much': 70,
        'rotation_basis': 'provisional',

        # 入水點橫向偏移（以肩寬為單位；正值=偏向身體外側，負值=越過中線）— 需俯瞰
        # -0.15 表示手腕越過身體長軸達肩寬的 15%
        'entry_crossing': -0.10,
        'entry_basis': 'provisional',

        # 換氣抬頭幅度（鼻子相對肩線的垂直位移 ÷ 軀幹長）
        'head_lift': 0.35,
        'head_basis': 'provisional',

        # 划頻（每分鐘划手次數，左右手合計；一個完整週期 = 2 次）
        'stroke_rate_min': 45,
        'stroke_rate_max': 70,
        'stroke_rate_basis': 'provisional',

        # 踢腿膝關節角度（度，180=完全打直）
        # 取各週期最大屈曲（最小角度）的平均
        'knee_optimal': 160,
        'knee_excessive_bend': 125,
        'knee_basis': 'provisional',
    },

    PROFILE_COMPETITIVE: {
        'elbow_optimal_min': 90,
        'elbow_optimal_max': 110,
        'elbow_dropped': 125,
        'elbow_basis': 'literature',   # 高肘抓水約 90-110°，教練共識一致

        'rotation_optimal_min': 40,
        'rotation_optimal_max': 65,
        'rotation_too_flat': 30,
        'rotation_too_much': 75,
        'rotation_basis': 'literature',  # 自由式滾轉約 40-60° 為文獻常見區間

        'entry_crossing': -0.05,       # 競技選手容忍度更低
        'entry_basis': 'provisional',

        'head_lift': 0.25,
        'head_basis': 'provisional',

        'stroke_rate_min': 60,
        'stroke_rate_max': 95,
        'stroke_rate_basis': 'provisional',

        'knee_optimal': 165,
        'knee_excessive_bend': 135,
        'knee_basis': 'provisional',
    },
}


def get_thresholds(profile: str = DEFAULT_PROFILE) -> dict:
    """取得指定族群的門檻。未知的 profile 退回預設值。"""
    return THRESHOLDS.get(profile, THRESHOLDS[DEFAULT_PROFILE])


def threshold_basis(profile: str, metric: str) -> str:
    """這個指標的門檻是有文獻依據還是暫定值。"""
    return get_thresholds(profile).get(f'{metric}_basis', 'provisional')


# 姿態點可信度門檻：低於此值的關節點不納入計算
MIN_VISIBILITY = 0.5

# 每個劃臂週期至少要有幾個有效影格才採計，避免用零星幾點就下判斷
MIN_FRAMES_PER_CYCLE = 4


# ---------------------------------------------------------------------------
# 問題嚴重度
# ---------------------------------------------------------------------------

SEVERITY_CRITICAL = "critical"
SEVERITY_MODERATE = "moderate"
SEVERITY_MINOR = "minor"


class FreestyleIssue:
    """一項偵測到的技術問題。"""

    def __init__(self, issue_type: str, severity: str, description: str, tip: str,
                 metric_value=None, basis: str = 'provisional'):
        self.issue_type = issue_type
        self.severity = severity
        self.description = description
        self.tip = tip
        self.metric_value = metric_value
        self.basis = basis  # 這項判定的門檻依據強度

    def __repr__(self):
        return f"FreestyleIssue({self.issue_type}, {self.severity})"


# ---------------------------------------------------------------------------
# 問題定義與教練建議
# ---------------------------------------------------------------------------

ISSUE_TYPES = {
    'dropped_elbow': {
        'name': '手肘下垂',
        'tip': '專注於高肘抓水，想像手臂越過一個桶子。抓水階段手肘要比手腕高。',
        'severity': SEVERITY_CRITICAL,
    },
    'flat_body': {
        'name': '身體轉肩不足',
        'tip': '增加身體轉肩幅度。轉肩要從髖部發動，不是肩膀。讓身體像滾木頭一樣轉動。',
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
        'tip': '稍微加快節奏，專注於加快手部轉換速度，減少每次划水後的停頓。',
        'severity': SEVERITY_MINOR,
    },
    'fast_stroke_rate': {
        'name': '划頻過快',
        'tip': '放慢速度、拉長划距，每次划水後多一點滑行。划距效率比划頻更重要。',
        'severity': SEVERITY_MINOR,
    },
}


def get_severity_emoji(severity: str) -> str:
    """嚴重度對應的圖示。"""
    if severity == SEVERITY_CRITICAL:
        return "🔴"
    elif severity == SEVERITY_MODERATE:
        return "🟡"
    else:
        return "🔵"


def get_severity_label(severity: str) -> str:
    """嚴重度對應的文字標籤。"""
    if severity == SEVERITY_CRITICAL:
        return "關鍵問題"
    elif severity == SEVERITY_MODERATE:
        return "待加強項目"
    else:
        return "次要建議"
