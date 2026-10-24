import asyncio
import cgi
import os
import shutil
import socket
import uuid
from asyncio import CancelledError
from pathlib import Path
import typing as T

import gradio as gr
import requests
import tqdm
from gradio_pdf import PDF
from string import Template
import logging

from pdf2zh import __version__
from pdf2zh.high_level import translate
from pdf2zh.doclayout import ModelInstance
from pdf2zh.config import ConfigManager
from pdf2zh.translator import (
    AnythingLLMTranslator,
    AzureOpenAITranslator,
    AzureTranslator,
    BaseTranslator,
    BingTranslator,
    DeepLTranslator,
    DeepLXTranslator,
    DifyTranslator,
    ArgosTranslator,
    GeminiTranslator,
    GoogleTranslator,
    MiniMaxTranslator,
    ModelScopeTranslator,
    OllamaTranslator,
    OpenAITranslator,
    SiliconTranslator,
    TencentTranslator,
    XinferenceTranslator,
    ZhipuTranslator,
    GrokTranslator,
    GroqTranslator,
    DeepseekTranslator,
    OpenAIlikedTranslator,
    QwenMtTranslator,
    X302AITranslator,
)
from babeldoc.docvision.doclayout import OnnxModel
from babeldoc import __version__ as babeldoc_version

logger = logging.getLogger(__name__)


class _LazyModel:
    """Defers model loading until first access so the GUI starts instantly."""

    def __init__(self):
        self._model = None

    def _ensure_loaded(self):
        if self._model is None:
            self._model = OnnxModel.load_available()

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        self._ensure_loaded()
        return getattr(self._model, name)


BABELDOC_MODEL = _LazyModel()
# The following variables associate strings with translators
service_map: dict[str, BaseTranslator] = {
    "Google": GoogleTranslator,
    "Bing": BingTranslator,
    "DeepL": DeepLTranslator,
    "DeepLX": DeepLXTranslator,
    "Ollama": OllamaTranslator,
    "Xinference": XinferenceTranslator,
    "AzureOpenAI": AzureOpenAITranslator,
    "OpenAI": OpenAITranslator,
    "Zhipu": ZhipuTranslator,
    "ModelScope": ModelScopeTranslator,
    "Silicon": SiliconTranslator,
    "Gemini": GeminiTranslator,
    "Azure": AzureTranslator,
    "Tencent": TencentTranslator,
    "Dify": DifyTranslator,
    "AnythingLLM": AnythingLLMTranslator,
    "Argos Translate": ArgosTranslator,
    "Grok": GrokTranslator,
    "Groq": GroqTranslator,
    "DeepSeek": DeepseekTranslator,
    "MiniMax": MiniMaxTranslator,
    "OpenAI-liked": OpenAIlikedTranslator,
    "Ali Qwen-Translation": QwenMtTranslator,
    "302.AI": X302AITranslator,
}

# The following variables associate strings with specific languages
lang_map = {
    "Simplified Chinese": "zh",
    "Traditional Chinese": "zh-TW",
    "English": "en",
    "French": "fr",
    "German": "de",
    "Japanese": "ja",
    "Korean": "ko",
    "Russian": "ru",
    "Spanish": "es",
    "Italian": "it",
}

# The following variable associate strings with page ranges
page_map = {
    "All": None,
    "First": [0],
    "First 5 pages": list(range(0, 5)),
    "Others": None,
}

