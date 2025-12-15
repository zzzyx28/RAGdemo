#file:src/pages/Register.vue
<template>
  <v-container class="fill-height register-container" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="pa-6 rounded-xl" style="box-shadow: 0 4px 20px rgba(0,0,0,0.08); border: none;">
          <v-card-title class="text-h4 text-center mb-4" style="font-weight: 500; color: #2c3e50;">
            用户注册 📝
          </v-card-title>

          <v-card-text>
            <v-form @submit.prevent="handleRegister">
              <v-text-field
                v-model="username"
                label="用户名"
                prepend-inner-icon="mdi-account-outline"
                required
                variant="outlined"
                density="comfortable"
                class="mb-3"
                :rules="[rules.required, rules.min]"
              ></v-text-field>

              <v-text-field
                v-model="email"
                label="邮箱"
                prepend-inner-icon="mdi-email-outline"
                type="email"
                required
                variant="outlined"
                density="comfortable"
                class="mb-3"
                :rules="[rules.required, rules.email]"
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
                :rules="[rules.required, rules.passwordMin]"
              ></v-text-field>

              <v-text-field
                v-model="confirmPassword"
                label="确认密码"
                prepend-inner-icon="mdi-lock-check-outline"
                type="password"
                required
                variant="outlined"
                density="comfortable"
                class="mb-3"
                :rules="[rules.required, rules.passwordMatch]"
              ></v-text-field>

              <v-btn
                type="submit"
                color="primary"
                block
                size="large"
                :loading="loading"
                class="mt-4 text-none"
              >
                注 册
              </v-btn>
            </v-form>

            <v-alert v-if="error" type="error" class="mt-4" density="compact">
                {{ error }}
            </v-alert>

            <v-alert v-if="success" type="success" class="mt-4" density="compact">
                {{ success }}
            </v-alert>

          </v-card-text>

          <v-card-actions class="justify-center">
            <v-btn variant="text" size="small" class="text-none">
              <router-link to="/login" style="text-decoration: none; color: inherit;">
                已有账号？去登录
              </router-link>
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { post, tokenManager } from '@/utils/api';

const router = useRouter();
const username = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const loading = ref(false);
const error = ref('');
const success = ref('');

// 表单验证规则
const rules = reactive({
  required: (value: string) => !!value || '此字段为必填项',
  min: (value: string) => (value && value.length >= 3) || '至少需要3个字符',
  email: (value: string) => {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(value) || '请输入有效的邮箱地址';
  },
  passwordMin: (value: string) => (value && value.length >= 8) || '密码至少需要8个字符',
  passwordMatch: () => password.value === confirmPassword.value || '两次输入的密码不一致'
});

const handleRegister = async () => {
  // 重置提示信息
  error.value = '';
  success.value = '';

  // 基本表单验证
  if (!username.value || !email.value || !password.value || !confirmPassword.value) {
    error.value = '请填写所有字段';
    return;
  }

  if (username.value.length < 3) {
    error.value = '用户名至少需要3个字符';
    return;
  }

  // 邮箱格式验证
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailPattern.test(email.value)) {
    error.value = '请输入有效的邮箱地址';
    return;
  }

  if (password.value.length < 8) {
    error.value = '密码至少需要8个字符';
    return;
  }

  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致';
    return;
  }

  loading.value = true;

  try {
    const result = await post('/register', {
      username: username.value,
      email: email.value,
      password: password.value
    }, { skipAuth: true });

    if (result.code !== 200 && result.code !== 201) {
      error.value = result.message || '注册失败，请稍后重试。';
      return;
    }

    // 注册成功
    success.value = '注册成功！即将跳转到登录页面...';

    // 3秒后跳转到登录页面
    setTimeout(() => {
      router.push('/login');
    }, 3000);

  } catch (e: any) {
    error.value = e.message || '网络连接失败，请检查服务器是否运行。';
    } finally {
      loading.value = false;
    }
  };
</script>

<style scoped>
.register-container {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}
</style>
