# 技术图片与图解资产库

本目录管理跨文档复用的架构图、流程图、状态机、时序图和技术图解。详细规则见 [技术图片资产规范](../../03-工程开发方法/知识库管理/技术图片资产规范.md)。

## 自动归档入口

将图片文件及同名 JSON 元数据一起提交到 `待归档/`，GitHub Actions 会自动：
1. 校验元数据和目标 Markdown 文档；
2. 将图片移动到目标文档旁的 `images/`；
3. 插入 Markdown 图片引用和图示说明；
4. 更新本资产库的自动归档记录；
5. 提交归档结果，并由图片/链接检查工作流验证。

元数据最小格式（例如图片 `evcc-architecture.svg` 对应 `evcc-architecture.json`）：

```json
{
  "title": "EVCC 系统架构概念图",
  "document": "04-充电系统与产品/EVCC/README.md",
  "source": "AI-generated concept illustration",
  "status": "Draft"
}
```

`document` 必须是仓库中已存在的 Markdown 文件；不覆盖同名目标图片。支持 PNG、JPG/JPEG、WEBP、GIF、SVG，单张图片最大 20 MiB。不得提交敏感信息或未授权材料。

## 资产管理原则
- 图片与目标文档一起归档；可复用素材通过相关文档链接引用。
- 记录图片标题、来源、审核状态与必要的技术说明。
- AI 生成图片默认是概念示意图，不得冒充标准原文或实测证据。
- 旧素材应保留来源与上下文，避免只搬运文件而丢失解释。

## 自动归档记录
- [技术图片自动归档流水线示意图](../../03-工程开发方法/知识库管理/AI协作与自动归档规范.md) · [图片文件](../../03-工程开发方法/知识库管理/images/technical-image-archive-workflow.svg) · 状态：Draft · 来源：Repository workflow validation example
