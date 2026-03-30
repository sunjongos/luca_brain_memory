import React from 'react';
import { PlayCircle, Ear, Brain, Activity, CheckCircle, Volume2, Mic, ArrowRight } from 'lucide-react';

function App() {
  return (
    <>
      <div className="bg-blob-1"></div>
      <div className="bg-blob-2"></div>

      {/* ── Navbar ── */}
      <nav className="glass" style={{ position: 'fixed', top: 0, width: '100%', zIndex: 50, padding: '20px 0' }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, letterSpacing: '-0.5px' }}>
            Sound <span className="text-gradient">Tuning</span>
          </h1>
          <button className="btn-primary" style={{ padding: '10px 24px', fontSize: '1rem' }}>무료 체험하기</button>
        </div>
      </nav>

      {/* ── Hero Section ── */}
      <section style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', paddingTop: '100px' }}>
        <div className="container" style={{ textAlign: 'center', position: 'relative' }}>

          <div className="animate-float" style={{ display: 'inline-flex', alignItems: 'center', background: 'rgba(99,102,241,0.1)', padding: '8px 16px', borderRadius: '30px', border: '1px solid rgba(99,102,241,0.3)', marginBottom: '30px', color: '#a855f7', fontWeight: 600 }}>
            <Activity size={18} style={{ marginRight: '8px' }} />
            <span>0.1초 만에 묻고 답하는 진짜 영어의 시작</span>
          </div>

          <h1 style={{ fontSize: '4.5rem', fontWeight: 800, lineHeight: 1.2, marginBottom: '24px', letterSpacing: '-1.5px' }}>
            귀가 뚫리는 기적은 없다.<br />
            '소리 블록'으로 입과 귀를 <span className="text-gradient">동시에 튜닝하라.</span>
          </h1>

          <p style={{ fontSize: '1.25rem', color: 'var(--text-muted)', maxWidth: '750px', margin: '0 auto 40px', lineHeight: 1.8 }}>
            무작정 따라 하는 섀도잉과 단어 암기는 이제 그만.<br />
            영어가 안 들리는 진짜 이유인 <strong>'소리의 갭(Gap)'</strong>을 부수고 원어민처럼 소통하세요.
          </p>

          <div style={{ display: 'flex', gap: '20px', justifyContent: 'center' }}>
            <button className="btn-primary animate-glow" style={{ display: 'flex', alignItems: 'center' }}>
              구독 시작하기 <ArrowRight style={{ marginLeft: '10px' }} size={20} />
            </button>
            <button className="glass" style={{ padding: '16px 32px', fontSize: '1.125rem', fontWeight: 600, color: 'white', border: '1px solid rgba(255,255,255,0.2)' }}>
              튜닝 원리 보기
            </button>
          </div>
        </div>
      </section>

      {/* ── Problem Section (Pain Points) ── */}
      <section style={{ backgroundColor: 'rgba(0,0,0,0.3)' }}>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: '60px' }}>
            <h2 style={{ fontSize: '2.5rem', fontWeight: 700, marginBottom: '16px' }}>당신이 겪고 있는 영어의 한계</h2>
            <p className="text-gradient" style={{ fontSize: '1.125rem', fontWeight: 600 }}>왜 단어를 다 아는데 들리지 않고 말이 안 나올까요?</p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '30px' }}>
            {/* PP 1 */}
            <div className="glass-card">
              <div style={{ background: 'rgba(99,102,241,0.1)', width: '60px', height: '60px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '20px' }}>
                <Ear color="#818cf8" size={32} />
              </div>
              <h3 style={{ fontSize: '1.5rem', marginBottom: '16px' }}>들리지 않는 '리스닝의 한계'</h3>
              <p style={{ color: 'var(--text-muted)' }}>머릿속 정박자와 원어민의 실제 뭉개지는 연음·엇박자 사이의 거대한 갭(Gap) 때문에 눈으로 아는 문장도 귀로는 놓칩니다.</p>
            </div>
            {/* PP 2 */}
            <div className="glass-card">
              <div style={{ background: 'rgba(168,85,247,0.1)', width: '60px', height: '60px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '20px' }}>
                <Brain color="#c084fc" size={32} />
              </div>
              <h3 style={{ fontSize: '1.5rem', marginBottom: '16px' }}>단어만 둥둥 떠다니는 '버퍼링'</h3>
              <p style={{ color: 'var(--text-muted)' }}>개별 단어를 문법에 맞춰 조립하려다 보니 뇌의 작업 기억 한계를 초과하여 결국 입 밖으로 문장이 나오지 않습니다.</p>
            </div>
            {/* PP 3 */}
            <div className="glass-card">
              <div style={{ background: 'rgba(236,72,153,0.1)', width: '60px', height: '60px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '20px' }}>
                <Mic color="#f472b6" size={32} />
              </div>
              <h3 style={{ fontSize: '1.5rem', marginBottom: '16px' }}>무작정 섀도잉의 실패</h3>
              <p style={{ color: 'var(--text-muted)' }}>입, 턱, 혀의 정확한 위치나 리듬에 대한 이론적 이해 없이 청각형 학습만 고집하여 발음 콤플렉스를 극복하지 못합니다.</p>
            </div>
          </div>
        </div>
      </section>

      {/* ── Solution Section (Advantages) ── */}
      <section>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: '80px' }}>
            <h2 style={{ fontSize: '3rem', fontWeight: 800, marginBottom: '20px' }}>오직 <span className="text-gradient">Sound Tuning</span>만의 압도적 장점</h2>
            <p style={{ fontSize: '1.25rem', color: 'var(--text-muted)' }}>수학 공식처럼 떨어지는 소리의 법칙을 몸으로 체득하세요.</p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '60px' }}>
            <div style={{ display: 'flex', gap: '40px', alignItems: 'center' }}>
              <div style={{ flex: 1 }} className="glass-card">
                <Volume2 size={48} color="#818cf8" style={{ marginBottom: '20px' }} />
                <h3 style={{ fontSize: '2rem', marginBottom: '20px' }}>1. 원어민의 소리 작동 원리 체득</h3>
                <p style={{ fontSize: '1.125rem', color: 'var(--text-muted)', lineHeight: 1.8 }}>뱉는 소리(내용어)와 먹는 소리(기능어)를 구분하고, 박수를 치며 영어 특유의 강세와 엇박자 리듬을 체득합니다. 조음 기관 위치를 명확히 잡아주어 내가 스스로 낼 수 있는 소리로 만들고 리스닝을 완성합니다.</p>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '40px', alignItems: 'center', flexDirection: 'row-reverse' }}>
              <div style={{ flex: 1 }} className="glass-card">
                <PlayCircle size={48} color="#c084fc" style={{ marginBottom: '20px' }} />
                <h3 style={{ fontSize: '2rem', marginBottom: '20px' }}>2. '소리 블록'을 통한 0.1초 스피킹</h3>
                <p style={{ fontSize: '1.125rem', color: 'var(--text-muted)', lineHeight: 1.8 }}>원어민이 무의식중에 숨 쉬듯 사용하는 의미 단위 덩어리입니다. [시작] + [코어] + [디테일] 3단계 블록 조합만으로 긴 문장도 단 2~3번의 생각만으로 버퍼링 없이 즉시 뱉어낼 수 있습니다.</p>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '40px', alignItems: 'center' }}>
              <div style={{ flex: 1 }} className="glass-card">
                <CheckCircle size={48} color="#f472b6" style={{ marginBottom: '20px' }} />
                <h3 style={{ fontSize: '2rem', marginBottom: '20px' }}>3. 시각형 학습자 맞춤형 이론 기반 훈련</h3>
                <p style={{ fontSize: '1.125rem', color: 'var(--text-muted)', lineHeight: 1.8 }}>청각형 언어 천재들이 아닌 보통 사람들을 위해, 소리가 왜 다르게 나는지 연음과 소리 규칙을 이성적으로 이해시킵니다. 머리로 납득한 뒤 입과 몸으로 훈련하여 가장 빠르고 확실한 성장을 보장합니다.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── CTA / Pricing Placeholder ── */}
      <section style={{ textAlign: 'center', background: 'linear-gradient(180deg, rgba(15,17,21,1) 0%, rgba(30,27,75,1) 100%)' }}>
        <div className="container" style={{ padding: '80px 0' }}>
          <h2 style={{ fontSize: '3.5rem', fontWeight: 800, marginBottom: '24px' }}>진짜 당신의 영어를 만날 시간</h2>
          <p style={{ fontSize: '1.25rem', color: 'var(--text-muted)', marginBottom: '40px' }}>지금 바로 구독하고 소리 블록 훈련을 시작하세요.</p>
          <button className="btn-primary animate-glow" style={{ fontSize: '1.5rem', padding: '20px 60px' }}>지금 바로 결제하기 (PayPal)</button>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer style={{ padding: '40px 0', textAlign: 'center', borderTop: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-muted)' }}>
        <p>© 2026 Sound Tuning English. Powered by Luca Super Agent.</p>
      </footer>
    </>
  );
}

export default App;
