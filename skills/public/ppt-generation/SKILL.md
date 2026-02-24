---
name: ppt-generation
描述: 当用户请求生成、创建或制作演示文稿（PPT/PPTX）时使用此技能。通过为每张幻灯片生成图像并将其组合成 PowerPoint 文件来创建视觉效果丰富的幻灯片。
---

# PPT 生成技能

## 概览

本技能通过为每张幻灯片创建 AI 生成的图像并将其组合成 PPTX 文件来生成专业的 PowerPoint 演示文稿。工作流包括规划具有统一视觉风格的演示文稿结构、按顺序生成幻灯片图像（使用前一张幻灯片作为风格一致性的参考），并将它们组装成最终的演示文稿。

## 核心能力

- 规划和构建具有统一视觉风格的多幻灯片演示文稿
- 支持多种演示风格：商务、学术、简约、Apple Keynote、创意
- 使用 image-generation 技能为每张幻灯片生成独特的 AI 图像
- 通过使用前一张幻灯片作为参考图像来保持视觉一致性
- 将图像组合成专业的 PPTX 文件

## 演示风格

创建演示计划时选择以下风格之一：

| 风格 | 描述 | 适用场景 |
|-------|-------------|----------|
| **glassmorphism** | 毛玻璃面板配模糊效果，漂浮的半透明卡片，鲜艳的渐变背景，通过分层创造深度 | 科技产品、AI/SaaS 演示、未来感提案 |
| **dark-premium** | 深黑色背景（#0a0a0a），发光的强调色，微妙的发光效果，奢侈品牌美学 | 高端产品、高管演示、高端品牌 |
| **gradient-modern** | 大胆的网格渐变，流畅的色彩过渡，当代排版，鲜艳而精致 | 初创公司、创意机构、品牌发布 |
| **neo-brutalist** | 原始粗犷的排版，高对比度，故意的"丑陋"美学，反设计即设计，孟菲斯风格启发 | 前卫品牌、Z世代目标、颠覆性初创公司 |
| **3d-isometric** | 干净的等距插图，漂浮的 3D 元素，柔和阴影，科技前沿美学 | 科技说明、产品功能、SaaS 演示 |
| **editorial** | 杂志级布局，精致的排版层次，戏剧性的摄影，Vogue/Bloomberg 美学 | 年度报告、奢侈品牌、思想领导力 |
| **minimal-swiss** | 基于网格的精确性，Helvetica 启发的排版，大胆运用负空间，永恒现代主义 | 建筑、设计公司、高端咨询 |
| **keynote** | Apple 风格美学，大胆排版，戏剧性图像，高对比度，电影感 | 主题演讲、产品发布、励志演讲 |

## 工作流

### 第一步：理解需求

当用户请求生成演示文稿时，确定：

- 主题/题材：演示文稿是关于什么的
- 幻灯片数量：需要多少张幻灯片（默认：5-10）
- **风格**：business / academic / minimal / keynote / creative
- 纵横比：标准（16:9）或经典（4:3）
- 内容大纲：每张幻灯片的要点
- 您不需要检查 `/mnt/user-data` 下的文件夹

### 第二步：创建演示计划

在 `/mnt/user-data/workspace/` 中创建包含演示结构的 JSON 文件。**重要**：包含 `style` 字段来定义整体视觉一致性。

```json
{
  "title": "演示标题",
  "style": "keynote",
  "style_guidelines": {
    "color_palette": "深黑色背景，白色文字，单一强调色（蓝色或橙色）",
    "typography": "粗体无衬线标题，干净正文，戏剧性的大小对比",
    "imagery": "高质量摄影，全出血图像，电影构图",
    "layout": "充足的留白，居中焦点，每张幻灯片最少元素"
  },
  "aspect_ratio": "16:9",
  "slides": [
    {
      "slide_number": 1,
      "type": "title",
      "title": "主标题",
      "subtitle": "副标题或标语",
      "visual_description": "用于图像生成的详细描述"
    },
    {
      "slide_number": 2,
      "type": "content",
      "title": "幻灯片标题",
      "key_points": ["要点1", "要点2", "要点3"],
      "visual_description": "用于图像生成的详细描述"
    }
  ]
}
```

