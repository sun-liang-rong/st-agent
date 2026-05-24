"""攻略导出服务"""
import logging
import os
import tempfile
from typing import Optional

logger = logging.getLogger("app.export_service")


def export_to_pdf(content: str, output_path: str, title: str = "旅游攻略") -> bool:
    """将 Markdown 攻略内容导出为 PDF"""
    try:
        from weasyprint import HTML

        html_content = _markdown_to_html(content, title)
        HTML(string=html_content).write_pdf(output_path)
        logger.info("✅ PDF 导出成功 | path=%s", output_path)
        return True
    except ImportError:
        logger.warning("⚠️ weasyprint 未安装，尝试使用 reportlab")
        return _export_pdf_reportlab(content, output_path, title)
    except Exception as e:
        logger.error("❌ PDF 导出失败: %s", e)
        return False


def _export_pdf_reportlab(content: str, output_path: str, title: str = "旅游攻略") -> bool:
    """使用 reportlab 生成简单 PDF（降级方案）"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.units import cm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()

        # 尝试注册中文字体
        try:
            font_path = "/System/Library/Fonts/PingFang.ttc"
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('PingFang', font_path))
                cn_style = ParagraphStyle('Chinese', parent=styles['Normal'], fontName='PingFang', fontSize=11, leading=16)
            else:
                cn_style = styles['Normal']
        except Exception:
            cn_style = styles['Normal']

        title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=22, leading=28, spaceAfter=20)

        elements = []
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 0.5 * cm))

        for line in content.split("\n"):
            line = line.strip()
            if not line:
                elements.append(Spacer(1, 0.3 * cm))
                continue
            # Strip markdown bold markers for plain text
            clean = line.replace("**", "").replace("##", "").replace("###", "").strip()
            if line.startswith("###"):
                elements.append(Paragraph(clean, ParagraphStyle('H3', parent=cn_style, fontSize=14, leading=18, spaceBefore=10)))
            elif line.startswith("##"):
                elements.append(Paragraph(clean, ParagraphStyle('H2', parent=cn_style, fontSize=16, leading=20, spaceBefore=14)))
            elif line.startswith("- "):
                elements.append(Paragraph(f"  {clean}", cn_style))
            else:
                elements.append(Paragraph(clean, cn_style))

        doc.build(elements)
        logger.info("✅ PDF (reportlab) 导出成功 | path=%s", output_path)
        return True
    except Exception as e:
        logger.error("❌ reportlab PDF 导出失败: %s", e)
        return False


def _markdown_to_html(content: str, title: str = "旅游攻略") -> str:
    """将 Markdown 内容转换为带样式的 HTML"""
    import re

    # Simple markdown to HTML conversion
    html_lines = []
    for line in content.split("\n"):
        line = line.rstrip()
        if line.startswith("### "):
            html_lines.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("# "):
            html_lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("- "):
            item = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line[2:])
            html_lines.append(f"<li>{item}</li>")
        elif line.strip() == "":
            html_lines.append("<br/>")
        else:
            line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
            html_lines.append(f"<p>{line}</p>")

    body = "\n".join(html_lines)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<style>
  @page {{
    size: A4;
    margin: 2cm;
  }}
  body {{
    font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
    font-size: 12pt;
    line-height: 1.6;
    color: #333;
  }}
  h1 {{
    text-align: center;
    color: #d97706;
    font-size: 24pt;
    border-bottom: 3px solid #f59e0b;
    padding-bottom: 10px;
    margin-bottom: 20px;
  }}
  h2 {{
    color: #92400e;
    font-size: 16pt;
    margin-top: 24px;
    border-left: 4px solid #f59e0b;
    padding-left: 10px;
  }}
  h3 {{
    color: #b45309;
    font-size: 13pt;
    margin-top: 16px;
  }}
  li {{
    margin-left: 20px;
    margin-bottom: 4px;
  }}
  .header {{
    background: linear-gradient(135deg, #f59e0b, #ef4444);
    color: white;
    padding: 30px;
    text-align: center;
    border-radius: 0 0 20px 20px;
    margin: -2cm -2cm 20px -2cm;
  }}
  .header h1 {{
    color: white;
    border: none;
    font-size: 28pt;
  }}
  .header p {{
    color: rgba(255,255,255,0.85);
    font-size: 11pt;
  }}
  .watermark {{
    text-align: center;
    color: #d97706;
    font-size: 9pt;
    margin-top: 40px;
    border-top: 1px solid #fde68a;
    padding-top: 10px;
  }}
</style>
</head>
<body>
<div class="header">
  <h1>{title}</h1>
  <p>由 ST-Agent AI 智能生成</p>
</div>
{body}
<div class="watermark">
  ST-Agent | AI 旅游攻略与图片生成平台
</div>
</body>
</html>"""


