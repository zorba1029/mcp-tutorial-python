# MCP 루트 컨텍스트

루트 컨텍스트는 모델 컨텍스트 프로토콜의 기본 개념으로, 여러 요청과 세션에서 대화 기록과 공유 상태를 유지하기 위한 지속적인 계층을 제공합니다.

## 소개

이번 수업에서는 MCP에서 루트 컨텍스트를 생성, 관리, 활용하는 방법을 살펴보겠습니다.

## 학습 목표

이 수업을 마치면 다음을 수행할 수 있습니다.

- 루트 컨텍스트의 목적과 구조를 이해합니다.
- MCP 클라이언트 라이브러리를 사용하여 루트 컨텍스트를 생성하고 관리합니다.
- .NET, Java, JavaScript 및 Python 애플리케이션에서 루트 컨텍스트 구현
- 다중 턴 대화 및 상태 관리를 위해 루트 컨텍스트 활용
- 루트 컨텍스트 관리를 위한 모범 사례 구현

## 루트 컨텍스트 이해

루트 컨텍스트는 일련의 관련 상호작용에 대한 기록과 상태를 보관하는 컨테이너 역할을 합니다. 루트 컨텍스트를 통해 다음과 같은 작업을 수행할 수 있습니다.

- **대화 지속성**: 일관성 있는 다중 대화 유지
- **메모리 관리**: 상호 작용 전반에 걸쳐 정보 저장 및 검색
- **상태 관리**: 복잡한 워크플로의 진행 상황 추적
- **컨텍스트 공유**: 여러 클라이언트가 동일한 대화 상태에 액세스할 수 있도록 허용

MCP에서 루트 컨텍스트는 다음과 같은 주요 특징을 갖습니다.

- 각 루트 컨텍스트에는 고유한 식별자가 있습니다.
- 대화 기록, 사용자 기본 설정 및 기타 메타데이터를 포함할 수 있습니다.
- 필요에 따라 생성, 접근, 보관이 가능합니다.
- 세분화된 액세스 제어 및 권한을 지원합니다.

## 루트 컨텍스트 라이프사이클

```인어
플로우차트 TD
    A[루트 컨텍스트 생성] --> B[메타데이터로 초기화]
    B --> C[컨텍스트 ID로 요청 보내기]
    C --> D[결과로 컨텍스트 업데이트]
    디 --> 씨
    D --> E[완료 시 컨텍스트 보관]
```

## 루트 컨텍스트 작업

루트 컨텍스트를 생성하고 관리하는 방법의 예는 다음과 같습니다.

<세부정보>
<summary>csharp</summary>

