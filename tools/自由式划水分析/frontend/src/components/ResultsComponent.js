import React, { useState, useEffect, useCallback, useRef } from 'react';

import { API_BASE_URL } from '../config';

function ResultsComponent({ videoId, onReset }) {
  const [report, setReport] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [score, setScore] = useState(null);
  const [issues, setIssues] = useState([]);
  const [quickInsight, setQuickInsight] = useState('');
  const [biggestRedFlag, setBiggestRedFlag] = useState(null);
  const [strengths, setStrengths] = useState([]);
  const videoRef = useRef(null);

  const fetchReport = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/result/${videoId}/report`);
      const data = await response.json();

      if (response.ok) {
        setReport(data.report);
        parseReport(data.report);
      } else {
        setError('報告載入失敗');
      }
    } catch (err) {
      setError('連線錯誤，無法載入報告');
    } finally {
      setLoading(false);
    }
  }, [videoId]);

  useEffect(() => {
    fetchReport();
  }, [fetchReport]);

  const parseReport = (reportText) => {
    // Extract score
    const scoreMatch = reportText.match(/技術總評分：(\d+)\/10/);
    if (scoreMatch) {
      setScore(parseInt(scoreMatch[1]));
    }

    // Extract Quick Insight
    const insightMatch = reportText.match(/📊 快速洞察\n━+\n(.+?)(?:\n\n|$)/s);
    if (insightMatch) {
      setQuickInsight(insightMatch[1].trim());
    }

    // Extract Biggest Red Flag
    const redFlagMatch = reportText.match(/🚨 最大警訊\n━+\n⚠️ {2}(.+?)\n\n💡 如何改善：\n {3}(.+?)(?:\n\n|$)/s);
    if (redFlagMatch) {
      setBiggestRedFlag({
        issue: redFlagMatch[1].trim(),
        fix: redFlagMatch[2].trim()
      });
    }

    // Extract Strengths
    const strengthsMatch = reportText.match(/✅ 做得好的地方\n━+\n((?:• .+\n?)+)/);
    if (strengthsMatch) {
      const strengthsList = strengthsMatch[1]
        .split('\n')
        .filter(line => line.trim().startsWith('•'))
        .map(line => line.replace('•', '').trim());
      setStrengths(strengthsList);
    }

    // Extract issues from ACTION PLAN section
    const actionPlanMatch = reportText.match(/🎯 您的行動計畫\n━+\n依序專注在這些項目：\n\n((?:.|\n)+?)(?:\n\n━|$)/);
    const parsedIssues = [];

    if (actionPlanMatch) {
      const actionItems = actionPlanMatch[1];

      // Extract critical issues
      const criticalMatches = actionItems.matchAll(/\d+\. 🚨 優先修正：(.+?)\n {3}→ (.+?)(?:\n\n|\n\d|$)/gs);
      for (const match of criticalMatches) {
        parsedIssues.push({
          severity: 'critical',
          description: match[1].trim(),
          fix: match[2].trim()
        });
      }

      // Extract moderate issues
      const moderateMatches = actionItems.matchAll(/\d+\. ⚠️ 待加強：(.+?)\n {3}→ (.+?)(?:\n\n|\n\d|$)/gs);
      for (const match of moderateMatches) {
        parsedIssues.push({
          severity: 'moderate',
          description: match[1].trim(),
          fix: match[2].trim()
        });
      }
    }

    setIssues(parsedIssues);
  };

  const videoUrl = `${API_BASE_URL}/result/${videoId}/video`;

  const getScoreEmoji = (score) => {
    if (score >= 9) return '🏆';
    if (score >= 7) return '🎯';
    if (score >= 5) return '👍';
    return '💪';
  };

  const getScoreFeedback = (score) => {
    if (score >= 9) return '奧運等級的動作！';
    if (score >= 7) return '技術很扎實！';
    if (score >= 5) return '持續進步中！';
    return '還有進步空間！';
  };

  return (
    <div>
      {/* Hero Section with Score */}
      <div className="card" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', textAlign: 'center' }}>
        <h2 style={{ fontSize: '2rem', marginBottom: '20px', color: 'white' }}>
          🏊‍♂️ 您的划水分析
        </h2>

        {!loading && score !== null && (
          <div style={{ margin: '30px 0' }}>
            <div style={{
              display: 'inline-block',
              background: 'rgba(255,255,255,0.2)',
              borderRadius: '20px',
              padding: '30px 50px',
              backdropFilter: 'blur(10px)'
            }}>
              <div style={{ fontSize: '4rem', marginBottom: '10px' }}>
                {getScoreEmoji(score)}
              </div>
              <div style={{ fontSize: '3.5rem', fontWeight: 'bold', margin: '10px 0' }}>
                {score}/10
              </div>
              <div style={{ fontSize: '1.3rem', opacity: 0.9 }}>
                {getScoreFeedback(score)}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Quick Insight */}
      {!loading && quickInsight && (
        <div className="card" style={{
          background: 'linear-gradient(135deg, #E3F2FD 0%, #F3E5F5 100%)',
          border: '2px solid #667eea'
        }}>
          <h3 style={{ fontSize: '1.5rem', marginBottom: '15px', color: '#333' }}>
            📊 快速洞察
          </h3>
          <p style={{
            fontSize: '1.2rem',
            lineHeight: '1.7',
            color: '#555',
            margin: 0
          }}>
            {quickInsight}
          </p>
        </div>
      )}

      {/* Biggest Red Flag */}
      {!loading && biggestRedFlag && (
        <div className="card" style={{
          background: '#FFF3F3',
          border: '3px solid #D32F2F'
        }}>
          <h3 style={{ fontSize: '1.6rem', marginBottom: '15px', color: '#D32F2F' }}>
            🚨 最大警訊
          </h3>
          <div style={{
            background: 'white',
            borderRadius: '12px',
            padding: '20px',
            marginBottom: '15px'
          }}>
            <p style={{
              fontSize: '1.15rem',
              color: '#333',
              margin: '0 0 10px 0',
              fontWeight: '500'
            }}>
              ⚠️  {biggestRedFlag.issue}
            </p>
          </div>
          <div style={{
            background: 'rgba(255,255,255,0.7)',
            borderRadius: '12px',
            padding: '20px'
          }}>
            <h4 style={{ fontSize: '1.1rem', marginBottom: '10px', color: '#36B37E' }}>
              💡 如何改善：
            </h4>
            <p style={{
              fontSize: '1.05rem',
              color: '#555',
              margin: 0,
              lineHeight: '1.6'
            }}>
              {biggestRedFlag.fix}
            </p>
          </div>
        </div>
      )}

      {/* What's Working */}
      {!loading && strengths.length > 0 && (
        <div className="card" style={{
          background: '#F1F8F4',
          border: '2px solid #36B37E'
        }}>
          <h3 style={{ fontSize: '1.5rem', marginBottom: '20px', color: '#36B37E' }}>
            ✅ 做得好的地方
          </h3>
          <div style={{ maxWidth: '700px', margin: '0 auto' }}>
            {strengths.map((strength, idx) => (
              <div
                key={idx}
                style={{
                  background: 'white',
                  borderRadius: '12px',
                  padding: '15px 20px',
                  marginBottom: '10px',
                  fontSize: '1.05rem',
                  color: '#333',
                  display: 'flex',
                  alignItems: 'center'
                }}
              >
                <span style={{ color: '#36B37E', marginRight: '10px', fontSize: '1.3rem' }}>✓</span>
                {strength}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Video Section with Auto-Play */}
      <div className="card">
        <h3 style={{ textAlign: 'center', marginBottom: '20px', fontSize: '1.5rem' }}>
          📹 標註分析影片
        </h3>

        <div style={{
          maxWidth: '800px',
          margin: '0 auto',
          borderRadius: '12px',
          overflow: 'hidden',
          boxShadow: '0 8px 24px rgba(0,0,0,0.15)'
        }}>
          <video
            ref={videoRef}
            controls
            autoPlay  // AUTO-PLAY!
            muted     // Muted to allow autoplay
            loop
            style={{ width: '100%', display: 'block' }}
          >
            <source src={videoUrl} type="video/mp4" />
            您的瀏覽器不支援影片播放。
          </video>
        </div>

        <div style={{ textAlign: 'center', marginTop: '20px' }}>
          <a
            href={videoUrl}
            download
            className="button"
            style={{
              textDecoration: 'none',
              display: 'inline-block',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
            }}
          >
            📥 下載影片
          </a>
        </div>
      </div>

      {/* What to Fix - Action Items */}
      {!loading && issues.length > 0 && (
        <div className="card">
          <h3 style={{ fontSize: '1.8rem', marginBottom: '25px', textAlign: 'center' }}>
            🎯 您的行動計畫
          </h3>

          <div style={{ maxWidth: '700px', margin: '0 auto' }}>
            {issues.map((issue, idx) => (
              <div
                key={idx}
                style={{
                  background: issue.severity === 'critical' ? '#FFF3F3' : '#FFF9E6',
                  border: `2px solid ${issue.severity === 'critical' ? '#D32F2F' : '#FFAB00'}`,
                  borderRadius: '12px',
                  padding: '25px 20px 20px 20px',
                  marginBottom: '15px',
                  position: 'relative'
                }}
              >
                <div style={{
                  position: 'absolute',
                  top: '-12px',
                  left: '20px',
                  background: issue.severity === 'critical' ? '#D32F2F' : '#FFAB00',
                  color: 'white',
                  padding: '4px 12px',
                  borderRadius: '12px',
                  fontSize: '0.85rem',
                  fontWeight: 'bold'
                }}>
                  {idx + 1}. {issue.severity === 'critical' ? '🚨 優先修正' : '⚠️  待加強'}
                </div>

                <div style={{ marginTop: '5px', fontSize: '1.1rem', lineHeight: '1.6', marginBottom: '15px' }}>
                  {issue.description}
                </div>

                {issue.fix && (
                  <div style={{
                    background: 'rgba(255,255,255,0.7)',
                    borderRadius: '8px',
                    padding: '12px 15px',
                    borderLeft: '3px solid #36B37E'
                  }}>
                    <div style={{ fontSize: '0.9rem', fontWeight: 'bold', marginBottom: '5px', color: '#36B37E' }}>
                      💡 如何改善：
                    </div>
                    <div style={{ fontSize: '1rem', color: '#555', lineHeight: '1.6' }}>
                      {issue.fix}
                    </div>
                  </div>
                )}
              </div>
            ))}

            <div style={{
              background: '#E3F2FD',
              borderRadius: '12px',
              padding: '20px',
              marginTop: '25px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '1.2rem', marginBottom: '10px' }}>
                💡 <strong>小提醒：</strong>
              </div>
              <div style={{ fontSize: '1rem', color: '#555', lineHeight: '1.6' }}>
一次專注改善<strong>一個問題</strong>，改善後再重新拍攝分析一次，
                小幅進步會快速累積！ 🚀
              </div>
            </div>
          </div>
        </div>
      )}

      {/* No Issues - Celebration */}
      {!loading && issues.length === 0 && score >= 8 && (
        <div className="card" style={{ textAlign: 'center', background: '#F1F8F4' }}>
          <div style={{ fontSize: '4rem', marginBottom: '20px' }}>🎉</div>
          <h3 style={{ fontSize: '2rem', color: '#36B37E', marginBottom: '15px' }}>
            技術非常好！
          </h3>
          <p style={{ fontSize: '1.2rem', color: '#666' }}>
            您的自由式動作很扎實，繼續保持！
          </p>
        </div>
      )}

      {/* Full Technical Report (Collapsible) */}
      <div className="card">
        <details style={{ cursor: 'pointer' }}>
          <summary style={{
            fontSize: '1.3rem',
            fontWeight: 'bold',
            padding: '10px',
            userSelect: 'none',
            background: '#F4F6FF',
            borderRadius: '8px'
          }}>
            📊 完整技術報告
          </summary>

          <div style={{ marginTop: '20px' }}>
            {loading && (
              <div style={{ textAlign: 'center' }}>
                <div className="loading-spinner"></div>
                <p>載入詳細分析中...</p>
              </div>
            )}
            {error && (
              <div className="error-message">{error}</div>
            )}
            {!loading && !error && (
              <div className="report-content" style={{
                whiteSpace: 'pre-wrap',
                background: 'white',
                padding: '20px',
                borderRadius: '8px',
                fontSize: '0.95rem',
                lineHeight: '1.7'
              }}>
                {report}
              </div>
            )}
          </div>
        </details>
      </div>

      {/* Action Button */}
      <div style={{ textAlign: 'center', marginTop: '30px' }}>
        <button
          className="button"
          onClick={onReset}
          style={{
            fontSize: '1.2rem',
            padding: '15px 40px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
          }}
        >
          🔄 分析另一支影片
        </button>
      </div>
    </div>
  );
}

export default ResultsComponent;
