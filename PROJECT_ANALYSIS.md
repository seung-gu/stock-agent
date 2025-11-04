# 프로젝트 분석 및 개선 제안

**분석 일자**: 2025년 10월  
**현재 성능**: 약 8개 에이전트, 125-150개 툴 호출, 60-90초 소요

---

## 📊 프로젝트 구조 분석

### 현재 아키텍처

```
MarketReportAgent (최상위 Orchestrator)
├── LiquidityAgent (병렬 실행)
│   ├── TNXAgent (^TNX)
│   ├── NFCIAgent (NFCI)
│   └── DXAgent (DX=F)
├── BroadIndexAgent (병렬 실행)
│   ├── EquityTrendAgent (^GSPC)
│   ├── EquityTrendAgent (^IXIC)
│   ├── EquityTrendAgent (^DJI)
│   └── MarketBreadthAgent (S5FI/S5TH)
└── EquityTrendAgent x 5개 (병렬 실행)
    ├── IAU
    ├── QLD
    ├── NVDA
    ├── MSFT
    └── COPX
```

**총 에이전트**: 약 8개 (실제 실행되는 최상위 에이전트 기준)  
**총 툴 호출**: 125-150개 (에이전트당 평균 15-19개 툴 호출)

---

## 🔍 주요 성능 병목 지점

### 1. **데이터 소스 인스턴스 생성 오버헤드**

**문제점**:
- `get_data_source()`가 매번 새로운 인스턴스를 생성
- 캐시는 클래스 레벨이지만, 인스턴스 생성 비용이 있음

**현재 코드**:
```python
# agent_tools.py - 매 툴 호출마다 실행
src = get_data_source(source)  # → 매번 새 인스턴스
```

**영향**: 각 툴 호출마다 불필요한 객체 생성

---

### 2. **LLM 라운드트립 빈도**

**문제점**:
- 각 툴 호출마다 LLM이 다음 툴을 결정하기 위해 대기
- 에이전트가 순차적으로 툴을 호출 (병렬 불가)

**현재 흐름**:
```
LLM → fetch_data() → LLM → analyze_OHLCV_data() → LLM → generate_chart() → ...
```

**영향**: 툴당 평균 0.5-0.7초 (LLM 대기 시간 포함)

---

### 3. **중복 데이터 페칭**

**문제점**:
- 같은 심볼에 대해 여러 에이전트가 독립적으로 데이터 페칭
- 캐시는 있지만, 첫 번째 에이전트가 캐시를 채우기 전까지는 중복 호출 가능

**예시**:
- `EquityTrendAgent("^GSPC")`와 `BroadIndexAgent` 내부의 `EquityTrendAgent("^GSPC")`가 동시 실행 시 중복 페칭

**영향**: 네트워크 I/O 중복

---

### 4. **InvestingSource 스크래핑 오버헤드**

**문제점**:
- `InvestingSource`는 항상 스크래핑을 수행 (캐시 검증을 위해)
- 파일 기반 캐시이지만, 매번 HTTP 요청 발생

**현재 코드**:
```python
# 항상 스크래핑 실행
scraped = self._scrape_data(url)  # HTTP 요청
```

**영향**: MarketBreadthAgent 실행 시 추가 지연

---

### 5. **Synthesis Agent의 긴 컨텍스트 처리**

**문제점**:
- 각 Orchestrator의 Synthesis Agent가 모든 sub-agent 결과를 합침
- MarketReportAgent는 최종적으로 모든 결과를 다시 합침
- 긴 컨텍스트 = 느린 LLM 응답

**영향**: 최종 리포트 생성 시 추가 시간 소요

---

## 💡 개선 제안

### 우선순위 1: 데이터 소스 싱글톤 패턴

**목적**: 인스턴스 생성 오버헤드 제거

