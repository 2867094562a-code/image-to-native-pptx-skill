# 图片转原生可编辑 PPTX Skill

简体中文 · [English](README.md)

把已经确认的 PPT 页面图片，按参考样式逐元素重建为 **Microsoft PowerPoint 原生可编辑对象**：文本框、形状、线条、自由曲线、表格，以及带可编辑数据的图表。原图只用于测量和验收，不会放进最终 PPT；经用户允许，摄影区域改成原生占位框。

这是**由智能体辅助分析和重建的工作流**，不是“一键识图后完美转换”的程序。需要识别参考内容、记录坐标、搭建对象并逐页对照，不宣称未经校准的“95% 相似”或像素完全一致。

## 安装

需要 Node.js 20+、Python 3.10+。真实 Office 验证另需本机 Microsoft PowerPoint。本仓库不包含 Office 和字体文件。

```sh
git clone https://github.com/2867094562a-code/image-to-native-pptx-skill.git
cd image-to-native-pptx-skill
npm ci --ignore-scripts
python3 -m pip install -r requirements.txt
```

在 Codex 中自动发现：把仓库改为克隆到 `~/.codex/skills/image-to-native-pptx`，然后重启应用或重新加载 Skill。不要覆盖已有的同名 Skill。其他支持 `SKILL.md` 的智能体也能读取入口。依赖命令在克隆目录中执行。

调用示例：

> 使用 $image-to-native-pptx，把这些已经确认的 PPT 图片做成原生可编辑 PPTX。保留文案、版式和页面顺序，照片改为原生占位框，不允许图片对象。交付 Office 验证后的文件、结构审计和逐页对照。

## 运行随附示例

```sh
node scripts/build_native.cjs examples/layout.json work/example.pptx
python3 scripts/audit_native_pptx.py work/example.pptx --output work/Native_Audit_Report.json
```

示例有两页，包含原生成果牌、时间线、进度条、图片占位框、手工设计的曲线、表格和图表。可用 `node scripts/make_example.cjs` 重新生成示例坐标 JSON。

实际复刻流程：

1. 用 `python3 scripts/inventory_images.py references --output work/inventory.json` 盘点可读原图，另外确认原始页面顺序。
2. 分析图片，按[坐标格式](references/layout-format.md)编写 `layout.json`。原图小字不清晰时记录待核对内容，不能默默编造。
3. 先制作复杂代表页并在 PowerPoint 渲染；已有用户认可的原生示例时，沿用示例的搭建方法和细节水平，再完成其余页面。
4. 执行原生结构审计，在真实 Office 中打开、编辑、保存、关闭并重开，导出 PNG 后逐页对照。差异通过修改原生对象修正。
5. 交付 PPTX、源码、页面坐标、审计报告、对照图和质量说明。

JSON 渲染器**没有图片插入接口**。后处理会规范化重复段落属性、重复对象 ID 和悬空图表坐标轴引用；这些处理不能替代真实 Office 验证。

## 组件库与模板复用

随附 `native_components.cjs` 提供原创的成果牌、进度条、时间线和照片占位组件，另有三组演示配色。原生对象生成使用 [PptxGenJS](https://github.com/gitbrent/PptxGenJS)，现有 PPT 组件复用使用 [pptx-automizer](https://github.com/singerla/pptx-automizer)，两者均由 `npm ci` 安装。

```sh
# 从已有原生组件库复用第 2、7、9 页。
node scripts/reuse_native.cjs library.pptx work/reused.pptx 2,7,9

# 按页码拆分，保留原生对象并清除未引用的页面资源。
python3 scripts/split_pptx.py complete.pptx work/template-B.pptx --slides 1-4,13-24
```

页码从 1 开始，输出遵循指定序列。拆分采用原生文件部件复制，不重画页面；每份结果仍需用 Office 打开检查。[组件库调研](references/libraries.md)记录了可安装项目、适用范围和实际测试状态。

## 真实 Office 验证

Windows 已安装 Microsoft PowerPoint 时：

```sh
python scripts/office_verify_windows.py work/example.pptx --output work/Office_Final.pptx --renders work/Office_Rendered --report work/Office_Verification.json
python scripts/audit_native_pptx.py work/Office_Final.pptx --output work/Native_Audit_Report.json
```

脚本执行文字编辑、另存、内容清单对比、关闭、重新打开及逐页 PNG 导出。**本项目尚未在 Windows 上实测该 COM 脚本。** macOS 使用真实 PowerPoint 的界面完成对应验证，详见[验证说明](references/office-validation.md)。LibreOffice 的草稿预览必须明确标识来源。

原图和 Office 预览均按 `slide-01.png` 等名称准备后：

```sh
python3 scripts/compare_pages.py work/Reference work/Office_Rendered work/Comparison
```

审计会对幻灯片媒体、图片/blip 对象、图片/OLE 关系和重复原生 ID 报错，并统计对象、核对已声明文案、提示基础越界及重叠候选。它不等于独立 OCR、完整 XML Schema 验证或视觉验收；复杂组合变换、旋转和字体溢出仍需看渲染图。

## 测试和边界

```sh
npm test
```

测试覆盖原生示例生成、表格与图表数据源、图片注入失败、拆分页序及组件库复用。不包含全自动识图、摄影的纯形状逼真重建、字体绝对匹配或相似度认证。商用字体应来自官方且确认授权；本仓库不分发字体、用户演示文稿和原始参考截图。

源码采用 MIT 许可证，依赖保留各自许可证。本项目与 Microsoft 无隶属关系。
