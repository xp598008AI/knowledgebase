# 技术图片与图解资产库

本目录管理跨文档复用的架构图、流程图、状态机、时序图和技术图解。详细规则见 [技术图片资产规范](../../知识库管理/技术图片资产规范.md)。

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
- [技术图片自动归档流水线示意图](../../知识库管理/AI协作与自动归档规范.md) · [图片文件](../../知识库管理/images/technical-image-archive-workflow.svg) · 状态：Draft · 来源：Repository workflow validation example
- [ISO 15118-20 DC V2H 系统与通信协同示意图](../../04-充电系统与产品/充电系统/协议与时序/ISO15118.md) · [图片文件](../../04-充电系统与产品/充电系统/协议与时序/images/iso15118-dc-v2h-workflow.svg) · 状态：Draft · 来源：AI-generated conceptual engineering diagram; verify against the applicable ISO 15118-20 edition and system design

## SVG直写归档记录

- [ASPICE工程实践指南](../../03-工程开发方法/ASPICE/ASPICE工程实践指南.md) · [工程总览图](../../03-工程开发方法/ASPICE/images/aspice-engineering-overview-v41.svg) · [工作产品流转图](../../03-工程开发方法/ASPICE/images/aspice-work-product-loop-v1.svg) · v1 / 2026-10-13 / Draft · 来源：AI辅助原创工程概念图；直写归档，非队列自动归档。

- [ASPICE全32过程输入输出、流转与评审图v2](../../03-工程开发方法/ASPICE/ASPICE工程实践指南.md) · [总图](../../03-工程开发方法/ASPICE/images/aspice-all-process-io-review-v2.svg) · 另含6张分区图（见正文） · 2026-10-13 / Draft · 来源：AI辅助原创SVG工程图；32个建议评审点；本地渲染已检查；直写归档。
