# 给 Claude Code 的 Cloudflare Pages 同步说明

## 目标

把本仓库 `ai-handout-site/` 目录中经过审核的静态网站更新到**现有** Cloudflare Pages 项目 `ai-handout-school`，让网址 `https://ai-handout-school.pages.dev/` 与新版网站代码一致。原有私有题库及母库不参与发布。

**此说明适用于拥有终端与 Cloudflare 部署权限的 Claude Code 或其他编程代理。** 普通 Claude 网页聊天仅凭网址不能自动登录 Cloudflare、更改项目或部署。完整的小白书 Skill 是制书工作流技能，不会附带 Cloudflare 凭据或自动获得网站部署权。

## 当前结构

- 公开网站代码：`https://github.com/samuelyeung-space/datahub-skills/tree/main/ai-handout-site`
- 新版 Vercel 站：`https://ai-handout-school.vercel.app`
- 需要更新的 Cloudflare Pages Direct Upload 项目：`ai-handout-school`
- 目标网址：`https://ai-handout-school.pages.dev/`

之前的 CF 网站使用 `wrangler pages deploy` 直接上传。Cloudflare 官方说明：现有 Direct Upload 项目不能原地改为 Git integration。若需要保留相同 pages.dev 网址，应继续通过 Wrangler 部署；也可以配置 GitHub Actions + Wrangler 在每次 Git 推送时自动部署，首次需要在 CI 中安全设置 Cloudflare 凭据。

## 执行

1. 使用用户明确授权的 GitHub 访问获取这个**公开**仓库，进入其工作目录。
2. 只检查并部署 `ai-handout-site/index.html`、`app.js`、`ai.txt`、`_headers`（以及存在时的 `404.html`）。不要把 `README.md`、`vercel.json`、`.env`、`git`、整个题库或私有文件上传到站点。
3. 先检查 `ai-handout-site/deploy-cloudflare.sh` 的内容和实际 Cloudflare 项目名称。
4. 使用现有 Wrangler 授权的 Cloudflare 账号。若未授权，提示用户在本机浏览器完成 `npx wrangler login` 的正常登录；不要请求用户把 API Token、账户密码或验证码贴进聊天。
5. 登录成功且项目可访问后，从仓库根目录执行：

   ```bash
   bash ai-handout-site/deploy-cloudflare.sh
   ```

6. 部署完成后**实际访问** `https://ai-handout-school.pages.dev/` 与 `https://ai-handout-school.pages.dev/ai.txt`，验证新版文案出现；`app.js` 可加载；Skill 下载地址为公开 ZIP；`ai.txt` 指向真实 Skill 和题库。
7. 汇报 CF 生产部署 URL、实际版本/状态、所读资源及无法验证的项目。不要只凭 GitHub 提交或 CLI 返回就声称线上已同步。

## 长期自动同步（可选）

如需以后 Claude Code **只提交代码**就让现有 CF 域名自动更新，可给此 Direct Upload 项目建立 GitHub Actions + Wrangler CI。必须在 GitHub Secrets 设置 `CLOUDFLARE_API_TOKEN`、`CLOUDFLARE_ACCOUNT_ID`（最小权限），由仓库管理员通过 GitHub 界面操作；CI 只允许发布 `ai-handout-site` 的上述白名单文件。不要把 Token 写入源码、日志、聊天或网站。配置完成后先做一次真实部署测试再称为“自动同步”。

官方说明：
- https://developers.cloudflare.com/pages/get-started/direct-upload/
- https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/
- https://developers.cloudflare.com/workers/wrangler/commands/pages/