```csharp
// .NET 예제: 루트 컨텍스트 관리
Microsoft.Mcp.Client를 사용하여
시스템 사용
System.Threading.Tasks를 사용하여
System.Collections.Generic을 사용하여;

공개 클래스 RootContextExample
{
    개인 읽기 전용 IMcpClient _client;
    개인 읽기 전용 IRootContextManager _contextManager;
    
    public RootContextExample(IMcpClient 클라이언트, IRootContextManager 컨텍스트 관리자)
    {
        _클라이언트 = 클라이언트;
        _contextManager = 컨텍스트관리자;
    }
    
    공개 비동기 작업 DemonstrateRootContextAsync()
    {
        // 1. 새로운 루트 컨텍스트를 생성합니다.
        var contextResult = await _contextManager.CreateRootContextAsync(new RootContextCreateOptions
        {
            이름 = "고객 지원 세션",
            메타데이터 = 새 사전<문자열, 문자열>
            {
                ["고객 이름"] = "Acme Corporation",
                ["우선순위 수준"] = "높음",
                ["도메인"] = "클라우드 서비스"
            }
        });
        
        문자열 contextId = contextResult.ContextId;
        Console.WriteLine($"ID가 {contextId}인 루트 컨텍스트가 생성되었습니다");
        
        // 2. 컨텍스트를 사용한 첫 번째 상호 작용
        var response1 = await _client.SendPromptAsync(
            "클라우드에서 웹 서비스 배포를 확장하는 데 문제가 있습니다."
            새로운 SendPromptOptions { RootContextId = contextId }
        );
        
        Console.WriteLine($"첫 번째 응답: {response1.GeneratedText}");
        
        // 두 번째 상호 작용 - 모델은 이전 대화에 액세스할 수 있습니다.
        var response2 = await _client.SendPromptAsync(
            "네, Kubernetes를 사용하여 컨테이너화된 배포를 사용하고 있습니다."
            새로운 SendPromptOptions { RootContextId = contextId }
        );
        
        Console.WriteLine($"두 번째 응답: {response2.GeneratedText}");
        
        // 3. 대화에 기반한 컨텍스트에 메타데이터 추가
        _contextManager.UpdateContextMetadataAsync(contextId, new Dictionary<string, string>을 기다립니다.
        {
            ["기술 환경"] = "쿠버네티스",
            ["IssueType"] = "스케일링"
        });
        
        // 4. 컨텍스트 정보 가져오기
        var contextInfo = _contextManager.GetRootContextInfoAsync(contextId)를 기다립니다.
        
        Console.WriteLine("컨텍스트 정보:");
        Console.WriteLine($"- 이름: {contextInfo.Name}");
        Console.WriteLine($"- 생성됨: {contextInfo.CreatedAt}");
        Console.WriteLine($"- 메시지: {contextInfo.MessageCount}");
        
        // 5. 대화가 완료되면 컨텍스트를 보관합니다.
        _contextManager.ArchiveRootContextAsync(contextId)를 기다립니다.
        Console.WriteLine($"보관된 컨텍스트 {contextId}");
    }
}
```

이전 코드에서 우리는 다음을 수행했습니다.

1. 고객 지원 세션에 대한 루트 컨텍스트를 생성했습니다.
1. 해당 컨텍스트 내에서 여러 메시지를 보내 모델이 상태를 유지할 수 있도록 합니다.
1. 대화에 따른 관련 메타데이터로 맥락을 업데이트했습니다.
1. 대화 내용을 이해하기 위해 컨텍스트 정보를 검색했습니다.
1. 대화가 완료된 후 맥락을 보관했습니다.

</세부정보>

## 예: 재무 분석을 위한 루트 컨텍스트 구현

이 예에서는 재무 분석 세션에 대한 루트 컨텍스트를 만들어 여러 상호작용에서 상태를 유지하는 방법을 보여드리겠습니다.

<세부정보>
<summary>자바</summary>

