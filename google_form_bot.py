"""
Бот для форми: ДОСЛІДЖЕННЯ ВЗАЄМОЗВ'ЯЗКУ НАРЦИСИЗМУ ТА ЛІДЕРСЬКОГО ПОТЕНЦІАЛУ
Запуск: python google_form_bot.py
"""

import asyncio
import random
import sys
from playwright.async_api import async_playwright

# =============================================
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfFV_A3Imf0x1yuM93hwPhU7lGJLXXUG-tGuLZym4efA4ubDg/viewform"

# Скільки відповідей від кожної групи:
COUNT_STUDENT = 0   # Студенти: 18-22, неповна вища
COUNT_YOUTH   = 0   # Молодь: 22-25, освіта рандом
COUNT_WORKER  = 1   # Волонтери: 25-31, повна вища

# Пауза між відправками (хвилини):
DELAY_MIN_MINUTES = 8
DELAY_MAX_MINUTES = 15

# Порядок статі (рівно 15 значень):
# 0 = Чоловіча, 1 = Жіноча, 2 = Бажаю не вказувати
GENDER_ORDER = [0]
# =============================================

EDUCATIONS_RANDOM = ["Неповна вища", "Повна вища", "Бакалавр", "Магістр"]


def generate_personas():
    student_ages = random.sample(range(18, 23), min(COUNT_STUDENT, 5))
    while len(student_ages) < COUNT_STUDENT:
        age = random.randint(18, 22)
        if age != student_ages[-1]:
            student_ages.append(age)

    youth_ages = []
    while len(youth_ages) < COUNT_YOUTH:
        age = random.randint(22, 25)
        if not youth_ages or age != youth_ages[-1]:
            youth_ages.append(age)

    worker_ages = random.sample(range(25, 32), min(COUNT_WORKER, 7))
    while len(worker_ages) < COUNT_WORKER:
        age = random.randint(25, 31)
        if age != worker_ages[-1]:
            worker_ages.append(age)

    personas = (
        [{"age": student_ages[i], "education": "Неповна вища", "management": ["Ні", "Ні", "Так"]} for i in range(COUNT_STUDENT)] +
        [{"age": youth_ages[i],   "education": None,            "management": ["Так", "Ні"]}       for i in range(COUNT_YOUTH)] +
        [{"age": worker_ages[i],  "education": "Повна вища",   "management": ["Так", "Так", "Ні"]} for i in range(COUNT_WORKER)]
    )

    # Перемішуємо але стежимо щоб однакові віки не йшли підряд
    random.shuffle(personas)
    result = []
    for p in personas:
        if result and result[-1]["age"] == p["age"]:
            insert_pos = max(0, len(result) - 2)
            result.insert(insert_pos, p)
        else:
            result.append(p)

    # Додаємо стать з фіксованого списку
    gender_names = ["Чоловіча", "Жіноча", "Бажаю не вказувати"]
    for i, p in enumerate(result):
        p["gender"] = GENDER_ORDER[i] if i < len(GENDER_ORDER) else random.randint(0, 1)

    return result


async def countdown(seconds):
    for remaining in range(seconds, 0, -1):
        mins = remaining // 60
        secs = remaining % 60
        sys.stdout.write(f"\r  ⏳ Наступна форма через: {mins:02d}:{secs:02d}  ")
        sys.stdout.flush()
        await asyncio.sleep(1)
    sys.stdout.write("\r  ✅ Починаємо наступну форму!              \n")
    sys.stdout.flush()


async def scroll_to_bottom(page):
    await page.evaluate("""
        async () => {
            await new Promise(resolve => {
                let total = 0;
                const timer = setInterval(() => {
                    window.scrollBy(0, 400);
                    total += 400;
                    if (total >= document.body.scrollHeight) {
                        clearInterval(timer);
                        window.scrollTo(0, 0);
                        resolve();
                    }
                }, 80);
            });
        }
    """)
    await page.wait_for_timeout(400)


async def click_next(page):
    await page.wait_for_timeout(300)
    for label in ["Далі", "Next"]:
        try:
            btn = page.locator(f'div[role="button"]:has-text("{label}")').first
            if await btn.count() > 0:
                await btn.click(timeout=5000)
                await page.wait_for_timeout(1500)
                print(f"    ➡️  Натиснуто: {label}")
                return
        except:
            pass
    print("    ⚠️  Кнопка Далі не знайдена!")


async def click_submit(page):
    await page.wait_for_timeout(500)
    try:
        btn = page.locator('div[role="button"]:has-text("Надіслати")').first
        await btn.click(timeout=10000)
        await page.wait_for_timeout(4000)
        print("    📨 Форму надіслано!")
        return True
    except:
        url = page.url
        if "formResponse" in url or "closedform" in url:
            print("    📨 Форму надіслано (підтверджено)!")
            return True
        print("    ⚠️  Не вдалося надіслати")
        return False


