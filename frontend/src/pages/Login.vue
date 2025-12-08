<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="pa-6 rounded-xl elevation-5">
          <v-card-title class="text-h4 text-center mb-4 font-weight-bold">
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

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const username = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');

const handleLogin = async () => {
  error.value = '';
  loading.value = true;

  try {
    const response = await fetch('http://localhost:5000/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: username.value,
        password: password.value
      }),
    });

    if (!response.ok) {
      const data = await response.json();
      error.value = data.msg || '登录失败，请检查用户名和密码。';
      return;
    }

    const data = await response.json();

    // 1. 存储 Token (核心步骤)
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('username', data.username);

    // 2. 路由跳转到主页
    router.push('/');

  } catch (e) {
    error.value = '网络连接失败，请检查服务器是否运行。';
  } finally {
    loading.value = false;
  }
};
</script>
