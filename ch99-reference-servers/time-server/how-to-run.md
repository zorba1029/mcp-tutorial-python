# Time Server 실행 및 테스트 가이드

이 가이드는 MCP Time Server를 실행하고 테스트하는 방법을 설명합니다.

## 📋 목차

1. [환경 설정](#환경-설정)
2. [서버 실행 방법](#서버-실행-방법)
3. [테스트 클라이언트 실행](#테스트-클라이언트-실행)
4. [MCP Inspector 사용](#mcp-inspector-사용)
5. [지원하는 기능](#지원하는-기능)

## 🔧 환경 설정

### 필수 요구사항
- Python 3.10+
- uv (Python 패키지 관리자)

### 의존성 설치
```bash
cd ch99-reference-servers/time-server
uv sync
```

## 🚀 서버 실행 방법

### 방법 1: 기본 실행 (UTC timezone 사용)
```bash
cd ch99-reference-servers/time-server
uv run python -m mcp_server_time
```

### 방법 2: 특정 timezone으로 실행
```bash
cd ch99-reference-servers/time-server
uv run python -m mcp_server_time --local-timezone Asia/Seoul
```

### 방법 3: 직접 서버 파일 실행
```bash
cd ch99-reference-servers/time-server
uv run python src/mcp_server_time/server.py
```

### 실행 옵션
- `--local-timezone`: 기본 로컬 timezone 설정 (기본값: UTC)
- `--help`: 도움말 표시

## 🧪 테스트 클라이언트 실행

### 자동화된 테스트 실행
```bash
cd ch99-reference-servers/time-server
uv run python test_time_client.py
```

### 테스트 내용
테스트 클라이언트는 다음 기능들을 자동으로 테스트합니다:

1. **현재 시간 조회**:
   - 🇰🇷 한국 시간 (Asia/Seoul)
   - 🗽 뉴욕 시간 (America/New_York)
   - 🇬🇧 런던 시간 (Europe/London)

2. **시간 변환**:
   - 한국 오후 3시 → 뉴욕 시간
   - 런던 오전 9시 → 도쿄 시간

### 예상 출력
```
🕐 Time Server 테스트 시작
==================================================
📋 사용 가능한 도구들:
  - get_current_time: Get current time in specified timezone
  - convert_time: Convert time between timezones

🇰🇷 한국 현재 시간:
  {
  "timezone": "Asia/Seoul",
  "datetime": "2025-07-16T20:37:19+09:00",
  "is_dst": false
}

🗽 뉴욕 현재 시간:
  {
  "timezone": "America/New_York", 
  "datetime": "2025-07-16T07:37:19-04:00",
  "is_dst": true
}

✅ 모든 테스트 완료!
```

## 🔍 MCP Inspector 사용

### Inspector로 서버 실행 및 테스트
```bash
# time-server 디렉토리로 이동
cd ch99-reference-servers/time-server

# Inspector로 서버 실행
npx @modelcontextprotocol/inspector uv run python -m mcp_server_time
```

이 명령어를 실행하면:
1. Inspector가 자동으로 시작됩니다
2. 브라우저가 열리고 Inspector 인터페이스가 표시됩니다
3. Time Server가 자동으로 연결됩니다

### 별도 실행 방법 (고급)

**수동으로 Inspector와 서버를 분리 실행하려면:**

1. **터미널 1에서 Inspector 실행:**
   ```bash
   npx @modelcontextprotocol/inspector --port 6278
   ```

2. **브라우저에서 Inspector 접속**
   - `http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=<토큰>` 접속

3. **Connect 설정:**
   - **Transport**: `STDIO` 선택
   - **Command**: `uv`
   - **Arguments** (각각 새 줄에 입력):
     ```
     run
     python
     -m
     mcp_server_time
     ```
   - **Working Directory**: `/your/path/to/ch99-reference-servers/time-server`

### Inspector에서 테스트

#### get_current_time 도구
- **Tool**: `get_current_time` 선택
- **Arguments**: `Asia/Seoul` (값만 입력)

#### convert_time 도구  
- **Tool**: `convert_time` 선택
- **source_timezone**: `Asia/Seoul`
- **time**: `15:00`
- **target_timezone**: `America/New_York`

## ⚙️ 지원하는 기능

### 1. get_current_time
지정된 timezone의 현재 시간을 조회합니다.

**Parameters:**
- `timezone` (string): IANA timezone 이름

**Example:**
```json
{
  "timezone": "Asia/Seoul"
}
```

### 2. convert_time
시간을 다른 timezone으로 변환합니다.

**Parameters:**
- `source_timezone` (string): 출발 timezone
- `time` (string): 시간 (HH:MM 형식, 24시간)
- `target_timezone` (string): 목적지 timezone

**Example:**
```json
{
  "source_timezone": "Asia/Seoul",
  "time": "15:00", 
  "target_timezone": "America/New_York"
}
```

### 지원하는 Timezone 목록
- `Asia/Seoul` (한국, UTC+9)
- `America/New_York` (뉴욕, UTC-5/-4)
- `America/Los_Angeles` (LA, UTC-8/-7)
- `Europe/London` (런던, UTC+0/+1)
- `Europe/Paris` (파리, UTC+1/+2)
- `Asia/Tokyo` (도쿄, UTC+9)
- `Australia/Sydney` (시드니, UTC+10/+11)

## 🐛 문제 해결

### 1. 모듈을 찾을 수 없음 오류
```bash
# 현재 디렉토리 확인
pwd
# time-server 디렉토리로 이동
cd ch99-reference-servers/time-server
# 의존성 재설치
uv sync
```

### 2. Timezone 오류
- 지원하는 timezone 목록을 확인하세요
- 정확한 IANA timezone 이름을 사용하세요 (예: `Asia/Seoul`)

### 3. Inspector 연결 실패
- Working Directory 경로가 정확한지 확인하세요
- 서버가 실행 중인지 확인하세요
- 포트 충돌이 없는지 확인하세요

## 📚 추가 정보

- **서버 코드**: `src/mcp_server_time/server.py`
- **테스트 클라이언트**: `test_time_client.py`
- **프로젝트 설정**: `pyproject.toml`
- **의존성**: `uv.lock`

## 🎯 사용 사례

1. **현재 시간 확인**: 다양한 지역의 현재 시간 조회
2. **회의 시간 조정**: 여러 timezone간 시간 변환
3. **일정 관리**: 국제적인 일정 관리를 위한 시간 계산
4. **개발/테스트**: MCP 서버 개발 및 테스트 용도

## 🔧 MCP 개발 방식: @mcp vs @server 데코레이터

이 time-server는 **Core MCP** 방식(`@server`)을 사용합니다. MCP Python SDK에는 두 가지 개발 방식이 있습니다.

### 📦 FastMCP 방식 (`@mcp`) - 간편한 방식

**특징:**
- ✅ 매우 간단하고 직관적
- ✅ 도구별 개별 함수 작성
- ✅ 자동 스키마 생성
- ✅ 빠른 프로토타이핑에 적합
- ❌ 유연성 제한적

**코드 예시:**
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("서버명")

@mcp.tool()
def get_weather(location: str) -> dict:
    """Get weather for location"""
    return {"location": location, "temperature": 22}

@mcp.tool()
def convert_currency(amount: float, from_cur: str, to_cur: str) -> float:
    """Convert currency"""
    return amount * 1.1
```

### ⚙️ Core MCP 방식 (`@server`) - 저수준 방식

**특징:**
- ✅ 완전한 제어와 유연성
- ✅ 성능 최적화 가능
- ✅ 복잡한 비즈니스 로직 구현
- ✅ 프로덕션 환경에 적합
- ❌ 코드가 복잡하고 길어짐

**코드 예시 (현재 time-server 방식):**
```python
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("서버명")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_weather",
            description="Get weather for location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
    if name == "get_weather":
        location = arguments["location"]
        result = {"location": location, "temperature": 22}
        return [TextContent(type="text", text=json.dumps(result))]
```

### 📊 비교표

| 특징 | FastMCP (`@mcp`) | Core MCP (`@server`) |
|------|------------------|---------------------|
| **사용 난이도** | ✅ 매우 간단 | ❌ 복잡함 |
| **코드량** | ✅ 짧음 | ❌ 긴 편 |
| **개별 함수** | ✅ 도구별 개별 함수 | ❌ 하나의 큰 함수 |
| **자동 스키마** | ✅ 자동 생성 | ❌ 수동 작성 |
| **유연성** | ❌ 제한적 | ✅ 매우 높음 |
| **성능** | ❌ 추상화 오버헤드 | ✅ 최적화된 성능 |
| **Context 지원** | ✅ 간단 | ✅ 완전 지원 |
| **적용 분야** | 프로토타이핑, 학습 | 프로덕션, 복잡한 로직 |

### 🤔 Time Server가 Core MCP를 선택한 이유

1. **프로덕션 품질**: 참조 구현으로서 안정성과 성능 중시
2. **정밀한 제어**: JSON 스키마, 에러 처리 등을 세밀하게 조정
3. **성능 최적화**: 불필요한 추상화 레이어 제거
4. **표준 호환성**: MCP 프로토콜의 순수한 구현 제공
5. **복잡한 로직**: 여러 도구를 하나의 통합된 로직에서 처리

### 📋 선택 가이드

**FastMCP (`@mcp`) 사용 권장:**
- 🚀 빠른 프로토타이핑
- 📚 학습 및 데모 목적
- 🎯 간단한 도구들
- ⏰ 개발 속도가 중요한 경우

**Core MCP (`@server`) 사용 권장:**
- 🏭 프로덕션 환경
- 🧠 복잡한 비즈니스 로직
- ⚡ 성능이 중요한 경우
- 🎛️ 세밀한 제어가 필요한 경우

### 💡 실제 사용 예시

**FastMCP로 간단한 도구 만들기:**
```python
# 파일: simple_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Simple Calculator")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

if __name__ == "__main__":
    mcp.run()
```

**Core MCP로 복잡한 로직 구현:**
```python
# 현재 time-server와 같은 방식
# - 여러 도구를 하나의 call_tool에서 처리
# - 세밀한 에러 처리 및 스키마 정의
# - 성능 최적화된 구현
```

### 🎓 학습 권장 순서

1. **FastMCP부터 시작** - 개념 이해와 빠른 개발
2. **Core MCP 학습** - 심화 학습과 프로덕션 준비
3. **상황에 맞게 선택** - 프로젝트 요구사항에 따라 결정

이 time-server는 **Core MCP의 모범 사례**를 보여주는 좋은 참조 구현입니다!

## 📦 Python 패키지 구조: __init__.py와 __main__.py

Time Server는 표준 Python 패키지 구조를 사용하여 깔끔하고 전문적인 실행 방식을 제공합니다.

### 🗂 패키지 구조 이해

```
src/mcp_server_time/
├── __init__.py          # 패키지 진입점, main() 함수 정의
├── __main__.py          # python -m 실행시 진입점
└── server.py           # 실제 서버 로직 (실행 코드 없음)
```

### 📄 각 파일의 역할

#### 1. **`__init__.py` - 패키지 초기화 및 진입점**

```python
# src/mcp_server_time/__init__.py
from .server import serve

def main():
    """MCP Time Server - Time and timezone conversion functionality for MCP"""
    import argparse
    import asyncio
    
    parser = argparse.ArgumentParser(description="give a model the ability to handle time queries and timezone conversions")
    parser.add_argument("--local-timezone", type=str, default="UTC", 
                       help="Override local timezone (default: UTC)")
    args = parser.parse_args()
    
    asyncio.run(serve(args.local_timezone))
    
if __name__ == "__main__":
    main()
```

**역할:**
- ✅ **패키지 API 정의**: 외부에서 import할 수 있는 함수들 정의
- ✅ **실행 진입점**: `main()` 함수로 실행 로직 제공
- ✅ **명령행 인수 처리**: argparse를 통한 옵션 처리
- ✅ **모듈 import**: 다른 모듈에서 필요한 함수들 import

#### 2. **`__main__.py` - 모듈 실행 진입점**

```python
# src/mcp_server_time/__main__.py
from mcp_server_time import main

main()
```

**역할:**
- ✅ **`python -m` 지원**: 패키지를 모듈로 실행 가능하게 함
- ✅ **간단한 래퍼**: `__init__.py`의 `main()` 함수를 호출
- ✅ **표준 관례**: Python 패키지의 표준 실행 방식

#### 3. **`server.py` - 순수 서버 로직**

```python
# src/mcp_server_time/server.py
async def serve(local_timezone: str | None = None) -> None:
    # 실제 서버 구현
    server = Server("mcp-time-server")
    # ... 서버 로직 ...

# 주석 처리된 실행 코드 (의도적)
# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(serve())
```

**역할:**
- ✅ **순수 로직**: 비즈니스 로직만 포함
- ✅ **재사용성**: 다른 모듈에서 import하여 사용 가능
- ✅ **관심사 분리**: 실행 코드와 로직 코드 분리

### 🔄 실행 흐름

#### **`python -m mcp_server_time` 실행 시:**

```
1. Python이 mcp_server_time 패키지 찾기
   ↓
2. __main__.py 실행
   ↓
3. from mcp_server_time import main
   ↓  
4. __init__.py에서 main() 함수 로드
   ↓
5. main() 함수 실행
   ↓
6. argparse로 인수 처리
   ↓
7. serve() 함수 호출 (server.py)
   ↓
8. 서버 시작
```

### 📋 다양한 실행 방법 비교

| 실행 방법 | 명령어 | 사용하는 파일 | 특징 |
|----------|--------|--------------|------|
| **모듈 실행** (권장) | `python -m mcp_server_time` | `__main__.py` → `__init__.py` | ✅ 표준 방식, 패키지 구조 유지 |
| **직접 실행** | `python server.py` | `server.py` | ❌ 비권장, 상대 import 문제 |
| **패키지 설치 후** | `mcp-server-time` | `pyproject.toml` script | ✅ 가장 깔끔, 설치 필요 |

### 🎯 이 구조의 장점

#### 1. **관심사 분리 (Separation of Concerns)**
```python
# server.py - 비즈니스 로직만
async def serve(local_timezone):
    # 서버 구현

# __init__.py - 실행 로직만  
def main():
    # CLI 처리, 서버 시작

# __main__.py - 진입점만
main()
```

#### 2. **재사용성 (Reusability)**
```python
# 다른 프로젝트에서 사용 가능
from mcp_server_time.server import serve
await serve("Asia/Seoul")

# 또는 명령행 도구로 사용
from mcp_server_time import main
main()
```

#### 3. **테스트 용이성 (Testability)**
```python
# 단위 테스트 가능
from mcp_server_time.server import TimeServer
server = TimeServer()
result = server.get_current_time("Asia/Seoul")
```

#### 4. **배포 편의성 (Distribution)**
```python
# pyproject.toml에서 스크립트 정의
[project.scripts]
mcp-server-time = "mcp_server_time:main"
```

### 🚀 실제 사용 패턴

#### **개발 중에는:**
```bash
# 빠른 테스트
cd ch99-reference-servers/time-server
uv run python -m mcp_server_time

# Inspector와 함께
npx @modelcontextprotocol/inspector uv run python -m mcp_server_time
```

#### **배포 후에는:**
```bash
# 설치
pip install mcp-server-time

# 실행
mcp-server-time --local-timezone Asia/Seoul
```

### 💡 모범 사례 (Best Practices)

#### **✅ 권장사항:**

1. **`server.py`에는 순수 로직만**
   ```python
   # ✅ 좋음
   async def serve(params):
       # 서버 로직
   
   # ❌ 피하기
   if __name__ == "__main__":
       asyncio.run(serve())
   ```

2. **`__init__.py`에서 실행 로직 관리**
   ```python
   # ✅ 좋음
   def main():
       parser = argparse.ArgumentParser()
       # CLI 처리
   ```

3. **`__main__.py`는 최대한 간단하게**
   ```python
   # ✅ 좋음
   from package_name import main
   main()
   ```

#### **🔧 고급 패턴:**

```python
# __init__.py에서 조건부 실행
def main():
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        # 개발 모드
        asyncio.run(serve(debug=True))
    else:
        # 프로덕션 모드
        parser = argparse.ArgumentParser()
        # ... 일반 처리
```

### 📚 추가 학습 자료

1. **Python 공식 문서**: [Packages](https://docs.python.org/3/tutorial/modules.html#packages)
2. **PEP 338**: [Executing modules as scripts](https://peps.python.org/pep-0338/)
3. **Real Python**: [Python Modules and Packages](https://realpython.com/python-modules-packages/)

이 구조는 **Python 패키지 개발의 모범 사례**를 보여주는 훌륭한 예시입니다! 🐍✨ 