# 汉化（篝火）：下拉与单选的显示名，内部值保持上游原样，翻译逻辑不受影响
SERVICE_LABELS = {
    "Argos Translate": "Argos 离线翻译",
    "Silicon": "硅基流动（SiliconCloud）",
    "Zhipu": "智谱（Zhipu）",
    "ModelScope": "魔搭（ModelScope）",
    "Tencent": "腾讯云机器翻译",
    "Azure": "Azure 翻译",
    "AzureOpenAI": "Azure OpenAI",
    "OpenAI-liked": "兼容 OpenAI 接口的服务",
    "Ali Qwen-Translation": "阿里通义 Qwen-MT",
}
LANG_LABELS = {
    "Simplified Chinese": "简体中文",
    "Traditional Chinese": "繁体中文",
    "English": "英语",
    "French": "法语",
    "German": "德语",
    "Japanese": "日语",
    "Korean": "韩语",
    "Russian": "俄语",
    "Spanish": "西班牙语",
    "Italian": "意大利语",
}
PAGE_LABELS = {
    "All": "全部",
    "First": "第一页",
    "First 5 pages": "前 5 页",
    "First 20 pages": "前 20 页",
    "Others": "自定义",
}
FILE_TYPE_CHOICES = [("文件", "File"), ("链接", "Link")]
MODE_CHOICES = [("快速", "fast"), ("精细", "precise")]

# 翻译服务设置项的中文名：先按完整名，再按后缀，前缀是服务商
_ENV_SUFFIX = {
    "_API_KEY": "密钥",
    "_AUTH_KEY": "密钥",
    "_ACCESS_TOKEN": "访问令牌",
    "_BASE_URL": "接口地址",
    "_API_URL": "接口地址",
    "_ENDPOINT": "接口地址",
    "_HOST": "服务地址",
    "_MODEL": "模型名",
    "_STREAM": "流式输出（true 开启，false 关闭）",
    "_STOP_TOKENS": "停止词（空格分隔）",
    "_MAX_TOKENS": "最大输出长度（-1 表示不限制）",
    "_API_VERSION": "接口版本",
    "_SECRET_ID": "密钥编号（SecretId）",
    "_SECRET_KEY": "密钥（SecretKey）",
    "_DOMAINS": "领域提示",
}
_ENV_PREFIX = {
    "DEEPLX": "DeepLX", "DEEPL": "DeepL", "OLLAMA": "Ollama",
    "XINFERENCE": "Xinference", "AZURE_OPENAI": "Azure OpenAI",
    "OPENAILIKED": "兼容接口", "OPENAI": "OpenAI", "MODELSCOPE": "魔搭",
    "ZHIPU": "智谱", "SILICON": "硅基流动", "X302AI": "302.AI",
    "GEMINI": "Gemini", "AZURE": "Azure 翻译", "TENCENTCLOUD": "腾讯云",
    "DIFY": "Dify", "ANYTHINGLLM": "AnythingLLM", "GROK": "Grok",
    "GROQ": "Groq", "DEEPSEEK": "DeepSeek", "MINIMAX": "MiniMax",
    "ALI": "通义 Qwen-MT",
}


def env_label_zh(key: str) -> str:
    """把设置项名（如 OPENAI_API_KEY）转成「OpenAI 密钥」这样的中文标签。"""
    if key in _ENV_FULL:
        return _ENV_FULL[key]
    up = str(key).upper()
    for suf, zh_suf in _ENV_SUFFIX.items():
        if up.endswith(suf):
            head = up[: -len(suf)]
            for pre in sorted(_ENV_PREFIX, key=len, reverse=True):
                if head == pre:
                    return f"{_ENV_PREFIX[pre]} {zh_suf}"
            break
    for pre in sorted(_ENV_PREFIX, key=len, reverse=True):
        if up.startswith(pre + "_"):
            return f"{_ENV_PREFIX[pre]} {up[len(pre) + 1:]}"
    return str(key)


# 进度条文字：未收录的阶段名统一显示「处理中」，避免出现英文
PROGRESS_LABELS = {
    "Translate paragraphs": "翻译段落",
    "Typeset pages": "排版页面",
    "Translate Paragraphs": "翻译段落",
    "Typesetting": "排版页面",
    "Parse PDF and Create Intermediate Representation": "解析 PDF",
    "DetectScannedFile": "检测是否为扫描件",
    "Parse Page Layout": "识别页面版面",
    "Parse Table": "识别表格",
    "Parse Paragraphs": "识别段落",
    "Parse Formulas and Styles": "识别公式与样式",
    "Remove Char Descent": "调整字符基线",
    "Add Fonts": "添加字体",
    "Generate drawing instructions": "生成绘制指令",
    "Add Debug Information": "添加调试信息",
    "Subset font": "字体子集化",
    "Save PDF": "保存 PDF",
}
_ENV_FULL = {
    "AnythingLLM_URL": "AnythingLLM 接口地址",
    "AnythingLLM_APIKEY": "AnythingLLM 密钥",
}