```java
// Java 예제: 루트 컨텍스트 구현
패키지 com.example.mcp.contexts;

com.mcp.client.McpClient를 가져옵니다.
com.mcp.client.ContextManager를 가져옵니다.
com.mcp.models.RootContext를 가져옵니다.
com.mcp.models.McpResponse를 가져옵니다.

java.util.HashMap을 가져옵니다.
java.util.Map을 가져옵니다.
java.util.UUID를 가져옵니다.

공개 클래스 RootContextsDemo {
    개인 최종 McpClient 클라이언트;
    개인 최종 ContextManager contextManager;
    
    공개 RootContextsDemo(문자열 serverUrl) {
        이 클라이언트 = 새 McpClient.Builder()
            .setServerUrl(서버 URL)
            .짓다();
            
        이 컨텍스트 관리자 = 새 컨텍스트 관리자(클라이언트);
    }
    
    public void demonstrateRootContext()는 예외를 발생시킵니다.
        // 컨텍스트 메타데이터 생성
        Map<String, String> 메타데이터 = new HashMap<>();
        metadata.put("프로젝트 이름", "재무 분석");
        metadata.put("userRole", "재무 분석가");
        metadata.put("dataSource", "2025년 1분기 재무 보고서");
        
        // 1. 새로운 루트 컨텍스트를 생성합니다.
        RootContext context = contextManager.createRootContext("재무 분석 세션", 메타데이터);
        문자열 contextId = context.getId();
        
        System.out.println("생성된 컨텍스트: " + contextId);
        
        // 2. 첫 번째 상호 작용
        McpResponse 응답1 = 클라이언트.sendPrompt(
            "기술 부문의 1분기 재무 데이터 추세를 분석합니다."
            컨텍스트 ID
        );
        
        System.out.println("첫 번째 응답: " + response1.getGeneratedText());
        
        // 3. 응답에서 얻은 중요한 정보로 컨텍스트를 업데이트합니다.
        contextManager.addContextMetadata(contextId,
            Map.of("identifiedTrend", "클라우드 인프라 비용 증가"));
        
        // 두 번째 상호작용 - 동일한 컨텍스트 사용
        McpResponse 응답2 = 클라이언트.sendPrompt(
            "클라우드 인프라 비용 증가의 원인은 무엇입니까?"
            컨텍스트 ID
        );
        
        System.out.println("두 번째 응답: " + response2.getGeneratedText());
        
        // 4. 분석 세션 요약 생성
        McpResponse 요약응답 = 클라이언트.sendPrompt(
            "기술 부문 재무 분석을 3~5가지 핵심 요점으로 요약해 주세요"
            컨텍스트 ID
        );
        
        // 요약을 컨텍스트 메타데이터에 저장합니다.
        contextManager.addContextMetadata(contextId,
            Map.of("분석요약", 요약응답.getGeneratedText()));
            
        // 업데이트된 컨텍스트 정보 가져오기
        RootContext 업데이트 컨텍스트 = contextManager.getRootContext(contextId);
        
        System.out.println("컨텍스트 정보:");
        System.out.println("- 생성됨: " + updatedContext.getCreatedAt());
        System.out.println("- 마지막 업데이트: " + updatedContext.getLastUpdatedAt());
        System.out.println("- 분석 요약: " +
            updatedContext.getMetadata().get("분석 요약"));
            
        // 5. 완료되면 컨텍스트를 보관합니다.
        contextManager.archiveContext(컨텍스트Id);
        System.out.println("컨텍스트가 보관되었습니다");
    }
}
```

이전 코드에서 우리는 다음을 수행했습니다.

1. 재무 분석 세션에 대한 루트 컨텍스트를 생성했습니다.
2. 해당 컨텍스트 내에서 여러 메시지를 보내 모델이 상태를 유지할 수 있도록 합니다.
3. 대화에 따른 관련 메타데이터로 맥락을 업데이트했습니다.
4. 분석 세션 요약을 생성하여 컨텍스트 메타데이터에 저장했습니다.
5. 대화가 완료되면 맥락을 보관합니다.

</세부정보>

## 예: 루트 컨텍스트 관리

대화 내역과 상태를 유지하려면 루트 컨텍스트를 효과적으로 관리하는 것이 중요합니다. 아래는 루트 컨텍스트 관리를 구현하는 방법의 예입니다.

<세부정보>
<요약>자바스크립트</요약>

