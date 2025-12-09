# JWT 认证机制说明文档

## 一、JWT 认证概述

### 1.1 什么是 JWT？

JWT (JSON Web Token) 是一种开放标准（RFC 7519），用于在各方之间安全地传输信息。JWT 由三部分组成：
- **Header（头部）**：包含令牌类型和签名算法
- **Payload（载荷）**：包含声明（claims），如用户ID、过期时间等
- **Signature（签名）**：用于验证令牌的完整性

### 1.2 JWT 的优势

1. **无状态认证**：服务器不需要存储会话信息，所有信息都在Token中
2. **跨域支持**：可以在不同域名间使用
3. **可扩展性**：易于在微服务架构中使用
4. **安全性**：使用签名确保Token未被篡改

### 1.3 本项目中的JWT实现

本项目使用 **Flask-JWT-Extended** 库实现JWT认证，支持：
- Access Token（访问令牌）：用于API请求认证，有效期24小时
- Refresh Token（刷新令牌）：用于刷新Access Token，有效期30天

---

## 二、后端实现

### 2.1 配置说明

**文件位置**：`backend/app/config.py`

```python
# JWT 认证配置
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-prod')
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # Access Token 24小时过期
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)  # Refresh Token 30天过期
JWT_TOKEN_LOCATION = ['headers']  # 从请求头获取Token
JWT_HEADER_NAME = 'Authorization'
JWT_HEADER_TYPE = 'Bearer'
```

**重要提示**：
- 开发环境可以使用默认密钥
- **生产环境必须通过环境变量设置强密钥**，否则应用启动会失败

### 2.2 认证接口

#### 2.2.1 用户注册

**接口**：`POST /api/register`

**请求体**：
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}
```

**响应**：
```json
{
  "code": 201,
  "message": "注册成功",
  "data": {
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com"
    }
  }
}
```

#### 2.2.2 用户登录

**接口**：`POST /api/login`

**请求体**：
```json
{
  "username": "testuser",
  "password": "password123"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "username": "testuser",
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com"
    }
  }
}
```

#### 2.2.3 刷新Token

**接口**：`POST /api/refresh`

**请求头**：
```
Authorization: Bearer <refresh_token>
```

**响应**：
```json
{
  "code": 200,
  "message": "Token刷新成功",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "username": "testuser"
  }
}
```

#### 2.2.4 用户登出

**接口**：`POST /api/logout`

**请求头**：
```
Authorization: Bearer <access_token>
```

**响应**：
```json
{
  "code": 200,
  "message": "登出成功"
}
```

**注意**：JWT是无状态的，服务端无法主动撤销Token。登出接口主要用于记录日志，实际的Token撤销需要客户端删除本地存储的Token。

#### 2.2.5 获取用户信息

**接口**：`GET /api/profile`

**请求头**：
```
Authorization: Bearer <access_token>
```

**响应**：
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com"
    }
  }
}
```

### 2.3 保护路由

使用 `@jwt_required()` 装饰器保护需要认证的路由：

```python
from flask_jwt_extended import jwt_required, get_jwt_identity

@kb_bp.route('/upload', methods=['POST'])
@jwt_required()  # 需要有效的Access Token
def upload_file():
    user_id = get_jwt_identity()  # 获取Token中的用户ID
    # ... 处理逻辑
```

**已保护的路由**：
- `POST /api/upload` - 文件上传
- `POST /api/delete` - 文件删除
- `GET /api/kb-info` - 获取知识库信息
- `POST /api/chat` - 聊天接口
- `GET /api/profile` - 获取用户信息

### 2.4 错误处理

后端实现了完整的JWT错误处理：

**文件位置**：`backend/app/middleware/error_handler.py`

**错误类型**：
- `NoAuthorizationError` (401)：缺少认证头
- `InvalidHeaderError` (422)：认证头格式错误
- `WrongTokenError` (422)：Token类型错误
- `RevokedTokenError` (401)：Token已被撤销
- `FreshTokenRequired` (422)：需要Fresh Token
- `UserLookupError` (401)：用户不存在或已被禁用

所有JWT错误都会返回统一的错误响应格式。

---

## 三、前端实现

### 3.1 统一的HTTP请求工具

**文件位置**：`frontend/src/utils/api.ts`

该工具提供了以下功能：
- 自动添加Authorization头
- 自动处理Token刷新
- 统一的错误处理
- 支持GET、POST、PUT、DELETE、文件上传

#### 3.1.1 基本使用

```typescript
import { get, post, upload } from '@/utils/api'

// GET请求
const result = await get('/kb-info')

// POST请求
const result = await post('/delete', { filename: 'test.pdf' })

// 文件上传
const formData = new FormData()
formData.append('file', file)
const result = await upload('/upload', formData)
```

#### 3.1.2 Token管理

```typescript
import { tokenManager } from '@/utils/api'

// 获取Token
const token = tokenManager.getToken()

// 保存Token
tokenManager.saveToken(accessToken, refreshToken)

// 清除Token
tokenManager.clearTokens()

// 刷新Token
const newToken = await tokenManager.refreshAccessToken()
```

