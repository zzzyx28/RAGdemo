<template>
  <v-navigation-drawer
    v-model="localDrawer"
    temporary
    location="left"
    width="280"
    class="chat-history-sidebar"
  >
    <template v-slot:prepend>
      <v-toolbar color="primary" dark>
        <v-toolbar-title class="text-h6">对话历史</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn
          icon="mdi-plus"
          variant="text"
          @click="handleNewConversation"
          title="新建对话"
        ></v-btn>
      </v-toolbar>
    </template>

    <v-list density="compact" nav>
      <v-list-item
        v-for="conv in conversations"
        :key="conv.id"
        :active="selectedConversationId === conv.id"
        @click="handleSelectConversation(conv.id)"
        class="conversation-item"
      >
        <template v-slot:prepend>
          <v-icon icon="mdi-message-text" class="mr-2"></v-icon>
        </template>

        <v-list-item-title class="text-body-2 conversation-title">
          {{ conv.title }}
        </v-list-item-title>

        <v-list-item-subtitle class="text-caption text-grey">
          {{ formatDate(conv.updated_at) }}
        </v-list-item-subtitle>

        <template v-slot:append>
          <v-menu location="bottom">
            <template v-slot:activator="{ props }">
              <v-btn
                icon="mdi-dots-vertical"
                size="x-small"
                variant="text"
                v-bind="props"
                @click.stop
              ></v-btn>
            </template>
            <v-list density="compact">
              <v-list-item @click.stop="handleRenameConversation(conv)">
                <v-list-item-title>重命名</v-list-item-title>
                <template v-slot:prepend>
                  <v-icon icon="mdi-pencil" size="small"></v-icon>
                </template>
              </v-list-item>
              <v-list-item @click.stop="handleDeleteConversation(conv.id)">
                <v-list-item-title>删除</v-list-item-title>
                <template v-slot:prepend>
                  <v-icon icon="mdi-delete" size="small" color="error"></v-icon>
                </template>
              </v-list-item>
            </v-list>
          </v-menu>
        </template>
      </v-list-item>

      <v-list-item v-if="conversations.length === 0" class="text-center text-grey">
        <v-list-item-title class="text-caption">
          暂无对话记录
        </v-list-item-title>
      </v-list-item>
    </v-list>

    <!-- 重命名对话框 -->
    <v-dialog v-model="renameDialog" max-width="400">
      <v-card>
        <v-card-title>重命名对话</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="renameTitle"
            label="对话标题"
            variant="outlined"
            autofocus
            @keydown.enter="confirmRename"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="renameDialog = false">取消</v-btn>
          <v-btn color="primary" variant="flat" @click="confirmRename">确定</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { Conversation } from '@/types/chat';

interface Props {
  modelValue: boolean;
  conversations: Conversation[];
  selectedConversationId: number | null;
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void;
  (e: 'select', conversationId: number | null): void;
  (e: 'new'): void;
  (e: 'delete', conversationId: number): void;
  (e: 'rename', conversationId: number, newTitle: string): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const localDrawer = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
});

const renameDialog = ref(false);
const renameTitle = ref('');
const currentRenameId = ref<number | null>(null);

const handleNewConversation = () => {
  emit('new');
};

const handleSelectConversation = (conversationId: number) => {
  emit('select', conversationId);
};

const handleDeleteConversation = (conversationId: number) => {
  emit('delete', conversationId);
};

const handleRenameConversation = (conv: Conversation) => {
  currentRenameId.value = conv.id;
  renameTitle.value = conv.title;
  renameDialog.value = true;
};

const confirmRename = () => {
  if (currentRenameId.value && renameTitle.value.trim()) {
    emit('rename', currentRenameId.value, renameTitle.value.trim());
    renameDialog.value = false;
    renameTitle.value = '';
    currentRenameId.value = null;
  }
};

const formatDate = (dateString: string) => {
  if (!dateString) return '';
  
  // 后端返回的是 UTC 时间的 ISO 格式字符串（带 Z 后缀）
  const date = new Date(dateString);
  
  // 检查日期是否有效
  if (isNaN(date.getTime())) {
    return '';
  }
  
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  if (days === 0) {
    const hours = Math.floor(diff / (1000 * 60 * 60));
    if (hours === 0) {
      const minutes = Math.floor(diff / (1000 * 60));
      return minutes <= 0 ? '刚刚' : `${minutes}分钟前`;
    }
    return `${hours}小时前`;
  } else if (days === 1) {
    return '昨天';
  } else if (days < 7) {
    return `${days}天前`;
  } else {
    // 使用本地时间显示日期
    return date.toLocaleDateString('zh-CN', { 
      year: 'numeric',
      month: 'short', 
      day: 'numeric' 
    });
  }
};
</script>

<style scoped>
.chat-history-sidebar {
  z-index: 1000;
}

.conversation-item {
  margin-bottom: 4px;
  border-radius: 8px;
}

.conversation-item:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.conversation-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 180px;
}
</style>

