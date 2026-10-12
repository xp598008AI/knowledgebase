# 自定义 GPT：GitHub 直连技术图片自动归档配置

## 目标流程

自定义 GPT 生成技术图片 → GPT Action 先把元数据 JSON 写入 GitHub 私有仓库 → 再把真实图片字节写入同目录待归档队列 → 现有 GitHub Actions 自动将图片归档到目标 Markdown 同级的 `images/` 目录、插入引用、更新资产库索引并检查链接。

**不需要 Cloudflare、单独服务器或本地中转。** 但仍需在 GPT Builder 配置 GitHub Token。完整自动化是否可用，取决于 GPT 是否能访问并传递刚生成图片的真实二进制数据，必须通过实测确认。

## 一、创建 GitHub Token

1. 打开 GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens。
2. 创建仅授权 `xp598008AI/knowledgebase` 的 Token。
3. Repository permissions 只授予 `Contents: Read and write`。
4. 在 GPT Builder 的 Action Authentication 中选择 **API Key**，Auth Type 选择 **Bearer**，粘贴 Token。
5. 不要把 Token 写进仓库、Instructions 或对话；不要使用有不必要全仓库权限的 Token。

## 二、配置 GPT Action

1. 打开 GPT Builder → Configure → Actions → Create new action。
2. 将本目录中的 `GitHub直连图片归档Action.openapi.yaml` 完整内容粘贴到 Schema。
3. Authentication 选择 API Key / Bearer，填入上一步创建的 Token。
4. 保存并检查两个操作是否出现：
   - `stageTechnicalImageMetadata`
   - `uploadTechnicalImageToQueue`

该 Action 直接调用 GitHub REST API，不需要额外部署服务。

## 三、合并到 GPT Instructions 的规则

将以下规则合并进已有 Instructions，不要覆盖原有技术回答规范：

- 每次生成新的技术图片后，除非用户明确要求不要归档，否则尝试自动归档；非技术图片不自动归档。
- 归档前确定图片标题、现有目标 Markdown 路径、来源和状态。AI 生成图默认状态为 Draft。目标文档必须已存在；不确定时先询问用户，不猜路径。
- 生成一个 ASCII 文件名 stem（仅字母、数字、连字符、下划线），并选择 PNG/JPG/JPEG/WEBP/GIF/SVG 扩展名。
- 先调用 `stageTechnicalImageMetadata`，写入 sidecar JSON。JSON 至少包含 `title`、`document`、`source`、`status`、`filename`。将 UTF-8 JSON 文本正确编码成标准 Base64，作为 API 的 `content`。
- 只有元数据调用成功后，才调用 `uploadTechnicalImageToQueue` 上传图片。图片 `content` 必须是当前生成图片真实文件字节的标准 Base64，不含 data URI 前缀。
- 严禁编造、截断、伪造 Base64；不要用图片 URL、Markdown、预览描述或占位符冒充图片字节。如果无法取得原始字节，明确说明本次没有上传。
- 两次 GitHub API 调用都成功，只表示文件进入队列；必须等待 GitHub Actions 完成，才能报告“已归档”。如果第一步成功、第二步失败，队列会留下孤立 sidecar，应重试同名图片上传，不要重复创建 sidecar。
- 如果 API 返回 422 或提示文件已存在，不要覆盖旧文件；换一个新的唯一 stem 并重新执行。
- 只把非敏感且有权归档的图片上传到私有仓库。

## 四、验收清单

- [ ] Action Schema 保存成功，两个操作都可见。
- [ ] Token 权限限定到目标私有仓库的 Contents 读写。
- [ ] 选择一个已存在的 Markdown 文档作为目标。
- [ ] 先创建同名 JSON sidecar，再上传真实的测试图片。
- [ ] 图片与 JSON 出现在 `06-创新、扩展与职业竞争/技术图片资产库/待归档/`。
- [ ] `Auto-archive technical images` 工作流成功。
- [ ] 图片进入目标文档同级 `images/`，Markdown 引用可渲染。
- [ ] 技术图片资产库 README 更新，链接检查通过。
- [ ] 实测 GPT 可以传递刚生成图片的原始字节；若不行，不得声称全自动端到端已完成。

## 当前状态

GitHub 直连 Action 的 OpenAPI 契约已提交。尚未配置你的 GPT Action/Token，也尚未完成真实图片二进制传输和端到端测试。不要把“契约已写入仓库”当作“自动上传已验证”。
