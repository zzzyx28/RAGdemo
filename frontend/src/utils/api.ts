/**
 * 统一的HTTP请求工具
 * 自动处理JWT Token、错误处理和Token刷新
 */

const API_BASE_URL = 'http://localhost:5000/api'

/**
 * API响应接口
 */
export interface APIResponse<T = any> {
  code: number
  message: string
  data: T
  errors?: {
    details?: string | string[]
    [key: string]: any
  }
}

/**
 * 请求配置接口
 */
interface RequestConfig extends RequestInit {
  skipAuth?: boolean  // 是否跳过认证（用于登录、注册等接口）
  skipErrorHandler?: boolean  // 是否跳过统一错误处理
}

/**
 * 从localStorage获取Token
 */
function getToken(): string | null {
  return localStorage.getItem('access_token')
}

/**
 * 从localStorage获取Refresh Token
 */
function getRefreshToken(): string | null {
  return localStorage.getItem('refresh_token')
}

/**
 * 保存Token到localStorage
 */
function saveToken(accessToken: string, refreshToken?: string): void {
  localStorage.setItem('access_token', accessToken)
  if (refreshToken) {
    localStorage.setItem('refresh_token', refreshToken)
  }
}

/**
 * 清除Token
 */
function clearTokens(): void {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('username')
}

/**
 * 刷新Access Token
 */
async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken()
  if (!refreshToken) {
    return null
  }

  try {
    const response = await fetch(`${API_BASE_URL}/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${refreshToken}`
      }
    })

    if (!response.ok) {
      // Refresh Token也过期了，需要重新登录
      clearTokens()
      return null
    }

    const result = await response.json()
    if (result.code === 200 && result.data?.access_token) {
      saveToken(result.data.access_token)
      return result.data.access_token
    }

    return null
  } catch (error) {
    console.error('刷新Token失败:', error)
    clearTokens()
    return null
  }
}

/**
 * 处理401错误：尝试刷新Token后重试
 */
async function handle401Error(
  url: string,
  originalConfig: RequestConfig
): Promise<Response | null> {
  // 尝试刷新Token
  const newToken = await refreshAccessToken()
  
  if (!newToken) {
    // 刷新失败，跳转到登录页
    if (typeof window !== 'undefined') {
      window.location.href = '/login'
    }
    return null
  }

  // 使用新Token重试请求
  const retryConfig: RequestInit = {
    ...originalConfig,
    headers: {
      ...originalConfig.headers,
      'Authorization': `Bearer ${newToken}`
    }
  }

  return fetch(url, retryConfig)
}

/**
 * 统一的HTTP请求函数
 */
async function request<T = any>(
  endpoint: string,
  config: RequestConfig = {}
): Promise<APIResponse<T>> {
  const { skipAuth = false, skipErrorHandler = false, ...fetchConfig } = config

  // 构建完整URL
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`

  // 设置默认headers
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(fetchConfig.headers as Record<string, string> || {})
  }

  // 添加认证头（如果需要）
  if (!skipAuth) {
    const token = getToken()
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
  }

  // 合并配置
  const finalConfig: RequestInit = {
    ...fetchConfig,
    headers
  }

  try {
    let response = await fetch(url, finalConfig)

    // 处理401错误：Token过期，尝试刷新
    if (response.status === 401 && !skipAuth) {
      const retryResponse = await handle401Error(url, finalConfig)
      if (retryResponse) {
        response = retryResponse
      } else {
        // 刷新失败，返回401错误
        throw new Error('认证失败，请重新登录')
      }
    }

    // 处理其他HTTP错误
    if (!response.ok && !skipErrorHandler) {
      const errorData = await response.json().catch(() => ({
        message: `请求失败: ${response.status} ${response.statusText}`
      }))
      
      // 422错误通常是Token格式错误
      if (response.status === 422) {
        clearTokens()
        if (typeof window !== 'undefined') {
          window.location.href = '/login'
        }
        throw new Error(errorData.message || errorData.msg || 'Token无效，请重新登录')
      }

      throw new Error(errorData.message || errorData.msg || `请求失败: ${response.status}`)
    }

    // 解析响应
    const data = await response.json()
    return data

  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error('网络请求失败')
  }
}

/**
 * GET请求
 */
export async function get<T = any>(
  endpoint: string,
  config?: RequestConfig
): Promise<APIResponse<T>> {
  return request<T>(endpoint, {
    ...config,
    method: 'GET'
  })
}

/**
 * POST请求
 */
export async function post<T = any>(
  endpoint: string,
  body?: any,
  config?: RequestConfig
): Promise<APIResponse<T>> {
  return request<T>(endpoint, {
    ...config,
    method: 'POST',
    body: body ? JSON.stringify(body) : undefined
  })
}

/**
 * PUT请求
 */
export async function put<T = any>(
  endpoint: string,
  body?: any,
  config?: RequestConfig
): Promise<APIResponse<T>> {
  return request<T>(endpoint, {
    ...config,
    method: 'PUT',
    body: body ? JSON.stringify(body) : undefined
  })
}

/**
 * DELETE请求
 */
export async function del<T = any>(
  endpoint: string,
  config?: RequestConfig
): Promise<APIResponse<T>> {
  return request<T>(endpoint, {
    ...config,
    method: 'DELETE'
  })
}

/**
 * 文件上传请求（FormData）
 */
export async function upload<T = any>(
  endpoint: string,
  formData: FormData,
  config?: RequestConfig
): Promise<APIResponse<T>> {
  const { skipAuth = false, ...fetchConfig } = config || {}

  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`

  const headers: Record<string, string> = {}

  // 添加认证头
  if (!skipAuth) {
    const token = getToken()
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
  }

  // FormData不需要设置Content-Type，浏览器会自动设置
  const finalConfig: RequestInit = {
    ...fetchConfig,
    method: 'POST',
    headers,
    body: formData
  }

  try {
    let response = await fetch(url, finalConfig)

    // 处理401错误
    if (response.status === 401 && !skipAuth) {
      const retryResponse = await handle401Error(url, finalConfig)
      if (retryResponse) {
        response = retryResponse
      } else {
        throw new Error('认证失败，请重新登录')
      }
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        message: `上传失败: ${response.status} ${response.statusText}`
      }))
      throw new Error(errorData.message || errorData.msg || `上传失败: ${response.status}`)
    }

    return await response.json()

  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error('上传失败')
  }
}

/**
 * 导出Token管理函数（供外部使用）
 */
export const tokenManager = {
  getToken,
  getRefreshToken,
  saveToken,
  clearTokens,
  refreshAccessToken
}
