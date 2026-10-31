(function () {
  'use strict';
  const message = '请先读取 https://ai-handout-school.vercel.app/ai.txt ，按其中公开的 Skill 说明自行访问题库。请沿目录按需读取并核对真实题目，不能只凭文件名声称已经取得题图或评分。按我提供的课程、专题、学生基础、语言和册别制作小白书；学生册和详解册分开。若当前 AI 不支持联网或文档生成，请准确说明尚未完成的部分。';
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
