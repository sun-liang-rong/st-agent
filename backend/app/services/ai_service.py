"""AI 服务模块 — 旅游攻略生成"""
import asyncio
import httpx
import json
import os
import uuid
import logging
import time
from typing import Optional, AsyncGenerator
from openai import AsyncOpenAI
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger("app.ai_service")


# ── 重试辅助函数 ──
MAX_RETRIES = 3
RETRY_DELAYS = [1, 2, 4]  # seconds

def _is_retryable_error(e: Exception) -> bool:
    """判断错误是否可重试（服务端超时/过载/无响应）"""
    if isinstance(e, httpx.HTTPStatusError):
        # 5xx 服务端错误 或 429 限流 → 可重试
        return e.response.status_code in (429,) or e.response.status_code >= 500
    if isinstance(e, (httpx.TimeoutException, httpx.ConnectError,
                      httpx.RemoteProtocolError, httpx.StreamError,
                      httpx.ReadTimeout, httpx.WriteTimeout)):
        return True
    return False


class AIService:
    """AI 服务类 — 旅游攻略 + 图片生成"""

    def __init__(self):
        self.api_key = settings.SENSENOVA_API_KEY
        self.api_base = settings.SENSENOVA_API_BASE
        self.prompt_model = settings.SENSENOVA_PROMPT_MODEL
        self.u1_model = settings.SENSENOVA_U1_MODEL
        self.u1_api_base = settings.SENSENOVA_U1_API_BASE
        logger.info(
            "✅ AI 服务初始化 | prompt_model=%s u1_model=%s api_base=%s",
            self.prompt_model, self.u1_model, self.api_base,
        )

    async def generate_travel_itinerary_stream(
        self,
        destination: str,
        days: int = 3,
        preferences: str = "",
    ):
        """
        根据目的地和偏好流式生成旅游攻略 Markdown 文本
        异步生成器，逐个 yield 文本 token
        """
        system_prompt = """你是一个专业的旅游规划专家。根据用户的目的地信息，自动解析天数、偏好，生成一份详细、实用的旅游攻略。

## 解析规则
- 从用户的输入中自动提取天数（如"三日"、"3天"、"一日游"、"两天"等关键词）
- 从用户的输入中自动提取偏好（如"美食"、"亲子"、"情侣"、"穷游"等关键词）
- 如果用户输入中没有明确天数，默认按 3 天规划
- 行程天数要合理，一日游即 1 天，三日游即 3 天

## 输出要求
- 使用 Markdown 格式
- 结构清晰，包含以下板块（按顺序）：
  1. **行程概览** — 一句话总结这趟旅行
  2. **每日详细行程** — 每天分上午/下午/晚上，含景点名称、推荐理由、预估时间
  3. **美食推荐** — 当地必吃特色美食 + 推荐餐厅
  4. **住宿建议** — 推荐区域 + 价位参考
  5. **预算估算** — 交通+住宿+餐饮+门票 的预估总花费
  6. **出行小贴士** — 最佳季节、交通方式、注意事项

## 格式规范
- 用 `##` 和 `###` 标题层级
- 用 `-` 列表展示每日行程
- 景点名称用 **加粗** 标出
- 保持实用、具体，不要泛泛而谈
- 如果用户有特殊偏好（如情侣游、亲子游、穷游等），行程要贴合偏好
- 每日行程安排要合理，考虑地理位置的邻近性"""

        if days and days > 0:
            user_message = f"目的地: {destination}\n天数: {days}天\n偏好: {preferences if preferences else '无特殊偏好'}"
        else:
            # 让 AI 从 destination 文本中自行解析天数和偏好
            user_message = f"请为「{destination}」规划旅行攻略"
        data = {
            "model": self.prompt_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.7,
            "max_tokens": 4000,
            "stream": True,
        }

        url = f"{self.api_base}/chat/completions"
        start_time = time.time()
        token_count = 0

        # ── 重试循环：最多 MAX_RETRIES 次 ──
        for attempt in range(1, MAX_RETRIES + 1):
            logger.info(
                "📤 [攻略生成] 开始请求 (attempt %d/%d) | destination=%s days=%d preferences=%s model=%s",
                attempt, MAX_RETRIES, destination, days, preferences or "无", self.prompt_model,
            )
            logger.debug(
                "📦 [攻略生成] 请求参数 | messages=%s temperature=0.7 max_tokens=4000 stream=True",
                json.dumps(data["messages"], ensure_ascii=False),
            )

            try:
                async with httpx.AsyncClient(timeout=120.0, mounts={"all://": httpx.AsyncHTTPTransport()}) as client:
                    async with client.stream(
                        "POST",
                        url,
                        headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                        json=data,
                    ) as response:
                        logger.info(
                            "📡 [攻略生成] 连接建立 (attempt %d/%d) | status=%s",
                            attempt, MAX_RETRIES, response.status_code,
                        )
                        response.raise_for_status()
                        async for line in response.aiter_lines():
                            if not line.startswith("data: "):
                                continue
                            json_str = line[6:].strip()
                            if json_str == "[DONE]":
                                break
                            try:
                                chunk = json.loads(json_str)
                                choices = chunk.get("choices", [])
                                if not choices:
                                    # choices 为空数组时跳过（如 finish_reason 信号）
                                    continue
                                delta = choices[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    token_count += 1
                                    yield content
                            except json.JSONDecodeError:
                                continue

                # 正常完成
                elapsed = time.time() - start_time
                logger.info(
                    "✅ [攻略生成] 流式完成 (attempt %d/%d) | destination=%s tokens=%d elapsed=%.2fs",
                    attempt, MAX_RETRIES, destination, token_count, elapsed,
                )
                return  # 成功退出

            except Exception as e:
                elapsed = time.time() - start_time
                retryable = _is_retryable_error(e) and token_count == 0
                # token_count > 0 说明已输出过内容，重试会导致内容重复，不重试

                if retryable and attempt < MAX_RETRIES:
                    delay = RETRY_DELAYS[attempt - 1]
                    logger.warning(
                        "⚠️ [攻略生成] 第%d次失败, %ds后重试 (attempt %d/%d) | error=%s elapsed=%.2fs",
                        attempt, delay, attempt, MAX_RETRIES, str(e), elapsed,
                    )
                    await asyncio.sleep(delay)
                else:
                    reason = "已输出部分内容" if token_count > 0 else "不可重试错误"
                    logger.error(
                        "❌ [攻略生成] %s | destination=%s attempt=%d/%d error=%s elapsed=%.2fs",
                        reason, destination, attempt, MAX_RETRIES, str(e), elapsed,
                    )
                    raise  # 让调用者处理

    async def generate_travel_image(
        self,
        destination: str,
        preferences: str = "",
        itinerary: str = "",
    ) -> Optional[str]:
        """
        根据目的地和攻略内容生成旅游海报图片
        返回图片本地路径，失败返回 None
        """
        # 取攻略前 1200 字作为图片生成的上下文参考
        itinerary_snippet = itinerary[:1200] if itinerary else ""
        prompt = f"""A vintage 1930s Republican-era Chinese newspaper travel page for {destination}.

# Newspaper Style & Texture (CRITICAL)
- Style: Authentic 1930s Republican-era Chinese newspaper front page
- Paper: Aged kraft paper texture, deep yellowed patina, foxing stains, worn and frayed edges, subtle creases and tear marks
- Printing: Traditional letterpress printing effect, slight ink bleed, uneven ink density, retro black ink on aged paper
- Color Palette: Monochromatic sepia/ochre base, faded vermillion red for borders, muted ink black, no bright colors

# Layout & Composition (solve clutter)
- Layout: Classic newspaper masthead at the top with large bold headline for the destination
- Columns: 2-3 vertical text columns, clearly separated by thin vintage dividers
- Decorative elements: Ornate corner filigree, woodcut-style border patterns, small ornamental flourishes
- Sections: Clear visual blocks for each day of itinerary with subtle header lines

# Illustration Style (separate from text areas)
- Illustrations: Small, delicate Chinese ink wash (水墨) sketches embedded in each itinerary section
- Style: Minimalist line art, faded sepia tone, matches the aged paper aesthetic
- Placement: Illustrations are small, placed in margins or at top/bottom of columns, not overlapping text blocks

# CRITICAL CONTROL INSTRUCTIONS (avoid garbled text)
- Text: Use decorative, period-appropriate Chinese typography that looks like newspaper print
- DO NOT render the full itinerary text as readable content; use stylized text blocks to mimic newspaper layout
- NO modern fonts, NO clean sans-serif, NO digital gradients, NO neon colors
- Maintain a nostalgic, historical, time-worn atmosphere throughout the entire design"""

        start_time = time.time()

        # ── 使用 OpenAI SDK 调用（与文档示例一致） ──
        client = AsyncOpenAI(
            base_url="https://token.sensenova.cn/v1",
            api_key=self.api_key,
        )

        for attempt in range(1, MAX_RETRIES + 1):
            logger.info(
                "📤 [图片生成] 开始请求 (attempt %d/%d) | destination=%s preferences=%s model=%s",
                attempt, MAX_RETRIES, destination, preferences or "无", self.u1_model,
            )
            logger.debug(
                "📦 [图片生成] 请求参数 (attempt %d/%d) | prompt=%s size=1344x3136 n=1",
                attempt, MAX_RETRIES, prompt,
            )

            try:
                resp = await client.images.generate(
                    model=self.u1_model,
                    prompt=prompt,
                    n=1,
                    size="1344x3136",
                )

                elapsed = time.time() - start_time
                image_url = resp.data[0].url if resp.data else None

                logger.info(
                    "📡 [图片生成] 响应收到 (attempt %d/%d) | has_url=%s elapsed=%.2fs",
                    attempt, MAX_RETRIES, bool(image_url), elapsed,
                )

                if not image_url:
                    logger.warning("⚠️ [图片生成] 未返回图片URL (attempt %d/%d)", attempt, MAX_RETRIES)
                    return None

                # 下载图片到本地
                cover_id = str(uuid.uuid4())
                cover_dir = "generated"
                os.makedirs(cover_dir, exist_ok=True)
                cover_path = os.path.join(cover_dir, f"{cover_id}.png")

                download_start = time.time()
                async with httpx.AsyncClient(timeout=60.0) as dl_client:
                    img_response = await dl_client.get(image_url)
                    img_response.raise_for_status()
                    with open(cover_path, "wb") as f:
                        f.write(img_response.content)

                download_elapsed = time.time() - download_start
                total_elapsed = time.time() - start_time
                logger.info(
                    "✅ [图片生成] 下载完成 (attempt %d/%d) | path=%s size=%d bytes download_time=%.2fs total_time=%.2fs",
                    attempt, MAX_RETRIES, cover_path, len(img_response.content),
                    download_elapsed, total_elapsed,
                )
                return cover_path

            except Exception as e:
                elapsed = time.time() - start_time
                retryable = _is_retryable_error(e)

                if retryable and attempt < MAX_RETRIES:
                    delay = RETRY_DELAYS[attempt - 1]
                    logger.warning(
                        "⚠️ [图片生成] 第%d次失败, %ds后重试 (attempt %d/%d) | error=%s elapsed=%.2fs",
                        attempt, delay, attempt, MAX_RETRIES, str(e), elapsed,
                    )
                    await asyncio.sleep(delay)
                else:
                    reason = "不可重试错误" if not retryable else "全部重试耗尽"
                    logger.error(
                        "❌ [图片生成] %s | destination=%s attempt=%d/%d error=%s elapsed=%.2fs",
                        reason, destination, attempt, MAX_RETRIES, str(e), elapsed,
                    )
                    if attempt == MAX_RETRIES:
                        logger.debug("堆栈跟踪", exc_info=True)
                    return None


aiservice = AIService()
