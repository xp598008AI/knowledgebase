# 从 ChatGPT 技术图到知识库：优先 SVG 直写

## 推荐路径：SVG 源码直接入库，无需本地中转

对于流程图、架构图、时序图、状态机和技术知识卡片，优先使用 SVG 矢量图源码：
1. 根据技术内容生成 SVG 源码（纯文本）。
2. 通过 GitHub 文件接口把源码直接创建为仓库中的 `.svg` 文件。
3. 更新目标 Markdown，插入相对路径，例如 `![系统架构图](images/system-architecture.svg)`。
4. 读回 SVG 和 Markdown，确认文件与引用都存在。

示例：[ASPICE V 模型 SVG](../ASPICE/images/aspice-v-model.svg)，已嵌入 [ASPICE 文档](../ASPICE/README.md)。

这条路径不需要 Cloudflare、服务器、下载 PNG 或传输图片二进制。SVG 是可由 GitHub 文件接口直接保存的文本，适合结构化技术图。需要注意：保存成功和 Markdown 引用正确已可通过文件接口核验；实际页面渲染仍应打开 GitHub 文档检查。

## PNG/JPG 位图上传（仅在确实需要位图时）

PNG/JPG/WebP/GIF 是二进制文件。若 ChatGPT 生成图没有可读取的真实文件字节，不能仅凭对话中的预览自动上传；不要把图片 URL、描述或伪造 Base64 当成图片本身。

需要上传本地位图时，可使用已有脚本 `scripts/push_technical_image.py`：

1. 在 GitHub 为 `xp598008AI/knowledgebase` 创建 Fine-grained Token，仅授予 `Contents: Read and write`。
2. 在 PowerShell 当前窗口设置环境变量：

```powershell
$env:GH_TOKEN = "粘贴你自己的 token"
```

3. 在仓库目录执行示例命令：

```powershell
python scripts/push_technical_image.py "C:\\path\\to\\evcc-architecture.png" --title "EVCC 系统架构图" --document "04-充电系统与产品/EVCC/README.md" --source "ChatGPT generated concept illustration" --status Draft
```

脚本会检查目标 Markdown，并把图片与 JSON 元数据写入待归档队列。之后由 GitHub Actions 自动归档、插入 Markdown、更新资产索引并检查引用。只有工作流成功结束后，才能报告“已自动归档”。

## 统一规范

- SVG 优先用于结构化技术图；PNG/JPG 用于必须保留的位图素材。
- 图片放在目标 Markdown 同级的 `images/` 目录；跨文档共用素材放入技术图片资产库。
- 通过相对路径引用，不使用临时 URL。
- AI 生成图默认状态为 Draft，经过人工核对后再更新审核状态。
- 每次操作后读回文件和 Markdown 验证；不要仅凭提交成功推断渲染或 Actions 已通过。
- 不要将 Token 写入代码、Markdown 或聊天。
