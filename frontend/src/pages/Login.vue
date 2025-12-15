<template>
  <v-container class="fill-height login-container" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="pa-6 rounded-xl" style="box-shadow: 0 4px 20px rgba(0,0,0,0.08); border: none;">
          <v-card-title class="text-h4 text-center mb-4" style="font-weight: 500; color: #2c3e50;">
            企业助手登录 🔒
          </v-card-title>

          <v-card-text>
            <v-form @submit.prevent="handleLogin">
              <v-text-field
                v-model="username"
                label="用户名"
                prepend-inner-icon="mdi-account-outline"
                required
                variant="outlined"
                density="comfortable"
                class="mb-3"
              ></v-text-field>

              <v-text-field
                v-model="password"
                label="密码"
                prepend-inner-icon="mdi-lock-outline"
                type="password"
                required
                variant="outlined"
                density="comfortable"
                class="mb-3"
              ></v-text-field>

              <v-btn
                type="submit"
                color="primary"
                block
                size="large"
                :loading="loading"
                class="mt-4 text-none"
              >
                登 录
              </v-btn>
            </v-form>

            <v-alert v-if="error" type="error" class="mt-4" density="compact">
                {{ error }}
            </v-alert>

          </v-card-text>

          <v-card-actions class="justify-center">
            <v-btn variant="text" size="small" class="text-none">
              <router-link to="/register" style="text-decoration: none; color: inherit;">
                没有账号？去注册
              </router-link>
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.login-container {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}
</style>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { post, tokenManager } from '@/utils/api';

const router = useRouter();
const username = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');

const handleLogin = async () => {
  error.value = '';
  loading.value = true;

  try {
    const result = await post<{
      access_token: string;
      refresh_token: string;
      username: string;
      user: any;
    }>('/login', {
      username: username.value,
      password: password.value
    }, { skipAuth: true });

    // 检查返回数据结构
    if (result.code !== 200 || !result.data?.access_token) {
      error.value = result.message || '登录失败，服务器返回数据格式错误。';
      return;
    }

    // 存储 Token 和用户信息
    tokenManager.saveToken(
      result.data.access_token,
      result.data.refresh_token
    );
    localStorage.setItem('username', result.data.username || '');

    // 路由跳转到主页
    router.push('/');

  } catch (e: any) {
    error.value = e.message || '网络连接失败，请检查服务器是否运行。';
  } finally {
    loading.value = false;
  }
};
</script>
