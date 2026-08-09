"""Analyzes swimming stroke metrics and detects technique issues.

設計要點
--------
**所有訊號都相對身體，不相對影格。**
鏡頭跟拍時，關節點的絕對座標會整體漂移，這個漂移可能比動作本身還大。
所以週期偵測用「手腕 − 肩中點」，長度類指標除以軀幹長而不是影格高。
這樣拍近拍遠、鏡頭有沒有跟拍，得到的數字才有可比性。

**先分期再取值。**
抓水角度只在水下期有意義，把整支影片的手肘角度平均起來會混進回復期
（手肘也彎）和前伸期（接近打直），得到一個誰都不代表的數字。
所以先切出劃臂週期，再在週期內取對應相位的值。

**視角不對就不輸出。**
滾轉與左右偏移從側拍量不到，算出來的數字沒有物理意義。
這種情況回報 unavailable，而不是給一個看起來合理的假數字。
"""

import math
import numpy as np
from typing import List, Dict, Optional

from src.models.freestyle_rules import (
    MIN_VISIBILITY, MIN_FRAMES_PER_CYCLE,
    FreestyleIssue, ISSUE_TYPES,
    SEVERITY_CRITICAL, SEVERITY_MODERATE, SEVERITY_MINOR,
    VIEW_SIDE, VIEW_OVERHEAD, VIEW_LABELS,
    DEFAULT_PROFILE, get_thresholds, threshold_basis,
    metric_is_valid_for_view, required_view_label,
)

_TORSO_POINTS = ('left_shoulder', 'right_shoulder', 'left_hip', 'right_hip')