async def fill_all_radios_random(page, label=""):
    print(f"  📄 {label}")
    await scroll_to_bottom(page)
    groups = page.locator('[role="radiogroup"]')
    count = await groups.count()
    print(f"    🔘 Груп запитань: {count}")
    for i in range(count):
        group = groups.nth(i)
        try:
            await group.scroll_into_view_if_needed()
        except:
            pass
        await page.wait_for_timeout(50)
        options = group.locator('[role="radio"]')
        opt_count = await options.count()
        if opt_count > 0:
            chosen = random.randint(0, opt_count - 1)
            try:
                await options.nth(chosen).click(timeout=3000)
            except:
                pass


async def page_2_demographics(page, persona):
    print("  📄 Сторінка 2 — Демографія")
    await scroll_to_bottom(page)

    # Вік
    age = persona["age"]
    try:
        inp = page.locator('input[type="text"], input[type="number"]').first
        await inp.fill(str(age), timeout=5000)
        print(f"    ✏️  Вік: {age}")
    except Exception as e:
        print(f"    ⚠️  Вік помилка: {e}")

    # Стать + Управлінський досвід
    gender_names = ["Чоловіча", "Жіноча", "Бажаю не вказувати"]
    groups = page.locator('[role="radiogroup"]')
    count = await groups.count()
    for i in range(count):
        group = groups.nth(i)
        await group.scroll_into_view_if_needed()
        options = group.locator('[role="radio"]')
        opt_count = await options.count()
        if opt_count > 0:
            if i == 0:
                # Стать — з фіксованого списку
                chosen = persona["gender"]
                print(f"    👤 Стать: {gender_names[chosen]}")
            else:
                # Управлінський досвід
                mgmt_choice = random.choice(persona["management"])
                chosen = 0 if mgmt_choice == "Так" else 1
                print(f"    💼 Управлінський досвід: {mgmt_choice}")
            try:
                await options.nth(chosen).click(timeout=3000)
                await page.wait_for_timeout(100)
            except:
                pass

    # Освіта — останнє текстове поле
    edu = persona["education"] if persona["education"] else random.choice(EDUCATIONS_RANDOM)
    try:
        all_inputs = page.locator('input[type="text"]')
        inp_count = await all_inputs.count()
        await all_inputs.nth(inp_count - 1).fill(edu, timeout=3000)
        print(f"    ✏️  Освіта: {edu}")
    except Exception as e:
        print(f"    ⚠️  Освіта помилка: {e}")


async def run_bot():
    personas = generate_personas()
    total = len(personas)

    gender_names = ["Чоловіча", "Жіноча", "Бажаю не вказувати"]
    print(f"🎯 Всього форм: {total}")
    print(f"⏱️  Пауза між формами: {DELAY_MIN_MINUTES}-{DELAY_MAX_MINUTES} хв")
    total_min = total * (DELAY_MIN_MINUTES + 3)
    total_max = total * (DELAY_MAX_MINUTES + 4)
    print(f"🕐 Орієнтовний час: {total_min//60}г {total_min%60}хв — {total_max//60}г {total_max%60}хв")
    print(f"\n📋 Розподіл віків:  {[p['age'] for p in personas]}")
    print(f"👤 Розподіл статі: {[gender_names[p['gender']] for p in personas]}\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        page.set_default_timeout(10000)

        success = 0

        for attempt, persona in enumerate(personas, start=1):
            print(f"\n{'='*50}")
            print(f"🚀 Форма {attempt}/{total} | Вік: {persona['age']} | Стать: {gender_names[persona['gender']]} | Освіта: {persona['education'] or 'рандом'}")
            print(f"{'='*50}")

            try:
                await page.goto(FORM_URL, wait_until="networkidle")
                await page.wait_for_timeout(1500)

                print("  📄 Сторінка 1 — Вступ")
                await click_next(page)

                await page_2_demographics(page, persona)
                await click_next(page)

                await fill_all_radios_random(page, "Сторінка 3 — NPI-16 (16 питань)")
                await click_next(page)

                await fill_all_radios_random(page, "Сторінка 4 — Розенберг (10 питань)")
                await click_next(page)

                await fill_all_radios_random(page, "Сторінка 5 — КОС-2 (40 питань)")
                await click_next(page)

                print("  📄 Сторінка 6 — Вступ Лідер")
                await click_next(page)

                await fill_all_radios_random(page, "Сторінка 7 — Я-Лідер (48 питань)")
                await click_next(page)

                print("  📄 Сторінка 8 — Надіслати")
                ok = await click_submit(page)

                if ok:
                    success += 1
                    print(f"  🎉 Успішно! Надіслано: {success}/{total}")
                else:
                    print(f"  ❌ Помилка відправки")

            except Exception as e:
                print(f"  ❌ Критична помилка: {e}")

            if attempt < total:
                delay_seconds = random.randint(
                    DELAY_MIN_MINUTES * 60,
                    DELAY_MAX_MINUTES * 60
                )
                mins = delay_seconds // 60
                secs = delay_seconds % 60
                print(f"\n  🎲 Рандомна пауза: {mins} хв {secs} сек")
                await countdown(delay_seconds)

        await browser.close()
        print(f"\n{'='*50}")
        print(f"✅ Все готово! Успішно надіслано: {success}/{total}")
        print(f"{'='*50}")


if __name__ == "__main__":
    asyncio.run(run_bot())