**구현**:
```python
# utils/data_sources.py
_source_instances: dict[str, DataSource] = {}

def get_data_source(source: str) -> DataSource:
    """Get data source by name (singleton pattern)."""
    source_lower = source.lower()
    if source_lower not in _source_instances:
        sources = {
            'yfinance': YFinanceSource,
            'fred': FREDSource,
            'investing': InvestingSource,
            'finnhub': FinnhubSource,
        }
        _source_instances[source_lower] = sources[source_lower]()
    return _source_instances[source_lower]
```

**예상 효과**: 툴 호출당 약 0.01초 절약 (총 1-2초 절약)

---

### 우선순위 2: 프리페치 전략 개선

**목적**: 병렬 실행 전에 공통 데이터를 미리 페칭

**구현**:
```python
# run_market_report.py
async def pre_fetch_common_data():
    """Pre-fetch common data before agent execution."""
    common_symbols = {
        'yfinance': ['^TNX', 'DX=F', '^GSPC', '^IXIC', '^DJI'],
        'fred': ['NFCI'],
        'investing': ['S5FI', 'S5TH']
    }
    
    tasks = []
    for source, symbols in common_symbols.items():
        src = get_data_source(source)
        for symbol in symbols:
            # 최장 기간으로 페칭 (1y 또는 5y)
            period = '5y' if source == 'yfinance' else '1y'
            tasks.append(src.fetch_data(symbol, period))
    
    await asyncio.gather(*tasks)

# run() 메서드 시작 전에 호출
await pre_fetch_common_data()
```

**예상 효과**: 약 5-10초 절약 (병렬 페칭 + 캐시 히트)

---

### 우선순위 3: InvestingSource 캐시 검증 최적화

**목적**: 불필요한 스크래핑 방지

**구현**:
```python
# utils/data_sources.py - InvestingSource
async def fetch_data(self, symbol: str, period: str = None) -> dict[str, Any]:
    local, is_validated = self._load_local_cache(symbol)
    
    # 검증된 캐시가 있고 오늘 날짜 데이터가 있으면 스크래핑 스킵
    if is_validated and local is not None:
        today = datetime.now().date()
        if today in local.index.date:
            print(f"[INVESTING][CACHE] Using validated cache, skipping scrape")
            # 스크래핑 없이 캐시 사용
            merged = local
        else:
            # 오늘 데이터 없으면 스크래핑
            scraped = self._scrape_data(url)
            # ... 기존 로직
    else:
        # 기존 로직
```

**예상 효과**: MarketBreadthAgent 실행 시 약 2-3초 절약

---

### 우선순위 4: 툴 호출 배치화

**목적**: LLM 라운드트립 감소 (가능한 경우)

**구현**:
- 현재는 LLM이 각 툴을 순차 호출하므로 배치화 어려움
- 대신 에이전트 인스트럭션 최적화로 불필요한 툴 호출 방지

**인스트럭션 개선**:
```python
# trend_agent.py
instructions = f"""
...
EFFICIENCY RULES:
- Call fetch_data() ONCE for the longest period
- Reuse cached data for all subsequent tool calls
- Do NOT call fetch_data() multiple times for the same symbol/period
- Combine multiple analyses in single tool calls when possible
...
"""
```

**예상 효과**: 약 5-10% 툴 호출 감소

---

### 우선순위 5: Synthesis Agent 컨텍스트 축소

**목적**: 긴 컨텍스트 처리 시간 단축

**구현**:
```python
# orchestrator_agent.py
def _create_synthesis_prompt(self) -> str:
    """Create synthesis prompt with summarized sub-results."""
    prompt_parts = ["Please synthesize the following analyses:", ""]
    
    for agent, result in zip(self.sub_agents, self.sub_agent_results):
        result_text = result.final_output if hasattr(result, 'final_output') else str(result)
        
        # 요약 전략: 긴 내용은 요약, 짧은 내용은 그대로
        if len(result_text) > 2000:
            # 요약 에이전트 호출 또는 간단한 요약
            result_text = self._summarize_result(result_text)
        
        prompt_parts.append(f"--- {agent.agent_name} ---")
        prompt_parts.append(result_text)
        prompt_parts.append("")
    
    return "\n".join(prompt_parts)
```

**예상 효과**: Synthesis 단계에서 약 5-10초 절약