### 第三步：按顺序生成幻灯片图像

**重要**：**严格按顺序一张一张地**生成幻灯片。不要并行或批量生成图像。每张幻灯片都依赖于前一张幻灯片的输出作为参考图像。并行生成幻灯片会破坏视觉一致性，这是不允许的。

1. 阅读 image-generation 技能：`/mnt/skills/public/image-generation/SKILL.md`

2. **对于第一张幻灯片（幻灯片1）**，创建一个建立视觉风格的提示：

```json
{
  "prompt": "专业演示幻灯片。[计划中的 style_guidelines]。标题：'您的标题'。[visual_description]。这张幻灯片为整个演示建立视觉语言。",
  "style": "[基于选择的风格 - 例如，Apple Keynote 美学，戏剧性照明，电影感]",
  "composition": "干净的布局，清晰的文字层次，[风格特定的构图]",
  "color_palette": "[来自 style_guidelines]",
  "typography": "[来自 style_guidelines]"
}
```

```bash
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt/user-data/workspace/slide-01-prompt.json \
  --output-file /mnt/user-data/outputs/slide-01.jpg \
  --aspect-ratio 16:9
```

3. **对于后续幻灯片（幻灯片2+）**，使用前一张幻灯片作为参考图像：

```json
{
  "prompt": "专业演示幻灯片，延续参考图像的视觉风格。保持相同的色彩方案、排版风格和整体美学。标题：'幻灯片标题'。[visual_description]。保持与参考的视觉一致性。",
  "style": "完全匹配参考图像的风格",
  "composition": "与参考相似的布局原则，适应此内容",
  "color_palette": "与参考图像相同",
  "consistency_note": "这张幻灯片必须看起来与参考图像属于同一个演示文稿"
}
```

```bash
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt/user-data/workspace/slide-02-prompt.json \
  --reference-images /mnt/user-data/outputs/slide-01.jpg \
  --output-file /mnt/user-data/outputs/slide-02.jpg \
  --aspect-ratio 16:9
```

4. **继续处理所有剩余幻灯片**，始终参考前一张幻灯片：

```bash
# 幻灯片3参考幻灯片2
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt/user-data/workspace/slide-03-prompt.json \
  --reference-images /mnt/user-data/outputs/slide-02.jpg \
  --output-file /mnt/user-data/outputs/slide-03.jpg \
  --aspect-ratio 16:9

# 幻灯片4参考幻灯片3
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt/user-data/workspace/slide-04-prompt.json \
  --reference-images /mnt/user-data/outputs/slide-03.jpg \
  --output-file /mnt/user-data/outputs/slide-04.jpg \
  --aspect-ratio 16:9
```

### 第四步：组合 PPT

所有幻灯片图像生成完成后，调用组合脚本：

```bash
python /mnt/skills/public/ppt-generation/scripts/generate.py \
  --plan-file /mnt/user-data/workspace/presentation-plan.json \
  --slide-images /mnt/user-data/outputs/slide-01.jpg /mnt/user-data/outputs/slide-02.jpg /mnt/user-data/outputs/slide-03.jpg \
  --output-file /mnt/user-data/outputs/presentation.pptx
```

参数：

- `--plan-file`：演示计划 JSON 文件的绝对路径（必填）
- `--slide-images`：按顺序排列的幻灯片图像绝对路径（必填，空格分隔）
- `--output-file`：输出 PPTX 文件的绝对路径（必填）

[!注意]
不要读取 Python 文件，只需使用参数调用它。

## 完整示例：Glassmorphism 风格（最现代前卫）

用户请求："创建一个关于 AI 产品发布的演示文稿"

### 第一步：创建演示计划

