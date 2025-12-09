import { ref, nextTick, watch, type Ref } from 'vue';
import { useRouter } from 'vue-router';
import type { Message } from '@/types/chat';

export function useChat(
  isAuthenticated: Ref<boolean>,
  showSnackbar: (text: string, color?: 'success' | 'error' | 'warning' | 'info') => void
) {
  const router = useRouter();
  const messages = ref<Message[]>([]);
  const inputMessage = ref('');
  const isLoading = ref(false);
  const ragEnabled = ref(true);
  const chatContainer = ref<HTMLElement | null>(null);

  // 自动滚动到底部
  const scrollToBottom = () => {
    nextTick(() => {
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
      }
    });
  };

  // 监听消息变化，自动滚动到底部
  watch(() => messages.value.length, () => {
    scrollToBottom();
  }, { deep: true });

  // 处理 Enter 键：Shift+Enter 换行，Enter 发送
  const handleKeyDown = (event: KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  // 处理流式响应的辅助函数
  async function processStreamResponse(response: Response, assistantMsgIndex: number) {
    const assistantMsg = messages.value[assistantMsgIndex];

    if (!response.body || !assistantMsg) {
      if (assistantMsg) assistantMsg.content = "服务器未返回数据";
      isLoading.value = false;
      scrollToBottom();
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.slice(6);
          if (dataStr === '[DONE]') break;

          try {
            const data = JSON.parse(dataStr);

            // 处理特定事件：检索完成
            if (data.type === 'searching_end') {
              assistantMsg.isRagSearching = false;
              if (data.sources) {
                assistantMsg.sources = data.sources;
              }
            }
            // 处理流式文本
            else if (data.content) {
              assistantMsg.isRagSearching = false; // 确保检索状态被清除
              assistantMsg.content += data.content;
              scrollToBottom();
            }
          } catch (parseError) {
            console.error('解析SSE数据失败:', parseError);
          }
        }
      }
    }

    // 流式响应完成后滚动到底部
    scrollToBottom();
  }

  const sendMessage = async () => {
    if (!inputMessage.value.trim() || isLoading.value) return;

    // 检查登录状态
    if (!isAuthenticated.value) {
      showSnackbar('请先登录后再进行对话', 'warning');
      return;
    }

    const userText = inputMessage.value;
    messages.value.push({ role: 'user', content: userText });
    inputMessage.value = '';
    isLoading.value = true;
    scrollToBottom();

    const assistantMsgIndex = messages.value.push({
      role: 'assistant',
      content: '',
      isRagSearching: ragEnabled.value,
      sources: []
    }) - 1;

    try {
      const { tokenManager } = await import('@/utils/api');
      let token = tokenManager.getToken();

      if (!token) {
        showSnackbar("登录状态已失效，请重新登录", 'warning');
        isLoading.value = false;
        messages.value.pop();
        messages.value.pop(); // 同时移除用户消息
        return;
      }

      const performRequest = async (current_token: string) => {
        return fetch('http://localhost:5000/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${current_token}`
          },
          body: JSON.stringify({
            message: userText,
            use_rag: ragEnabled.value
          }),
        });
      };

      let response = await performRequest(token);

      // 尝试刷新Token并重试
      if (response.status === 401) {
        const newToken = await tokenManager.refreshAccessToken();

        if (newToken) {
          token = newToken; // 更新token
          response = await performRequest(newToken); // 使用新Token重试
        } else {
          showSnackbar('登录状态已失效，请重新登录。', 'warning');
          tokenManager.clearTokens();
          router.push('/login');
          isLoading.value = false;
          messages.value.pop();
          return;
        }
      }

      // 处理 422 错误（JWT token 无效）或重试后的非200/401错误
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: '服务器返回错误' }));
        const errorMsg = `请求失败: ${errorData.error || errorData.message || '服务器错误'}`;

        const assistantMsg = messages.value[assistantMsgIndex];
        if (assistantMsg) {
          assistantMsg.content = errorMsg;
          assistantMsg.isRagSearching = false;
        }

        if (response.status === 422 || response.status === 401) {
          // Token无效/认证失败
          showSnackbar(errorMsg, 'error');
          tokenManager.clearTokens();
          router.push('/login');
        } else {
          showSnackbar(errorMsg, 'error');
        }

        isLoading.value = false;
        return;
      }

      // 处理流式响应
      await processStreamResponse(response, assistantMsgIndex);

    } catch (e: any) {
      console.error(e);
      const assistantMsg = messages.value[messages.value.length - 1];
      if (assistantMsg && assistantMsg.role === 'assistant') {
        assistantMsg.content = `系统错误，请检查后端连接或网络：${e.message || '未知错误'}`;
        assistantMsg.isRagSearching = false;
      }
    } finally {
      isLoading.value = false;
      scrollToBottom();
    }
  };

  return {
    messages,
    inputMessage,
    isLoading,
    ragEnabled,
    chatContainer,
    sendMessage,
    handleKeyDown
  };
}

