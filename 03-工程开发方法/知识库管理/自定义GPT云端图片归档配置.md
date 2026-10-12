# 自定义 GPT：云端技术图片自动归档配置

## 目标流程

自定义 GPT 生成技术图片 → 用户明确要求归档（按当前需求配置为生成后自动提交）→ GPT Action 调用 Cloudflare Worker → Worker 将图片与元数据一次性提交到私有 GitHub 队列 → 现有 GitHub Actions 自动归档、插入 Markdown、更新资产索引并校验。

**当前状态：Worker 源码和 OpenAPI 契约已提交；Worker 尚未部署，GPT Action 尚未配置，端到端图像字节传输尚未验证。**

## 第一步：部署 Worker

在仓库根目录运行：

    cd cloudflare/technical-image-ingest
    npm install --global wrangler
    npx wrangler login
    npx wrangler deploy
    npx wrangler secret put GH_TOKEN
    npx wrangler secret put INGEST_TOKEN

按提示分别粘贴两个秘密值。GH_TOKEN 使用仅对 xp598008AI/knowledgebase 授权、Contents Read and write 的 fine-grained token；INGEST_TOKEN 是另外生成的高熵随机密钥。二者不能相同，也不能提交到 Git。

部署后访问 Worker URL 的 /health，预期返回 ok=true。该检查不证明 GitHub 写入已成功。

## 第二步：配置自定义 GPT Action

1. 打开 GPT Builder → Configure → Actions → Create new action。
2. 将 cloudflare/technical-image-ingest/openapi.yaml 的内容粘贴到 Schema。
3. 把 servers[0].url 换成实际 Worker HTTPS URL。
4. Authentication 选择 API Key，Auth Type 选择 Bearer，并填入 INGEST_TOKEN。
5. 保存 Action；如 GPT Builder 报 Schema 错误，按界面提示修正。

## 第三步：建议的 GPT Instructions

将以下规则合并进自定义 GPT 的 Instructions，不要覆盖已有技术回答规范：

- 图片生成完成后，若用户已明确授权本次归档或当前任务明确要求生成后自动归档，则调用 archiveTechnicalImage；其他情况不上传。
- 上传前确定标题、目标 Markdown 路径和来源；审核状态默认 Draft。
- image_base64 必须是当前生成图片的真实二进制 Base64。禁止编造 Base64、使用占位符，或用 Markdown/临时 URL 冒充图像数据。
- 如果 Action 上下文无法访问当前生成图片的原始字节，明确说明本次尚未上传，不要提交空数据，也不要声称成功。
- HTTP 201 只代表 GitHub 队列已收到提交。需等 GitHub Actions 完成，才可确认图片已归档并插入文档。
- 目标文档必须是已存在的 Markdown；不确定时询问用户，不猜测路径。
- AI 生成图片默认是概念图，状态使用 Draft。

## 第四步：端到端验收

- [ ] Worker /health 可访问。
- [ ] 未授权 POST 返回 HTTP 401。
- [ ] 用真实非敏感图片调用 Action，返回 HTTP 201 和 commit URL。
- [ ] 待归档目录出现图片和同名 JSON sidecar。
- [ ] Auto-archive technical images 工作流成功。
- [ ] 目标 Markdown 图片可正确渲染。
- [ ] 资产库索引出现记录。
- [ ] 图片与 Markdown 链接验证工作流成功。
- [ ] 实测自定义 GPT 能把刚生成图片的原始字节传给 Action；否则不能将无本地中转标记为端到端完成。

## 当前限制

OpenAPI 声明不能赋予模型读取图像二进制的能力。云端 Worker 消除了本地上传环节，但“生成图片 → 获取图片字节 → Action 请求”仍必须在 GPT Builder 中实测。只有测试通过，才可确认完整方案可用。
