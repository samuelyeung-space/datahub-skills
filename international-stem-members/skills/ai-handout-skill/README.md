# 小白书制作 Skill

这是面向国际课程及竞赛老师的公开、可分享的 AI 技能。支持 Skills 的 AI 可以导入整个文件夹；其他能访问网页的 AI 可以先读取 SKILL.md 并在当前会话应用。

- 正式入口：https://ai-handout-school.vercel.app
- 公开题库：https://github.com/samuel-resource-members/international-stem-members
- 单题检索：按课程→试卷→单题的真实链接取资料
- 测试：python scripts/read_bank.py --check （仅检索公开文字；不下载大型 ZIP）

此 Skill 的用途是制作能自学的学生册与同编号详解册，不等于自动取得全部原题 PDF、图片或官方评分。缺少原件时清楚说明并换用材料齐全的题目。不同平台是否支持持久安装、联网、解压和 PDF 导出取决于平台本身。

考试资料版权归相应权利人所有。技能文件不包含密钥或私人数据。

## 仅适用于有文件写入能力的 AI

可在审核后运行 [安全安装程序](https://github.com/samuelyeung-space/datahub-skills/blob/main/international-stem-members/install_skill.py)；Codex 使用 `.agents/skills`，Claude Code 使用 `.claude/skills`。默认项目级安装，不覆盖同名旧 Skill；网页聊天仍需平台自己的安装流程。

**重要：**通过网页读取、下载 ZIP、写入项目技能目录和完成账号级持久安装是四种不同状态，只有实际核验后才可说“装好了”。
