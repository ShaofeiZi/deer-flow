---
name: image-generation
描述: 当用户请求生成、创作、设想或可视化包括角色、场景、产品或任何视觉内容的图像时，请使用本技能。支持结构化提示和参考图像以实现引导生成。
---

# 图像生成技能

## 概览

本技能通过结构化提示和一个 Python 脚本生成高质量图像。工作流包括创建 JSON 格式的提示，以及在可选参考图像的辅助下执行生成。

## 核心能力

- 为 AIGC 图像生成创建结构化 JSON 提示
- 支持多个参考图像进行风格/构图引导
- 通过自动化 Python 脚本执行生成图像
- 处理各种图像生成场景（角色设计、场景、产品等）

## 工作流

### 第一步：理解需求

当用户请求生成图像时，确定：

- 主题/内容：图像应包含的主题
- 风格偏好：艺术风格、情绪、色彩方案
- 技术规格：纵横比、构图、照明
- 参考图像：用于引导生成的参考图像
- 您不需要检查 `/mnt/user-data` 下的文件夹

### 第二步：创建结构化提示

在 `/mnt/user-data/workspace/` 生成命名模式为：`{descriptive-name}.json` 的结构化 JSON 文件

### 第三步：执行生成

调用 Python 脚本：
```bash
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt/user-data/workspace/prompt-file.json \
  --reference-images /path/to/ref1.jpg /path/to/ref2.png \
  --output-file /mnt/user-data/outputs/generated-image.jpg
  --aspect-ratio 16:9
```

参数：

- `--prompt-file`：提示文件的完整路径（必填）
- `--reference-images`：参考图像的完整路径（可选，多个）
- `--output-file`：输出图像的完整路径（必填）
- `--aspect-ratio`：图像的纵横比（可选，默认 16:9）

[!注意]
不要读取 Python 文件，只需使用参数调用它。

## 角色生成功能示例

用户请求："Create a Tokyo street style woman character in 1990s"

创建提示文件：`/mnt/user-data/workspace/asian-woman.json`
```json
{
  "characters": [{
    "gender": "female",
    "age": "mid-20s",
    "ethnicity": "Japanese",
    "body_type": "slender, elegant",
    "facial_features": "delicate features, expressive eyes, subtle makeup with emphasis on lips, long dark hair partially wet from rain",
    "clothing": "stylish trench coat, designer handbag, high heels, contemporary Tokyo street fashion",
    "accessories": "minimal jewelry, statement earrings, leather handbag",
    "era": "1990s"
  }],
  "negative_prompt": "blurry face, deformed, low quality, overly sharp digital look, oversaturated colors, artificial lighting, studio setting, posed, selfie angle",
  "style": "Leica M11 street photography aesthetic, film-like rendering, natural color palette with slight warmth, bokeh background blur, analog photography feel",
  "composition": "medium shot, rule of thirds, subject slightly off-center, environmental context of Tokyo street visible, shallow depth of field isolating subject",
  "lighting": "neon lights from signs and storefronts, wet pavement reflections, soft ambient city glow, natural street lighting, rim lighting from background neons",
  "color_palette": "muted naturalistic tones, warm skin tones, cool blue and magenta neon accents, desaturated compared to digital photography, film grain texture"
}
```

执行生成：
```bash
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt/user-data/workspace/cyberpunk-hacker.json \
  --output-file /mnt/user-data/outputs/cyberpunk-hacker-01.jpg \
  --aspect-ratio 2:3
```

