"""
generate_report.py
Llama a la API de Anthropic con el MCP de ClickUp conectado,
genera el reporte HTML actualizado y lo guarda en index.html
"""

import anthropic
import os

# ── Configuración ──────────────────────────────────────────────────────────────

PROMPT = "actualiza el reporte interactivo plan maestro Movilnet a la fecha de hoy"

OUTPUT_FILE = "index.html"

MCP_SERVERS = [
    {
        "type": "url",
        "url": "https://mcp.clickup.com/mcp",
        "name": "clickup",
        "authorization_token": os.environ["CLICKUP_API_TOKEN"],
    }
]

# ── Llamada a la API ───────────────────────────────────────────────────────────

def generate_report():
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print("Consultando ClickUp y generando reporte...")

    response = client.beta.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8096,
        mcp_servers=MCP_SERVERS,
        messages=[
            {
                "role": "user",
                "content": PROMPT,
            }
        ],
        betas=["mcp-client-2025-04-04"],
    )

    # Extraer el HTML de la respuesta
    html_content = None
    for block in response.content:
        if block.type == "text":
            html_content = block.text
            break

    if not html_content:
        raise ValueError("La respuesta no contiene texto. Revisa la conexión con ClickUp.")

    # Si Claude devuelve el HTML envuelto en ```html ... ```, lo limpiamos
    if "```html" in html_content:
        html_content = html_content.split("```html")[1].split("```")[0].strip()
    elif "```" in html_content:
        html_content = html_content.split("```")[1].split("```")[0].strip()

    # Guardar el archivo
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✓ Reporte guardado en {OUTPUT_FILE}")
    print(f"  Tokens usados: {response.usage.input_tokens} entrada / {response.usage.output_tokens} salida")


if __name__ == "__main__":
    generate_report()