创建 `/mnt/user-data/workspace/ai-product-plan.json`：
```json
{
  "title": "Introducing Nova AI",
  "style": "glassmorphism",
  "style_guidelines": {
    "color_palette": "鲜艳的紫到青渐变背景（#667eea→#00d4ff），毛玻璃面板配15-20%白色透明度，电光强调色",
    "typography": "SF Pro Display 风格，粗体700字重白色标题配微妙文字阴影，干净400字重正文，玻璃上对比度极佳",
    "imagery": "抽象3D玻璃球体，漂浮的半透明几何形状，柔和发光球体，通过分层透明度创造深度",
    "layout": "居中毛玻璃卡片配32px圆角，48-64px内边距，漂浮于渐变之上，柔和阴影创造分层深度",
    "effects": "玻璃面板上背景模糊20-40px，微妙白色边框发光，匹配渐变的柔和彩色阴影，光线折射效果",
    "visual_language": "Apple Vision Pro / visionOS 美学，通过透明度创造高端深度感，未来感但平易近人，2024设计趋势"
  },
  "aspect_ratio": "16:9",
  "slides": [
    {
      "slide_number": 1,
      "type": "title",
      "title": "Introducing Nova AI",
      "subtitle": "Intelligence, Reimagined",
      "visual_description": "令人惊艳的渐变背景从深紫色（#667eea）通过洋红流向青色（#00d4ff）。中央：大型毛玻璃面板配强背景模糊，包含粗体白色标题'Introducing Nova AI'和较轻的副标题。漂浮的3D玻璃球体和抽象形状围绕卡片创造深度。柔和光芒从玻璃面板后方散发。高端visionOS美学。玻璃卡片有微妙白色边框（1px rgba 255,255,255,0.3）和柔和紫色调阴影。"
    },
    {
      "slide_number": 2,
      "type": "content",
      "title": "Why Nova?",
      "key_points": ["10倍更快的处理速度", "类人理解能力", "企业级安全性"],
      "visual_description": "相同的紫青渐变背景。左侧：漂浮的毛玻璃卡片配粗体白色标题'Why Nova?'，下方三个要点配微妙玻璃胶囊徽章。右侧：抽象3D神经网络可视化，由相互连接的玻璃节点组成，配柔和发光。漂浮的半透明几何形状（二十面体、环面）增加深度。与前一张幻灯片一致的玻璃态美学。"
    },
    {
      "slide_number": 3,
      "type": "content",
      "title": "How It Works",
      "key_points": ["自然语言输入", "多模态处理", "即时洞察"],
      "visual_description": "与前几张幻灯片一致的渐变背景。中央构图：三张略微倾斜的堆叠毛玻璃卡片展示工作流程步骤，由柔和发光线条连接。每张卡片有一个抽象图标。漂浮的玻璃球体和光粒子围绕构图。顶部粗体白色标题'How It Works'。通过卡片分层和透明度创造深度。"
    },
    {
      "slide_number": 4,
      "type": "content",
      "title": "Built for Scale",
      "key_points": ["100万+并发用户", "99.99%正常运行时间", "全球基础设施"],
      "visual_description": "相同的渐变背景。不对称布局：右侧大型毛玻璃面板以粗体排版显示指标。左侧：由玻璃面板和连接线组成的抽象3D地球，代表全球规模。漂浮的数据可视化元素作为小型玻璃卡片显示数字。整体柔和环境发光。高端科技美学。"
    },
    {
      "slide_number": 5,
      "type": "conclusion",
      "title": "The Future Starts Now",
      "subtitle": "Join the waitlist",
      "visual_description": "戏剧性结尾幻灯片。渐变背景略微增加鲜艳度。中央毛玻璃卡片配粗体标题'The Future Starts Now'和行动号召副标题。卡片后方：柔和光线爆发和漂浮玻璃粒子创造庆祝效果。多层玻璃形状创造深度。最具视觉冲击力的幻灯片，同时保持风格一致性。"
    }
  ]
}
```

### 第二步：阅读 image-generation 技能

阅读 `/mnt/skills/public/image-generation/SKILL.md` 了解如何生成图像。

### 第三步：使用参考链按顺序生成幻灯片图像

**幻灯片1 - 标题（建立视觉语言）：**