# Check if this is a public demo, which has resource limits
flag_demo = False

# Limit resources
if ConfigManager.get("PDF2ZH_DEMO"):
    flag_demo = True
    service_map = {
        "Google": GoogleTranslator,
    }
    page_map = {
        "First": [0],
        "First 20 pages": list(range(0, 20)),
    }
    client_key = ConfigManager.get("PDF2ZH_CLIENT_KEY")
    server_key = ConfigManager.get("PDF2ZH_SERVER_KEY")


# Limit Enabled Services
enabled_services: T.Optional[T.List[str]] = ConfigManager.get("ENABLED_SERVICES")
if isinstance(enabled_services, list):
    default_services = ["Google", "Bing"]
    enabled_services_names = [str(_).lower().strip() for _ in enabled_services]
    enabled_services = [
        k
        for k in service_map.keys()
        if str(k).lower().strip() in enabled_services_names
    ]
    if len(enabled_services) == 0:
        raise RuntimeError("No services available.")
    enabled_services = default_services + enabled_services
else:
    enabled_services = list(service_map.keys())


# 下拉选项：(中文显示名, 内部值)
service_choices = [(SERVICE_LABELS.get(k, k), k) for k in enabled_services]
lang_choices = [(LANG_LABELS.get(k, k), k) for k in lang_map]


def page_choices():
    return [(PAGE_LABELS.get(k, k), k) for k in page_map]


# Configure about Gradio show keys
hidden_gradio_details: bool = bool(ConfigManager.get("HIDDEN_GRADIO_DETAILS"))


# Public demo control
def verify_recaptcha(response):
    """
    This function verifies the reCAPTCHA response.
    """
    recaptcha_url = "https://www.google.com/recaptcha/api/siteverify"
    data = {"secret": server_key, "response": response}
    result = requests.post(recaptcha_url, data=data).json()
    return result.get("success")


