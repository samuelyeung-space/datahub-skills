(function () {
  'use strict';
  const message = '请打开 https://ai-handout-school.vercel.app/ai.txt ，先读取完整小白书 Skill，并尽可能根据当前 AI 的实际能力安装它：如有 Codex 或 Claude Code 的项目文件操作权限，可审查公开安装程序并按平台许可安装；如是网页聊天的原生 Skills，请走该平台的创建或上传/安装流程，需要我的操作时只提示必要的一步；如果无法持久安装，就在本次对话加载并遵循 Skill。请明确报告：已安装且实际验证、仅本次对话使用，还是因权限/功能受限未安装，绝不能将读过 Skill 当作已安装。然后按我的课程、专题和学生基础，沿公开题库索引真实取题、核对必要图形与答案，制作学生册和详解册。';
  const button = document.getElementById('copy');
  const feedback = document.getElementById('feedback');
  const fallback = document.getElementById('fallback');
  if (!button || !feedback || !fallback) return;
  function manual() {
    fallback.value = message;
    fallback.style.display = 'block';
    fallback.focus();
    fallback.select();
    feedback.textContent = '已选中指令，可手动复制并粘贴给 AI。';
  }
  button.addEventListener('click', function () {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(message).then(function () {
        feedback.textContent = '已复制，直接粘贴给你的 AI。';
        fallback.style.display = 'none';
      }, manual);
    } else {
      manual();
    }
  });
})();