创建 `/mnt/user-data/workspace/nova-slide-01.json`：
```json
{
  "prompt": "超高端演示标题幻灯片，玻璃态设计。背景：从深紫色（#667eea）通过洋红（#f093fb）到青色（#00d4ff）的平滑流动渐变，柔和而鲜艳。中央：大型毛玻璃面板配强背景模糊效果，32px圆角，包含粗体白色无衬线标题'Introducing Nova AI'（72pt，SF Pro Display风格，font-weight 700）配微妙文字阴影，下方较轻字重的副标题'Intelligence, Reimagined'。玻璃面板有微妙白色边框（1px rgba 255,255,255,0.25）和柔和紫色调投影。卡片周围漂浮：带折射效果的3D玻璃球体，半透明几何形状（二十面体、抽象团块），创造深度和维度。柔和发光从玻璃面板后方散发。小型漂浮光粒子。Apple Vision Pro / visionOS UI美学。专业演示幻灯片，16:9纵横比。超现代，高端科技产品发布感。",
  "style": "Glassmorphism, visionOS aesthetic, Apple Vision Pro UI style, premium tech, 2024 design trends",
  "composition": "居中玻璃卡片作为焦点，漂浮3D元素在边缘创造深度，40%负空间，清晰视觉层次",
  "lighting": "渐变发出的柔和环境光，通过玻璃元素的光线折射，3D形状上的微妙轮廓光",
  "color_palette": "Purple gradient #667eea, magenta #f093fb, cyan #00d4ff, frosted white rgba(255,255,255,0.15), pure white text #ffffff",
  "effects": "玻璃面板上的背景模糊，带色调的柔和投影，光线折射，玻璃上的微妙噪点纹理，漂浮粒子"
}
```

```bash
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt/user-data/workspace/nova-slide-01.json \
  --output-file /mnt/user-data/outputs/nova-slide-01.jpg \
  --aspect-ratio 16:9
```

**幻灯片2 - 内容（必须参考幻灯片1以保持一致性）：**

创建 `/mnt/user-data/workspace/nova-slide-02.json`：
```json
{
  "prompt": "演示幻灯片，延续参考图像的精确视觉风格。相同的紫到青渐变背景，相同的玻璃态美学，相同的排版风格。左侧：毛玻璃卡片配背景模糊，包含粗体白色标题'Why Nova?'（匹配参考字体风格），下方三个功能点作为微妙玻璃胶囊徽章。右侧：抽象3D神经网络可视化，由相互连接的玻璃节点组成，配柔和青色发光，漂浮在空间中。漂浮的半透明几何形状（匹配参考风格）增加深度。毛玻璃具有相同的处理：白色边框，紫色调阴影，相同的模糊强度。关键：这张幻灯片必须看起来与参考图像属于完全相同的演示文稿 - 相同的颜色，相同的玻璃处理，相同的整体美学。",
  "style": "MATCH REFERENCE EXACTLY - Glassmorphism, visionOS aesthetic, same visual language",
  "composition": "不对称分割：玻璃卡片左侧（40%），3D可视化右侧（40%），元素间呼吸空间",
  "color_palette": "EXACTLY match reference: purple #667eea, cyan #00d4ff gradient, same frosted white treatment, same text white",
  "consistency_note": "CRITICAL: Must be visually identical in style to reference image. Same gradient colors, same glass blur intensity, same shadow treatment, same typography weight and style. Viewer should immediately recognize this as the same presentation."
}
```

```bash
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt/user-data/workspace/nova-slide-02.json \
  --reference-images /mnt/user-data/outputs/nova-slide-01.jpg \
  --output-file /mnt/user-data/outputs/nova-slide-02.jpg \
  --aspect-ratio 16:9
```

**幻灯片3-5：继续相同模式，每张参考前一张幻灯片**

后续幻灯片的关键一致性规则：
- 始终在提示中包含"延续参考图像的精确视觉风格"
- 指定"相同的渐变背景"、"相同的玻璃处理"、"相同的排版"
- 包含 `consistency_note` 强调风格匹配
- 参考紧邻的前一张幻灯片图像

