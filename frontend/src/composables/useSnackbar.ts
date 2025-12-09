import { ref } from 'vue';
import type { SnackbarState } from '@/types/chat';

export function useSnackbar() {
  const snackbar = ref<SnackbarState>({
    show: false,
    text: '',
    color: 'success',
    timeout: 4000
  });

  /**
   * 统一显示 SnackBar 提示
   */
  const showSnackbar = (text: string, color: 'success' | 'error' | 'warning' | 'info' = 'info') => {
    snackbar.value.text = text;
    snackbar.value.color = color;
    snackbar.value.show = true;
  };

  /**
   * 统一解析后端错误信息
   */
  const parseErrorMsg = (result: any): string => {
    if (result.errors?.details) {
      return Array.isArray(result.errors.details) 
        ? result.errors.details.join('; ') 
        : result.errors.details;
    }
    return result.message || '未知错误';
  };

  return {
    snackbar,
    showSnackbar,
    parseErrorMsg
  };
}

