# Cloudflare Worker：技术图片云端归档入口

此 Worker 是仓库内的实现稿，**不是已部署服务**。部署后接收图片 Base64 与归档元数据，并将图片及 JSON sidecar 作为单个 Git commit 写入现有待归档队列。既有 GitHub Actions 负责归档、插入 Markdown、更新索引和链接校验。

## API

- GET /health：健康检查。
- POST /v1/archive-image：需要 Authorization: Bearer <INGEST_TOKEN>。
- 请求体最大约 29 MiB；图片最大 20 MiB。
- 支持 PNG/JPEG/WEBP/GIF/SVG；SVG 拒绝常见脚本和事件属性。
- document 必须指向仓库中已存在的相对 Markdown 路径。
- 默认状态为 Draft。

请求体字段：title、document、image_base64、mime_type 必填；filename、source、status 可选。image_base64 必须是真实图片二进制的标准 Base64，不是图片 URL，也不带 data URI 前缀。

## 部署步骤（需要仓库所有者执行）

1. 安装 Node.js 与 Wrangler，并运行 npx wrangler login。
2. 在此目录运行 npx wrangler deploy，记录部署生成的 HTTPS Worker URL。
3. 创建仅授予 xp598008AI/knowledgebase 的 fine-grained GitHub token，Contents 权限 Read and write。执行 npx wrangler secret put GH_TOKEN 并粘贴 token。
4. 生成独立的高熵随机调用密钥，执行 npx wrangler secret put INGEST_TOKEN。密钥只放在 Worker secret 与自定义 GPT Action 鉴权设置中。
5. 访问部署 URL 的 /health。它只能证明 Worker 可访问，不证明 GitHub 写入成功。

## 重要能力边界

- 此提交仅将 Worker 源码和配置放进仓库；它没有部署到 Cloudflare，也没有获得 Cloudflare/GitHub token 或 Action 密钥。
- 自定义 GPT Actions 只能发送它实际获得的输入数据。必须验证当前 GPT 能否把刚生成的图像二进制转换成 image_base64 并提交给 Action。图片可视预览、Markdown 或临时 URL 并不等于接口收到了图片字节。
- 如果 GPT Action 上下文无法读取图像原始字节，云端入口虽可部署，自动上传链路仍不完整；不可声称端到端完成。
- Worker 使用非强制 fast-forward 更新；若 main 在读 ref 后发生并发提交，GitHub 会拒绝更新以避免覆盖。确认没有重复提交后再重试。
- 请勿上传机密、个人敏感数据或未获授权素材。