### 第四步：组合最终 PPT

```bash
python /mnt/skills/public/ppt-generation/scripts/generate.py \
  --plan-file /mnt/user-data/workspace/nova-plan.json \
  --slide-images /mnt/user-data/outputs/nova-slide-01.jpg /mnt/user-data/outputs/nova-slide-02.jpg /mnt/user-data/outputs/nova-slide-03.jpg /mnt/user-data/outputs/nova-slide-04.jpg /mnt/user-data/outputs/nova-slide-05.jpg \
  --output-file /mnt/user-data/outputs/nova-presentation.pptx
```

## 风格特定指南

### Glassmorphism 风格（推荐 - 最现代前卫）
```json
{
  "style": "glassmorphism",
  "style_guidelines": {
    "color_palette": "鲜艳渐变背景（紫色#667eea到粉色#f093fb，或青色#4facfe到蓝色#00f2fe），毛玻璃白色面板配20%透明度，在渐变上突出的强调色",
    "typography": "SF Pro Display 或 Inter 字体风格，粗体600-700字重标题，干净400字重正文，白色文字配微妙投影以便在玻璃上阅读",
    "imagery": "漂浮在空间中的抽象3D形状，柔和模糊的球体，玻璃材质的几何原语，通过重叠半透明层创造深度",
    "layout": "漂浮卡片面板配背景模糊效果，充足内边距（48-64px），圆角（24-32px半径），柔和阴影创造分层深度",
    "effects": "毛玻璃模糊（backdrop-filter: blur 20px），微妙白色边框（1px rgba 255,255,255,0.2），面板后方柔和发光，带投影的漂浮元素",
    "visual_language": "Apple Vision Pro UI 等高端科技美学，通过透明度创造深度，光线穿过玻璃表面折射"
  }
}
```

### Dark Premium 风格
```json
{
  "style": "dark-premium",
  "style_guidelines": {
    "color_palette": "深黑色基底（#0a0a0a 到 #121212），发光强调色（电光蓝#00d4ff，霓虹紫#bf5af2，或金色#ffd700），微妙灰色渐变创造深度（#1a1a1a 到 #0a0a0a）",
    "typography": "优雅无衬线（Neue Haas Grotesk 或 Suisse Int'l 风格），戏剧性大小对比（72pt+标题，18pt正文），标题字间距-0.02em，纯白（#ffffff）文字",
    "imagery": "戏剧性工作室照明，轮廓光和边缘发光，电影感产品拍摄，抽象光线轨迹，高端材质纹理（拉丝金属，哑光表面）",
    "layout": "充足负空间（60%+），不对称平衡，内容锚定于网格但留有呼吸空间，每张幻灯片单一焦点",
    "effects": "关键元素后方微妙环境发光，光晕效果，颗粒纹理叠加（2-3%透明度），边缘暗角",
    "visual_language": "奢侈科技品牌美学（Bang & Olufsen, Porsche Design），通过克制展现精致，每个元素都有意图"
  }
}
```

### Gradient Modern 风格
```json
{
  "style": "gradient-modern",
  "style_guidelines": {
    "color_palette": "大胆网格渐变（Stripe/Linear 风格：紫-粉-橙 #7c3aed→#ec4899→#f97316，或冷色调：青-蓝-紫 #06b6d4→#3b82f6→#8b5cf6），根据背景强度使用白色或深色文字",
    "typography": "现代几何无衬线（Satoshi, General Sans, 或 Clash Display 风格），可变字重，超大粗体标题（80pt+），舒适正文（20pt）",
    "imagery": "抽象流体形状，变形渐变，3D渲染抽象物体，柔和有机形态，漂浮几何原语",
    "layout": "动态不对称构图，带混合模式的重叠元素，文字与渐变流动融合，全出血背景",
    "effects": "平滑渐变过渡，微妙噪点纹理（3-5%增加深度），匹配渐变色调的柔和阴影，暗示运动的动态模糊",
    "visual_language": "当代 SaaS 美学（Stripe, Linear, Vercel），活力而专业，前瞻科技感"
  }
}
```