```javascript
// JavaScript 예제: MCP 루트 컨텍스트 관리
const { McpClient, RootContextManager } = require('@mcp/client');

클래스 ContextSession {
  생성자(serverUrl, apiKey = null) {
    // MCP 클라이언트 초기화
    이 클라이언트 = 새 McpClient({
      서버 URL,
      API 키
    });
    
    // 컨텍스트 관리자 초기화
    이 컨텍스트 관리자 = 새로운 RootContextManager(이 클라이언트);
  }
  
  /**
   * 새로운 대화 컨텍스트를 만듭니다.
   * @param {string} sessionName - 대화 세션의 이름
   * @param {Object} 메타데이터 - 컨텍스트에 대한 추가 메타데이터
   * @returns {Promise<string>} - 컨텍스트 ID
   */
  비동기 createConversationContext(세션 이름, 메타데이터 = {}) {
    노력하다 {
      const contextResult = this.contextManager.createRootContext({를 기다립니다.
        이름: 세션 이름,
        메타데이터: {
          ...메타데이터,
          createdAt: new Date().toISOString(),
          상태: '활성'
        }
      });
      
      console.log(`ID: ${contextResult.id}인 루트 컨텍스트 '${sessionName}'이 생성되었습니다`);
      contextResult.id를 반환합니다.
    } catch (오류) {
      console.error('루트 컨텍스트 생성 오류:', error);
      오류를 던지다;
    }
  }
  
  /**
   * 기존 컨텍스트에서 메시지 보내기
   * @param {string} contextId - 루트 컨텍스트 ID
   * @param {string} message - 사용자의 메시지
   * @param {Object} 옵션 - 추가 옵션
   * @returns {Promise<Object>} - 응답 데이터
   */
  비동기 sendMessage(contextId, 메시지, 옵션 = {}) {
    노력하다 {
      // 지정된 컨텍스트를 사용하여 메시지를 보냅니다.
      const 응답 = this.client.sendPrompt(메시지, {
        rootContextId: 컨텍스트 ID,
        온도: 옵션.온도 || 0.7,
        허용된 도구: 옵션.허용된 도구 || []
      });
      
      // 대화에서 중요한 통찰력을 선택적으로 저장합니다.
      if (옵션.storeInsights) {
        이것을 기다립니다.storeConversationInsights(contextId, message, response.generatedText);
      }
      
      반품 {
        메시지: 응답.생성된 텍스트,
        도구 호출: 응답.도구 호출 || [],
        컨텍스트 ID
      };
    } catch (오류) {
      console.error(`컨텍스트 ${contextId}에서 메시지를 보내는 중 오류가 발생했습니다`, error);
      오류를 던지다;
    }
  }
  
  /**
   * 대화에서 중요한 통찰력을 저장합니다.
   * @param {string} contextId - 루트 컨텍스트 ID
   * @param {string} userMessage - 사용자의 메시지
   * @param {string} aiResponse - AI의 응답
   */
  비동기 storeConversationInsights(contextId, userMessage, aiResponse) {
    노력하다 {
      // 잠재적인 통찰력 추출(실제 앱에서는 더 정교할 것입니다)
      const 결합된 텍스트 = 사용자 메시지 + "\n" + aiResponse;
      
      // 잠재적인 통찰력을 식별하기 위한 간단한 휴리스틱
      const insightWords = ["중요한", "핵심 요점", "기억하세요", "의미 있는", "결정적인"];
      
      const potentialInsights = 결합된 텍스트
        .나뉘다(".")
        .filter(문장 =>
          insightWords.some(단어 => 문장.toLowerCase().includes(단어))
        )
        .map(문장 => 문장.trim())
        .filter(문장 => 문장.길이 > 10);
      
      // 컨텍스트 메타데이터에 통찰력 저장
      (잠재적통찰력.길이 > 0)인 경우 {
        상수 통찰력 = {};
        potentialInsights.forEach((통찰력, 인덱스) => {
          통찰력[`insight_${Date.now()}_${index}`] = 통찰력;
        });
        
        this.contextManager.updateContextMetadata(contextId, insights)를 기다립니다.
        console.log(`컨텍스트 ${contextId}에 ${potentialInsights.length}개의 인사이트가 저장되었습니다`);
      }
    } catch (오류) {
      console.warn('대화 통찰력을 저장하는 중 오류:', error);
      // 심각하지 않은 오류이므로 경고만 기록합니다.
    }
  }
  
  /**
   * 컨텍스트에 대한 요약 정보를 가져옵니다.
   * @param {string} contextId - 루트 컨텍스트 ID
   * @returns {Promise<Object>} - 컨텍스트 정보
   */
  비동기 getContextInfo(contextId) {
    노력하다 {
      const contextInfo = this.contextManager.getContextInfo(contextId)를 기다립니다.
      
      반품 {
        id: contextInfo.id,
        이름: contextInfo.name,
        생성됨: new Date(contextInfo.createdAt).toLocaleString(),
        마지막 업데이트: 새 Date(contextInfo.lastUpdatedAt).toLocaleString(),
        메시지 개수: contextInfo.messageCount,
        메타데이터: contextInfo.metadata,
        상태: contextInfo.status
      };
    } catch (오류) {
      console.error(`${contextId}에 대한 컨텍스트 정보를 가져오는 중 오류 발생`, error);
      오류를 던지다;
    }
  }
  
  /**
   * 대화의 요약을 맥락에 맞게 생성합니다.
   * @param {string} contextId - 루트 컨텍스트 ID
   * @returns {Promise<string>} - 생성된 요약
   */
  비동기 generateContextSummary(contextId) {
    노력하다 {
      // 모델에 지금까지의 대화 요약을 생성하도록 요청합니다.
      const 응답 = this.client.sendPrompt(를 기다립니다.
        "지금까지 나눈 대화를 3~4 문장으로 요약해 주시고, 논의된 주요 사항을 강조해 주십시오."
        { rootContextId: contextId, 온도: 0.3 }
      );
      
      // 요약을 컨텍스트 메타데이터에 저장합니다.
      이 contextManager.updateContextMetadata(contextId, {를 기다립니다.
        대화 요약: 응답.생성된 텍스트,
        요약: new Date().toISOString()
      });
      
      응답.생성된 텍스트를 반환합니다.
    } catch (오류) {
      console.error(`${contextId}에 대한 컨텍스트 요약을 생성하는 중 오류가 발생했습니다:`, error);
      오류를 던지다;
    }
  }
  
  /**
   * 더 이상 필요하지 않은 컨텍스트를 보관합니다.
   * @param {string} contextId - 루트 컨텍스트 ID
   * @returns {Promise<Object>} - 아카이브 작업의 결과
   */
  비동기 archiveContext(contextId) {
    노력하다 {
      // 보관 전 최종 요약 생성
      const 요약 = this.generateContextSummary(contextId)를 기다립니다.
      
      // 컨텍스트를 보관합니다
      this.contextManager.archiveContext(contextId)를 기다립니다.
      
      반품 {
        상태: "보관됨",
        컨텍스트 ID,
        요약
      };
    } catch (오류) {
      console.error(`컨텍스트 ${contextId}를 보관하는 중 오류 발생:`, error);
      오류를 던지다;
    }
  }
}

// 사용 예
async function demonstrateContextSession() {
  const session = new ContextSession('https://mcp-server-example.com');
  
  try {
    // 1. Create a new context for a product support conversation
    const contextId = await session.createConversationContext(
      'Product Support - Database Performance',
      {
        customer: 'Globex Corporation',
        product: 'Enterprise Database',
        severity: 'Medium',
        supportAgent: 'AI Assistant'
      }
    );
    
    // 2. First message in the conversation
    const response1 = await session.sendMessage(
      contextId,
      "I'm experiencing slow query performance on our database cluster after the latest update.",
      { storeInsights: true }
    );
    console.log('Response 1:', response1.message);
    
    // Follow-up message in the same context
    const response2 = await session.sendMessage(
      contextId,
      "Yes, we've already checked the indexes and they seem to be properly configured.",
      { storeInsights: true }
    );
    console.log('Response 2:', response2.message);
    
    // 3. Get information about the context
    const contextInfo = await session.getContextInfo(contextId);
    console.log('Context Information:', contextInfo);
    
    // 4. Generate and display conversation summary
    const summary = await session.generateContextSummary(contextId);
    console.log('Conversation Summary:', summary);
    
    // 5. Archive the context when done
    const archiveResult = await session.archiveContext(contextId);
    console.log('Archive Result:', archiveResult);
    
    // 6. Handle any errors gracefully
  } catch (error) {
    console.error('Error in context session demonstration:', error);
  }
}

demonstrateContextSession();
```

