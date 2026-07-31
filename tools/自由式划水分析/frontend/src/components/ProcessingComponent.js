import React, { useState, useEffect } from 'react';

import { API_BASE_URL } from '../config';

const processingMessages = [
  "🔍 正在偵測身體動作...",
  "🤖 AI 正在觀察您的泳姿...",
  "📐 正在計算手臂角度...",
  "🏊‍♂️ 正在檢查划水節奏...",
  "📊 正在以教練視角分析技術...",
  "🎬 正在製作標註影片...",
  "✨ 正在加上視覺標記..."
];

function ProcessingComponent({ videoId, onComplete }) {
  const [status, setStatus] = useState({ progress: 0, message: '開始分析...' });
  const [error, setError] = useState(null);
  const [funMessage, setFunMessage] = useState(processingMessages[0]);

  useEffect(() => {
    // Change fun messages periodically
    const messageInterval = setInterval(() => {
      const randomMessage = processingMessages[Math.floor(Math.random() * processingMessages.length)];
      setFunMessage(randomMessage);
    }, 3000);

    const pollStatus = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/status/${videoId}`);
        const data = await response.json();

        if (response.ok) {
          setStatus(data);

          if (data.status === 'completed') {
            clearInterval(pollStatus);
            clearInterval(messageInterval);
            setTimeout(() => onComplete(), 1000);
          } else if (data.status === 'failed') {
            clearInterval(pollStatus);
            clearInterval(messageInterval);
            setError(data.error || '分析失敗，請再試一次。');
          }
        }
      } catch (err) {
        console.error('Error polling status:', err);
      }
    }, 2000);

    return () => {
      clearInterval(pollStatus);
      clearInterval(messageInterval);
    };
  }, [videoId, onComplete]);

  const getStageEmoji = (progress) => {
    if (progress < 20) return '🚀';
    if (progress < 50) return '🔍';
    if (progress < 70) return '📊';
    if (progress < 90) return '🎬';
    return '✅';
  };

  return (
    <div>
      <div className="card" style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '4rem', marginBottom: '20px', animation: 'float 3s ease-in-out infinite' }}>
          {getStageEmoji(status.progress || 0)}
        </div>
        <h2 style={{ fontSize: '2rem', marginBottom: '15px', color: 'white' }}>
          分析中...
        </h2>
        <p style={{ fontSize: '1.2rem', opacity: 0.9 }}>
          {funMessage}
        </p>
      </div>

      {!error && (
        <div className="card">
          <div className="progress-container">
            <div className="progress-bar" style={{ height: '40px', borderRadius: '20px' }}>
              <div
                className="progress-fill"
                style={{
                  width: `${status.progress || 0}%`,
                  background: 'linear-gradient(90deg, #667eea, #764ba2)',
                  fontSize: '1.1rem',
                  fontWeight: 'bold'
                }}
              >
                {status.progress || 0}%
              </div>
            </div>

            <div style={{
              textAlign: 'center',
              marginTop: '25px',
              fontSize: '1.1rem',
              color: '#555'
            }}>
              {status.message || '處理中...'}
            </div>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '15px',
            marginTop: '30px'
          }}>
            {[
              { icon: '🔍', label: '偵測姿勢', done: status.progress >= 20 },
              { icon: '📐', label: '量測角度', done: status.progress >= 50 },
              { icon: '📊', label: '分析動作', done: status.progress >= 70 },
              { icon: '🎬', label: '產生影片', done: status.progress >= 90 },
              { icon: '📝', label: '撰寫報告', done: status.progress >= 100 }
            ].map((step, idx) => (
              <div
                key={idx}
                style={{
                  background: step.done ? '#E8F5E9' : '#F5F5F5',
                  border: `2px solid ${step.done ? '#36B37E' : '#E0E0E0'}`,
                  borderRadius: '12px',
                  padding: '15px',
                  textAlign: 'center',
                  transition: 'all 0.3s ease',
                  transform: step.done ? 'scale(1.05)' : 'scale(1)'
                }}
              >
                <div style={{ fontSize: '2rem', marginBottom: '8px' }}>
                  {step.done ? '✅' : step.icon}
                </div>
                <div style={{
                  fontSize: '0.9rem',
                  color: step.done ? '#36B37E' : '#666',
                  fontWeight: step.done ? 'bold' : 'normal'
                }}>
                  {step.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {error && (
        <div className="card">
          <div style={{
            background: '#FFF3F3',
            border: '2px solid #D32F2F',
            borderRadius: '12px',
            padding: '30px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '4rem', marginBottom: '20px' }}>😕</div>
            <h3 style={{ color: '#D32F2F', marginBottom: '15px' }}>
              發生問題
            </h3>
            <p style={{ color: '#666', fontSize: '1.1rem' }}>{error}</p>
          </div>
        </div>
      )}

      <div style={{
        background: 'linear-gradient(135deg, #E3F2FD 0%, #F3E5F5 100%)',
        borderRadius: '16px',
        padding: '25px',
        marginTop: '20px',
        border: '2px solid #667eea'
      }}>
        <h4 style={{ marginBottom: '15px', fontSize: '1.2rem', color: '#333' }}>
          ⚡ 背後正在進行的分析
        </h4>
        <ul style={{ margin: 0, paddingLeft: '25px', lineHeight: '1.9', color: '#555' }}>
          <li>AI 在每一影格辨識 33 個身體關節點</li>
          <li>計算關節角度、身體轉肩幅度與時間節奏</li>
          <li>與理想自由式動作標準進行比對</li>
          <li>產生標註骨架與角度的分析影片</li>
          <li>產生個人化的改善建議</li>
        </ul>
        <div style={{
          background: 'rgba(255,255,255,0.7)',
          borderRadius: '8px',
          padding: '15px',
          marginTop: '15px',
          fontSize: '0.95rem',
          color: '#666'
        }}>
          <strong>⏱️ 一般耗時：</strong>約 30 秒到 2 分鐘
        </div>
      </div>
    </div>
  );
}

export default ProcessingComponent;
