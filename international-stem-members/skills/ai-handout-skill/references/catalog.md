# 公开题库的读取方式

# Question Bank Links

## Question bank

- Repository: <https://github.com/samuel-resource-members/international-stem-members>
- How to read it — start here: <https://raw.githubusercontent.com/samuel-resource-members/international-stem-members/main/catalog/README.md>
- Course index (JSON): <https://raw.githubusercontent.com/samuel-resource-members/international-stem-members/main/catalog/index.json>
- Course → papers: `https://raw.githubusercontent.com/samuel-resource-members/international-stem-members/main/catalog/courses/<course_id>.json`
- Paper → questions: `https://raw.githubusercontent.com/samuel-resource-members/international-stem-members/main/catalog/papers/<paper>.json`
- One question (Markdown): `https://raw.githubusercontent.com/samuel-resource-members/international-stem-members/main/questions/<course_id>/<question_id>.md`
- Original PDFs, assets, and marking material: release ZIPs listed inside every question file (`https://github.com/samuel-resource-members/international-stem-members/releases`)

## AI retrieval behaviour

1. Open the course index and pick the course. Open the course file and pick papers by year, paper, or chapter. Open paper files or single question files.
2. Read `search_text` (OCR). When formulas, subscripts, or diagrams matter, download the listed shard or package ZIP and extract the question PDF or assets.
3. Read only what the current book needs. Do not download the whole library unless the runtime genuinely requires a local clone.
4. If a course, year, or paper is not in the index, state exactly what is missing and continue with the verified material that exists.
5. Open the links directly. Never ask the teacher to register, join, or authorise anything.

## Working rules

The platform-independent rules needed to start are in [`SKILL_BOOTSTRAP.md`](./SKILL_BOOTSTRAP.md).


## 核验要点

- 每次从真实 index.json 的 courses[].file 开始，不根据标签猜路径。
- 单题 Markdown 的 OCR 可能遗漏图、公式、选项和公共题干。必要时取得原 PDF 核对。
- files[] 指向 Release ZIP 不等于 ZIP 已下载，也不等于单题资料已提取。member 为 null 时需要确认文件归属。
- answer_candidates 只是候选，须实际查看、匹配年份卷别题号，才能作为评分依据。
- question_count 是索引记录数量，不代表全部题均有高清图、可编辑公式、分类和官方答案。

## 真实最小验收

公开示例：
https://raw.githubusercontent.com/samuel-resource-members/international-stem-members/main/questions/AMC10/live-poshenloh-amc10-2023a-question_paper__q01.md

此例可以检查文字和题型，不以此代表题图或官方答案也已下载。客户端不支持大 ZIP 时优先选材料完整的题，不要求老师搬运整个题库。