이전 코드에서 우리는 다음을 수행했습니다.

1. `createConversationContext` 함수를 사용하여 제품 지원 대화에 대한 루트 컨텍스트를 생성했습니다. 이 경우 컨텍스트는 데이터베이스 성능 문제에 관한 것입니다.

1. 해당 컨텍스트 내에서 여러 메시지를 전송하여 모델이 `sendMessage` 함수를 사용하여 상태를 유지할 수 있도록 합니다. 전송되는 메시지는 느린 쿼리 성능 및 인덱스 구성과 관련된 것입니다.

1. 대화에 따른 관련 메타데이터로 맥락을 업데이트했습니다.

1. `generateContextSummary` 함수를 사용하여 대화 요약을 생성하고 컨텍스트 메타데이터에 저장했습니다.

1. 대화가 완료되면 `archiveContext` 함수를 사용하여 컨텍스트를 보관합니다.

1. 견고성을 보장하기 위해 오류를 우아하게 처리했습니다.

</세부정보>

## 다중 턴 지원을 위한 루트 컨텍스트

이 예에서는 다중 턴 지원 세션에 대한 루트 컨텍스트를 생성하여 여러 상호 작용에서 상태를 유지하는 방법을 보여줍니다.

<세부정보>
<summary>파이썬</summary>