### Neo-Brutalist 风格
```json
{
  "style": "neo-brutalist",
  "style_guidelines": {
    "color_palette": "高对比度原色：纯黑，纯白，配大胆强调色（热粉#ff0080，电黄#ffff00，或原始红#ff0000），可选：孟菲斯风格粉彩作为次要色",
    "typography": "超粗压缩字体（Impact, Druk, 或 Bebas Neue 风格），大写标题，极端大小对比，故意紧凑或重叠的字间距",
    "imagery": "原始未过滤摄影，故意视觉噪点，半色调图案，剪贴拼贴美学，手绘元素，贴纸和印章",
    "layout": "破碎网格，重叠元素，粗黑边框（4-8px），可见结构，反留白（密集但有组织的混乱）",
    "effects": "硬阴影（无模糊，偏移8-12px），像素化点缀，扫描线，CRT屏幕效果，故意的'错误'",
    "visual_language": "反企业叛逆，DIY杂志美学遇上数字，原始真实感，通过大胆令人难忘"
  }
}
```

### 3D Isometric 风格
```json
{
  "style": "3d-isometric",
  "style_guidelines": {
    "color_palette": "柔和当代调色板：柔和紫色（#8b5cf6），青色（#14b8a6），温暖珊瑚色（#fb7185），配奶油色或浅灰背景（#fafafa），元素间饱和度一致",
    "typography": "友好几何无衬线（Circular, Gilroy, 或 Quicksand 风格），中等字重标题，极佳可读性，舒适24pt正文",
    "imagery": "干净等距3D插图，一致30°等距角度，柔和粘土渲染美学，漂浮平台和设备，可爱简化物体",
    "layout": "中央等距场景作为主角，文字平衡于3D元素周围，清晰视觉层次，舒适边距（64px+）",
    "effects": "柔和投影（20px模糊，30%透明度），3D物体上的环境光遮蔽，表面微妙渐变，一致光源（左上）",
    "visual_language": "友好科技插图（Slack, Notion, Asana 风格），平易近人的复杂性，通过简化实现清晰"
  }
}
```

### Editorial 风格
```json
{
  "style": "editorial",
  "style_guidelines": {
    "color_palette": "精致中性色：米白（#f5f5f0），炭灰（#2d2d2d），配单一强调色（酒红#7c2d12，森林绿#14532d，或海军蓝#1e3a5f），偶尔全彩摄影",
    "typography": "精致衬线标题（Playfair Display, Freight, 或 Editorial New 风格），干净无衬线正文（Söhne, Graphik），戏剧性大小层次（96pt标题，16pt正文），充足行高1.6",
    "imagery": "杂志级摄影，戏剧性裁剪，全出血图像，有意留白的肖像，编辑照明（Vogue, Bloomberg Businessweek 风格）",
    "layout": "精致网格系统（12列），有意不对称，引用作为设计元素，文字环绕图像，优雅边距",
    "effects": "最少效果 - 让摄影和排版闪耀，微妙图像处理（轻微去饱和，胶片颗粒），优雅边框和线条",
    "visual_language": "高端杂志美学，知性精致，通过设计克制提升内容"
  }
}
```

### Minimal Swiss 风格
```json
{
  "style": "minimal-swiss",
  "style_guidelines": {
    "color_palette": "纯白（#ffffff）或米白（#fafaf9）背景，纯黑（#000000）文字，单一大胆强调色（瑞士红#ff0000，克莱因蓝#002fa7，或信号黄#ffcc00）",
    "typography": "Helvetica Neue 或 Aktiv Grotesk，严格字体比例（12/16/24/48/96），正文中等字重，仅强调时使用粗体，左对齐右参差",
    "imagery": "客观摄影，几何形状，干净图标，数学精确，有意留白作为构图元素",
    "layout": "严格网格遵守（精神上可见基线网格），模块化构图，充足留白（40%+幻灯片），内容对齐于不可见网格线",
    "effects": "无 - 形式纯粹，无阴影，无渐变，无装饰元素，偶尔单根细线",
    "visual_language": "国际排版风格，形式追随功能，永恒现代主义，Dieter Rams启发的克制"
  }
}
```

