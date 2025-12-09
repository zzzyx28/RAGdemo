import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

export function useAuth() {
  const router = useRouter();
  const isAuthenticated = ref(!!localStorage.getItem('access_token'));
  const currentUsername = ref(localStorage.getItem('username') || '');

  const updateAuthState = () => {
    isAuthenticated.value = !!localStorage.getItem('access_token');
    currentUsername.value = localStorage.getItem('username') || '';
  };

  // 监听其他标签页的 storage 变化
  window.addEventListener('storage', updateAuthState);

  // 监听页面可见性变化，当页面重新可见时检查登录状态（用于从登录页返回的情况）
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
      updateAuthState();
    }
  });

  onMounted(() => {
    updateAuthState();
  });

  // 登出处理函数
  const handleLogout = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        await fetch('http://localhost:5000/api/logout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }
        }).catch(() => {/* 忽略登出接口错误 */});
      }
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('username');
      updateAuthState();
      router.push('/login');
    }
  };

  // 处理登录点击
  const handleLoginClick = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('username');
    isAuthenticated.value = false;
    router.push('/login');
  };

  return {
    isAuthenticated,
    currentUsername,
    updateAuthState,
    handleLogout,
    handleLoginClick
  };
}

