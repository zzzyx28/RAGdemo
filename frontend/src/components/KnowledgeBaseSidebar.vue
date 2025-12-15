<template>
  <v-navigation-drawer :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" 
                       width="300" color="#f8f9fa" class="border-e">
    <div class="pa-4">
      <v-btn block color="primary" prepend-icon="mdi-plus" class="mb-4 text-none" elevation="0" disabled>
        新建知识库
      </v-btn>

      <div class="text-subtitle-2 text-grey-darken-1 mb-2 font-weight-bold">
        当前知识库 ({{ kbStats.fileCount }})
      </div>

      <v-list density="compact" nav bg-color="transparent" v-if="kbFiles.length > 0">
        <v-list-item
          v-for="(file, i) in kbFiles"
          :key="i"
          rounded="lg"
          :value="file.name"
          class="mb-1 knowledge-item"
        >
          <template v-slot:prepend>
            <v-icon :icon="getFileIcon(file.type)" :color="getFileColor(file.type)"></v-icon>
          </template>

          <v-list-item-title class="font-weight-medium text-body-2 text-truncate">{{ file.name }}</v-list-item-title>
          <v-list-item-subtitle class="text-caption" style="font-size: 10px !important;">{{
              file.size
            }}
          </v-list-item-subtitle>

          <template v-slot:append>
            <div class="d-flex align-center">
              <v-icon icon="mdi-check-circle" size="small" color="success" class="status-icon"></v-icon>

              <v-btn
                icon="mdi-trash-can-outline"
                size="x-small"
                variant="text"
                color="error"
                class="delete-btn ml-1"
                @click.stop="$emit('delete-file', file.name)"
                title="删除知识库文件"
              ></v-btn>
            </div>
          </template>
        </v-list-item>
      </v-list>

      <div v-else class="text-center py-10 text-grey-lighten-1">
        <v-icon icon="mdi-folder-open-outline" size="large" class="mb-2"></v-icon>
        <div class="text-caption">暂无文档，请上传</div>
      </div>

      <v-divider class="my-3"></v-divider>

      <div
        class="upload-zone pa-4 border-dashed rounded-lg text-center cursor-pointer position-relative"
        :class="{ 'bg-blue-lighten-5': isDragging }"
        @click="triggerUpload"
        @dragover.prevent="handleDragover"
        @dragleave.prevent="handleDragleave"
        @drop.prevent="handleDropInternal"
        style="transition: background-color 0.2s;"
      >
        <div v-if="isUploading" class="d-flex flex-column align-center justify-center py-2">
          <v-progress-circular indeterminate color="primary" size="24" class="mb-2"></v-progress-circular>
          <div class="text-caption text-primary">正在上传并索引...</div>
        </div>

        <div v-else class="text-grey-darken-1">
          <v-icon icon="mdi-cloud-upload" size="large" class="mb-2" :color="isDragging ? 'primary' : ''"></v-icon>
          <div class="text-caption">
            {{ isDragging ? '松开鼠标上传' : '点击或拖拽上传文档' }}
            <br><span class="text-grey-lighten-1" style="font-size: 10px">(支持 PDF, Word, MD)</span>
          </div>
        </div>

        <input
          type="file"
          ref="fileInput"
          style="display: none"
          @change="handleFileSelect"
          accept=".pdf,.md,.txt,.doc,.docx"
          multiple
        >
      </div>
    </div>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import type { KnowledgeFile } from '@/types/chat';

interface Props {
  modelValue: boolean;
  kbFiles: KnowledgeFile[];
  kbStats: { fileCount: number; vectorCount: number };
  isUploading: boolean;
  getFileIcon: (type: string) => string;
  getFileColor: (type: string) => string;
  handleFileSelect: (e: Event) => void;
  handleDrop: (e: DragEvent) => void;
}

const props = defineProps<Props>();
defineEmits<{
  'update:modelValue': [value: boolean];
  'delete-file': [filename: string];
}>();

const fileInput = ref<HTMLInputElement | null>(null);
const isDragging = ref(false);

// 内部处理 triggerUpload
const triggerUpload = () => {
  if (!props.isUploading) fileInput.value?.click();
};

// 处理拖拽事件
const handleDragover = (e: DragEvent) => {
  e.preventDefault();
  isDragging.value = true;
};

const handleDragleave = (e: DragEvent) => {
  e.preventDefault();
  isDragging.value = false;
};

const handleDropInternal = (e: DragEvent) => {
  e.preventDefault();
  isDragging.value = false;
  props.handleDrop(e);
};

// 暴露方法给父组件
defineExpose({
  fileInput,
  triggerUpload
});
</script>

<style scoped>
.border-dashed {
  border: 2px dashed #e0e0e0;
}

/* 知识库列表项优化 */
.knowledge-item {
  transition: background-color 0.15s ease;
}

.knowledge-item:hover {
  background-color: rgba(33, 150, 243, 0.05) !important; /* 悬停时的淡蓝色背景 */
}

/* 让删除按钮默认隐藏，悬停时显示 */
.delete-btn {
  display: none;
}

.knowledge-item:hover .delete-btn {
  display: inline-flex;
}

.knowledge-item:hover .status-icon {
  display: none; /* 悬停时隐藏绿勾，显示垃圾桶 */
}
</style>