#### 3.1.3 自动Token刷新机制

当API请求返回401错误时，工具会自动：
1. 使用Refresh Token刷新Access Token
2. 使用新Token重试原请求
3. 如果刷新失败，清除Token并跳转到登录页

### 3.2 登录流程

**文件位置**：`frontend/src/pages/Login.vue`

```typescript
const handleLogin = async () => {
  const result = await post('/login', {
    username: username.value,
    password: password.value
  }, { skipAuth: true })

  if (result.code === 200) {
    // 保存Token
    tokenManager.saveToken(
      result.data.access_token,
      result.data.refresh_token
    )
    localStorage.setItem('username', result.data.username)
    
    // 跳转到主页
    router.push('/')
  }
}
```

### 3.3 路由守卫

**文件位置**：`frontend/src/router/index.ts`

```typescript
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const requiresAuth = to.meta.requiresAuth

  // 需要认证的路由
  if (requiresAuth && !token) {
    next('/login')
  }
  // 已登录用户访问登录/注册页
  else if (token && (to.name === 'Login' || to.name === 'Register')) {
    next('/')
  }
  else {
    next()
  }
})
```

### 3.4 Token存储

Token存储在浏览器的 `localStorage` 中：
- `access_token`：访问令牌
- `refresh_token`：刷新令牌
- `username`：用户名（用于显示）

**安全提示**：
- localStorage中的Token可能受到XSS攻击
- 生产环境建议考虑使用httpOnly Cookie存储Token
- 确保前端代码没有XSS漏洞

---

## 四、安全最佳实践

### 4.1 后端安全

1. **强密钥**：生产环境必须使用强随机密钥
   ```bash
   export JWT_SECRET_KEY=$(openssl rand -hex 32)
   ```

2. **HTTPS**：生产环境必须使用HTTPS传输Token

3. **Token过期时间**：
   - Access Token：建议24小时或更短
   - Refresh Token：建议7-30天

4. **Token黑名单**（可选）：
   - 实现Token撤销机制
   - 使用Redis存储已撤销的Token
   - 在验证Token时检查黑名单

### 4.2 前端安全

1. **XSS防护**：
   - 对所有用户输入进行转义
   - 使用CSP（Content Security Policy）
   - 避免使用 `innerHTML`

2. **CSRF防护**：
   - 使用CSRF Token
   - 验证请求来源

3. **Token存储**：
   - 考虑使用httpOnly Cookie（需要后端配合）
   - 定期检查Token有效性

### 4.3 常见攻击防护

1. **Token泄露**：
   - 不要在URL中传递Token
   - 不要在日志中记录Token
   - 使用HTTPS传输

2. **Token重放攻击**：
   - 使用较短的过期时间
   - 实现Token黑名单
   - 使用nonce机制

3. **中间人攻击**：
   - 强制使用HTTPS
   - 验证SSL证书

---

## 五、故障排查

### 5.1 常见问题

#### 问题1：Token过期后无法自动刷新

**原因**：Refresh Token也过期了

**解决**：用户需要重新登录

#### 问题2：401错误但Token未过期

**可能原因**：
- Token格式错误
- 服务器密钥已更改
- Token被撤销（如果实现了黑名单）

**解决**：清除Token，重新登录

#### 问题3：CORS错误

**原因**：后端CORS配置不正确

**解决**：检查 `backend/app/config.py` 中的 `CORS_ORIGINS` 配置

### 5.2 调试技巧

1. **查看Token内容**：
   - 访问 https://jwt.io
   - 粘贴Token查看内容（不包含签名验证）

2. **检查网络请求**：
   - 打开浏览器开发者工具
   - 查看Network标签
   - 检查请求头中的Authorization字段

3. **查看后端日志**：
   - 检查 `backend/logs/app.log`
   - 查看JWT相关错误信息

---

## 六、扩展功能

### 6.1 Token黑名单

如果需要实现Token撤销功能，可以：

1. 在登出时将Token的JTI存入Redis
2. 创建JWT回调函数检查黑名单
3. 在验证Token时检查是否在黑名单中

### 6.2 多设备登录管理

1. 在Token中存储设备ID
2. 限制每个用户的设备数量
3. 提供设备管理界面

### 6.3 权限控制

1. 在Token中存储用户角色和权限
2. 使用装饰器检查权限
3. 实现基于角色的访问控制（RBAC）

---

## 七、总结

本项目的JWT认证实现包括：

✅ **后端**：
- 完整的JWT配置
- 登录、注册、刷新、登出接口
- 路由保护装饰器
- 完善的错误处理

✅ **前端**：
- 统一的HTTP请求工具
- 自动Token刷新机制
- 路由守卫
- 统一的错误处理

✅ **安全**：
- Token过期管理
- 自动刷新机制
- 错误处理

该实现已经可以满足大多数Web应用的需求。在生产环境部署时，请确保：
1. 使用强密钥
2. 启用HTTPS
3. 配置正确的CORS
4. 定期检查安全更新