### Keynote 风格（Apple风格）
```json
{
  "style": "keynote",
  "style_guidelines": {
    "color_palette": "深黑色（#000000 到 #1d1d1f），纯白文字，标志性蓝色（#0071e3）或渐变强调（创意用紫-粉，科技用蓝-青）",
    "typography": "San Francisco Pro Display，极端字重对比（粗体80pt+标题，轻体24pt正文），标题负字间距（-0.03em），光学对齐",
    "imagery": "电影感摄影，浅景深，戏剧性照明（轮廓光，聚光照明），产品英雄镜头配反射，全出血图像",
    "layout": "最大化负空间，每张幻灯片单一强力图像或声明，内容居中或戏剧性偏移，无杂乱",
    "effects": "微妙渐变叠加，关键元素上的光晕和发光，表面反射，平滑渐变背景",
    "visual_language": "Apple WWDC 主题演讲美学，通过简洁展现自信，每个像素都经过考量，戏剧性呈现"
  }
}
```

## 输出处理

生成完成后：

- PPTX 文件保存在 `/mnt/user-data/outputs/`
- 使用 `present_files` 工具与用户分享生成的演示文稿
- 如有请求，也分享单独的幻灯片图像
- 提供演示文稿的简要描述
- 如需要，提供迭代或重新生成特定幻灯片的选项

## 注意

### 关键质量指南

**专业结果的提示工程：**
- 无论用户使用何种语言，图像提示始终使用英文
- 对视觉细节极其具体 - 模糊的提示产生通用结果
- 包含精确的十六进制颜色代码（例如，#667eea 而不是"紫色"）
- 指定排版细节：字重（400/700），大小层次，字间距
- 精确描述效果："背景模糊20px"，"投影8px模糊30%透明度"
- 参考真实设计系统："visionOS 美学"，"Stripe 网站风格"，"Bloomberg Businessweek 布局"

**视觉一致性（最重要）：**
- **按顺序生成幻灯片** - 每张幻灯片必须参考前一张
- 第一张幻灯片至关重要 - 它为整个演示建立视觉语言
- 在每张后续幻灯片提示中，明确说明："延续参考图像的精确视觉风格"
- 在提示中强调使用 SAME、EXACT、MATCH 关键词来强制一致性
- 在幻灯片1之后的每个 JSON 提示中包含 `consistency_note` 字段
- 如果幻灯片看起来不一致，用更强的参考强调重新生成

**现代美学的设计原则：**
- 拥抱负空间 - 40-60%的空白创造高端感
- 限制每张幻灯片的元素 - 一个焦点，一个信息
- 通过分层创造深度（阴影，透明度，z深度）
- 排版层次：巨大标题（72pt+），舒适正文（18-24pt）
- 颜色克制：一个主要调色板，最多1-2个强调色

**常见错误避免：**
- ❌ 模糊提示如"专业幻灯片" - 要具体
- ❌ 每张幻灯片太多元素/文字 - 杂乱=不专业
- ❌ 幻灯片间颜色不一致 - 始终参考前一张幻灯片
- ❌ 跳过参考图像参数 - 这会破坏视觉一致性
- ❌ 在一个演示中使用不同设计风格
- ❌ 并行生成幻灯片 - 幻灯片必须按顺序一张一张生成（幻灯片1 → 2 → 3...），绝不能同时生成

**不同场景的推荐风格：**
- 科技产品发布 → `glassmorphism` 或 `gradient-modern`
- 奢侈/高端品牌 → `dark-premium` 或 `editorial`
- 初创公司路演 → `gradient-modern` 或 `minimal-swiss`
- 高管演示 → `dark-premium` 或 `keynote`
- 创意机构 → `neo-brutalist` 或 `gradient-modern`
- 数据/分析 → `minimal-swiss` 或 `3d-isometric`