```python
# Python 예제: 다중 턴 지원을 위한 루트 컨텍스트
import asyncio
from datetime import datetime
from mcp_client import McpClient, RootContextManager

class AssistantSession:
    def __init__(self, server_url, api_key=None):
        self.client = McpClient(server_url=server_url, api_key=api_key)
        self.context_manager = RootContextManager(self.client)
    
    async def create_session(자기, 이름, 사용자_정보=없음):
        """Create a new root context for an assistant session"""
        metadata = {
            "session_type": "assistant",
            "created_at": datetime.now().isoformat(),
        }
        
        # Add user information if provided
        if user_info:
            metadata.update({f"user_{k}": v for k, v in user_info.items()})
            
        # Create the root context
        context = await self.context_manager.create_root_context(name, metadata)
        return context.id
    
    async def send_message(self, context_id, message, tools=None):
        """루트 컨텍스트 내에서 메시지 보내기"""
        # 컨텍스트 ID로 옵션 생성
        options = {
            "root_context_id": context_id
        }
        
        # Add tools if specified
        if tools:
            options["allowed_tools"] = tools
        
        # Send the prompt within the context
        response = await self.client.send_prompt(message, options)
        
        # Update context metadata with conversation progress
        await self.context_manager.update_context_metadata(
            context_id,
            {
                f"message_{datetime.now().timestamp()}": message[:50] + "...",
                "last_interaction": datetime.now().isoformat()
            }
        )
        
        return response
    
    async def get_conversation_history(자기, 컨텍스트_id):
        """컨텍스트에서 대화 기록을 검색합니다"""
        context_info = await self.context_manager.get_context_info(context_id)
        messages = await self.client.get_context_messages(context_id)
        
        return {
            "context_info": context_info,
            "messages": messages
        }
    
    async def end_session(self, context_id):
        """컨텍스트를 보관하여 보조 세션을 종료합니다"""
        # 먼저 요약 프롬프트를 생성합니다
        summary_response = await self.client.send_prompt(
            "Please summarize our conversation and any key points or decisions made.",
            {"root_context_id": context_id}
        )
        
        # Store summary in metadata
        await self.context_manager.update_context_metadata(
            context_id,
            {
                "summary": summary_response.generated_text,
                "ended_at": datetime.now().isoformat(),
                "status": "completed"
            }
        )
        
        # Archive the context
        await self.context_manager.archive_context(context_id)
        
        return {
            "status": "completed",
            "summary": summary_response.generated_text
        }

# 사용 예
async def demo_assistant_session():
    assistant = AssistantSession("https://mcp-server-example.com")
    
   # 1. Create session
    context_id = await assistant.create_session(
        "Technical Support Session",
        {"name": "Alex", "technical_level": "advanced", "product": "Cloud Services"}
    )
    print(f"Created session with context ID: {context_id}")
    
    # 2. First interaction
    response1 = await assistant.send_message(
        context_id, 
        "I'm having trouble with the auto-scaling feature in your cloud platform.",
        ["documentation_search", "diagnostic_tool"]
    )
    print(f"Response 1: {response1.generated_text}")
    
    # Second interaction in the same context
    response2 = await assistant.send_message(
        context_id,
        "Yes, I've already checked the configuration settings you mentioned, but it's still not working."
    )
    print(f"Response 2: {response2.generated_text}")
    
    # 3. Get history
    history = await assistant.get_conversation_history(context_id)
    print(f"Session has {len(history['messages'])} messages")
    
    # 4. End session
    end_result = await assistant.end_session(context_id)
    print(f"Session ended with summary: {end_result['summary']}")

__name__ == "__main__"인 경우:
    asyncio.run(demo_assistant_session())
```

