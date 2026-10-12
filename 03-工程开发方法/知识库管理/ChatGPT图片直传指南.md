# 从 ChatGPT 图片到知识库：快速上传

本流程把“图片文件进入 GitHub”这一步缩短为一次本地命令；上传后由 GitHub Actions 自动归档、插入 Markdown、更新资产索引并执行检查。

## 1. 保存图片文件

在 ChatGPT 中生成图片后，将图片保存到本地，例如 `evcc-architecture.png`。上传脚本接收的是本地文件，不能直接读取对话中图片的临时显示对象。

## 2. 创建只对本仓库授权的 GitHub Token

在 GitHub 的 Settings → Developer settings → Personal access tokens 中创建 fine-grained token：
- Repository access：仅选择 `xp598008AI/knowledgebase`
- Repository permissions：Contents = Read and write
- 其他权限保持 No access

按组织策略设置有效期。不要把 token 粘贴进聊天、提交进仓库或写进脚本。

## 3. 配置环境变量

PowerShell 当前窗口中执行：

```powershell
$env:GH_TOKEN = "粘贴你自己的 token"
```

不要把真实 token 保存到脚本或 README。关闭终端后该环境变量会失效。

## 4. 一条命令上传图片并启动自动归档

先克隆仓库并进入目录；更新到最新 main：

```powershell
git clone https://github.com/xp598008AI/knowledgebase.git
cd knowledgebase
git pull
python scripts/push_technical_image.py "C:\\path\\to\\evcc-architecture.png" --title "EVCC 系统架构图" --document "04-充电系统与产品/EVCC/README.md" --source "ChatGPT generated concept illustration" --status Draft
```

如果已克隆仓库，跳过 `git clone`，在仓库目录中运行即可。也可以将路径换成实际图片路径与目标 Markdown 路径。

上传脚本会先确认目标文档存在，然后把图片和 JSON 元数据作为**同一个 Git commit** 推送到待归档队列，避免图片和元数据分两次推送引起工作流竞争。

## 5. 验证结果

打开 GitHub Actions：
- [自动归档工作流](https://github.com/xp598008AI/knowledgebase/actions/workflows/auto-archive-technical-images.yml)
- [图片与 Markdown 链接验证](https://github.com/xp598008AI/knowledgebase/actions/workflows/validate-knowledge-images.yml)

等待工作流完成后，打开目标 Markdown 检查图片渲染和技术内容。AI 生成图默认应使用 Draft 状态，经过人工核对后再标记为 Reviewed/Approved。

## 限制

- 该方法需要用户把 ChatGPT 图片保存到本地并运行一次命令；目前 ChatGPT 对话本身没有直接把临时生成图传给此私有仓库的授权上传动作。
- 上传 token 只应保存在本地环境变量中。若 token 泄露，应立即在 GitHub 撤销。
- 不要上传客户机密、个人敏感数据或无授权素材。
