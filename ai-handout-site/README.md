# 小白书工作台

面向教师的公开静态入口：https://ai-handout-school.vercel.app/

AI 机器读取说明：https://ai-handout-school.vercel.app/ai.txt

分享版 Skill：https://raw.githubusercontent.com/samuelyeung-space/datahub-skills/main/international-stem-members/skills/ai-handout-skill/SKILL.md

公开真题库：https://github.com/samuel-resource-members/international-stem-members

网页源代码在本目录，包含 index.html、ai.txt、vercel.json、_headers。Vercel 项目从此目录部署；Cloudflare Pages 旧地址可能没有与本次源代码同步。

不在页面和仓库中加入凭据、学员私人资料或未授权的私库资源。网页本身不下载题库大文件。

## 将现有 Cloudflare Pages 网站同步为新版

当前 CF 项目属于 Wrangler 直接上传路径；不能仅靠 GitHub push 自动同步。给有终端及 Cloudflare 授权的 Claude Code 阅读 [部署说明](CLAUDE_CLOUDFLARE_DEPLOY.md)，审查后运行 `bash ai-handout-site/deploy-cloudflare.sh`（从仓库根目录执行）。脚本只上传公开网站所需的静态文件，不传完整仓库。无 Cloudflare 授权时不应声称同步成功。