---

### 우선순위 6: 에이전트 중복 제거

**문제점**:
- `BroadIndexAgent` 내부에 `EquityTrendAgent("^GSPC")` 등이 있음
- 만약 `MarketReportAgent`에도 동일한 심볼을 분석하는 에이전트가 있다면 중복

**해결**:
- 에이전트 설계 재검토하여 중복 제거
- 또는 결과 공유 메커니즘 도입

**예상 효과**: 중복 제거 시 약 10-20% 시간 절약

---

## 📈 예상 성능 개선 효과

| 개선 항목 | 예상 절약 시간 | 구현 난이도 |
|---------|--------------|------------|
| 데이터 소스 싱글톤 | 1-2초 | 낮음 |
| 프리페치 전략 | 5-10초 | 중간 |
| InvestingSource 최적화 | 2-3초 | 낮음 |
| 툴 호출 최적화 | 3-5초 | 중간 |
| Synthesis 최적화 | 5-10초 | 중간 |
| 중복 제거 | 5-15초 | 높음 |
| **총합** | **21-45초** | - |

**목표**: 60-90초 → **30-50초** (약 40-50% 개선)

---

## 🏗️ 추가 개선 아이디어 (장기)

### 1. **스트리밍 응답**
- LLM 응답을 스트리밍하여 첫 번째 결과부터 처리 시작
- 사용자 경험 개선 (대기 시간 감소)

### 2. **캐시 TTL 도입**
- 데이터 소스 캐시에 TTL(Time To Live) 추가
- 오래된 데이터 자동 갱신

### 3. **모니터링 및 프로파일링**
- 각 에이전트/툴 호출 시간 측정
- 병목 지점 자동 감지

### 4. **병렬 툴 호출 (가능한 경우)**
- 독립적인 툴 호출을 병렬 실행
- LLM 프레임워크 제약 확인 필요

---

## ⚠️ 주의사항

1. **캐시 일관성**: 싱글톤 패턴 도입 시 멀티스레드 환경에서의 안전성 확보
2. **에러 처리**: 프리페치 실패 시 기존 로직으로 폴백
3. **테스트**: 각 개선 사항에 대한 회귀 테스트 필수

---

## 📝 실행 계획

1. **1단계** (빠른 효과): 데이터 소스 싱글톤 + InvestingSource 최적화 ✅ **완료**
2. **2단계** (중간 효과): 프리페치 전략 구현 ✅ **완료**
3. **3단계** (장기 효과): Synthesis 최적화 및 중복 제거 (추후 구현)

각 단계마다 성능 측정 및 검증 필요.

---

## ✅ 구현 완료된 개선 사항

### 1. 데이터 소스 싱글톤 패턴
- **파일**: `src/utils/data_sources.py`
- **변경사항**: `get_data_source()` 함수가 싱글톤 패턴으로 동작하여 인스턴스 재사용
- **효과**: 툴 호출당 객체 생성 오버헤드 제거

### 2. InvestingSource 캐시 최적화
- **파일**: `src/utils/data_sources.py` - `InvestingSource.fetch_data()`
- **변경사항**: 검증된 캐시에 오늘 날짜 데이터가 있으면 스크래핑 스킵
- **효과**: 동일 일자 내 반복 실행 시 스크래핑 오버헤드 제거

### 3. 프리페치 전략 구현
- **파일**: `src/run_market_report.py`
- **변경사항**: 에이전트 실행 전 공통 데이터를 병렬로 미리 페칭
- **효과**: 캐시 히트율 향상, 중복 API 호출 감소

---

## 🧪 테스트 권장사항

다음 명령어로 성능 개선 효과를 측정하세요:

```bash
# Before/After 비교를 위해 실행 시간 측정
time python -m src.run_market_report
```

또는 Python에서 직접 측정:

```python
import time
import asyncio
from src.run_market_report import run_market_report

start = time.time()
result = asyncio.run(run_market_report())
elapsed = time.time() - start
print(f"⏱️ Total execution time: {elapsed:.2f} seconds")
```