def export_to_image(content: str, output_path: str, title: str = "旅游攻略") -> bool:
    """将攻略内容导出为图片"""
    try:
        # 使用 weasyprint 先生成 PDF，再转图片
        # 降级方案：直接生成带 HTML 的长图
        html_content = _markdown_to_html(content, title)
        temp_html = output_path.replace(".png", ".html")
        with open(temp_html, "w", encoding="utf-8") as f:
            f.write(html_content)

        try:
            from weasyprint import HTML
            temp_pdf = output_path.replace(".png", ".pdf")
            HTML(string=html_content).write_pdf(temp_pdf)

            # 尝试用 pdf2image 转图片
            try:
                from pdf2image import convert_from_path
                images = convert_from_path(temp_pdf, dpi=150)
                if images:
                    images[0].save(output_path, "PNG")
                    os.remove(temp_pdf)
                    os.remove(temp_html)
                    logger.info("✅ 图片导出成功 | path=%s", output_path)
                    return True
            except ImportError:
                pass

            # pdf2image 不可用时，返回 PDF
            os.remove(temp_html)
            if os.path.exists(temp_pdf):
                # Rename PDF as the output
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(temp_pdf, output_path.replace(".png", ".pdf"))
                logger.info("✅ 降级为 PDF 导出 | path=%s", output_path.replace(".png", ".pdf"))
                return True

        except ImportError:
            pass

        # 最后降级：生成简单文本图片
        return _export_simple_image(content, output_path, title)

    except Exception as e:
        logger.error("❌ 图片导出失败: %s", e)
        return False


def _export_simple_image(content: str, output_path: str, title: str = "旅游攻略") -> bool:
    """最简单的文本图片导出（降级方案）"""
    try:
        from PIL import Image, ImageDraw, ImageFont

        width = 800
        font_size = 16
        line_height = 24
        margin = 40

        lines = content.split("\n")
        total_lines = len(lines) + 5
        height = total_lines * line_height + margin * 2

        img = Image.new("RGB", (width, max(height, 400)), "white")
        draw = ImageDraw.Draw(img)

        # 渐变标题栏
        for y in range(60):
            r = int(245 - (245 - 239) * y / 60)
            g = int(158 - (158 - 68) * y / 60)
            b = int(11 - (11 - 4) * y / 60)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # 尝试加载中文字体
        try:
            font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", font_size)
            title_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 24)
        except Exception:
            font = ImageFont.load_default()
            title_font = font

        draw.text((margin, 15), title, fill="white", font=title_font)

        y_offset = 80
        for line in lines:
            clean = line.replace("**", "").replace("##", "").replace("###", "").strip()
            if clean:
                draw.text((margin, y_offset), clean, fill="#333333", font=font)
            y_offset += line_height

        img.save(output_path, "PNG")
        logger.info("✅ 简单图片导出成功 | path=%s", output_path)
        return True
    except Exception as e:
        logger.error("❌ 简单图片导出失败: %s", e)
        return False