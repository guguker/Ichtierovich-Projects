last_genie_expression = None
import os
import random
import pygame
from openai import OpenAI
from dotenv import load_dotenv

# нейронка init
load_dotenv()  # .env
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)
model_name = "openai/gpt-3.5-turbo"
# "google/gemini-2.0-flash-exp:free"
# "deepseek/deepseek-r1-0528-qwen3-8b:free"
# "deepseek/deepseek-r1-0528:free"
# "tngtech/deepseek-r1t-chimera:free"
# "mistralai/devstral-small:free"

# пайгейм init
pygame.init()
WIDTH, HEIGHT = 700, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Игра Акинатор")

# grафика
background = pygame.image.load("background.jpg")
genie_images = {
    "neutral": pygame.image.load("genie.png"),
    "happy": pygame.image.load("genie_happy.png"),
    "nervous": pygame.image.load("genie_nervous.png"),
    "thinker": pygame.image.load("genie_thinker.png")
}
current_genie = genie_images["neutral"]

# кнопка конца координата
end_button_y = 350

# кнопки для ответов данные
button_width = 120
button_height = 50
button_spacing = 20
total_width = 5 * button_width + 4 * button_spacing
start_x = (WIDTH - total_width) // 2
button_y = 250

button_yes = pygame.Rect(start_x + 0 * (button_width + button_spacing), button_y, button_width, button_height)
button_no = pygame.Rect(start_x + 1 * (button_width + button_spacing), button_y, button_width, button_height)
button_unknown = pygame.Rect(start_x + 2 * (button_width + button_spacing), button_y, button_width, button_height)
button_maybe_yes = pygame.Rect(start_x + 3 * (button_width + button_spacing), button_y, button_width, button_height)
button_maybe_no = pygame.Rect(start_x + 4 * (button_width + button_spacing), button_y, button_width, button_height)

# шрифт
font = pygame.font.Font(None, 28)

def draw_question_box(text, font, pos, max_width=660, padding=10, bg_color=(255,255,255), alpha=200):
    """
    функция, что редачит текст от нейронки в приемлемый вид, создавая фон, границу и ограничивая размеры.
    """
    words = text.replace('\n', ' \n ').split()
    lines = []
    current_line = ""
    
    for word in words:
        if word == "\n":
            lines.append(current_line)
            current_line = ""
            continue
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width - 2 * padding:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    # высота
    line_height = font.get_height()
    box_height = len(lines) * line_height + 2 * padding
    box_width = max_width

    # полупрозрачный фон
    box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
    box_surface.set_alpha(alpha)
    box_surface.fill(bg_color)
    screen.blit(box_surface, pos)
    pygame.draw.rect(screen, (0, 0, 0), (*pos, box_width, box_height), 2)

    # ввод текста в окошко
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, (0, 0, 0))
        screen.blit(text_surface, (pos[0] + padding, pos[1] + padding + i * line_height))

def draw_text(text, x, y, color=(0,0,0)):
    """ выводит строку text в координатах (x,y). """
    lines = text.split('\n')
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        screen.blit(text_surface, (x, y + i*30))

def draw_button_text(text, rect):
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

# что мы передаем гпт
messages = [
    {
        "role": "system",
        "content": (
            "Ты — Акинатор. Игрок загадал персонажа (реального или вымышленного). "
            "Твоя задача — угадать его, задавая короткие уточняющие вопросы, на которые можно ответить: "
            "Да, Нет, Не знаю, Скорее да, Скорее нет. "
            "После 10 вопросов сделай предположение, сказав фразу вида: 'Я думаю, ты загадал: ...'. "
            "Не объясняй, что ты делаешь. Не пиши вступлений. Просто задавай вопросы."
            "❗Важно: не рассуждай, не объясняй, не используй список персонажей.\n"
            "Никаких описаний типа 'возможно это'. Только один конкретный вопрос."
        )
    },
    {
        "role": "assistant",
        "content": (
            "Привет! Мы начинаем игру в Акинатора 🎩\n"
            "Я задам тебе вопросы, а ты отвечай: Да, Нет, Не знаю, Скорее да, Скорее нет.\n"
            "Нажми любую кнопку, и начнём!"
        )
    }
]

# 1 вопрос
short_messages = messages[:1] + messages[-11:]  # максимум 6 раундов (assistant-user)
resp = client.chat.completions.create(
    model=model_name,
    messages=short_messages,
    max_tokens=500
)
question = resp.choices[0].message.content
messages.append({"role": "assistant", "content": question})

show_end_button = False
end_button = pygame.Rect(WIDTH // 2 - 75, end_button_y, 150, 50)
pressed_button = None

running = True
while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # клики мыши
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            user_answer = None
            if button_yes.collidepoint(mouse_pos):
                user_answer = "Да"
            elif button_no.collidepoint(mouse_pos):
                user_answer = "Нет"
            elif button_unknown.collidepoint(mouse_pos):
                user_answer = "Не знаю"
            elif button_maybe_yes.collidepoint(mouse_pos):
                user_answer = "Скорее да"
            elif button_maybe_no.collidepoint(mouse_pos):
                user_answer = "Скорее нет"

            if user_answer:
                pressed_button = user_answer
                # отправляем наш ответ в гпт
                messages.append({"role": "user", "content": user_answer})
                # если вопросов было меньше 10, запрашиваем следующий вопрос
                if len(messages) < 2*10:  # 1 system + 10*(assistant+user) ≈ 21
                    short_messages = messages[:1] + messages[-11:]  # максимум 6 раундов (assistant-user)
                    resp = client.chat.completions.create(
                        model=model_name,
                        messages=short_messages,
                        max_tokens=600
                    )
                    question = resp.choices[0].message.content
                    messages.append({"role": "assistant", "content": question})
                    new_expression = random.choice(["neutral", "happy", "nervous", "thinker"])
                    while new_expression == last_genie_expression:
                        new_expression = random.choice(["neutral", "happy", "nervous", "thinker"])
                    current_genie = genie_images[new_expression]
                    last_genie_expression = new_expression
                    pressed_button = None
                else:
                    # после 10 вопросов просим GPT сделать предположение
                    messages.append({"role": "user", "content": "Сделай догадку на основе предыдущих вопросов."})
                    short_messages = messages[:1] + messages[-11:]  # максимум 6 раундов (assistant-user)
                    resp = client.chat.completions.create(
                        model=model_name,
                        messages=short_messages,
                        max_tokens=600
                    )
                    guess = resp.choices[0].message.content
                    question = f"Я думаю, это: {guess}"
                    current_genie = genie_images["happy"]  # джинн доволен отгадкой
                    show_end_button = True

            if show_end_button and end_button.collidepoint(mouse_pos):
                running = False

    # рисуем фон и джинна
    screen.blit(background, (0, 0))
    scaled_genie = pygame.transform.scale(current_genie, (420, 620))  # ширина, высота
    screen.blit(scaled_genie, (240, 400))

    # рисуем текущий вопрос на экране
    draw_question_box(question, font, (20, 50), max_width=660)

    # рисуем кнопки ответов
    for rect, label in zip(
        [button_yes, button_no, button_unknown, button_maybe_yes, button_maybe_no],
        ["Да", "Нет", "Не знаю", "Скорее да", "Скорее нет"]
    ):
        color = (60, 130, 190) if pressed_button == label else (80, 160, 220)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)
        draw_button_text(label, rect)

    if show_end_button:
        pygame.draw.rect(screen, (200, 80, 80), end_button)
        pygame.draw.rect(screen, (0, 0, 0), end_button, 2)
        draw_button_text("Конец", end_button)

    pygame.display.flip()

pygame.quit()