이전 코드에서 우리는 다음을 수행했습니다.

1. `create_session` 함수를 사용하여 기술 지원 세션에 대한 루트 컨텍스트를 생성했습니다. 이 컨텍스트에는 이름, 기술 수준 등의 사용자 정보가 포함됩니다.

1. 해당 컨텍스트 내에서 여러 메시지를 전송하여 모델이 `send_message` 함수를 사용하여 상태를 유지할 수 있도록 했습니다. 전송되는 메시지는 자동 크기 조정 기능의 문제와 관련이 있습니다.

1. 컨텍스트 정보와 메시지를 제공하는 `get_conversation_history` 함수를 사용하여 대화 기록을 검색합니다.

1. `end_session` 함수를 사용하여 컨텍스트를 보관하고 요약을 생성하여 세션을 종료했습니다. 요약에는 대화의 주요 내용이 담겨 있습니다.

</세부정보>

## 루트 컨텍스트 모범 사례

루트 컨텍스트를 효과적으로 관리하기 위한 몇 가지 모범 사례는 다음과 같습니다.

- **집중된 컨텍스트 만들기**: 명확성을 유지하기 위해 다양한 대화 목적이나 도메인에 대해 별도의 루트 컨텍스트를 만듭니다.

- **만료 정책 설정**: 저장소를 관리하고 데이터 보존 정책을 준수하기 위해 오래된 컨텍스트를 보관하거나 삭제하는 정책을 구현합니다.

- **관련 메타데이터 저장**: 컨텍스트 메타데이터를 사용하여 나중에 유용할 수 있는 대화에 대한 중요한 정보를 저장합니다.

- **컨텍스트 ID를 일관되게 사용**: 컨텍스트가 생성되면 연속성을 유지하기 위해 관련된 모든 요청에 ​​해당 ID를 일관되게 사용합니다.

- **요약 생성**: 맥락이 ​​커지면 맥락 크기를 관리하면서 필수 정보를 포착하기 위해 요약을 생성하는 것을 고려하세요.

- **접근 제어 구현**: 다중 사용자 시스템의 경우 대화 컨텍스트의 개인 정보 보호 및 보안을 보장하기 위해 적절한 접근 제어를 구현합니다.

- **맥락 제한 처리**: 맥락 크기 제한을 인지하고 매우 긴 대화를 처리하기 위한 전략을 구현하세요.

- **완료 시 보관**: 대화가 완료되면 컨텍스트를 보관하여 대화 기록을 보존하는 동시에 리소스를 확보합니다.

## 다음은 무엇입니까?

- [5.5 라우팅](../mcp-routing/README.md)