class StrokeAnalyzer:
    """從姿態資料分析自由式技術。"""

    def __init__(self, view: str = VIEW_SIDE, profile: str = DEFAULT_PROFILE):
        """
        Args:
            view: 拍攝視角（VIEW_SIDE / VIEW_OVERHEAD）
            profile: 選手族群（PROFILE_STUDENT / PROFILE_COMPETITIVE）
        """
        self.view = view
        self.profile = profile
        self.th = get_thresholds(profile)
        self.metrics = {}
        self.issues = []

    # ------------------------------------------------------------------
    # 主流程
    # ------------------------------------------------------------------

    def analyze_video(self, pose_data: List[Dict]) -> Dict:
        """分析整支影片。"""
        print(f"\n分析划水動作中…（視角：{VIEW_LABELS.get(self.view, self.view)}）")

        valid_frames = [f for f in pose_data if f['pose'] is not None]
        if not valid_frames:
            return {'error': '影片中偵測不到有效的姿態資料', 'metrics': {}, 'issues': []}

        print(f"有效影格：{len(valid_frames)}/{len(pose_data)}")

        body_scale = self._body_scale(valid_frames)
        if body_scale is None or body_scale <= 0:
            return {
                'error': '無法估計身體尺度（軀幹關節點偵測不足），無法進行正規化分析',
                'metrics': {}, 'issues': []
            }

        cycles = self._detect_cycles(valid_frames)
        print(f"偵測到劃臂週期：{len(cycles)} 個")

        self.metrics = {
            'view': self.view,
            'profile': self.profile,
            'body_scale_px': body_scale,
            'cycle_count': len(cycles),
            'valid_frame_ratio': len(valid_frames) / len(pose_data),
            'elbow':       self._metric('elbow',       self._analyze_elbow, valid_frames, cycles),
            'kick':        self._metric('kick',        self._analyze_kick, valid_frames, cycles),
            'head':        self._metric('head',        self._analyze_head, valid_frames, body_scale),
            'stroke_rate': self._metric('stroke_rate', self._analyze_stroke_rate, valid_frames, cycles),
            'rotation':    self._metric('rotation',    self._analyze_rotation, valid_frames, cycles),
            'entry':       self._metric('entry',       self._analyze_entry, valid_frames, cycles),
        }

        self.issues = self._detect_issues()
        return {'metrics': self.metrics, 'issues': self.issues}

    def _metric(self, name: str, fn, *args) -> Dict:
        """視角對才計算；不對就明確標成 unavailable。

        這裡刻意不回傳「還算合理的估計值」——一個量錯對象的數字比沒有數字更危險，
        因為它會讓使用者以為自己看到了實際情況。
        """
        if not metric_is_valid_for_view(name, self.view):
            return {
                'available': False,
                'reason': f'此指標需要{required_view_label(name)}影片才量得準，'
                          f'目前是{VIEW_LABELS.get(self.view, self.view)}',
            }
        result = fn(*args)
        result['available'] = True
        return result

    # ------------------------------------------------------------------
    # 基礎量測
    # ------------------------------------------------------------------

    @staticmethod
    def _midpoint(lm: Dict, a: str, b: str):
        return ((lm[a]['x'] + lm[b]['x']) / 2.0,
                (lm[a]['y'] + lm[b]['y']) / 2.0)

    @staticmethod
    def _visible(lm: Dict, *names) -> bool:
        return all(lm[n]['visibility'] >= MIN_VISIBILITY for n in names)

    def _body_scale(self, frames: List[Dict]) -> Optional[float]:
        """軀幹長度（肩中點到髖中點，像素）的中位數。

        用中位數而非平均，避免少數偵測失準的影格把尺度拉歪。
        這是所有長度類指標的分母——換成影格高度的話，
        同一個動作拍近一點數值就會變大，跨影片無法比較。
        """
        lengths = []
        for f in frames:
            lm = f['pose']['landmarks']
            if not self._visible(lm, *_TORSO_POINTS):
                continue
            sx, sy = self._midpoint(lm, 'left_shoulder', 'right_shoulder')
            hx, hy = self._midpoint(lm, 'left_hip', 'right_hip')
            d = math.hypot(sx - hx, sy - hy)
            if d > 0:
                lengths.append(d)
        return float(np.median(lengths)) if lengths else None

    # ------------------------------------------------------------------
    # 劃臂週期偵測
    # ------------------------------------------------------------------

    def _detect_cycles(self, frames: List[Dict], side: str = 'left') -> List[Dict]:
        """切出劃臂週期。

        訊號用「手腕 x − 肩中點 x」：這是身體座標系下的位移，
        鏡頭平移或跟拍會同時移動手腕和肩膀，相減後就抵銷了。
        原本的版本直接用手腕絕對 x，跟拍時會有單調漂移蓋過振盪，
        導致找不到峰值、划頻整個算錯。

        再減去移動平均做去趨勢，只留下振盪成分才做峰值偵測。
        """
        samples = []
        for i, f in enumerate(frames):
            lm = f['pose']['landmarks']
            w = f'{side}_wrist'
            if not self._visible(lm, w, 'left_shoulder', 'right_shoulder'):
                continue
            cx, _ = self._midpoint(lm, 'left_shoulder', 'right_shoulder')
            samples.append((i, f['timestamp'], lm[w]['x'] - cx))

        if len(samples) < 10:
            return []

        idxs = [s[0] for s in samples]
        times = [s[1] for s in samples]
        sig = [s[2] for s in samples]
        duration = times[-1] - times[0]
        if duration <= 0:
            return []

        # 去趨勢：扣掉慢變的基線，只留振盪
        window = max(3, len(sig) // 8)
        baseline = self._moving_average(sig, window)
        detrended = [s - b for s, b in zip(sig, baseline)]

        # 最短週期間隔：假設划頻上限 120 次/分（每手 60 次/分 → 1 秒一個週期）
        rate = len(detrended) / duration          # 每秒取樣數
        min_gap = max(2, int(rate * 0.5))

        peaks = self._find_peaks(detrended, min_gap)

        cycles = []
        for a, b in zip(peaks, peaks[1:]):
            if idxs[b] - idxs[a] + 1 >= MIN_FRAMES_PER_CYCLE:
                cycles.append({
                    'start': idxs[a],
                    'end': idxs[b],
                    'start_t': times[a],
                    'end_t': times[b],
                })
        return cycles

    @staticmethod
    def _find_peaks(values: List[float], min_gap: int) -> List[int]:
        """區域極大值，並強制彼此間隔。

        同高的平台只取第一點，避免一段平坦訊號被算成好幾個峰。
        """
        candidates = []
        for i in range(1, len(values) - 1):
            if values[i] > values[i - 1] and values[i] >= values[i + 1]:
                candidates.append(i)
        peaks = []
        for c in candidates:
            if not peaks or (c - peaks[-1]) >= min_gap:
                peaks.append(c)
        return peaks

    @staticmethod
    def _moving_average(values: List[float], window: int) -> List[float]:
        if window < 2 or len(values) < window:
            return list(values)
        half = window // 2
        out = []
        for i in range(len(values)):
            lo, hi = max(0, i - half), min(len(values), i + half + 1)
            out.append(sum(values[lo:hi]) / (hi - lo))
        return out

    @staticmethod
    def _angle(p1: Dict, p2: Dict, p3: Dict) -> float:
        """p2 為頂點的夾角（度）。"""
        a = np.array([p1['x'], p1['y']])
        b = np.array([p2['x'], p2['y']])
        c = np.array([p3['x'], p3['y']])
        v1, v2 = a - b, c - b
        n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
        if n1 == 0 or n2 == 0:
            return 0.0
        cos = np.clip(np.dot(v1, v2) / (n1 * n2), -1.0, 1.0)
        return float(np.degrees(np.arccos(cos)))

    # ------------------------------------------------------------------
    # 各項指標
    # ------------------------------------------------------------------

    def _analyze_elbow(self, frames: List[Dict], cycles: List[Dict]) -> Dict:
        """抓水期手肘角度。

        只取「手腕低於肩線」的影格——那才是水下推進期。
        回復期手肘同樣彎曲、前伸期接近打直，把整個週期平均起來
        會得到一個介於中間、誰都不代表的數字（原本的做法就是這樣，
        平均常落在 130-150°，於是幾乎每支影片都被判成手肘下垂）。

        每個週期取水下期的最小角度＝該次抓水的最大屈曲，再跨週期平均。
        """
        per_cycle = {'left': [], 'right': []}

        for cyc in cycles:
            for side in ('left', 'right'):
                sh, el, wr = f'{side}_shoulder', f'{side}_elbow', f'{side}_wrist'
                angles = []
                for f in frames[cyc['start']:cyc['end'] + 1]:
                    lm = f['pose']['landmarks']
                    if not self._visible(lm, sh, el, wr):
                        continue
                    # y 向下為正：手腕 y 大於肩 y 代表手在肩線below（水下期）
                    if lm[wr]['y'] <= lm[sh]['y']:
                        continue
                    angles.append(self._angle(lm[sh], lm[el], lm[wr]))
                if len(angles) >= 2:
                    per_cycle[side].append(min(angles))

        left, right = per_cycle['left'], per_cycle['right']
        combined = left + right
        return {
            'catch_angle': float(np.mean(combined)) if combined else None,
            'left_avg': float(np.mean(left)) if left else None,
            'right_avg': float(np.mean(right)) if right else None,
            'asymmetry': (abs(np.mean(left) - np.mean(right))
                          if left and right else None),
            'cycles_used': len(combined),
        }

    def _analyze_kick(self, frames: List[Dict], cycles: List[Dict]) -> Dict:
        """踢腿膝關節角度。

        有意義的是最大屈曲，不是平均。膝關節在打水中週期性屈伸，
        平均值會落在中間，反映不出「屈曲過度」。
        原本的程式其實算了 min_knee_angle，但判定時卻用 avg。

        用第 10 百分位當代表性最大屈曲，比單一最小值穩健
        （單一最小值容易被一個偵測失準的影格決定）。
        """
        angles = []
        for f in frames:
            lm = f['pose']['landmarks']
            for side in ('left', 'right'):
                hip, knee, ank = f'{side}_hip', f'{side}_knee', f'{side}_ankle'
                if self._visible(lm, hip, knee, ank):
                    angles.append(self._angle(lm[hip], lm[knee], lm[ank]))

        if not angles:
            return {'peak_flexion': None, 'median_angle': None, 'samples': 0}

        return {
            'peak_flexion': float(np.percentile(angles, 10)),
            'median_angle': float(np.median(angles)),
            'samples': len(angles),
        }

    def _analyze_head(self, frames: List[Dict], body_scale: float) -> Dict:
        """換氣抬頭幅度。

        量「鼻子相對肩線」的垂直位移，再除以軀幹長。
        兩層都很重要：
        - 相對肩線 → 鏡頭上下晃動時，鼻子和肩膀一起動，相減後抵銷
        - 除以軀幹長 → 拍近拍遠得到同樣的數字

        原本用「鼻子絕對 y 的全片範圍 ÷ 影格高度」，
        鏡頭一晃或選手游近游遠，數值就整個變掉。
        """
        offsets = []
        for f in frames:
            lm = f['pose']['landmarks']
            if not self._visible(lm, 'nose', 'left_shoulder', 'right_shoulder'):
                continue
            _, sy = self._midpoint(lm, 'left_shoulder', 'right_shoulder')
            offsets.append(lm['nose']['y'] - sy)

        if len(offsets) < 5:
            return {'lift_ratio': None, 'stability': None, 'samples': len(offsets)}

        # 用 5-95 百分位範圍，避免單一離群影格主導
        spread = float(np.percentile(offsets, 95) - np.percentile(offsets, 5))
        ratio = spread / body_scale
        return {
            'lift_ratio': ratio,
            'stability': max(0.0, 1.0 - ratio),
            'samples': len(offsets),
        }

    def _analyze_stroke_rate(self, frames: List[Dict], cycles: List[Dict]) -> Dict:
        """划頻（每分鐘划手次數，左右手合計）。

        一個偵測到的週期 = 單手一次完整循環 = 2 次划手。
        週期偵測已經在身體座標系做過去趨勢，鏡頭跟拍不影響。
        """
        if len(cycles) < 2:
            return {'spm': None, 'cycles': len(cycles), 'duration': None,
                    'note': '週期數不足，無法可靠估計划頻'}

        duration = cycles[-1]['end_t'] - cycles[0]['start_t']
        if duration <= 0:
            return {'spm': None, 'cycles': len(cycles), 'duration': None}

        cycles_per_min = len(cycles) / duration * 60.0
        spm = cycles_per_min * 2.0

        if not (20 <= spm <= 140):
            return {'spm': None, 'cycles': len(cycles), 'duration': duration,
                    'note': f'估計值 {spm:.0f} 超出合理範圍，可能是週期偵測失準'}

        return {
            'spm': spm,
            'cycles_per_min': cycles_per_min,
            'cycles': len(cycles),
            'duration': duration,
        }

    def _analyze_rotation(self, frames: List[Dict], cycles: List[Dict]) -> Dict:
        """身體滾轉角度（僅俯瞰）。

        俯瞰時，身體趴平則兩肩橫向間距最大；滾轉 90° 時兩肩在畫面上重疊。
        所以 roll = arccos(當前肩寬 / 最大肩寬)。

        最大肩寬取第 95 百分位而非最大值，避免單一偵測誤差當基準。

        限制：若選手全程都沒有接近趴平的瞬間，基準會被低估，
        算出來的滾轉角會偏小。這點寫在報告裡讓使用者知道。
        """
        widths = []
        for f in frames:
            lm = f['pose']['landmarks']
            if not self._visible(lm, 'left_shoulder', 'right_shoulder'):
                widths.append(None)
                continue
            d = math.hypot(lm['left_shoulder']['x'] - lm['right_shoulder']['x'],
                           lm['left_shoulder']['y'] - lm['right_shoulder']['y'])
            widths.append(d)

        valid = [w for w in widths if w is not None and w > 0]
        if len(valid) < 5:
            return {'avg_rotation': None, 'peak_rotation': None, 'samples': len(valid)}

        ref = float(np.percentile(valid, 95))
        if ref <= 0:
            return {'avg_rotation': None, 'peak_rotation': None, 'samples': len(valid)}

        rolls = [math.degrees(math.acos(min(1.0, max(0.0, w / ref)))) for w in valid]

        return {
            'avg_rotation': float(np.mean(rolls)),
            'peak_rotation': float(np.percentile(rolls, 90)),
            'reference_width_px': ref,
            'samples': len(rolls),
        }

    def _analyze_entry(self, frames: List[Dict], cycles: List[Dict]) -> Dict:
        """入水點相對身體長軸的左右偏移（僅俯瞰）。

        身體長軸 = 髖中點 → 肩中點。手腕到這條軸的**帶號**垂直距離，
        以肩寬正規化。正值＝在自己這側，負值＝越過中線到對側。

        原本的版本量的是「手腕到肩中點的影像 x 距離」，
        側拍時那個方向是前後而不是左右，等於在量手臂前伸多遠，
        而且取全片最大值，手一伸直就必然超標。
        """
        per_side = {'left': [], 'right': []}

        for f in frames:
            lm = f['pose']['landmarks']
            if not self._visible(lm, *_TORSO_POINTS):
                continue
            sx, sy = self._midpoint(lm, 'left_shoulder', 'right_shoulder')
            hx, hy = self._midpoint(lm, 'left_hip', 'right_hip')
            axis = np.array([sx - hx, sy - hy])
            norm = np.linalg.norm(axis)
            if norm == 0:
                continue
            axis = axis / norm

            shoulder_w = math.hypot(lm['left_shoulder']['x'] - lm['right_shoulder']['x'],
                                    lm['left_shoulder']['y'] - lm['right_shoulder']['y'])
            if shoulder_w <= 0:
                continue

            for side in ('left', 'right'):
                wr = f'{side}_wrist'
                if not self._visible(lm, wr):
                    continue
                rel = np.array([lm[wr]['x'] - sx, lm[wr]['y'] - sy])
                # 2D 外積 → 帶號垂直距離
                signed = float(axis[0] * rel[1] - axis[1] * rel[0])
                per_side[side].append(signed / shoulder_w)

        result = {}
        worst = None
        for side in ('left', 'right'):
            vals = per_side[side]
            if len(vals) < 5:
                result[f'{side}_offset'] = None
                continue
            # 以該手自己的中位數決定「自己這側」是哪個符號，再統一成正值代表外側
            sign = 1.0 if np.median(vals) >= 0 else -1.0
            normalized = [v * sign for v in vals]
            # 最越線的時刻 = 最小值（最負）
            crossing = float(np.percentile(normalized, 5))
            result[f'{side}_offset'] = crossing
            worst = crossing if worst is None else min(worst, crossing)

        result['max_crossing'] = worst
        result['samples'] = len(per_side['left']) + len(per_side['right'])
        return result

    # ------------------------------------------------------------------
    # 問題判定
    # ------------------------------------------------------------------

    def _detect_issues(self) -> List[FreestyleIssue]:
        """依門檻產生問題清單。只處理視角允許、且真的算出值的指標。"""
        issues = []
        th = self.th
        m = self.metrics

        def add(key, severity_key, desc, value):
            issues.append(FreestyleIssue(
                key, ISSUE_TYPES[key]['severity'], desc,
                ISSUE_TYPES[key]['tip'], value,
                basis=threshold_basis(self.profile, severity_key),
            ))

        # 手肘
        e = m.get('elbow', {})
        if e.get('available') and e.get('catch_angle') is not None:
            a = e['catch_angle']
            if a > th['elbow_dropped']:
                add('dropped_elbow', 'elbow',
                    f"抓水時手肘下垂（水下期最大屈曲平均 {a:.0f}°"
                    f"，理想 {th['elbow_optimal_min']}–{th['elbow_optimal_max']}°）", a)

        # 滾轉
        r = m.get('rotation', {})
        if r.get('available') and r.get('avg_rotation') is not None:
            a = r['avg_rotation']
            if a < th['rotation_too_flat']:
                add('flat_body', 'rotation',
                    f"身體滾轉不足（平均 {a:.0f}°"
                    f"，理想 {th['rotation_optimal_min']}–{th['rotation_optimal_max']}°）", a)
            elif a > th['rotation_too_much']:
                add('over_rotation', 'rotation',
                    f"滾轉過度（平均 {a:.0f}°"
                    f"，理想 {th['rotation_optimal_min']}–{th['rotation_optimal_max']}°）", a)

        # 入水偏移
        en = m.get('entry', {})
        if en.get('available') and en.get('max_crossing') is not None:
            c = en['max_crossing']
            if c < th['entry_crossing']:
                add('crossing_centerline', 'entry',
                    f"入水點越過身體中線（達肩寬的 {abs(c)*100:.0f}%）", c)

        # 抬頭
        h = m.get('head', {})
        if h.get('available') and h.get('lift_ratio') is not None:
            v = h['lift_ratio']
            if v > th['head_lift']:
                add('head_lifting', 'head',
                    f"換氣時抬頭幅度偏大（垂直位移達軀幹長的 {v*100:.0f}%"
                    f"，建議低於 {th['head_lift']*100:.0f}%）", v)

        # 划頻
        s = m.get('stroke_rate', {})
        if s.get('available') and s.get('spm') is not None:
            spm = s['spm']
            if spm < th['stroke_rate_min']:
                add('slow_stroke_rate', 'stroke_rate',
                    f"划頻偏低（{spm:.0f} 次/分"
                    f"，此族群參考範圍 {th['stroke_rate_min']}–{th['stroke_rate_max']}）", spm)
            elif spm > th['stroke_rate_max']:
                add('fast_stroke_rate', 'stroke_rate',
                    f"划頻偏高（{spm:.0f} 次/分"
                    f"，此族群參考範圍 {th['stroke_rate_min']}–{th['stroke_rate_max']}）", spm)

        # 踢腿
        k = m.get('kick', {})
        if k.get('available') and k.get('peak_flexion') is not None:
            v = k['peak_flexion']
            if v < th['knee_excessive_bend']:
                add('excessive_knee_bend', 'knee',
                    f"踢腿時膝關節屈曲過大（最大屈曲 {v:.0f}°"
                    f"，建議不低於 {th['knee_excessive_bend']}°）", v)

        order = {SEVERITY_CRITICAL: 0, SEVERITY_MODERATE: 1, SEVERITY_MINOR: 2}
        issues.sort(key=lambda x: order[x.severity])
        return issues
