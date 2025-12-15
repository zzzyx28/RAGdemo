import { ref, type Ref } from 'vue';
import { get, post, put, del } from '@/utils/api';
import type { Conversation, Message } from '@/types/chat';

export function useConversationHistory(
  isAuthenticated: Ref<boolean>,
  showSnackbar: (text: string, color?: 'success' | 'error' | 'warning' | 'info') => void
) {
  const conversations = ref<Conversation[]>([]);
  const currentConversationId = ref<number | null>(null);
  const isLoading = ref(false);

  // 获取对话列表
  const fetchConversations = async () => {
    if (!isAuthenticated.value) {
      conversations.value = [];
      return;
    }

    try {
      isLoading.value = true;
      const response = await get<Conversation[]>('/chat/conversations');
      if (response.code === 200) {
        // 后端已经按更新时间倒序排列，直接使用
        conversations.value = response.data || [];
      } else {
        showSnackbar(response.message || '获取对话列表失败', 'error');
      }
    } catch (error: any) {
      console.error('获取对话列表失败:', error);
      showSnackbar(error.message || '获取对话列表失败', 'error');
    } finally {
      isLoading.value = false;
    }
  };

  // 创建新对话
  const createConversation = async (title: string = '新对话'): Promise<Conversation | null> => {
    if (!isAuthenticated.value) {
      showSnackbar('请先登录', 'warning');
      return null;
    }

    try {
      const response = await post<Conversation>('/chat/conversations', { title });
      if (response.code === 200) {
        const newConv = response.data;
        conversations.value.unshift(newConv);
        return newConv;
      } else {
        showSnackbar(response.message || '创建对话失败', 'error');
        return null;
      }
    } catch (error: any) {
      console.error('创建对话失败:', error);
      showSnackbar(error.message || '创建对话失败', 'error');
      return null;
    }
  };

  // 获取单个对话及其消息
  const fetchConversation = async (conversationId: number, updateList: boolean = false, silent: boolean = false): Promise<Conversation | null> => {
    if (!isAuthenticated.value) {
      return null;
    }

    try {
      const response = await get<Conversation>(`/chat/conversations/${conversationId}`);
      if (response.code === 200) {
        const conversation = response.data;
        // 如果需要在列表中更新，则更新列表中的对应项
        if (updateList && conversation) {
          const index = conversations.value.findIndex(c => c.id === conversationId);
          if (index !== -1) {
            // 更新现有对话，保持排序（按更新时间）
            conversations.value[index] = conversation;
            // 重新排序，确保最新的在最前面
            conversations.value.sort((a, b) => {
              const timeA = new Date(a.updated_at).getTime();
              const timeB = new Date(b.updated_at).getTime();
              return timeB - timeA;
            });
          } else {
            // 如果不在列表中，添加到列表开头
            conversations.value.unshift(conversation);
          }
        }
        return conversation;
      } else {
        if (!silent) {
          showSnackbar(response.message || '获取对话失败', 'error');
        }
        return null;
      }
    } catch (error: any) {
      console.error('获取对话失败:', error);
      if (!silent) {
        showSnackbar(error.message || '获取对话失败', 'error');
      }
      return null;
    }
  };

  // 更新对话标题
  const updateConversationTitle = async (conversationId: number, newTitle: string) => {
    if (!isAuthenticated.value) {
      return;
    }

    try {
      const response = await put<Conversation>(`/chat/conversations/${conversationId}`, {
        title: newTitle
      });
      if (response.code === 200) {
        const index = conversations.value.findIndex(c => c.id === conversationId);
        if (index !== -1) {
          conversations.value[index] = response.data;
        }
        showSnackbar('重命名成功', 'success');
      } else {
        showSnackbar(response.message || '重命名失败', 'error');
      }
    } catch (error: any) {
      console.error('重命名失败:', error);
      showSnackbar(error.message || '重命名失败', 'error');
    }
  };

  // 删除对话
  const deleteConversation = async (conversationId: number) => {
    if (!isAuthenticated.value) {
      return;
    }

    try {
      const response = await del(`/chat/conversations/${conversationId}`);
      if (response.code === 200) {
        conversations.value = conversations.value.filter(c => c.id !== conversationId);
        if (currentConversationId.value === conversationId) {
          currentConversationId.value = null;
        }
        showSnackbar('删除成功', 'success');
      } else {
        showSnackbar(response.message || '删除失败', 'error');
      }
    } catch (error: any) {
      console.error('删除对话失败:', error);
      showSnackbar(error.message || '删除失败', 'error');
    }
  };

  // 选择对话
  const selectConversation = (conversationId: number | null) => {
    currentConversationId.value = conversationId;
  };

  // 清空当前对话
  const clearCurrentConversation = () => {
    currentConversationId.value = null;
  };

  return {
    conversations,
    currentConversationId,
    isLoading,
    fetchConversations,
    createConversation,
    fetchConversation,
    updateConversationTitle,
    deleteConversation,
    selectConversation,
    clearCurrentConversation
  };
}

