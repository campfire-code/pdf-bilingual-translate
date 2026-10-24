# PDF 双语翻译（保版式，PDFMathTranslate）

> 篝火出品 · 收录于篝火 App 应用区 · 基于开源项目 [PDFMathTranslate/PDFMathTranslate](https://github.com/PDFMathTranslate/PDFMathTranslate)（**AGPL-3.0**）

把论文、说明书等 PDF 翻译成另一种语言，**公式、图表和排版保持原样**，同时生成纯译文版和中英对照版。

## 下载

到 [Releases](https://github.com/campfire-code/pdf-bilingual-translate/releases/latest) 下载：

| 电脑 | 文件 |
|---|---|
| Windows 10 / 11（64 位） | `pdf-bilingual-translate_版本号_pdf2zh-v1.9.11-with-assets-win64.zip`，约 520 MB |

- 这是上游官方的「带资源版」（已内置字体、版面识别模型等），解压即用，不必再联网下载模型。上游另有一个不带资源的小包，运行时要在线下载模型、网络不好容易失败，所以这里只转发布带资源版。
- 安装包来自上游官方发布，篝火没有修改，附 `SHA256SUMS.txt` 可核对。
- 上游只提供 Windows 免安装包，**没有 macOS / Linux 安装包**，见下面「Mac / Linux」。

## 怎么用（Windows）

1. 解压 zip，双击里面的 `pdf2zh.exe` 运行（上游说明）。
2. 如果下载后打不开，先安装 [vc_redist.x64.exe](https://aka.ms/vs/17/release/vc_redist.x64.exe) 再试（上游说明）。
3. 选好 PDF、翻译服务和目标语言后开始翻译，译文会生成在输出位置，包括译文版（`-mono.pdf`）和双语对照版（`-dual.pdf`）。

**说明**
- 软件界面和上游文档是英文。
- 默认的翻译服务是 Google。

## Mac / Linux

上游文档给出的安装方式（需要 Python 3.11 ~ 3.12）：

```bash
# 方式一：uv
pip install uv
uv tool install --python 3.12 pdf2zh

# 方式二：pip
pip install pdf2zh
```

- 命令行翻译：`pdf2zh document.pdf`，在当前目录生成译文版和双语对照版。
- 图形界面：`pdf2zh -i`，浏览器打开 `http://localhost:7860/`（没自动打开就手动访问），把 PDF 拖进去点 `Translate`。
- 上游还提供 Docker：`docker run -d -p 7860:7860 byaidu/pdf2zh`，浏览器访问 `http://localhost:7860/`。
- 在国内网络下载版面识别模型失败时，参考上游 README 的 “Solutions for network issues in installation” 一节。

## 翻译服务（需要你自己选、自己配）

以下均来自上游文档 `docs/ADVANCED.md` 的服务表，PDF 里的文字会发送给你选的服务，请自行评估保密要求。

- **表里无需密钥的**：Google（默认）、Bing。上游没有写明它们的额度或长期可用性，我们没有核实，正式使用前先试一份文件。
- **在线服务，需要自己的密钥**：OpenAI、302.AI、DeepL、Azure OpenAI、Azure（翻译）、智谱 Zhipu、魔搭 ModelScope、硅基流动 SiliconCloud、Gemini、腾讯云机器翻译、Grok、Groq、DeepSeek、MiniMax、阿里通义 Qwen-MT，以及任何兼容 OpenAI 接口的服务（用 `openailiked`，自己填地址、密钥、模型名）。密钥通过环境变量传入，例如 `OPENAI_API_KEY`。
- **需要自己的服务地址**：Ollama（本机，默认 `http://127.0.0.1:11434`）、Xinference、DeepLX、Dify、AnythingLLM；Argos Translate 的表项没有写环境变量。
- 用 `-s 服务名` 指定服务，如 `pdf2zh example.pdf -s openai:gpt-4o-mini`。
- 上游还列出了几个在线体验站（pdf2zh.com、沉浸式翻译 BabelDOC 等），免安装，但属于第三方服务，与篝火无关。

## 验收用例

| 操作 | 应得到 |
|---|---|
| Windows 解压后双击 `pdf2zh.exe`，选一份含公式的英文 PDF，服务选 Google，目标语言选中文，开始翻译 | 生成译文版和双语对照版 PDF，公式、图表位置与原文一致 |
| 换成自己的 OpenAI 兼容接口（填地址、密钥、模型名）再翻译一次 | 同样生成译文 PDF |

## 和上游的区别

- 仅新增中文说明与篝火发布流程（`tool.json`、`.github/workflows/release.yml`），软件代码与上游一致。
- 移除了上游全部工作流（构建、测试、发布等），它们依赖上游的密钥。
- 本仓库对应上游 v1.9.11。上游 2.0 版本已迁到新仓库 [PDFMathTranslate-next](https://github.com/PDFMathTranslate/PDFMathTranslate-next)，本仓库不包含。

## 归属与许可证

本仓库由**篝火**整理发布，是篝火 App 应用区收录的开源工具之一。软件全部功能与版权归 [PDFMathTranslate](https://github.com/PDFMathTranslate/PDFMathTranslate) 原作者所有，按 **GNU AGPL-3.0** 许可证再分发，完整协议见仓库内 `LICENSE`，对应源码即本仓库。全部工具目录见 [toolkit-hub](https://github.com/campfire-code/toolkit-hub)。

---

以下为上游原始说明：

<div align="center">
	<a href="https://go.warp.dev/PDFMathTranslate" target="_blank">
		<sup>Special thanks to:</sup>
		<br>
		<img alt="Warp sponsorship" width="400" src="https://github.com/warpdotdev/brand-assets/blob/main/Github/Sponsor/Warp-Github-LG-02.png">
		<br>
		<h>Warp, built for coding with multiple AI agents</b>
		<br>
		<sup>Available for macOS, Linux and Windows</sup>
	</a>
</div>

<br>

<div align="center">

English | [简体中文](docs/README_zh-CN.md) | [繁體中文](docs/README_zh-TW.md) | [日本語](docs/README_ja-JP.md) | [한국어](docs/README_ko-KR.md)

<img src="./docs/images/banner.png" width="320px"  alt="PDF2ZH"/>

<h2 id="title">PDFMathTranslate</h2>

<p>
  <!-- PyPI -->
  <a href="https://pypi.org/project/pdf2zh/">
    <img src="https://img.shields.io/pypi/v/pdf2zh"></a>
  <a href="https://pepy.tech/projects/pdf2zh">
    <img src="https://static.pepy.tech/badge/pdf2zh"></a>
  <a href="https://hub.docker.com/r/byaidu/pdf2zh">
    <img src="https://img.shields.io/docker/pulls/byaidu/pdf2zh"></a>
  <a href="https://hellogithub.com/repository/8ec2cfd3ef744762bf531232fa32bc47" target="_blank"><img src="https://api.hellogithub.com/v1/widgets/recommend.svg?rid=8ec2cfd3ef744762bf531232fa32bc47&claim_uid=JQ0yfeBNjaTuqDU&theme=small" alt="Featured｜HelloGitHub" /></a>
  <a href="https://gitcode.com/Byaidu/PDFMathTranslate/overview">
    <img src="https://gitcode.com/Byaidu/PDFMathTranslate/star/badge.svg"></a>
  <a href="https://huggingface.co/spaces/reycn/PDFMathTranslate-Docker">
    <img src="https://img.shields.io/badge/%F0%9F%A4%97-Online%20Demo-FF9E0D"></a>
  <a href="https://www.modelscope.cn/studios/AI-ModelScope/PDFMathTranslate">
    <img src="https://img.shields.io/badge/ModelScope-Demo-blue"></a>
  <a href="https://github.com/Byaidu/PDFMathTranslate/pulls">
    <img src="https://img.shields.io/badge/contributions-welcome-green"></a>
  <a href="https://t.me/+Z9_SgnxmsmA5NzBl">
    <img src="https://img.shields.io/badge/Telegram-2CA5E0?style=flat-squeare&logo=telegram&logoColor=white"></a>
  <!-- License -->
  <a href="./LICENSE">
    <img src="https://img.shields.io/github/license/Byaidu/PDFMathTranslate"></a>
</p>

<a href="https://trendshift.io/repositories/19816" target="_blank"><img src="https://trendshift.io/api/badge/repositories/19816" alt="PDFMathTranslate%2FPDFMathTranslate | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

</div>

<h2 id="updates">1. What does this do?</h2>

Scientific PDF document translation preserving layouts.

- 📊 Preserve formulas, charts, table of contents, and annotations.
- 🌐 Support [multiple languages](#usage), and diverse [translation services](#usage).
- 🤖 Provides [commandline tool](#usage), [interactive user interface](#install), and [Docker](#install)

<div align="center">
<img src="./docs/images/preview.gif" width="80%"/>
</div>

<h2 id="updates">2. Recent Updates</h2>

- [October 3, 2026] Translated PDFs automatically add spaces between adjacent CJK and Latin letters, including accented letters, in normal and `--ultrafast` modes.

- [October 2, 2026] Added the `--ultrafast` CLI mode for native-text PDFs. It uses `pdf-inspector` text positions for heuristic layout and skips ONNX layout and OCR.  (by [@reycn](https://github.com/reycn))
- [September 8, 2026] Experimental OCR support, with paragraph regrouping and adaptive typesetting. (by [@reycn](https://github.com/reycn))
- [March 23, 2026] Experimental support for v2.0 translation kernel using isolated environment (`--mode precise`). (by [@reycn](https://github.com/reycn))
- [March 22, 2026] Supporting MiniMax (PR by [@octo-patch](https://github.com/octo-patch))
- [March 22, 2026] Fixing OpenAI-related issues (PR by [@samqin123](https://github.com/samqin123))
- [March 22, 2026] Fixing HTTP-related issues (PR by [@soukouki](https://github.com/soukouki))
- [March 22, 2026] Faster model loading on mac and OONX platforms, GUI starting-up, version printing, and continuous integration.(by [@reycn](https://github.com/reycn))
- [May 9, 2025] pdf2zh 2.0 Preview Version [#586](https://github.com/Byaidu/PDFMathTranslate/issues/586): The Windows ZIP file and Docker image are now available.

  > [!NOTE]
  >
  > 2.0 Moved to a new repository under the organization: [PDFMathTranslate/PDFMathTranslate-next](https://github.com/PDFMathTranslate/PDFMathTranslate-next)
  > 
  > Version 2.0 official release has been published.

<h2 id="use-section">3. Use 🌟</h2>
<h3 id="demo">3.1 Online Service 🌟</h3>

You can try our application out using either of the following demos:

- [Public free service](https://pdf2zh.com/) online without installation _(recommended)_.
- [Immersive Translate - BabelDOC](https://app.immersivetranslate.com/babel-doc/) Free usage quota is available; please refer to the FAQ section on the page for details. _(recommended)_
- [Demo hosted on HuggingFace](https://huggingface.co/spaces/reycn/PDFMathTranslate-Docker)
- [Demo hosted on ModelScope](https://www.modelscope.cn/studios/AI-ModelScope/PDFMathTranslate) without installation.

Note that the computing resources of the demo are limited, so please avoid abusing them.

<h3 id="install">3.2 Local Installation</h3>

For different use cases, we provide distinct methods to use our program:

<details open>
  <summary>3.2.1 Python: Install using uv</summary>

1. Python installed (3.11 <= version <= 3.12)

2. Install our package:

   ```bash
   pip install uv
   uv tool install --python 3.12 pdf2zh
   ```

3. Execute translation, files generated in [current working directory](https://chatgpt.com/share/6745ed36-9acc-800e-8a90-59204bd13444):

   ```bash
   pdf2zh document.pdf
   ```

</details>
<details>
  <summary>3.2.2 Python: Install using pip</summary>

1. Python installed (3.11 <= version <= 3.12)
2. Install our package:

   ```bash
   pip install pdf2zh
   ```

3. Execute translation, files generated in [current working directory](https://chatgpt.com/share/6745ed36-9acc-800e-8a90-59204bd13444):

   ```bash
   pdf2zh document.pdf
   ```

</details>
<details>
  <summary>3.3.3 Python: Graphic user interface</summary>

1. Python installed (3.11 <= version <= 3.12)

2. Install our package:

  ```bash
  pip install pdf2zh
  ```

3. Start using in browser:

   ```bash
   pdf2zh -i
   ```

4. If your browser has not been started automatically, goto

   ```bash
   http://localhost:7860/
   ```

   <img src="./docs/images/gui.gif" width="500"/>

See [documentation for GUI](./docs/README_GUI.md) for more details.

</details>

<details>
  <summary>3.2.4 Application: On Windows</summary>

1. Download pdf2zh-version-win64.zip from [release page](https://github.com/Byaidu/PDFMathTranslate/releases)

2. Unzip and double-click `pdf2zh.exe` to run.


  > [!TIP]
  >
  > - If you're using Windows and cannot open the file after downloading, please install [vc_redist.x64.exe](https://aka.ms/vs/17/release/vc_redist.x64.exe) and try again.
  > 
</details>


<details>

<summary>3.2.5 Reference manager: Zotero Plugin</summary>


See [Zotero PDF2zh](https://github.com/guaguastandup/zotero-pdf2zh) for more details.

</details>


<details>
  <summary>3.2.6 Docker: Containerized Deployment</summary>

1. Pull and run:

   ```bash
   docker pull byaidu/pdf2zh
   docker run -d -p 7860:7860 byaidu/pdf2zh
   ```

2. Open in browser:

   ```
   http://localhost:7860/
   ```

For docker deployment on cloud service:

<div>
<a href="https://www.heroku.com/deploy?template=https://github.com/Byaidu/PDFMathTranslate">
  <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy" height="26"></a>
<a href="https://render.com/deploy">
  <img src="https://render.com/images/deploy-to-render-button.svg" alt="Deploy to Koyeb" height="26"></a>
<a href="https://zeabur.com/templates/5FQIGX?referralCode=reycn">
  <img src="https://zeabur.com/button.svg" alt="Deploy on Zeabur" height="26"></a>
<a href="https://template.sealos.io/deploy?templateName=pdf2zh">
  <img src="https://sealos.io/Deploy-on-Sealos.svg" alt="Deploy on Sealos" height="26"></a>
<a href="https://app.koyeb.com/deploy?type=git&builder=buildpack&repository=github.com/Byaidu/PDFMathTranslate&branch=main&name=pdf-math-translate">
  <img src="https://www.koyeb.com/static/images/deploy/button.svg" alt="Deploy to Koyeb" height="26"></a>
</div>

> [!TIP]
>
> - If you cannot access Docker Hub, please try the image on [GitHub Container Registry](https://github.com/Byaidu/PDFMathTranslate/pkgs/container/pdfmathtranslate).
> ```bash
> docker pull ghcr.io/byaidu/pdfmathtranslate
> docker run -d -p 7860:7860 ghcr.io/byaidu/pdfmathtranslate
> ```
</details>

<details>
  <summary>3.2.* Solutions for network issues in installation</summary>

  Users in specific regions may encounter network difficulties when loading the AI model. The current program relies on the AI model (`wybxc/DocLayout-YOLO-DocStructBench-onnx`), and some users are unable to download it due to these network issues.

  To address issues with downloading this model, use the following environment variable as a workaround:

  ```shell
  set HF_ENDPOINT=https://hf-mirror.com
  ```

  For PowerShell user:

  ```shell
  $env:HF_ENDPOINT = https://hf-mirror.com
  ```

  If the solution does not work to you / you encountered other issues, please refer to [Frequently Asked Questions](https://github.com/Byaidu/PDFMathTranslate/wiki#-faq--%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98).
</details>


<h2 id="usage">4. Technical Details</h2>

### Experimental automatic OCR (fast mode)

Fast mode automatically runs local OCR on selected image-only pages before
translation. Native text, existing OCR layers, and blank pages are skipped;
the original pages in dual output remain unchanged. Install with
`pip install 'pdf2zh[ocr]'` (or `pip install -e '.[ocr]'` from this checkout).
The first scanned page downloads the requested language data from Tesseract's
`tessdata_fast` 4.1.0 release into `~/.cache/pdf2zh/tessdata/4.1.0`; subsequent
runs reuse it offline. Native-text PDFs do not trigger downloads.
OCR uses the input language; `PDF2ZH_OCR_LANGUAGE=eng+deu` overrides it with
Tesseract language codes. Set `TESSDATA_PREFIX` to use your own data without
automatic downloads.

PyMuPDF supplies the OCR engine; the optional extra adds Pooch for cached downloads.
No separate Tesseract executable is required.
OCR words are regrouped into paragraphs within detected layout regions before
translation, with wrapped lines and soft hyphens joined. Translated paragraphs
start at the median source font size and shrink to fit their original boxes;
detected figures, tables, and standalone formulas remain untouched.
The initial implementation targets white-background scans: partial scans on
pages that already contain text are skipped, and handwritten text or inline
equations may be recognized incorrectly. Precise mode is unchanged.

### Ultrafast mode

Install the optional `pdf-inspector>=1.25.2,<2` dependency with
`pip install 'pdf2zh[ultrafast]'`, then run:

```bash
pdf2zh example.pdf --ultrafast
```

`--ultrafast` uses native PDF text positions from `pdf-inspector` for heuristic
layout. It skips ONNX layout and OCR; pages without native text are preserved
without OCR. Its heuristic text grouping retains the usual font and character
formula safeguards. It is best suited to PDFs that already contain native text;
use normal mode for complex tables or formulas. It is available only in fast
CLI mode and cannot be combined with `--mode precise`, `--babeldoc`, server or
GUI modes, or `--onnx`. It automatically skips font subsetting, so its output
PDFs are larger, while still using BabelDOC font assets as needed. With
`--ignore-cache`, it bypasses both translation-cache reads and writes; normal
mode keeps its existing `--ignore-cache` behavior. Ultrafast uses a shared
whole-document paragraph worker pool with 16 workers by default and submits
individual paragraph requests; `-t` overrides this value, while normal mode
keeps its default of 4. `[ultrafast perf]` INFO logs report stage and per-page
timings. `page_scan` is the paragraph-submission scan; `translation` is the
elapsed wait for the whole-document pool to drain, including API retries, so
it is not a sum of per-page waits. `paragraph_parse` covers both passes,
`typesetting` runs after translation completes, and `layout_extract` is
reported separately before font setup. `page_processing` includes nested
`layout_mask`, `paragraph_parse`, `translation`, and `typesetting` timings, so
do not sum the nested values again. This path does not import ONNX or OpenCV.

### 4.1 Advanced options

Execute the translation command in the command line to generate the translated document `example-mono.pdf` and the bilingual document `example-dual.pdf` in the current working directory. Use Google as the default translation service. More support translation services can find [HERE](https://github.com/Byaidu/PDFMathTranslate/blob/main/docs/ADVANCED.md#services).

<img src="./docs/images/cmd.explained.png" width="580px"  alt="cmd"/>

In the following table, we list all advanced options for reference:

| Option                | Function                                                                                                      | Example                                        |
| --------------------- | ------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| files                 | Local files                                                                                                   | `pdf2zh ~/local.pdf`                           |
| links                 | Online files                                                                                                  | `pdf2zh http://arxiv.org/paper.pdf`            |
| `-i`                  | [Enter GUI](#gui)                                                                                             | `pdf2zh -i`                                    |
| `-p`                  | [Partial document translation](https://github.com/Byaidu/PDFMathTranslate/blob/main/docs/ADVANCED.md#partial) | `pdf2zh example.pdf -p 1`                      |
| `-li`                 | [Source language](https://github.com/Byaidu/PDFMathTranslate/blob/main/docs/ADVANCED.md#languages)            | `pdf2zh example.pdf -li en`                    |
| `-lo`                 | [Target language](https://github.com/Byaidu/PDFMathTranslate/blob/main/docs/ADVANCED.md#languages)            | `pdf2zh example.pdf -lo zh`                    |
| `-s`                  | [Translation service](https://github.com/Byaidu/PDFMathTranslate/blob/main/docs/ADVANCED.md#services)         | `pdf2zh example.pdf -s deepl`                  |
| `-t`                  | [Multi-threads](https://github.com/Byaidu/PDFMathTranslate/blob/main/docs/ADVANCED.md#threads)                | `pdf2zh example.pdf -t 1`                      |
| `-o`                  | Output dir                                                                                                    | `pdf2zh example.pdf -o output`                 |
| `-f`, `-c`            | [Exceptions](https://github.com/Byaidu/PDFMathTranslate/blob/main/docs/ADVANCED.md#exceptions)                | `pdf2zh example.pdf -f "(MS.*)"`               |
| `-cp`                 | Compatibility Mode                                                                                            | `pdf2zh example.pdf --compatible`              |
| `--ultrafast`         | [Use native PDF text positions for heuristic layout; skip ONNX layout and OCR](./docs/ADVANCED.md#ultrafast) | `pdf2zh example.pdf --ultrafast`               |
| `--skip-subset-fonts` | [Skip font subset](https://github.com/Byaidu/PDFMathTranslate/blob/main/docs/ADVANCED.md#font-subset)         | `pdf2zh example.pdf --skip-subset-fonts`       |
| `--ignore-cache`      | [Ignore translate cache](https://github.com/Byaidu/PDFMathTranslate/blob/main/docs/ADVANCED.md#cache)         | `pdf2zh example.pdf --ignore-cache`            |
| `--share`             | Public link                                                                                                   | `pdf2zh -i --share`                            |
| `--authorized`        | [Authorization](https://github.com/Byaidu/PDFMathTranslate/blob/main/docs/ADVANCED.md#auth)                   | `pdf2zh -i --authorized users.txt [auth.html]` |
| `--prompt`            | [Custom Prompt](https://github.com/Byaidu/PDFMathTranslate/blob/main/docs/ADVANCED.md#prompt)                 | `pdf2zh --prompt [prompt.txt]`                 |
| `--onnx`              | [Use Custom DocLayout-YOLO ONNX model]                                                                        | `pdf2zh --onnx [onnx/model/path]`              |
| `--serverport`        | [Use Custom WebUI port]                                                                                       | `pdf2zh --serverport 7860`                     |
| `--dir`               | [batch translate]                                                                                             | `pdf2zh --dir /path/to/translate/`             |
| `--config`            | [configuration file](https://github.com/Byaidu/PDFMathTranslate/blob/main/docs/ADVANCED.md#cofig)             | `pdf2zh --config /path/to/config/config.json`  |
| `--serverport`        | [custom gradio server port]                                                                                   | `pdf2zh --serverport 7860`                     |
| `--mode`              | Translation mode: `fast` (default, v1) or `precise` (v2, experimental, requires pdf2zh_next submodule)         | `pdf2zh --mode precise example.pdf`            |
| `--babeldoc`          | Use Experimental backend [BabelDOC](https://funstory-ai.github.io/BabelDOC/) to translate                     | `pdf2zh --babeldoc` -s openai example.pdf      |
| `--mcp`               | Enable MCP STDIO mode                                                                                         | `pdf2zh --mcp`                                 |
| `--sse`               | Enable MCP SSE mode                                                                                           | `pdf2zh --mcp --sse`                           |

For detailed explanations, please refer to our document about [Advanced Usage](./docs/ADVANCED.md) for a full list of each option.

<h3 id="downstream">4.2 Downstream Development</h3>
For downstream applications, please refer to our document about [API Details](./docs/APIS.md) for further information about:

- [Python API](./docs/APIS.md#api-python), how to use the program in other Python programs
- [HTTP API](./docs/APIS.md#api-http), how to communicate with a server with the program installed

<h3 id="downstream">4.3 Differences between two major forks</h3>

- [Byaidu/PDFMathTranslate](https://github.com/Byaidu/PDFMathTranslate): The present and the original project for stable release.

- [PDFMathTranslate/PDFMathTranslate-next](https://github.com/PDFMathTranslate/PDFMathTranslate-next): A fork with web-ui and additional features. This fork handles a large number of marginal cases, improves PDF compatibility, and optimizes cross-column and cross-page semantic consistency, dynamic scaling, and dynamic scaling consistency, among many other translation quality improvements. However, this fork is intended solely for development and does not address compatibility issues and is not designed for community-contributions.

<h2 id="information">5. Project Information</h2>
<h3 id="citation">5.1 Citation</h3>

This work has been accepted by the [*Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing: System Demonstrations*](https://aclanthology.org/2025.emnlp-demos.71/) (EMNLP 2025). 

Citation:

```
@inproceedings{ouyang-etal-2025-pdfmathtranslate,
	    title = "{PDFM}ath{T}ranslate: Scientific Document Translation Preserving Layouts",
	    author = "Ouyang, Rongxin  and
	      Chu, Chang  and
	      Xin, Zhikuang  and
	      Ma, Xiangyao",
	    editor = {Habernal, Ivan  and
	      Schulam, Peter  and
	      Tiedemann, J{\"o}rg},
	    booktitle = "Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing: System Demonstrations",
	    month = nov,
	    year = "2025",
	    address = "Suzhou, China",
	    publisher = "Association for Computational Linguistics",
	    url = "https://aclanthology.org/2025.emnlp-demos.71/",
	    pages = "918--924",
	    ISBN = "979-8-89176-334-0",
	    abstract = "Language barriers in scientific documents hinder the diffusion and development of science and technologies. However, prior efforts in translating such documents largely overlooked the information in layouts. To bridge the gap, we introduce PDFMathTranslate, the world{'}s first open-source software for translating scientific documents while preserving layouts. Leveraging the most recent advances in large language models and precise layout detection, we contribute to the community with key improvements in precision, flexibility, and efficiency. The work is open-sourced at https://github.com/byaidu/pdfmathtranslate with more than 222k downloads."
	}
```
<h3 id="acknowledgement">5.2 Acknowledgement</h3>

- [Immersive Translation](https://immersivetranslate.com) sponsors monthly Pro membership redemption codes for active contributors to this project, see details at: [CONTRIBUTOR_REWARD.md](https://github.com/funstory-ai/BabelDOC/blob/main/docs/CONTRIBUTOR_REWARD.md)

- New backend: [BabelDOC](https://github.com/funstory-ai/BabelDOC)

- Document merging: [PyMuPDF](https://github.com/pymupdf/PyMuPDF)

- Document parsing: [Pdfminer.six](https://github.com/pdfminer/pdfminer.six)

- Document extraction: [MinerU](https://github.com/opendatalab/MinerU)

- Document Preview: [Gradio PDF](https://github.com/freddyaboulton/gradio-pdf)

- Multi-threaded translation: [MathTranslate](https://github.com/SUSYUSTC/MathTranslate)

- Layout parsing: [DocLayout-YOLO](https://github.com/opendatalab/DocLayout-YOLO)

- Document standard: [PDF Explained](https://zxyle.github.io/PDF-Explained/), [PDF Cheat Sheets](https://pdfa.org/resource/pdf-cheat-sheets/)

- Multilingual Font: [Go Noto Universal](https://github.com/satbyy/go-noto-universal)

<h3 id="contrib">5.3 Contributors</h3>

<a href="https://github.com/Byaidu/PDFMathTranslate/graphs/contributors">
  <img src="https://opencollective.com/PDFMathTranslate/contributors.svg?width=890&button=false" />
</a>

![Alt](https://repobeats.axiom.co/api/embed/dfa7583da5332a11468d686fbd29b92320a6a869.svg "Repobeats analytics image")

For details on how to contribute, please consult the [Contribution Guide](https://github.com/Byaidu/PDFMathTranslate/wiki/Contribution-Guide---%E8%B4%A1%E7%8C%AE%E6%8C%87%E5%8D%97).


<h3 id="star_hist">5.4 Star History</h3>
<!-- star-history:start -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/star-history/star-history-dark.svg">
  <img alt="Star history" src="assets/star-history/star-history-light.svg">
</picture>
<!-- star-history:end -->
