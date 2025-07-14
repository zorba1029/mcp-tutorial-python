# MCP Context 기능 실행 가이드

이 문서는 MCP의 Context 기능을 테스트하고 실행하는 방법을 설명합니다.

## Context란?

Context는 MCP 도구(tool)가 클라이언트와 상호작용할 수 있게 해주는 특별한 객체입니다. 다음과 같은 기능을 제공합니다:

- **로깅**: 다양한 레벨의 로그 메시지 전송
- **진행 상황 보고**: 작업 진행률을 실시간으로 알림
- **사용자 입력 요청**: 추가 정보나 선택 요청 (Elicitation)
- **세션 관리**: 리소스/도구 목록 변경 알림

## 주요 파일

### Context 기능 데모 (권장) ✅

1. **`context-simple-demo.py`** - Context 기본 기능을 보여주는 서버
   - 로깅 (debug, info, warning, error)
   - 진행 상황 보고
   - 작업 상태 추적

2. **`test-simple-context.py`** - 위 서버를 테스트하는 클라이언트
   - 로그 수집 및 표시
   - 다양한 도구 테스트
   - 통계 출력

### Elicitation 기능 데모 ✨

3. **`elicitation-server.py`** - Elicitation 기능을 보여주는 서버
   - 사용자 입력 요청 (Elicitation)
   - 구조화된 데이터 입력
   - 다단계 사용자 상호작용
   - 예약, 주문, 알림 설정 시나리오

4. **`test-elicitation.py`** - Elicitation 서버를 테스트하는 클라이언트
   - 자동 테스트 모드
   - 대화형 테스트 모드
   - 로그 수집 및 통계

## 실행 방법

### 1. 디렉토리 이동

```bash
cd ch05-advanced-topicss/04_mcp-root-contexts
```

### 2. Context 데모 실행

```bash
# Context 기본 기능 테스트 (서버 자동 시작)
uv run python test-simple-context.py
```

### 3. Elicitation 데모 실행

```bash
# 자동 테스트 모드
uv run python test-elicitation.py

# 대화형 테스트 모드
uv run python test-elicitation.py interactive
```

### 3. 실행 결과 예시

```
🚀 간단한 Context 테스트 시작
============================================================
✅ 서버에 연결되었습니다.

============================================================
1️⃣ 간단한 작업 실행 (3초)
============================================================
ℹ️ [INFO] 작업 시작: 데이터 백업
🔍 [DEBUG] 작업 ID: task_1752511589.428382, 예상 시간: 3초
ℹ️ [INFO] 작업 완료: 데이터 백업

✅ 결과: '데이터 백업' 작업이 3초 만에 완료되었습니다
```

### 4. Elicitation 실행 결과 예시

```
🚀 자동 테스트 모드로 실행합니다...
============================================================
✅ 서버에 연결되었습니다.

🚀 Elicitation 서버 테스트 시작

============================================================
1️⃣ 서버 정보 확인
============================================================
사용 가능한 도구: 3개
  - book_table: 레스토랑 테이블 예약 with Elicitation
  - process_order: 주문 처리 with 배송 옵션 선택
  - configure_notification: 알림 설정 with 다단계 Elicitation

============================================================
3️⃣ 예약 도구 테스트 - 정상 케이스
============================================================
ℹ️ [INFO] 예약 요청: 2024-12-24 19:00, 4명
ℹ️ [INFO] 예약 완료: 2024-12-24 19:00
예약 결과:
✅ 예약 완료: 2024-12-24 19:00, 4명
```

## Context 기능 테스트 내용

### Context 기본 기능 (`context-simple-demo.py`)

### 1. 간단한 작업 실행
- 3초 동안 진행되는 작업
- 진행 상황 실시간 보고
- 로그 메시지 출력

### 2. 배치 처리
- 5개 항목 순차 처리
- 각 항목별 진행률 표시
- 경고 메시지 시뮬레이션

### 3. 메트릭 모니터링
- 5초간 시스템 메트릭 수집
- CPU/메모리 사용률 시뮬레이션
- 조건에 따른 로그 레벨 변경

### 4. 리소스 조회
- 저장된 작업 목록 확인
- JSON 형식으로 데이터 반환

### Elicitation 기능 (`elicitation-server.py`)

#### 1. 테이블 예약 시나리오
- 정상 예약 처리
- 예약 불가 날짜 시 대체 날짜 확인
- 사용자 선택에 따른 처리

#### 2. 주문 처리 시나리오
- 배송 옵션 선택 (standard/express/overnight)
- 선물 포장 여부 확인
- 결제 방법 선택
- 특별 요청사항 입력

#### 3. 알림 설정 시나리오
- 다단계 사용자 입력
- 알림 활성화 여부
- 알림 채널 선택 (이메일/SMS)
- 알림 빈도 설정
- 방해 금지 시간 설정

## MCP Inspector로 테스트

개별 서버를 MCP Inspector로 테스트하려면:

```bash
# Context 데모 서버를 Inspector로 실행
uv run mcp dev context-simple-demo.py

# Elicitation 서버를 Inspector로 실행
uv run mcp dev elicitation-server.py
```

## 고급 기능 (참고)

### Context 고급 서버

`context-advanced-server.py`는 다음과 같은 고급 기능을 포함합니다:
- Elicitation (사용자 입력 요청)
- 세션 관리
- 리소스 업데이트 알림

하지만 Elicitation은 완전한 MCP 클라이언트(예: Claude Desktop)에서만 정상 작동합니다.

### Elicitation 서버 상세

`elicitation-server.py`는 다음과 같은 Elicitation 패턴을 보여줍니다:

- **BookingPreferences**: 예약 대체 날짜 확인
- **DeliveryOptions**: 배송 옵션 선택
- **PaymentMethod**: 결제 방법 선택
- **NotificationEnable**: 알림 활성화 설정
- **NotificationFrequency**: 알림 빈도 설정

각 스키마는 Pydantic BaseModel을 사용하여 구조화된 입력을 정의합니다.

## 문서 참조

- **`context-complete-guide.md`** - Context 사용법 완벽 가이드
- **`context-usage.md`** - Context 기본 사용법

## 문제 해결

### "Connection closed" 오류
- 서버 파일 경로가 올바른지 확인
- Python 환경이 활성화되어 있는지 확인

### JSON 파싱 오류
- Elicitation을 사용하는 도구는 표준 클라이언트에서 제한적
- `test-simple-context.py`로 테스트 권장

### Elicitation 테스트 제한사항
- `test-elicitation.py`에서는 elicitation이 트리거되지만 사용자 응답은 처리되지 않음
- 실제 대화형 테스트를 위해서는 Claude Desktop 등의 완전한 MCP 클라이언트 필요
- 대화형 모드(`interactive`)로 실행하면 수동으로 입력값을 테스트할 수 있음

## 요약

Context는 MCP 서버를 더욱 강력하고 사용자 친화적으로 만드는 핵심 기능입니다. 

- **기본 Context 기능**: `context-simple-demo.py`와 `test-simple-context.py`로 로깅과 진행 상황 보고 학습
- **Elicitation 기능**: `elicitation-server.py`와 `test-elicitation.py`로 사용자 상호작용 패턴 학습

두 가지 데모를 통해 MCP Context의 모든 주요 기능을 쉽게 이해하고 테스트할 수 있습니다. 