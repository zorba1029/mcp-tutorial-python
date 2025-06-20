# MCP Tutorial using Python

이 저장소는 **MCP(Model Context Protocol)**를 사용하여 다양한 종류의 AI 에이전트 도구 서버를 구축하는 방법을 배우기 위한 파이썬 튜토리얼 프로젝트입니다. `uv` 패키지 관리자를 사용하여 환경을 설정하고, 여러 통신 방식(stdio, SSE, HTTP Streaming)을 단계별로 학습합니다.

## 🚀 사용된 기술 스택

-   **언어**: Python 3.13+
-   **패키지 관리**: `uv`
-   **MCP 라이브러리**: `mcp`, `fastmcp`
-   **웹 프레임워크**: `FastAPI`, `Starlette`
-   **웹 서버**: `uvicorn`

## ⚙️ 프로젝트 설정

1.  **저장소 클론:**
    ```bash
    git clone <repository-url>
    cd mcp-tutorial-python
    ```

2.  **`uv` 설치:**
    `uv`가 설치되어 있지 않다면, 공식 문서에 따라 설치합니다.
    ```bash
    # 예시 (macOS/Linux)
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

3.  **가상환경 생성 및 의존성 설치:**
    `uv`가 자동으로 `pyproject.toml`을 읽어 가상환경을 만들고 필요한 모든 패키지를 설치합니다.
    ```bash
    uv sync
    ```

## 📚 챕터별 예제 실행 방법

각 챕터의 예제는 해당 디렉토리로 이동하여 실행하는 것을 권장합니다.

---

### Chapter 1: `stdio` 기반 서버

-   **설명**: 가장 기본적인 일대일 통신 방식인 `stdio`를 사용합니다.
-   **위치**: `ch01/`

```bash
# ch01 디렉토리로 이동
cd ch01

# 서버를 테스트하는 클라이언트 실행
uv run python 01_weather-client.py
```

---

### Chapter 3, Part 3: LLM 클라이언트와 `stdio`

-   **설명**: LLM이 도구를 선택하고 호출하는 과정을 시뮬레이션하는 클라이언트입니다.
-   **위치**: `ch03/03_llm-client/`

```bash
# 해당 디렉토리로 이동
cd ch03/03_llm-client

# 클라이언트 실행 (내부적으로 server.py를 자동으로 실행)
uv run python client.py
```

---

### Chapter 3, Part 4: VS Code와 연동하기

-   **설명**: 작성한 MCP 서버를 VS Code의 AI 기능(`@workspace`)과 직접 연동합니다.
-   **상세 안내**: `ch03/04_vscode/README.md` 파일을 참고하세요.

```bash
# 1. VS Code에 서버 등록 (프로젝트 루트에서 실행)
code --add-mcp '{"name":"Python LLM Server","command":"uv","args":["run","python","ch03/03_llm-client/server.py"]}'

# 2. VS Code 명령 팔레트(Cmd+Shift+P)에서 "MCP: Connect To Server" 실행
```

---

### Chapter 3, Part 5: SSE (Server-Sent Events) 서버

-   **설명**: 여러 클라이언트가 동시에 접속할 수 있는 웹 기반(HTTP) 서버입니다. `Starlette`과 `FastAPI` 두 가지 방식으로 구현되었습니다.
-   **위치**: `ch03/05_sse-server/`

**실행 방법 (두 개의 터미널 필요):**

1.  **[터미널 1] 서버 실행:**
    ```bash
    # 디렉토리 이동
    cd ch03/05_sse-server

    # FastAPI 버전 서버 실행 (자동 리로드 기능 포함)
    uv run python server-fastapi.py
    ```

2.  **[터미널 2] Inspector로 테스트:**
    -   웹 브라우저에서 Inspector(`http://localhost:6274`)를 열고, SSE Transport를 통해 `http://localhost:8000/sse`에 연결하여 테스트합니다.
    -   또는, `npx`를 사용하여 CLI에서 직접 테스트할 수 있습니다.
    ```bash
    npx @modelcontextprotocol/inspector --cli http://localhost:8000/sse --method tools/list
    ```

**FastAPI의 장점:**
-   서버 실행 후, 웹 브라우저에서 `http://localhost:8000/docs`로 접속하여 자동 생성된 API 문서를 확인하고 직접 테스트해볼 수 있습니다.

---

### Chapter 3, Part 6: HTTP 스트리밍

-   **설명**: 비동기 제너레이터를 사용하여 실시간으로 처리 과정을 클라이언트에게 스트리밍하는 방법을 학습합니다.
-   **위치**: `ch03/06_http-streaming/`
-   **상세 안내**: `ch03/06_http-streaming/06_how-to-work.md` 파일을 참고하세요.

**실행 방법 (두 개의 모드):**

1.  **서버 실행:**
    ```bash
    # 디렉토리 이동
    cd ch03/06_http-streaming

    # 서버 실행 (MCP 모드)
    uv run python server.py mcp
    ```

2.  **클라이언트 실행:**
    -   **MCP 클라이언트 모드:**
        ```bash
        # 별도의 터미널에서 실행
        uv run python client.py mcp
        ```
    -   **일반 HTTP 스트리밍 모드:**
        ```bash
        # 별도의 터미널에서 실행
        uv run python client.py
        ```