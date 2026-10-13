# 知识库管理

集中维护知识库的规则、索引、归档工具与通用模板。

- [知识库索引](INDEX.md)
- [AI 协作与自动归档规范](AI协作与自动归档规范.md)
- [知识分类与目录规划](知识分类与目录规划.md)
- [脚本](scripts/)：图片上传、导入、自动归档、图片引用与 Markdown 链接检查。
- [模板](templates/)：知识文档、技术卡片、测试报告与失效分析模板。
- [删除与恢复规则](../回收站/README.md)

从仓库根目录运行脚本，例如：

```bash
python 知识库管理/scripts/check_image_refs.py
python 知识库管理/scripts/auto_archive_technical_images.py
```

GitHub Actions 工作流保留在 `.github/workflows/`，调用本目录中的脚本。仓库根目录 `AGENTS.md` 保留为 AI 操作规则入口。资料删除默认移入回收站；本次目录迁移保留全部文件内容，不属于删除。
