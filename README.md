# Zhao lab 静态网站

根据用户提供的 5 份 Squarespace MHTML 快照重建。保留原站英文内容、标志、照片、论文次序、团队信息和主要布局；无框架、无数据库、无运行时第三方依赖。

## 本地运行

需要 Python 3.10 或更新版本，无需安装 Python 第三方库或 npm 包。

```powershell
cd F:\codex-zhaolab\zhao-lab
python scripts/build.py
python scripts/check.py
python -m http.server 8000 --bind 127.0.0.1 --directory dist
```

打开 http://127.0.0.1:8000 。按 Ctrl+C 停止服务。如果 8000 已占用，将端口改为 8001。已生成的 `dist/index.html` 也可以直接双击打开；网站正文不依赖 JavaScript。

## 页面和目录

| 页面 | 输出 |
| --- | --- |
| 首页 | `dist/index.html` |
| 研究方向 | `dist/research.html` |
| 论文发表 | `dist/publications.html` |
| 团队、联系方式、招聘邮箱 | `dist/team.html` |
| 课题组活动 | `dist/group-activities.html` |

`data/` 是内容源；`scripts/build.py` 是模板与生成器；`dist/site.css`、`dist/site.js` 是直接维护的样式与菜单脚本；`dist/assets/` 保存 34 个图像文件，其中 33 个已替换为用户提供的原格式文件（不重新压缩），1 个为未补充原文件的论文配图。`dist/` 必须提交到 Git，不能删除后只运行 build：它同时存放手工维护的样式和素材。旧路径 `new-page`、`new-page-1`、`new-page-2` 等有静态跳转。

## 更新内容

1. 修改相应 JSON 文件（UTF-8，字符串双引号，最后一项后不加逗号）。
2. 运行 `python scripts/build.py` 和 `python scripts/check.py`。
3. 刷新本地浏览器，检查改动，再提交源码及 `dist/`。

| 文件 | 修改内容 |
| --- | --- |
| `data/members.json` | 成员姓名、身份、学历、邮箱、照片；第一项为课题组负责人，使用 `biography_html` 保存履历 |
| `data/publications.json` | 论文编号、`period` 分组、`content_html` 完整文献、可选 `figure` |
| `data/pages.json` | 页面标题、简介、首页/活动图片 |
| `data/contact.json` | 机构、地址、邮箱、招聘邮箱、电话号码 |
| `data/assets.json` | 导出图片与来源 URL 的对应清单（溯源用，修改显示请改以上对应记录） |
| `data/news.json` | 空数组；原站无新闻条目，当前不生成新闻栏目 |

添加成员：复制一个普通成员对象，编辑 `name`、`role`、`education`、`email`，将新照片放进 `dist/assets/`，在 `image` 中填写相对路径及真实宽高。列表次序就是页面次序。不要凭空填入未知经历。

论文 `content_html` 保留了原有斜体、上下标、作者符号、链接及报道说明。例如 `<p><strong>19. Title.</strong><br>Authors.<br><a href="https://doi.org/...">Journal, year, volume, pages.</a></p>`。JSON 中引号须写成 `\"`。只填写可信的静态内容，不粘贴脚本或编辑后台代码。添加论文可复制一项，设置编号及 `at UCAS` / `before UCAS`；没有配图时省略 `figure`。

照片、论文和活动不通过外部 CDN 获取。横幅图片会按屏幕比例裁切，成员照片和论文图使用 contain 保持完整。未来新增新闻需要同时在生成器中增加模板/导航，空数据文件不会自动创建页面。

## 上传 GitHub

在 GitHub 创建空仓库，例如 `zhao-lab`，然后在本项目目录执行（替换 `<用户名>`）：

```powershell
git init
git add .
git commit -m "Rebuild Zhao lab as a static website"
git branch -M main
git remote add origin https://github.com/<用户名>/zhao-lab.git
git push -u origin main
```

若目录已经是 Git 仓库，无需再次初始化或添加已有的 origin。不要上传上级 `mhtml/`：原始快照含编辑后台及会话相关元数据，且网站运行不需要它们。本项目没有代替用户创建远端仓库或执行推送。

## GitHub Pages

仓库内已提供 `.github/workflows/pages.yml`。在 GitHub 仓库 **Settings → Pages → Source** 选择 **GitHub Actions**，推送 main 分支后，流程将构建、检查并发布 `dist/`。项目页面使用相对链接，支持 `https://<用户名>.github.io/zhao-lab/` 子路径，无需修改资源前缀。部署地址以 workflow 返回的 URL 为准。

不启用 Pages 时，仓库仍可正常保存项目。也可把 `dist/` 的全部内容上传到任何静态托管服务。自定义域名与 DNS 需在选定托管服务中另行设置。

## Cloudflare Pages

连接 GitHub 仓库 `lfssgg/zhaolab` 后，使用以下构建设置：

| 设置 | 值 |
| --- | --- |
| 生产分支 | `main` |
| 框架预设 | `None` |
| 根目录 | 留空（仓库根目录），不要填 `zhao-lab` 或 `dist` |
| 构建命令 | `npm run build` |
| 构建输出目录 | `dist` |

项目提供无 npm 依赖的 `package.json`。`npm run build` 调用 Python 生成页面并校验本地链接；Cloudflare Linux 环境使用 `python3`。也可以直接设置构建命令为 `python3 scripts/build.py && python3 scripts/check.py`。不要在 `dist` 内执行 npm 命令，该目录不是源码根目录。

遇到 `npm error enoent` 时，先确认部署的是含 `package.json` 的最新提交，且根目录为仓库根目录，再重新部署。若仅发布仓库内已构建的页面，可以使用构建命令 `exit 0` 和输出目录 `dist`，但该方式不会根据 JSON 自动重新生成页面。

以上设置适用于 **Pages**，无需部署命令、Wrangler 配置或服务端入口。

参考：[Pages 构建配置](https://developers.cloudflare.com/pages/configuration/build-configuration/)、[静态 HTML](https://developers.cloudflare.com/pages/framework-guides/deploy-anything/)。

## 恢复范围及限制

详见 [迁移清单](docs/MIGRATION.md) 和 [检查记录](docs/VALIDATION.md)。当前使用系统衬线字体代替未嵌入快照的 Tai Heritage Pro / Sutro；保留视觉方向，但不宣称逐像素一致。全部成员和论文信息按所提供快照恢复，不自动校正年份、身份、排序或原始文字。