def download_with_limit(url: str, save_path: str, size_limit: int) -> str:
    """
    This function downloads a file from a URL and saves it to a specified path.

    Inputs:
        - url: The URL to download the file from
        - save_path: The path to save the file to
        - size_limit: The maximum size of the file to download

    Returns:
        - The path of the downloaded file
    """
    chunk_size = 1024
    total_size = 0
    with requests.get(url, stream=True, timeout=10) as response:
        response.raise_for_status()
        content = response.headers.get("Content-Disposition")
        try:  # filename from header
            _, params = cgi.parse_header(content)
            filename = params["filename"]
        except Exception:  # filename from url
            filename = os.path.basename(url)
        filename = os.path.splitext(os.path.basename(filename))[0] + ".pdf"
        with open(save_path / filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                total_size += len(chunk)
                if size_limit and total_size > size_limit:
                    raise gr.Error("文件超过大小限制")
                file.write(chunk)
    return save_path / filename


def stop_translate_file(state: dict) -> None:
    """
    This function stops the translation process.

    Inputs:
        - state: The state of the translation process

    Returns:- None
    """
    session_id = state["session_id"]
    if session_id is None:
        return
    if session_id in cancellation_event_map:
        logger.info(f"Stopping translation for session {session_id}")
        cancellation_event_map[session_id].set()


def translate_file(
    file_type,
    file_input,
    link_input,
    service,
    lang_from,
    lang_to,
    page_range,
    page_input,
    prompt,
    threads,
    skip_subset_fonts,
    ignore_cache,
    vfont,
    mode_choice,
    recaptcha_response,
    state,
    progress=gr.Progress(),
    *envs,
):
    """
    This function translates a PDF file from one language to another.

    Inputs:
        - file_type: The type of file to translate
        - file_input: The file to translate
        - link_input: The link to the file to translate
        - service: The translation service to use
        - lang_from: The language to translate from
        - lang_to: The language to translate to
        - page_range: The range of pages to translate
        - page_input: The input for the page range
        - prompt: The custom prompt for the llm
        - threads: The number of threads to use
        - recaptcha_response: The reCAPTCHA response
        - state: The state of the translation process
        - progress: The progress bar
        - envs: The environment variables

    Returns:
        - The translated file
        - The translated file
        - The translated file
        - The progress bar
        - The progress bar
        - The progress bar
    """
    session_id = uuid.uuid4()
    state["session_id"] = session_id
    cancellation_event_map[session_id] = asyncio.Event()
    # Translate PDF content using selected service.
    if flag_demo and not verify_recaptcha(recaptcha_response):
        raise gr.Error("人机验证未通过")

    progress(0, desc="开始翻译……")

    output = Path("pdf2zh_files")
    output.mkdir(parents=True, exist_ok=True)

    if file_type == "File":
        if not file_input:
            raise gr.Error("请先选择 PDF 文件或填写文件链接")
        file_path = shutil.copy(file_input, output)
    else:
        if not link_input:
            raise gr.Error("请先选择 PDF 文件或填写文件链接")
        file_path = download_with_limit(
            link_input,
            output,
            5 * 1024 * 1024 if flag_demo else None,
        )

    filename = os.path.splitext(os.path.basename(file_path))[0]
    file_raw = output / f"{filename}.pdf"
    file_mono = output / f"{filename}-mono.pdf"
    file_dual = output / f"{filename}-dual.pdf"

    translator = service_map[service]
    if page_range != "Others":
        selected_page = page_map[page_range]
    else:
        selected_page = []
        for p in page_input.split(","):
            if "-" in p:
                start, end = p.split("-")
                selected_page.extend(range(int(start) - 1, int(end)))
            else:
                selected_page.append(int(p) - 1)
    lang_from = lang_map[lang_from]
    lang_to = lang_map[lang_to]

    _envs = {}
    for i, env in enumerate(translator.envs.items()):
        _envs[env[0]] = envs[i]
    for k, v in _envs.items():
        if str(k).upper().endswith("API_KEY") and str(v) == "***":
            # Load Real API_KEYs from local configure file
            real_keys: str = ConfigManager.get_env_by_translatername(
                translator, k, None
            )
            _envs[k] = real_keys

    print(f"Files before translation: {os.listdir(output)}")

    def progress_bar(t: tqdm.tqdm):
        desc = getattr(t, "desc", "")
        if desc == "":
            desc = "翻译中"
        progress(t.n / t.total, desc=PROGRESS_LABELS.get(desc, "处理中"))

    try:
        threads = int(threads)
    except ValueError:
        threads = 1

    param = {
        "files": [str(file_raw)],
        "pages": selected_page,
        "lang_in": lang_from,
        "lang_out": lang_to,
        "service": f"{translator.name}",
        "output": output,
        "thread": int(threads),
        "callback": progress_bar,
        "cancellation_event": cancellation_event_map[session_id],
        "envs": _envs,
        "prompt": Template(prompt) if prompt else None,
        "skip_subset_fonts": skip_subset_fonts,
        "ignore_cache": ignore_cache,
        "vfont": vfont,  # 添加自定义公式字体正则表达式
        "model": ModelInstance.value,
    }

    try:
        from pdf2zh.kernel import KernelRegistry
        from pdf2zh.kernel.protocol import TranslateRequest

        KernelRegistry.switch(mode_choice)
        kernel = KernelRegistry.get()
        request = TranslateRequest(
            files=[str(file_raw)],
            output=str(output),
            pages=selected_page,
            lang_in=lang_from,
            lang_out=lang_to,
            service=f"{translator.name}",
            thread=int(threads),
            envs=_envs,
            prompt=str(prompt) if prompt else None,
            skip_subset_fonts=skip_subset_fonts,
            ignore_cache=ignore_cache,
            vfont=vfont,
        )
        kernel.translate(
            request,
            callback=progress_bar,
            cancellation_event=cancellation_event_map[session_id],
        )
    except CancelledError:
        del cancellation_event_map[session_id]
        raise gr.Error("翻译已取消")
    print(f"Files after translation: {os.listdir(output)}")

    if not file_mono.exists() or not file_dual.exists():
        raise gr.Error("没有生成译文文件，请检查翻译服务设置后重试")

    progress(1.0, desc="翻译完成")

    return (
        str(file_mono),
        str(file_mono),
        str(file_dual),
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(visible=True),
    )


def babeldoc_translate_file(**kwargs):
    from babeldoc.high_level import init as babeldoc_init

    babeldoc_init()
    from babeldoc.high_level import async_translate as babeldoc_translate
    from babeldoc.translation_config import TranslationConfig as YadtConfig

    for translator in [
        GoogleTranslator,
        BingTranslator,
        DeepLTranslator,
        DeepLXTranslator,
        OllamaTranslator,
        XinferenceTranslator,
        AzureOpenAITranslator,
        OpenAITranslator,
        ZhipuTranslator,
        ModelScopeTranslator,
        SiliconTranslator,
        GeminiTranslator,
        AzureTranslator,
        TencentTranslator,
        DifyTranslator,
        AnythingLLMTranslator,
        ArgosTranslator,
        GrokTranslator,
        GroqTranslator,
        DeepseekTranslator,
        OpenAIlikedTranslator,
        QwenMtTranslator,
        X302AITranslator,
    ]:
        if kwargs["service"] == translator.name:
            translator = translator(
                kwargs["lang_in"],
                kwargs["lang_out"],
                "",
                envs=kwargs["envs"],
                prompt=kwargs["prompt"],
                ignore_cache=kwargs["ignore_cache"],
            )
            break
    else:
        raise ValueError("Unsupported translation service")
    import asyncio
    from babeldoc.main import create_progress_handler

    for file in kwargs["files"]:
        file = file.strip("\"'")
        yadt_config = YadtConfig(
            input_file=file,
            font=None,
            pages=",".join((str(x) for x in getattr(kwargs, "raw_pages", []))),
            output_dir=kwargs["output"],
            doc_layout_model=BABELDOC_MODEL,
            translator=translator,
            debug=False,
            lang_in=kwargs["lang_in"],
            lang_out=kwargs["lang_out"],
            no_dual=False,
            no_mono=False,
            qps=kwargs["thread"],
            use_rich_pbar=False,
            disable_rich_text_translate=not isinstance(translator, OpenAITranslator),
            skip_clean=kwargs["skip_subset_fonts"],
            report_interval=0.5,
        )

        async def yadt_translate_coro(yadt_config):
            progress_context, progress_handler = create_progress_handler(yadt_config)

            # 开始翻译
            with progress_context:
                async for event in babeldoc_translate(yadt_config):
                    progress_handler(event)
                    if yadt_config.debug:
                        logger.debug(event)
                    kwargs["callback"](progress_context)
                    if kwargs["cancellation_event"].is_set():
                        yadt_config.cancel_translation()
                        raise CancelledError
                    if event["type"] == "finish":
                        result = event["translate_result"]
                        logger.info("Translation Result:")
                        logger.info(f"  Original PDF: {result.original_pdf_path}")
                        logger.info(f"  Time Cost: {result.total_seconds:.2f}s")
                        logger.info(f"  Mono PDF: {result.mono_pdf_path or 'None'}")
                        logger.info(f"  Dual PDF: {result.dual_pdf_path or 'None'}")
                        file_mono = result.mono_pdf_path
                        file_dual = result.dual_pdf_path
                        break
            import gc

            gc.collect()
            return (
                str(file_mono),
                str(file_mono),
                str(file_dual),
                gr.update(visible=True),
                gr.update(visible=True),
                gr.update(visible=True),
            )

        return asyncio.run(yadt_translate_coro(yadt_config))


# Global setup
custom_blue = gr.themes.Color(
    c50="#E8F3FF",
    c100="#BEDAFF",
    c200="#94BFFF",
    c300="#6AA1FF",
    c400="#4080FF",
    c500="#165DFF",  # Primary color
    c600="#0E42D2",
    c700="#0A2BA6",
    c800="#061D79",
    c900="#03114D",
    c950="#020B33",
)

custom_css = """
    .secondary-text {color: #999 !important;}
    footer {visibility: hidden}
    .env-warning {color: #dd5500 !important;}
    .env-success {color: #559900 !important;}

    /* Add dashed border to input-file class */
    .input-file {
        border: 1.2px dashed #165DFF !important;
        border-radius: 6px !important;
    }

    .progress-bar-wrap {
        border-radius: 8px !important;
    }

    .progress-bar {
        border-radius: 8px !important;
    }

    .pdf-canvas canvas {
        width: 100%;
    }
    """

demo_recaptcha = """
    <script src="https://www.google.com/recaptcha/api.js?render=explicit" async defer></script>
    <script type="text/javascript">
        var onVerify = function(token) {
            el=document.getElementById('verify').getElementsByTagName('textarea')[0];
            el.value=token;
            el.dispatchEvent(new Event('input'));
        };
    </script>
    """

tech_details_string = f"""
                    <summary>技术信息</summary>
                    - 开源地址: <a href="https://github.com/Byaidu/PDFMathTranslate">Byaidu/PDFMathTranslate</a><br>
                    - BabelDOC: <a href="https://github.com/funstory-ai/BabelDOC">funstory-ai/BabelDOC</a><br>
                    - 界面作者: <a href="https://github.com/reycn">Rongxin</a><br>
                    - pdf2zh 版本: {__version__} <br>
                    - BabelDOC 版本: {babeldoc_version}
                """
cancellation_event_map = {}

# Gradio 6 takes these styling options in launch() rather than gr.Blocks()
launch_style_kwargs = {
    "theme": gr.themes.Default(
        primary_hue=custom_blue, spacing_size="md", radius_size="lg"
    ),
    "css": custom_css,
    "head": demo_recaptcha if flag_demo else "",
}


# The following code creates the GUI
with gr.Blocks(
    title="PDF 双语翻译（保版式）",
) as demo:
    gr.Markdown(
        "# PDF 双语翻译（保版式）\n基于开源项目 [PDFMathTranslate](https://github.com/Byaidu/PDFMathTranslate)，翻译时保留公式、图表和排版。"
    )

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## 文件 | 不超过 5 MB" if flag_demo else "## 文件")
            file_type = gr.Radio(
                choices=FILE_TYPE_CHOICES,
                label="来源",
                value="File",
            )
            file_input = gr.File(
                label="PDF 文件",
                file_count="single",
                file_types=[".pdf", ".doc", ".docx"],
                type="filepath",
                elem_classes=["input-file"],
            )
            link_input = gr.Textbox(
                label="文件链接",
                visible=False,
                interactive=True,
            )
            gr.Markdown("## 翻译设置")
            service = gr.Dropdown(
                label="翻译服务",
                choices=service_choices,
                value=enabled_services[0],
            )
            envs = []
            # 篝火修正：设置项输入框数量取各服务的最大值（OpenAI 等有 6 项，原来只有 3 个会报错）
            max_envs = max(len(t.envs) for t in service_map.values())
            for i in range(max_envs):
                envs.append(
                    gr.Textbox(
                        visible=False,
                        interactive=True,
                    )
                )
            with gr.Row():
                lang_from = gr.Dropdown(
                    label="原文语言",
                    choices=lang_choices,
                    value=ConfigManager.get("PDF2ZH_LANG_FROM", "English"),
                )
                lang_to = gr.Dropdown(
                    label="译文语言",
                    choices=lang_choices,
                    value=ConfigManager.get("PDF2ZH_LANG_TO", "Simplified Chinese"),
                )
            page_range = gr.Radio(
                choices=page_choices(),
                label="翻译页码",
                value=list(page_map.keys())[0],
            )

            page_input = gr.Textbox(
                label="自定义页码（如 1-3,5）",
                visible=False,
                interactive=True,
            )

            with gr.Accordion("更多高级选项", open=False):
                gr.Markdown("#### 高级选项")
                threads = gr.Textbox(
                    label="并发线程数", interactive=True, value="4"
                )
                skip_subset_fonts = gr.Checkbox(
                    label="跳过字体子集化", interactive=True, value=False
                )
                ignore_cache = gr.Checkbox(
                    label="忽略缓存", interactive=True, value=False
                )
                vfont = gr.Textbox(
                    label="自定义公式字体（正则表达式）",
                    interactive=True,
                    value=ConfigManager.get("PDF2ZH_VFONT", ""),
                )
                prompt = gr.Textbox(
                    label="自定义提示词（大模型）", interactive=True, visible=False
                )
                mode_choice = gr.Dropdown(
                    label="翻译模式",
                    choices=MODE_CHOICES,
                    value="fast",
                    interactive=True,
                )
                envs.append(prompt)

            def on_select_service(service, evt: gr.EventData):
                translator = service_map[service]
                _envs = []
                for i in range(max_envs + 1):
                    _envs.append(gr.update(visible=False, value=""))
                for i, env in enumerate(translator.envs.items()):
                    label = env[0]
                    value = ConfigManager.get_env_by_translatername(
                        translator, env[0], env[1]
                    )
                    visible = True
                    if hidden_gradio_details:
                        if (
                            "MODEL" not in str(label).upper()
                            and value
                            and hidden_gradio_details
                        ):
                            visible = False
                        # Hidden Keys From Gradio
                        if "API_KEY" in label.upper():
                            value = "***"  # We use "***" Present Real API_KEY
                    _envs[i] = gr.update(
                        visible=visible,
                        label=env_label_zh(label),
                        value=value,
                    )
                _envs[-1] = gr.update(visible=translator.CustomPrompt)
                return _envs

            def on_select_filetype(file_type):
                return (
                    gr.update(visible=file_type == "File"),
                    gr.update(visible=file_type == "Link"),
                )

            def on_select_page(choice):
                if choice == "Others":
                    return gr.update(visible=True)
                else:
                    return gr.update(visible=False)

            def on_vfont_change(value):
                ConfigManager.set("PDF2ZH_VFONT", value)
                return value

            output_title = gr.Markdown("## 翻译结果", visible=False)
            output_file_mono = gr.File(
                label="下载译文版（仅译文）", visible=False
            )
            output_file_dual = gr.File(
                label="下载双语对照版", visible=False
            )
            recaptcha_response = gr.Textbox(
                label="人机验证结果", elem_id="verify", visible=False
            )
            recaptcha_box = gr.HTML('<div id="recaptcha-box"></div>')
            translate_btn = gr.Button("开始翻译", variant="primary")
            cancellation_btn = gr.Button("取消", variant="secondary")
            tech_details_tog = gr.Markdown(
                tech_details_string,
                elem_classes=["secondary-text"],
            )
            page_range.select(on_select_page, page_range, page_input)
            service.select(
                on_select_service,
                service,
                envs,
            )
            vfont.change(on_vfont_change, inputs=vfont, outputs=None)
            file_type.select(
                on_select_filetype,
                file_type,
                [file_input, link_input],
                js=(
                    f"""
                    (a,b)=>{{
                        try{{
                            grecaptcha.render('recaptcha-box',{{
                                'sitekey':'{client_key}',
                                'callback':'onVerify'
                            }});
                        }}catch(error){{}}
                        return [a];
                    }}
                    """
                    if flag_demo
                    else ""
                ),
            )

        with gr.Column(scale=2):
            gr.Markdown("## 预览")
            preview = PDF(label="文档预览", visible=True, height=2000)

    # Event handlers
    file_input.upload(
        lambda x: x,
        inputs=file_input,
        outputs=preview,
        js=(
            f"""
            (a,b)=>{{
                try{{
                    grecaptcha.render('recaptcha-box',{{
                        'sitekey':'{client_key}',
                        'callback':'onVerify'
                    }});
                }}catch(error){{}}
                return [a];
            }}
            """
            if flag_demo
            else ""
        ),
    )

    state = gr.State({"session_id": None})

    translate_btn.click(
        translate_file,
        inputs=[
            file_type,
            file_input,
            link_input,
            service,
            lang_from,
            lang_to,
            page_range,
            page_input,
            prompt,
            threads,
            skip_subset_fonts,
            ignore_cache,
            vfont,
            mode_choice,
            recaptcha_response,
            state,
            *envs,
        ],
        outputs=[
            output_file_mono,
            preview,
            output_file_dual,
            output_file_mono,
            output_file_dual,
            output_title,
        ],
    ).then(lambda: None, js="()=>{grecaptcha.reset()}" if flag_demo else "")

    cancellation_btn.click(
        stop_translate_file,
        inputs=[state],
    )


def parse_user_passwd(file_path: str) -> tuple:
    """
    Parse the user name and password from the file.

    Inputs:
        - file_path: The file path to read.
    Outputs:
        - tuple_list: The list of tuples of user name and password.
        - content: The content of the file
    """
    tuple_list = []
    content = ""
    if not file_path:
        return tuple_list, content
    if len(file_path) == 2:
        try:
            with open(file_path[1], "r", encoding="utf-8") as file:
                content = file.read()
        except FileNotFoundError:
            print(f"出错：找不到文件 {file_path[1]}")
    try:
        with open(file_path[0], "r", encoding="utf-8") as file:
            tuple_list = [
                tuple(line.strip().split(",")) for line in file if line.strip()
            ]
    except FileNotFoundError:
        print(f"出错：找不到文件 {file_path[0]}")
    return tuple_list, content


def _has_ipv6() -> bool:
    """Check whether the system can bind an IPv6 socket."""
    try:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.close()
        return True
    except OSError:
        return False


def setup_gui(
    share: bool = False, auth_file: list = ["", ""], server_port=7860
) -> None:
    """
    Setup the GUI with the given parameters.

    Inputs:
        - share: Whether to share the GUI.
        - auth_file: The file path to read the user name and password.

    Outputs:
        - None
    """
    user_list, html = parse_user_passwd(auth_file)

    auth_kwargs = {}
    if len(user_list) > 0:
        auth_kwargs = {"auth": user_list, "auth_message": html}

    if flag_demo:
        demo.launch(
            server_name="0.0.0.0",
            max_file_size="5mb",
            inbrowser=True,
            **launch_style_kwargs,
        )
        return

    # Try binding addresses in order: "::" accepts both IPv4+IPv6 on most
    # dual-stack systems, "0.0.0.0" is IPv4-only, "127.0.0.1" is loopback,
    # and finally fall back to Gradio's share mode.
    bind_addresses = []
    if _has_ipv6():
        bind_addresses.append("[::]")
    bind_addresses.append("0.0.0.0")
    bind_addresses.append("127.0.0.1")

    for addr in bind_addresses:
        try:
            demo.launch(
                server_name=addr,
                debug=True,
                inbrowser=True,
                share=share,
                server_port=server_port,
                **auth_kwargs,
                **launch_style_kwargs,
            )
            return
        except Exception:
            print(
                f"使用 {addr} 启动界面失败。\n"
                "可能是代理软件开启了全局模式，请关闭后重试。"
            )

    # Last resort: let Gradio create a share link
    demo.launch(
        debug=True,
        inbrowser=True,
        share=True,
        server_port=server_port,
        **auth_kwargs,
        **launch_style_kwargs,
    )


# For auto-reloading while developing
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    setup_gui()