使用参考图像：
```json
{
  "characters": [{
    "gender": "based on [Image 1]",
    "age": "based on [Image 1]",
    "ethnicity": "human from [Image 1] adapted to Star Wars universe",
    "body_type": "based on [Image 1]",
    "facial_features": "matching [Image 1] with slight weathered look from space travel",
    "clothing": "Star Wars style outfit - worn leather jacket with utility vest, cargo pants with tactical pouches, scuffed boots, belt with holster",
    "accessories": "blaster pistol on hip, comlink device on wrist, goggles pushed up on forehead, satchel with supplies, personal vehicle based on [Image 2]",
    "era": "Star Wars universe, post-Empire era"
  }],
  "prompt": "Character inspired by [Image 1] standing next to a vehicle inspired by [Image 2] on a bustling alien planet street in Star Wars universe aesthetic. Character wearing worn leather jacket with utility vest, cargo pants with tactical pouches, scuffed boots, belt with blaster holster. The vehicle adapted to Star Wars aesthetic with weathered metal panels, repulsor engines, desert dust covering, parked on the street. Exotic alien marketplace street with multi-level architecture, weathered metal structures, hanging market stalls with colorful awnings, alien species walking by as background characters. Twin suns casting warm golden light, atmospheric dust particles in air, moisture vaporators visible in distance. Gritty lived-in Star Wars aesthetic, practical effects look, film grain texture, cinematic composition.",
  "negative_prompt": "clean futuristic look, sterile environment, overly CGI appearance, fantasy medieval elements, Earth architecture, modern city",
  "style": "Star Wars original trilogy aesthetic, lived-in universe, practical effects inspired, cinematic film look, slightly desaturated with warm tones",
  "composition": "medium wide shot, character in foreground with alien street extending into background, environmental storytelling, rule of thirds",
  "lighting": "warm golden hour lighting from twin suns, rim lighting on character, atmospheric haze, practical light sources from market stalls",
  "color_palette": "warm sandy tones, ochre and sienna, dusty blues, weathered metals, muted earth colors with pops of alien market colors",
  "technical": {
    "aspect_ratio": "9:16",
    "quality": "high",
    "detail_level": "highly detailed with film-like texture"
  }
}
```
```bash
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt/user-data/workspace/star-wars-scene.json \
  --reference-images /mnt/user-data/uploads/character-ref.jpg /mnt/user-data/uploads/vehicle-ref.jpg \
  --output-file /mnt/user-data/outputs/star-wars-scene-01.jpg \
  --aspect-ratio 16:9
```

## 常见场景

使用不同的 JSON 结构来适应不同场景。

**角色设计**：
- 物理属性（性别、年龄、种族、体型）
- 面部特征与表情
- 服装与配饰
- 历史时期或设定
- 姿势与情境

**场景生成**：
- 环境描述
- 时间与天气
- 情绪与氛围
- 关注点与构图

**产品可视化**：
- 产品细节与材质
- 照明设置
- 背景与情境
- 展示角度

## 具体模板

阅读以下模板文件仅在匹配用户请求时。

- [Doraemon Comic](templates/doraemon.md)

## 输出处理

完成生成后：

- 图像通常保存在 `/mnt/user-data/outputs/`
- 使用 present_files 工具与用户分享生成的图像
- 提供生成结果的简要描述
- 如需调整，愿意进行迭代

## 使用参考图像提升生成质量的提示

在视觉准确性关键的场景中，**先使用 `image_search` 工具寻找参考图像**，再进行生成。

**建议使用 image_search 的场景：**
- **角色/肖像生成**：查找类似姿势、表情或风格以指引面部特征与身材比例
- **具体对象或产品**：查找真实对象的参考图像以确保准确呈现
- **建筑或环境场景**：查找地点参考以捕捉真实细节
- **时尚与服装**：查找风格参考以确保服装细节与造型准确

**示例工作流：**
1. 调用 `image_search` 寻找合适的参考图像：
```
image_search(query="Japanese woman street photography 1990s", size="Large")
```
2. 下载返回的图像 URL 到本地文件
3. 使用下载的图像作为生成脚本中的 `--reference-images` 参数

这种方法通过为模型提供具体的视觉引导，而不仅仅依赖文本描述，显著提升生成质量。

## 备注

- 无论用户使用何种语言，提示请始终使用英文
- JSON 格式确保提示结构化、可解析
- 参考图像能显著提升生成质量
- 迭代式优化是获取最佳结果的常态
- 对于角色生成，请包含详细角色对象以及一个合并提示字段
