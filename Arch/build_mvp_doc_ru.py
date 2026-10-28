from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

from docx.enum.table import WD_ROW_HEIGHT_RULE, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_mvp_doc import (  # noqa: E402
    Builder, PAGE_W, INK, MUTED, SUBTLE, LINE, SOFT, BLUE, BLUE_SOFT,
    TEAL, TEAL_SOFT, AMBER, AMBER_SOFT, ROSE, ROSE_SOFT, GREEN, GREEN_SOFT,
    NAVY, WHITE, BODY_FONT, rgb, set_paragraph_bottom_border, add_field,
)

ROOT = Path(__file__).resolve().parent


class RuBuilder(Builder):
    def _setup_header_footer(self) -> None:
        section = self.doc.sections[0]
        p = section.header.paragraphs[0]
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = p.add_run("Мониторинг производственных тележек — план и архитектура MVP  ·  v0.1  ·  октябрь 2026")
        r.font.name = BODY_FONT
        r.font.size = Pt(8)
        r.font.color.rgb = rgb(SUBTLE)
        set_paragraph_bottom_border(p, LINE, 6, 4)

        p = section.footer.paragraphs[0]
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run("Внутренний документ проекта  ·  Страница ")
        r.font.name = BODY_FONT
        r.font.size = Pt(8)
        r.font.color.rgb = rgb(SUBTLE)
        add_field(p, "PAGE", "1")
        r = p.add_run(" из ")
        r.font.name = BODY_FONT
        r.font.size = Pt(8)
        r.font.color.rgb = rgb(SUBTLE)
        add_field(p, "NUMPAGES", "1")
        for run in p.runs:
            run.font.name = BODY_FONT
            run.font.size = Pt(8)
            run.font.color.rgb = rgb(SUBTLE)

    def _setup_properties(self) -> None:
        cp = self.doc.core_properties
        cp.title = "Мониторинг производственных тележек — план и архитектура MVP"
        cp.subject = "File-first MVP: React-карта координат из файла, готовая к Magma"
        cp.author = "Проектная команда"
        cp.last_modified_by = "Проектная команда"
        cp.category = "Архитектура / план MVP"
        cp.comments = "MVP 0.1: JSON-снимок, Leaflet, порт FleetRepository, переход к Magma."
        cp.keywords = "React, TypeScript, Leaflet, Magma, MVP, позиционирование, телеметрия"
        cp.created = datetime(2026, 10, 28, 17, 0)
        cp.modified = datetime(2026, 10, 28, 17, 0)
        cp.revision = 1
        settings = self.doc.settings.element
        update = OxmlElement("w:updateFields")
        update.set(qn("w:val"), "true")
        settings.append(update)

    def cover(self) -> None:
        table = self.doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        self._cover_width(table, PAGE_W)
        self._cover_margins(table)
        cell = table.rows[0].cells[0]
        cell.width = Cm(PAGE_W)
        self._cover_fill(cell, NAVY)
        table.rows[0].height = Cm(7.4)
        table.rows[0].height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
        self._no_borders(table)

        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(16)
        r = p.add_run("ПРОЕКТНЫЙ ЧЕРТЁЖ  /  MVP 0.1")
        r.font.name = BODY_FONT
        r.font.size = Pt(8.5)
        r.bold = True
        r.font.color.rgb = rgb("93C5FD")
        r._element.get_or_add_rPr().append(self._spacing(25))

        p = cell.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 0.95
        r = p.add_run("Мониторинг")
        r.font.name = BODY_FONT
        r.font.size = Pt(31)
        r.bold = True
        r.font.color.rgb = rgb(WHITE)

        p = cell.add_paragraph()
        p.paragraph_format.space_after = Pt(10)
        p.paragraph_format.line_spacing = 0.95
        r = p.add_run("производственных тележек")
        r.font.name = BODY_FONT
        r.font.size = Pt(25)
        r.bold = True
        r.font.color.rgb = rgb(WHITE)

        p = cell.add_paragraph()
        p.paragraph_format.space_after = Pt(8)
        r = p.add_run("План и архитектура MVP 0.1")
        r.font.name = BODY_FONT
        r.font.size = Pt(18)
        r.font.color.rgb = rgb("E2E8F0")

        p = cell.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run("React-карта на данных из файла, готовая к Magma")
        r.font.name = BODY_FONT
        r.font.size = Pt(10.5)
        r.font.color.rgb = rgb("CBD5E1")

        accent = self.doc.add_table(rows=1, cols=1)
        accent.alignment = WD_TABLE_ALIGNMENT.CENTER
        accent.autofit = False
        self._cover_width(accent, PAGE_W)
        cell2 = accent.rows[0].cells[0]
        cell2.width = Cm(PAGE_W)
        self._cover_fill(cell2, BLUE)
        accent.rows[0].height = Cm(0.16)
        accent.rows[0].height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
        cell2.paragraphs[0].paragraph_format.space_after = Pt(0)
        cell2.paragraphs[0].add_run(" ").font.size = Pt(1)

        self.p("", size=5, space_after=4)
        meta = [
            ("Тип документа", "План проекта и архитектура MVP"),
            ("Статус", "Черновик для обсуждения"),
            ("Версия / дата", "0.1  ·  28 октября 2026"),
            ("Аудитория", "Команда проекта, frontend-разработчик, интегратор"),
            ("Границы MVP", "Координаты из файла, точки на карте"),
        ]
        t = self.doc.add_table(rows=0, cols=2)
        t.alignment = WD_TABLE_ALIGNMENT.LEFT
        t.autofit = False
        self._cover_width(t, PAGE_W)
        t.columns[0].width = Cm(3.9)
        t.columns[1].width = Cm(12.9)
        self._cover_margins(t)
        self._no_borders(t)
        for label, value in meta:
            row = t.add_row()
            row.cells[0].width = Cm(3.9)
            row.cells[1].width = Cm(12.9)
            p = row.cells[0].paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(label)
            r.font.name = BODY_FONT
            r.font.size = Pt(8.3)
            r.font.color.rgb = rgb(SUBTLE)
            p = row.cells[1].paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(value)
            r.font.name = BODY_FONT
            r.font.size = Pt(9.2)
            r.font.color.rgb = rgb("1F2937")

        self.p("", size=8, space_after=4)
        self.callout(
            "Главная мысль",
            "Файл — не архитектура. Архитектура — это стабильный контракт снимка и заменяемый адаптер источника. "
            "Позже файл заменяется на API или Magma без переписывания карты, доменной модели и экрана.",
            "info",
        )
        self.p("", size=16, space_after=0)
        self.p("Октябрь 2026  ·  Внутренний документ проекта", size=8.8, color=SUBTLE, space_after=0)
        self.page_break()

    def _cover_width(self, table, width):
        tblPr = table._tbl.tblPr
        for existing in tblPr.findall(qn("w:tblW")):
            tblPr.remove(existing)
        for existing in tblPr.findall(qn("w:tblLayout")):
            tblPr.remove(existing)
        tblW = OxmlElement("w:tblW")
        tblW.set(qn("w:w"), str(int(width * 567)))
        tblW.set(qn("w:type"), "dxa")
        tblPr.append(tblW)
        layout = OxmlElement("w:tblLayout")
        layout.set(qn("w:type"), "fixed")
        tblPr.append(layout)

    def _cover_margins(self, table):
        tblPr = table._tbl.tblPr
        for existing in tblPr.findall(qn("w:tblCellMar")):
            tblPr.remove(existing)
        mar = OxmlElement("w:tblCellMar")
        for edge, value in (("top", 240), ("left", 240), ("bottom", 220), ("right", 240)):
            el = OxmlElement(f"w:{edge}")
            el.set(qn("w:w"), str(value))
            el.set(qn("w:type"), "dxa")
            mar.append(el)
        tblPr.append(mar)

    def _cover_fill(self, cell, fill):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), fill)
        tcPr.append(shd)

    def _no_borders(self, table):
        tblPr = table._tbl.tblPr
        for existing in tblPr.findall(qn("w:tblBorders")):
            tblPr.remove(existing)
        borders = OxmlElement("w:tblBorders")
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            el = OxmlElement(f"w:{edge}")
            el.set(qn("w:val"), "nil")
            borders.append(el)
        tblPr.append(borders)

    def _spacing(self, twips):
        el = OxmlElement("w:spacing")
        el.set(qn("w:val"), str(twips))
        return el

    def step(self, number: int, title: str, body: str) -> None:
        p = self.doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.8)
        p.paragraph_format.first_line_indent = Cm(-0.8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(f"Шаг {number}. ")
        r.bold = True
        r.font.color.rgb = rgb(BLUE)
        self._add_inline(p, f"**{title}**")
        self.p(body, space_after=5)

    def contents(self) -> None:
        p = self.p("Содержание", size=24, color=INK, bold=True, space_after=2)
        set_paragraph_bottom_border(p, BLUE, 12, 6)
        self.p("", size=4, space_after=6)
        p = self.doc.add_paragraph()
        run = p.add_run()
        begin = OxmlElement("w:fldChar")
        begin.set(qn("w:fldCharType"), "begin")
        instr = OxmlElement("w:instrText")
        instr.set(qn("xml:space"), "preserve")
        instr.text = 'TOC \\o "1-2" \\h \\z \\u'
        sep = OxmlElement("w:fldChar")
        sep.set(qn("w:fldCharType"), "separate")
        placeholder = OxmlElement("w:t")
        placeholder.text = "Щёлкните здесь правой кнопкой и выберите «Обновить поле», чтобы построить оглавление."
        end = OxmlElement("w:fldChar")
        end.set(qn("w:fldCharType"), "end")
        for el in (begin, instr, sep, placeholder, end):
            run._r.append(el)
        self.p("", size=4, space_after=4)
        self.callout(
            "Как обновить оглавление",
            "Это живое поле Word. После открытия документа щёлкните по нему правой кнопкой и выберите "
            "«Обновить поле» → «Обновить целиком». Номера страниц формирует Word, а не автор вручную.",
            "warning",
        )
        self.p("", size=4, space_after=2)
        self.p("Как читать документ", size=12.5, color=INK, bold=True, space_after=4)
        self.table(
            ["Кому", "Что читать", "Зачем"],
            [
                ["Руководителю / заказчику", "Резюме; главы 1–2, 6–7", "Границы, критерии, сроки, риски"],
                ["Frontend-разработчику", "Главы 2–5 и 9", "Архитектура, контракт, карта, порядок работы"],
                ["Интегратору / бэкенду", "Главы 2, 3, 8", "Контракт, передача файла, переход к Magma"],
                ["Ревьюеру", "2.5, 6.4, 7", "Критерии приёмки, DoD, риски"],
            ],
            [4.2, 6.0, 6.6],
            font_size=8.6,
            first_col_bold=True,
        )
        self.page_break()

    def summary(self) -> None:
        self.h1("Резюме", new_page=False)
        self.p(
            "Документ описывает MVP 0.1 веб-приложения для диспетчера: на карте площадки отображаются "
            "производственные тележки. Координаты **не вычисляются в браузере** — они приходят готовым JSON-снимком "
            "от движка позиционирования. Задача MVP — доказать пользовательский сценарий и зафиксировать контракт "
            "между «радиомиром» и интерфейсом. Magma, MQTT, RSSI и мультилатерация в этот инкремент не входят."
        )
        self.p(
            "Архитектура — небольшое React-приложение с одним заменяемым швом: портом `FleetRepository`. Первая "
            "реализация читает `/data/fleet.snapshot.json` раз в секунду. Позже тот же контракт можно получать по HTTP "
            "или WebSocket, не меняя карту, доменную модель и экран. Это и есть **готовность к Magma без зависимости "
            "MVP от Magma**."
        )
        self.p(
            "Оценка: **8–10 рабочих дней одного frontend-разработчика**, или две календарные недели с ревью и демо. "
            "Результат: работающее демо, версионируемый контракт, тесты, инструкция по развёртыванию и бэклог "
            "следующей фазы. Бэкенд, БД и радиооборудование для MVP 0.1 не нужны."
        )
        self.table(
            ["Коротко", "MVP 0.1"],
            [
                ["Цель", "Диспетчер открывает одну страницу и видит все тележки точками на карте площадки."],
                ["В границах", "JSON-снимок → опрос → валидация → карта, станции, точки, статусы, выбор, ошибки."],
                ["Вне границ", "RSSI, мультилатерация, Magma, MQTT, БД, история, авторизация, геозоны, CRUD станций."],
                ["Стек", "React + TypeScript + Vite · TanStack Query · Zod · Leaflet + OpenStreetMap."],
                ["Ключевое решение", "Один контракт снимка и один порт источника; файл сейчас, API/WebSocket позже."],
                ["Срок", "8–10 рабочих дней; две календарные недели с буфером."],
                ["Признак успеха", "Демо с пятью тележками, которое переживает битый файл и проходит чек-лист."],
            ],
            [3.8, 13.0],
            font_size=8.8,
            first_col_bold=True,
        )
        self.p("Пять решений, которые определяют всё", size=12.5, color=INK, bold=True, space_before=4, space_after=4)
        self.numbered([
            "**Сначала файл, не бэкенд.** Первый инкремент доказывает экран и контракт, не дожидаясь радио и Magma.",
            "**Сначала контракт.** JSON-схема ревьюится и версионируется до первого компонента.",
            "**Один порт, один адаптер.** `FleetRepository` — единственный шов между UI и источником данных.",
            "**Карта — не источник истины.** Leaflet рисует то, что дал домен; замена библиотеки не трогает данные.",
            "**Отказ мягкий и честный.** Битый или устаревший файл не обнуляет карту: сохраняется последний хороший снимок и показывается возраст.",
        ])
        self.callout(
            "Чего в документе нет",
            "Это не спецификация алгоритма позиционирования, не руководство по установке Magma и не production-runbook. "
            "Это план первого рабочего инкремента и швы, которые позволяют следующим этапам не делать переписывание.",
            "warning",
        )
        self.p("Что запомнить", size=12.5, color=INK, bold=True, space_before=2, space_after=4)
        self.bullets([
            "Браузер не читает произвольный файл с диска: снимок отдаёт тот же веб-сервер, что и приложение.",
            "Снимок — **полная картина**, а не поток дельт. Опрос полного снимка — самый простой надёжный MVP.",
            "TypeScript не проверяет данные в рантайме; **Zod** проверяет то, что реально пришло.",
            "Карта — рендерер. Загрузка, валидация и правила устаревания живут вне неё.",
            "Magma — будущий **серверный** источник, а не зависимость браузера.",
        ])
        self.p("Метрики успеха MVP", size=12.5, color=INK, bold=True, space_before=4, space_after=4)
        self.table(
            ["Метрика", "Цель", "Что доказывает"],
            [
                ["Время до полезной карты", "≤ 2,5 с в корпоративной сети", "Демо не хрупкое"],
                ["Свежесть снимка", "≤ 2 с от `generatedAt` до экрана", "Диспетчер может доверять «live»"],
                ["Ёмкость", "100 тележек при 1 Гц", "Запас для пилота"],
                ["Прозрачность отказов", "У каждого проверенного отказа есть видимое состояние", "Нет молчаливых устаревших данных"],
                ["Смена источника", "≤ 1 день на HTTP-адаптер", "Архитектура реальна, а не на словах"],
            ],
            [4.6, 5.4, 6.8],
            font_size=8.5,
            first_col_bold=True,
        )

    def ch1(self) -> None:
        self.h1("1. Контекст и границы MVP", new_page=False)
        self.p(
            "Производственная площадка — плохое место для спутниковой навигации: цеха, склады, металлоконструкции и "
            "крыши экранируют GPS/ГЛОНАСС. Поэтому используются свои базовые станции с точно известными координатами, "
            "а модем тележки измеряет уровень сигнала. По затуханию сигнала движок оценивает расстояния и вычисляет "
            "позицию мультилатерацией. С двумя станциями результат слабее и может быть неоднозначным; с тремя и более — "
            "точнее."
        )
        self.p(
            "Роль браузера начинается **после** того, как координата появилась. Браузер не читает радиоизмерения, не "
            "калибрует модель затухания и не решает задачу наименьших квадратов. Он получает координату, время и "
            "показатель качества и превращает их в точку на карте, которой можно доверять."
        )
        self.h2("1.1 Что нужно диспетчеру")
        self.bullets([
            "**Где тележка сейчас?** Точка на карте с именем или кодом актива.",
            "**Данные свежие?** Видимое время обновления и предупреждение, если источник остановился.",
            "**Насколько можно верить точке?** Радиус точности, метод позиционирования и цвет статуса.",
            "**Что это за тележка?** Клик открывает карточку с координатами, точностью и временем.",
        ])
        self.p(
            "Поэтому MVP — это **продукт визуализации**, а не продукт позиционирования. У проекта позиционирования "
            "свои риски и свой стенд. Визуализацию можно начинать сейчас, на файле, и быть готовой к первой реальной "
            "координате."
        )
        self.h2("1.2 Почему сначала файл")
        self.p(
            "Файл звучит скромно, но это осознанный архитектурный выбор. Он убирает всё, что может задержать первое "
            "демо: бэкенд, БД, радиооборудование, Magma, MQTT. При этом он заставляет зафиксировать то, что переживёт "
            "все изменения, — контракт снимка."
        )
        self.numbered([
            "**Снимает неизвестность.** Радио и Magma идут параллельно; команда UI не заблокирована.",
            "**Даёт демо за дни, а не месяцы.** Заказчик видит движение точек и даёт обратную связь по экрану.",
            "**Создаёт эталонный fixture.** Тот же файл становится тестом для репозитория, карты, ошибок и будущего API.",
            "**Рано проявляет границу интеграции.** Продюсер узнаёт, что нужно потребителю; потребитель — что может дать продюсер.",
            "**Делает замену дешёвой.** Файловый и HTTP-адаптер реализуют один и тот же небольшой интерфейс.",
        ])
        self.h2("1.3 Допущения")
        self.table(
            ["Допущение", "Почему важно", "Что подтвердить"],
            [
                ["«Magama» = Magma, open-source mobile core", "Объясняет будущую интеграцию и термины главы 8", "Руководитель / сеть"],
                ["Координаты — WGS84, широта/долгота", "Leaflet и контракт используют градусы; локальные метры конвертируются upstream", "Инженер позиционирования"],
                ["Файл пишет внешний процесс", "Браузер не читает произвольный путь; файл отдаёт веб-сервер", "Интегратор"],
                ["Частота около 1 Гц; до 100 тележек", "Определяет интервал опроса, размер файла и стратегию рендера", "Владелец продукта"],
                ["На демо есть интернет для тайлов", "OSM — внешняя зависимость; офлайн-вариант — план площадки", "IT / безопасность"],
                ["MVP развёрнут внутри периметра", "Авторизации в MVP нет; приложение закрыто сетью или reverse proxy", "Безопасность"],
            ],
            [4.8, 7.2, 4.8],
            font_size=8.4,
            first_col_bold=True,
        )
        self.callout(
            "Две станции — не полное решение",
            "Две окружности обычно пересекаются в двух точках, а измерения шумные. Двухстанционное решение может быть "
            "рабочим только с дополнительными ограничениями (геометрия площадки, прошлая позиция, timing advance, сектор "
            "соты). Поэтому UI обязан показывать метод и радиус точности, а не «слишком точную» точку.",
            "warning",
        )
        self.h2("1.4 Границы MVP")
        self.table(
            ["В границах", "Вне границ"],
            [
                ["Одностраничное React-приложение", "Расчёт координат по RSSI"],
                ["Карта площадки, станции и точки тележек", "Magma, AGW, Orchestrator, SIM"],
                ["Опрос JSON-снимка раз в секунду", "MQTT и бортовые агенты"],
                ["Выбор тележки, карточка, точность, метод", "БД, история, треки, воспроизведение"],
                ["Состояния loading / live / stale / error / empty", "Авторизация, роли, CRUD станций"],
                ["Валидация Zod и диагностика", "Геозоны, алерты, уведомления"],
                ["Тесты, README, статический деплой", "Мобильное приложение, 3D, мультиплощадочность"],
            ],
            [8.4, 8.4],
            font_size=8.5,
            first_col_bold=True,
        )
        self.h2("1.5 Критерии приёмки")
        self.table(
            ["#", "Проверка", "Чем подтверждается"],
            [
                ["AC-01", "Валидный снимок с 3 станциями и 5 тележками: 3 маркера и 5 точек за ≤ 2 с", "Ручная + E2E"],
                ["AC-02", "После замены файла точки двигаются без перезагрузки страницы", "Ручная + интеграционная"],
                ["AC-03", "Клик по точке открывает карточку с именем, координатами, точностью, методом, временем", "Компонентная"],
                ["AC-04", "Одна битая запись пропускается, остальные отображаются; счётчик виден", "Юнит + компонент"],
                ["AC-05", "Первый запрос упал / файл отсутствует: понятная ошибка и кнопка «Повторить»", "Компонентная"],
                ["AC-06", "Ошибка обновления: последние хорошие точки остаются, баннер не блокирует карту", "Интеграционная"],
                ["AC-07", "`generatedAt` старый: баннер устаревания даже при HTTP 200", "Юнит + компонент"],
                ["AC-08", "100 тележек при 1 Гц: панорамирование и зум остаются отзывчивыми", "Проверка производительности"],
                ["AC-09", "Тайлы недоступны: точки, станции, легенда и карточка работают на пустом фоне", "Ручная"],
                ["AC-10", "Выбор тележки с клавиатуры через список работает", "Ручная + a11y"],
            ],
            [1.4, 12.0, 3.4],
            font_size=8.2,
            first_col_bold=True,
        )

    def ch2(self) -> None:
        self.h1("2. Архитектура и поток данных")
        self.p(
            "В MVP 0.1 четыре участника: продюсер пишет снимок, статический сервер отдаёт приложение и снимок, браузер "
            "опрашивает и валидирует, карта рисует. Бэкенда и БД нет. Простота — это и есть цель: каждую часть можно "
            "проверить отдельно."
        )
        self.figure(
            "fig1-context-ru.png",
            "Рисунок 1. Контекст MVP: браузер читает один атомарный JSON-снимок с того же статического сервера, что и приложение.",
            "Схема: продюсер пишет fleet.snapshot.json; статический сервер отдаёт React-приложение и снимок; браузер опрашивает, валидирует Zod и рисует Leaflet; тайлы OSM — внешний слой.",
        )
        self.h2("2.1 Путь данных по шагам")
        self.step(1, "Продюсер пишет полный снимок",
                  "Скрипт или сервис пишет `site + baseStations + trucks` во временный файл и переименовывает его поверх "
                  "`fleet.snapshot.json`. На POSIX переименование атомарно: читатель видит либо старый, либо новый файл.")
        self.step(2, "Статический сервер отдаёт файл",
                  "Nginx (прод) или Vite (дев) отдают React-сборку и `/data/fleet.snapshot.json` с одного origin. "
                  "`Cache-Control: no-store` не даёт прокси вернуть вчерашние позиции.")
        self.step(3, "Браузер опрашивает раз в секунду",
                  "TanStack Query вызывает репозиторий по таймеру. Запрос содержит cache-buster как вторую защиту от кэша.")
        self.step(4, "Репозиторий парсит и валидирует",
                  "`JSON.parse` обёрнут в типизированную ошибку. Zod проверяет конверт, затем каждую станцию и тележку "
                  "отдельно; битые записи пропускаются и считаются.")
        self.step(5, "Домен получает новый снимок",
                  "В кэше запроса хранится последний успешный `FleetLoadResult`. Карта получает стабильный доменный объект, "
                  "а не сырой JSON.")
        self.step(6, "Карта обновляет позиции",
                  "Leaflet обновляет маркеры по стабильному `id`. Станции рисуются на снимок; круг точности — только у выбранной тележки.")
        self.step(7, "UI показывает здоровье данных",
                  "Заголовок показывает время последнего успешного запроса и `generatedAt`. Если продюсер остановился, "
                  "снимок становится устаревшим, даже если HTTP отвечает 200.")
        self.step(8, "Ошибка сохраняет последнюю картину",
                  "При сетевой или схемной ошибке с уже загруженными данными карта остаётся, появляется некритичный баннер. "
                  "При ошибке первого запроса — карточка с причиной и кнопкой «Повторить».")

        self.h2("2.2 Слои и правило зависимостей")
        self.table(
            ["Слой", "Что делает", "Чего не делает"],
            [
                ["`domain/`", "Типы, Zod-схемы, чистые правила устаревания и координат", "Не импортирует React, Leaflet, fetch, файлы"],
                ["`data/`", "Реализует порт: fetch, parse, validate, нормализация ошибок", "Не рисует UI и не знает о выбранной тележке"],
                ["`features/fleet-map/hooks`", "Опрос, кэш, производные данные, retry", "Не парсит сырой JSON и не рисует маркеры"],
                ["`features/fleet-map/components`", "Карта, маркеры, карточка, баннеры, легенда", "Не вызывает fetch напрямую и не знает URL файла"],
                ["`app/`", "Собирает конкретный адаптер, провайдеры, error boundary", "Не содержит бизнес-правил"],
            ],
            [4.4, 6.8, 5.6],
            font_size=8.3,
            first_col_bold=True,
        )
        self.p(
            "Правило простое: внешние слои могут импортировать внутренние, никогда наоборот. Домен — центр, у него нет "
            "зависимостей от фреймворка. Проверка: `src/domain` компилируется и тестируется в обычном Node без DOM."
        )

        self.h2("2.3 Порт FleetRepository")
        self.p(
            "Порт — единственный контракт между приложением и источником данных. Он намеренно меньше типичного API-клиента: "
            "один метод, один результат, один тип ошибки."
        )
        self.code(
            """// src/data/fleet-repository.ts
import type { FleetSnapshot } from '../domain/fleet';

export interface SourceDiagnostic {
  level: 'warning' | 'error';
  code: 'invalid-truck' | 'invalid-station' | 'duplicate-id' | 'clock-skew';
  message: string;
  recordIndex?: number;
}

export interface FleetLoadResult {
  snapshot: FleetSnapshot;
  diagnostics: SourceDiagnostic[];
}

export interface FleetRepository {
  loadSnapshot(options?: { signal?: AbortSignal }): Promise<FleetLoadResult>;
}""",
            "Порт возвращает валидный снимок и некритичные диагностики. UI не видит сырой JSON.",
        )
        self.p(
            "`FleetLoadResult` — не просто `FleetSnapshot`. Файл может быть валиден на 95%: четыре тележки в порядке, у "
            "пятой битая широта. Выбросить весь снимок хуже, чем нарисовать четыре точки и показать «1 запись пропущена». "
            "Диагностики делают это поведение явным."
        )

        self.h2("2.4 Файловый адаптер")
        self.p(
            "Адаптер — единственное место, которое знает URL файла, HTTP-метод, заголовки кэша и парсер JSON. Если "
            "транспорт меняется, меняется только этот файл."
        )
        self.code(
            """// src/data/json-file-fleet-repository.ts
export class JsonFileFleetRepository implements FleetRepository {
  constructor(private readonly url: string) {}

  async loadSnapshot({ signal }: { signal?: AbortSignal } = {}): Promise<FleetLoadResult> {
    let response: Response;
    try {
      response = await fetch(`${this.url}?t=${Date.now()}`, {
        signal, cache: 'no-store', headers: { Accept: 'application/json' },
      });
    } catch (cause) {
      throw new FleetSourceError('network', 'Cannot reach the snapshot file', cause);
    }
    if (!response.ok) throw new FleetSourceError('http', `Snapshot returned HTTP ${response.status}`);
    const json: unknown = await response.json().catch((cause) => {
      throw new FleetSourceError('invalid-json', 'Snapshot is not valid JSON', cause);
    });
    return parseFleetSnapshot(json);
  }
}""",
            "Адаптер переводит транспортные сбои в типизированные ошибки; решение о показе принимает UI.",
        )

        self.h2("2.5 Опрос и состояние")
        self.code(
            """// src/features/fleet-map/hooks/useFleetSnapshot.ts
import { keepPreviousData, useQuery } from '@tanstack/react-query';

export function useFleetSnapshot(repository: FleetRepository) {
  return useQuery({
    queryKey: ['fleet-snapshot'],
    queryFn: ({ signal }) => repository.loadSnapshot({ signal }),
    refetchInterval: 1000,
    refetchIntervalInBackground: false,
    staleTime: 0,
    retry: 1,
    placeholderData: keepPreviousData,
  });
}""",
            "Один запрос, один интервал. При ошибке предыдущие данные остаются; экран решает, как это показать.",
        )
        self.bullets([
            "`refetchIntervalInBackground: false` не опрашивает скрытую вкладку бесконечно.",
            "`retry: 1` не устраивает шторм повторов, если файла нет; следующий плановый опрос — и есть повтор.",
            "`staleTime: 0` корректен: каждый снимок — новая картина.",
            "`keepPreviousData` не даёт карте мигнуть белым при неудачном обновлении.",
        ])

        self.h2("2.6 Проверка гибкости")
        self.numbered([
            "**Смена источника.** Замените `JsonFileFleetRepository` на mock. Страница рисует те же данные без изменений в компонентах.",
            "**Смена транспорта.** Добавьте `HttpFleetRepository` на `/api/v1/fleet/snapshot`. Меняется только composition root.",
            "**Смена рендерера.** Замените Leaflet на заглушку, которая рисует `<ul>` с именами. Репозиторий, схема и состояние страницы не меняются.",
            "**Расширение контракта.** Добавьте необязательное поле `zone`. Старые файлы продолжают работать, новое поле появляется в карточке.",
            "**Отказ.** Переименуйте файл, испортите одну запись, отмотайте `generatedAt` на две минуты. Карта должна объяснить каждое состояние.",
        ])
        self.callout(
            "Что «гибкость» не значит",
            "Это не generic `DataSource<T>`, не плагинная система карт и не Redux «на всякий случай». Один доменный тип, "
            "один порт, один адаптер сейчас. Второй адаптер появляется тогда, когда он действительно нужен.",
            "info",
        )

    def ch3(self) -> None:
        self.h1("3. Контракт данных")
        self.p(
            "Контракт — один JSON-объект, **снимок**. В нём есть площадка, базовые станции и тележки на один момент "
            "времени. Снимок полный, а не инкрементальный: одного файла достаточно, чтобы нарисовать весь экран."
        )
        self.h2("3.1 Верхний уровень")
        self.table(
            ["Поле", "Тип", "Обяз.", "Правила"],
            [
                ["`schemaVersion`", "string", "да", "`1.x` для этого контракта; другая мажорная версия — фатальная ошибка"],
                ["`generatedAt`", "ISO 8601", "да", "Когда продюсер собрал снимок; UTC с `Z` или смещением"],
                ["`site`", "object", "да", "Площадка: id, имя, центр, зум, часовой пояс, режим карты"],
                ["`baseStations`", "array", "да", "0+ станций"],
                ["`trucks`", "array", "да", "0+ тележек; пустой массив валиден"],
            ],
            [3.4, 3.0, 2.2, 8.2],
            font_size=8.4,
            first_col_bold=True,
        )
        self.h2("3.2 Тележка")
        self.table(
            ["Поле", "Тип", "Обяз.", "Правила"],
            [
                ["`id`", "string", "да", "Стабильный ID актива, уникальный в снимке; никогда не индекс массива"],
                ["`name`", "string", "нет", "Отображаемое имя; иначе `id`"],
                ["`lat`, `lon`", "number", "да", "WGS84, конечные числа в допустимых диапазонах"],
                ["`updatedAt`", "ISO 8601", "да", "Когда измерена **эта тележка**, а не когда записан файл"],
                ["`status`", "enum", "да", "`moving`, `idle`, `offline`, `unknown`"],
                ["`accuracyM`", "number", "нет", "Радиус в метрах, ≥ 0; отсутствие = «неизвестно», а не 0"],
                ["`method`", "string", "нет", "`rssi-multilateration`, `timing-advance`, `cell-id`; неизвестное показывается как есть"],
                ["`speedMps`", "number", "нет", "Метры в секунду, ≥ 0"],
                ["`headingDeg`", "number", "нет", "0 ≤ значение < 360; 0 = север, по часовой"],
            ],
            [3.2, 3.0, 2.2, 8.4],
            font_size=8.2,
            first_col_bold=True,
        )
        self.h2("3.3 Пример")
        self.code(
            """{
  "schemaVersion": "1.0",
  "generatedAt": "2026-10-28T13:38:30.000Z",
  "site": {
    "id": "plant-1",
    "name": "Площадка 1 — сборка и логистика",
    "center": { "lat": 55.7558, "lon": 37.6173 },
    "defaultZoom": 17,
    "timeZone": "Europe/Moscow",
    "map": { "mode": "osm" }
  },
  "baseStations": [
    { "id": "bs-01", "name": "BS-01 / Северные ворота", "lat": 55.7562, "lon": 37.6168, "status": "online" }
  ],
  "trucks": [
    {
      "id": "truck-01", "name": "Тележка 01",
      "lat": 55.7559, "lon": 37.6171,
      "updatedAt": "2026-10-28T13:38:28.000Z",
      "status": "moving", "accuracyM": 18.5,
      "method": "rssi-multilateration"
    }
  ]
}""",
            "Полный стартовый файл: web/public/data/fleet.snapshot.example.json.",
        )
        self.h2("3.4 Валидация и политика ошибок")
        self.p(
            "Валидация двухступенчатая. **Конверт** (`schemaVersion`, `generatedAt`, `site`, массивы) — фатален: без него "
            "нельзя судить о свежести и месте. **Записи** проверяются по одной: битая тележка пропускается и считается, "
            "остальные рисуются."
        )
        self.table(
            ["Условие", "Поведение", "Что видит диспетчер"],
            [
                ["Файл отсутствует / 404", "Фатально при первом запросе; позже — сохранить прошлые данные", "Карточка ошибки с URL и «Повторить»"],
                ["Невалидный JSON", "Отклонить опрос; сохранить прошлые данные", "«Снимок не является валидным JSON»"],
                ["Конверт не прошёл схему", "Отклонить опрос; сохранить прошлые данные", "«Несовпадение контракта» + первая ошибка"],
                ["Одна битая тележка", "Пропустить только её", "«1 запись пропущена» в диагностике"],
                ["Дублирующийся ID", "Оставить первую, вторую пропустить", "«1 дубликат ID»"],
                ["`generatedAt` старый", "Данные оставить, снимок пометить устаревшим", "Янтарный баннер с возрастом"],
                ["Часы убежали > 5 мин", "Данные оставить, предупредить", "Предупреждение в диагностике"],
                ["Пустой `trucks`", "Валидный пустой снимок", "«В снимке нет тележек»"],
            ],
            [5.2, 6.0, 5.6],
            font_size=8.2,
            first_col_bold=True,
        )
        self.h2("3.5 Координаты и единицы")
        self.p(
            "Канонический контракт UI — **WGS84, десятичные градусы**. Локальные метры хороши для движка позиционирования, "
            "но не должны протекать в UI: компонент не должен знать начало координат площадки, проекцию и поворот плана."
        )
        self.table(
            ["Величина", "Единица", "Соглашение"],
            [
                ["Широта, долгота", "градусы", "WGS84; 6 знаков ≈ 0,11 м"],
                ["Точность", "метры", "Радиус, не диаметр; отсутствие = неизвестно"],
                ["Скорость", "м/с", "В UI можно показывать км/ч"],
                ["Курс", "градусы", "0 = север, по часовой, [0, 360)"],
                ["Время", "ISO 8601", "UTC с `Z` или явным смещением"],
            ],
            [4.4, 4.0, 8.4],
            font_size=8.4,
            first_col_bold=True,
        )
        self.p(
            "Если у продюсера только локальные метры, конвертируйте **до** записи файла. Для площадки в несколько "
            "километров достаточно равнопромежуточной аппроксимации вокруг начала координат:"
        )
        self.code(
            """// Локальные ENU-метры -> WGS84 для начала (lat0, lon0)
const R = 6_378_137; // метры
const lat = lat0 + (y / R) * (180 / Math.PI);
const lon = lon0 + (x / (R * Math.cos((lat0 * Math.PI) / 180))) * (180 / Math.PI);""",
            "Используйте один раз, в продюсере. Задокументируйте начало и оси: x = восток, y = север.",
        )
        self.h2("3.6 Версионирование и атомарная запись")
        self.bullets([
            "**Минорная версия** (`1.0` → `1.1`): добавить необязательное поле, новый метод или ослабить правило. Старые клиенты работают.",
            "**Мажорная версия** (`1.x` → `2.0`): переименовать/удалить обязательное поле, изменить единицы или смысл. Приложение отказывается читать файл с понятным сообщением.",
            "**Только добавление.** UI игнорирует неизвестные поля и показывает неизвестный `method` как есть.",
            "**Не переиспользуйте имя поля с новым смыслом.** Добавьте `zoneName`, а не меняйте `zone` со строки на объект.",
        ])
        self.p(
            "Браузер, опрашивающий файл раз в секунду, рано или поздно прочитает его во время записи. Продюсер обязан "
            "писать во временный файл в том же каталоге и переименовывать поверх цели. На POSIX `rename` атомарен: "
            "читатель видит либо старый, либо новый файл."
        )
        self.code(
            """// Node.js: атомарная замена
import { writeFile, rename } from 'node:fs/promises';

const target = '/srv/fleet/data/fleet.snapshot.json';
const temp = `${target}.tmp`;

await writeFile(temp, JSON.stringify(snapshot, null, 2), 'utf8');
await rename(temp, target); // атомарно на той же ФС""",
            "В Python используется `os.replace(temp, target)`.",
        )
        self.callout(
            "Файл — не финальное хранилище",
            "Снимок на 100 тележек — это 20–30 КБ. При перезаписи раз в секунду это около 2 ГБ записи на диск в сутки. "
            "Для демо и короткого пилота нормально; для 24/7 используйте API с состоянием в памяти/Redis или tmpfs. "
            "Файл — мост, а не телеметрическое хранилище.",
            "warning",
        )

    def ch4(self) -> None:
        self.h1("4. Карта и экран", new_page=False)
        self.p(
            "Экран близок к привычному паттерну «автобусы на карте»: большая карта, цветные точки, выбранный объект и "
            "небольшая легенда. Отличие в том, что точки приходят из собственной системы позиционирования, поэтому экран "
            "обязан честно показывать неопределённость и свежесть."
        )
        self.h2("4.1 Почему Leaflet")
        self.bullets([
            "**Небольшой и зрелый.** Leaflet — стабильная BSD-библиотека с большой экосистемой и низким порогом входа.",
            "**Без API-ключа.** OpenStreetMap-тайлы работают без коммерческого ключа, что упрощает демо и обсуждение закрытого контура.",
            "**Нужные примитивы уже есть.** Маркеры, круги в метрах, полилинии, попапы, тултипы, image overlay, fit-bounds.",
            "**Простая интеграция с React.** `react-leaflet` позволяет изолировать карту в одной папке.",
        ])
        self.p(
            "MapLibre GL JS — естественный апгрейд, если понадобятся векторные тайлы, плавный зум, 3D или сильно "
            "стилизованная карта. Архитектура оставляет эту возможность: Leaflet изолирован в `FleetMap.tsx` и маркерах, "
            "репозиторий и домен о нём не знают."
        )
        self.h2("4.2 Конфигурация карты")
        self.table(
            ["Режим", "Когда использовать", "Реализация"],
            [
                ["`osm`", "Разработка, демо с интернетом", "`TileLayer` с URL OSM и attribution"],
                ["`image`", "Закрытая сеть или плохая детализация OSM", "`ImageOverlay` с `bounds` из `site.map.imageBounds`"],
                ["`blank`", "Тайлы заблокированы, но точки важны", "Без слоя тайлов; нейтральный фон и сетка"],
            ],
            [2.8, 6.4, 7.6],
            font_size=8.4,
            first_col_bold=True,
        )
        self.p(
            "Публичные тайлы OSM подчиняются политике использования; для продакшена и офлайна нужен свой сервер тайлов "
            "или план площадки. План геопривязывается двумя углами в WGS84 (`imageBounds`); повёрнутый или не "
            "ориентированный на север план сместит все точки."
        )
        self.h2("4.3 Маркеры и статусы")
        self.table(
            ["Объект", "Вид", "Поведение"],
            [
                ["Тележка, moving", "Зелёная точка 14 px, белая обводка 2 px", "Тултип; клик выбирает; опционально стрелка курса"],
                ["Тележка, idle", "Янтарная точка", "Как moving"],
                ["Тележка, offline", "Серая точка, 60% прозрачности", "Остаётся на последней позиции; в карточке возраст"],
                ["Тележка, unknown", "Синяя точка", "Если статус отсутствует или неизвестен"],
                ["Выбранная", "20 px + кольцо 3 px + круг точности", "Открывает карточку; карта не прыгает на каждом обновлении"],
                ["Базовая станция", "Синий ромб/квадрат 12 px с подписью", "Всегда видна; тултип со статусом и координатами"],
                ["Круг точности", "Пунктирный круг радиусом `accuracyM`", "Только у выбранной тележки, чтобы не шуметь"],
            ],
            [3.6, 6.2, 7.0],
            font_size=8.3,
            first_col_bold=True,
        )
        self.callout(
            "Не кодируйте статус только цветом",
            "Около 8% мужчин имеют особенности цветовосприятия. Добавьте форму, иконку или подпись в тултипе и карточке. "
            "Легенда должна использовать слова и формы, а не только зелёный/янтарный/серый.",
            "warning",
        )
        self.h2("4.4 Макет экрана")
        self.code(
            """┌──────────────────────────────────────────────────────────┬─────────────────────┐
│ Заголовок: площадка · статус данных · последнее обновление│                     │
├──────────────────────────────────────────────────────────┤  Список тележек     │
│                                                          │  (поиск / фильтр)   │
│                         КАРТА                            │  ─────────────────  │
│              станции + точки + круг точности             │  Карточка выбранной │
│                                                          │  тележки: имя,      │
│                                                          │  координаты,        │
│                                                          │  точность, метод,   │
│                                                          │  время              │
├──────────────────────────────────────────────────────────┴─────────────────────┤
│ Легенда: ● moving  ● idle  ● offline  ◆ станция  ○ радиус точности            │
└────────────────────────────────────────────────────────────────────────────────┘""",
            "Desktop-first. На узком экране правая панель становится нижним листом; карта остаётся главной поверхностью.",
        )
        self.h2("4.5 Состояния экрана")
        self.table(
            ["Состояние", "Триггер", "Что видит пользователь"],
            [
                ["Первичная загрузка", "Данных ещё нет, первый запрос в полёте", "Скелетон карты + «Загрузка позиций…»; без фальшивых точек"],
                ["Live", "Свежий снимок и свежие тележки", "Карта, зелёный статус, время обновления"],
                ["Stale", "`generatedAt` старше 10 с", "Янтарный баннер «Данные устарели на N с»; точки приглушены"],
                ["Ошибка обновления", "Поздний опрос упал, прошлые данные есть", "Некритичный баннер + «Повторить»; карта остаётся"],
                ["Фатальная ошибка", "Нет данных и первый запрос упал", "Карточка с URL, причиной и кнопкой «Повторить»"],
                ["Пусто", "Валидный файл с нулём тележек", "Карта + «В снимке нет тележек»"],
                ["Частично битые", "Часть записей пропущена", "Карта + «N записей пропущено»"],
                ["Тайлы недоступны", "Слой тайлов не загрузился", "Пустой фон; точки и станции видны"],
            ],
            [3.6, 6.2, 7.0],
            font_size=8.2,
            first_col_bold=True,
        )
        self.h2("4.6 Точность и метод")
        self.p(
            "Точка без индикатора точности выглядит точнее, чем есть. Контракт несёт `accuracyM` и `method`, и карточка "
            "всегда показывает оба. Если `accuracyM` нет — «точность неизвестна», а не круг нулевого радиуса."
        )
        self.table(
            ["Значение `method`", "Подпись в UI", "Что значит"],
            [
                ["`rssi-multilateration`", "Мультилатерация RSSI", "Три и более станции; основной метод"],
                ["`timing-advance`", "Timing advance", "Резерв по двум станциям; грубая дистанция"],
                ["`cell-id`", "Cell ID", "Только обслуживающая сота; большая неопределённость"],
                ["другое", "Как есть", "Совместимость вперёд; не падать на новом методе"],
            ],
            [4.6, 5.0, 7.2],
            font_size=8.4,
            first_col_bold=True,
        )
        self.h2("4.7 Производительность и доступность")
        self.bullets([
            "`preferCanvas` для круговых маркеров при росте флота; SVG достаточно для нескольких десятков точек.",
            "Мемоизируйте `TruckMarker` по `id`, `lat`, `lon`, `status`, `selected`; не создавайте иконки на каждом рендере.",
            "Стабильный `key={truck.id}`. Никогда не используйте индекс массива.",
            "Круг точности — только у выбранной тележки; 100 кругов одновременно — визуальный шум и лишняя работа.",
            "`MapContainer` не пересоздаётся; иначе тайлы мигают и карта теряет состояние.",
            "Список тележек — настоящие `<ul>`/`<button>`, а не div с onClick: это доступный путь ко всем объектам.",
            "`aria-live=\"polite\"` для статуса данных и выбранной тележки; не объявляйте каждое обновление позиции.",
        ])
        self.h2("4.8 Yandex Maps: ориентир UX, не зависимость")
        self.p(
            "«Как автобусы на Яндекс Картах» описывает **опыт**, а не обязательно провайдера карты. Yandex Maps JS API "
            "требует API-ключ, внешние серверы и коммерческую лицензию; в закрытом контуре это может быть неприемлемо. "
            "Leaflet + OSM даёт тот же паттерн — точки, выбор, карточку — без ключа."
        )
        self.p(
            "Если заказчик требует Yandex Maps, добавьте `YandexMapCanvas` с теми же пропсами, что у `FleetMap`. Данные, "
            "схема и состояние страницы не меняются. Не протаскивайте координаты или SDK Яндекса в доменную модель."
        )

    def ch5(self) -> None:
        self.h1("5. Надёжность, безопасность, эксплуатация")
        self.p(
            "В MVP 0.1 нет бэкенда, но есть отказы: продюсер остановился, файл обрезан, сеть недоступна, тайлы заблокированы, "
            "часы врут. Цель — не «отказов нет», а «экран никогда не врёт о том, что знает»."
        )
        self.h2("5.1 Отказы")
        self.table(
            ["Отказ", "Как обнаружить", "Поведение", "Действие оператора"],
            [
                ["Продюсер не пишет", "Возраст `generatedAt`", "Stale-баннер, точки приглушены", "Проверить логи и диск"],
                ["Файл обрезан", "Ошибка JSON", "Сохранить прошлые данные, баннер", "Проверить атомарную запись"],
                ["Схема изменилась", "Ошибка конверта Zod", "Ошибка контракта", "Обновить приложение или продюсер"],
                ["Одна битая запись", "Ошибка записи Zod", "Пропустить, посчитать", "Исправить запись"],
                ["Сеть упала", "Fetch rejection", "Сохранить прошлые данные, баннер", "Проверить сеть / прокси"],
                ["Тайлы недоступны", "Ошибки слоя", "Пустой фон, точки видны", "План площадки или свои тайлы"],
                ["Часы врут", "Время > now + 5 мин", "Предупреждение, данные оставить", "NTP на хосте продюсера"],
            ],
            [3.6, 4.2, 5.0, 4.0],
            font_size=8.2,
            first_col_bold=True,
        )
        self.h2("5.2 Устаревание")
        self.p(
            "Есть два разных возраста, и путать их — частая ошибка. `generatedAt` говорит, когда **продюсер** сделал снимок. "
            "`updatedAt` — когда была измерена **тележка**. Файл может быть свежим, но содержать тележку, которую не видели "
            "пять минут."
        )
        self.table(
            ["Правило", "По умолчанию", "Смысл"],
            [
                ["Снимок устарел", "`now - generatedAt > 10 с`", "Продюсер не обновляет картину"],
                ["Тележка устарела", "`now - updatedAt > 30 с`", "Объект давно не выходил на связь"],
                ["Часы убежали", "`updatedAt > now + 5 мин`", "Не доверять относительному времени"],
                ["Интервал опроса", "1 с", "Задержка примерно один цикл + сеть"],
            ],
            [4.6, 5.0, 7.2],
            font_size=8.4,
            first_col_bold=True,
        )
        self.callout(
            "HTTP 200 — не признак свежести",
            "Если продюсер упал, Nginx будет отдавать последний файл с кодом 200 сколько угодно. Проверка свежести должна "
            "смотреть на `generatedAt`, а не на статус запроса. Это главное правило надёжности MVP.",
            "danger",
        )
        self.h2("5.3 Безопасность")
        self.bullets([
            "**Снимок публичен для всех, кто может открыть приложение.** Если позиции чувствительны, закрывайте всё приложение VPN/SSO/reverse proxy.",
            "**В бандле нет секретов.** Переменные `VITE_*` компилируются в JavaScript и не являются секретом. Токены Magma, пароли БД и API-ключи — только на сервере.",
            "**Минимум персональных данных.** Используйте ID актива, а не имена водителей и телефоны. IMSI в UI-контракт без необходимости не попадает.",
            "**Браузер не вызывает Magma напрямую.** CORS — не граница безопасности; учётные данные ядра не должны попадать в браузер.",
            "**HTTPS** вне localhost. Статическое приложение тоже может утекать позициями по открытому HTTP.",
            "**Приватность тайлов.** Публичный OSM видит примерный район карты. Для закрытой площадки — свои тайлы или план.",
        ])
        self.h2("5.4 Развёртывание")
        self.p(
            "Сборка — статический `dist/`. Снимок лежит отдельно в `/data/` и отдаётся с того же origin, чтобы не настраивать "
            "CORS. Ключевые детали Nginx: SPA-fallback на `index.html`, `Cache-Control: no-store` для `/data/`, долгий кэш "
            "для хешированных ассетов и gzip для JSON/JS. Пример конфигурации — в приложении A."
        )
        self.bullets([
            "Пишите снимок во временный файл в том же каталоге и переименовывайте поверх цели.",
            "Права: веб-сервер читает, продюсер пишет; больше никому не нужно.",
            "UTC-время и NTP на хосте продюсера: иначе «устарело» теряет смысл.",
            "Не редактируйте обслуживаемый файл вручную и не делайте `git pull` в каталог с ним.",
            "Для внешней проверки — cron, который читает снимок и алертит, если `generatedAt` старше 60 с.",
        ])
        self.h2("5.5 Мониторинг и диагностика")
        self.p(
            "Без бэкенда главная поверхность наблюдаемости — сам браузер. Добавьте небольшой popover «Здоровье данных»: URL "
            "источника, время последнего успешного запроса, `generatedAt`, версия схемы, количество станций/тележек и "
            "пропущенных записей. Это бесценно для первого разработчика и интегратора."
        )
        self.table(
            ["Сигнал", "Где видно", "О чём говорит"],
            [
                ["Последний успешный запрос", "Заголовок / диагностика", "Работают ли сеть и сервер"],
                ["Возраст `generatedAt`", "Заголовок / stale-баннер", "Жив ли продюсер"],
                ["Пропущенные записи", "Бейдж диагностики", "Деградирует ли качество данных"],
                ["Версия схемы", "Диагностика", "Совместимы ли приложение и продюсер"],
                ["Ошибки тайлов", "Консоль / пустая карта", "Доступен ли провайдер карты"],
            ],
            [4.6, 6.0, 6.2],
            font_size=8.3,
            first_col_bold=True,
        )

    def ch6(self) -> None:
        self.h1("6. План работ")
        self.p(
            "План построен вокруг одного принципа: каждый день заканчивается тем, что можно показать. Первое демо — не "
            "«архитектура готова», а «пять точек двигаются по карте». Оценка — 58 идеальных часов, что укладывается в "
            "8–10 рабочих дней при 6–7 продуктивных часах в день. Календарь ниже — 10 дней с буфером."
        )
        self.h2("6.1 Команда и допущения")
        self.table(
            ["Роль", "Занятость", "Ответственность"],
            [
                ["Frontend-разработчик", "Полная, 8–10 дней", "React, карта, слой данных, тесты, деплой"],
                ["Инженер позиционирования", "2–3 часа в неделю", "Контракт, система координат, пример данных"],
                ["Дизайнер / продукт", "2–3 часа в неделю", "Макет, язык статусов, приёмка демо"],
                ["Ревьюер / QA", "0,5 дня на гейтах", "Критерии, отказные сценарии, релиз"],
            ],
            [4.6, 4.2, 8.0],
            font_size=8.4,
            first_col_bold=True,
        )
        self.h2("6.2 Календарь на две недели")
        self.table(
            ["День", "Фокус", "Результат", "Гейт"],
            [
                ["1", "Ревью контракта; каркас; оболочка карты", "Схема v1 согласована; Vite; Leaflet с центром площадки", "G0: контракт заморожен"],
                ["2", "Домен, Zod, пример файла, репозиторий", "Валидный снимок в тестах; отладочный вывод", "—"],
                ["3", "Опрос, маркеры станций, точки тележек", "Точки двигаются из файла; время обновления", "G1: первые точки"],
                ["4", "Выбор, карточка, цвета статусов", "Клик по точке или списку; карточка и круг точности", "—"],
                ["5", "Ошибки, пусто, stale; ревью", "Демо 1; список замечаний; проверка границ", "G2: рабочий экран"],
                ["6", "Адаптивность, доступность, диагностика", "Мобильный/десктоп; клавиатура; здоровье данных", "—"],
                ["7", "Юнит-, компонентные и интеграционные тесты", "Тесты зелёные; отказы покрыты", "—"],
                ["8", "Сборка, Nginx, README, runbook", "Release candidate на реальном URL", "G3: RC"],
                ["9", "Баги, производительность, демо-данные, репетиция", "Отполированное демо; проверка 100 тележек", "—"],
                ["10", "Демо заказчику, передача, тег", "Принятый MVP; `v0.1.0`; бэклог фазы 1", "G4: готово"],
            ],
            [1.3, 5.2, 7.3, 3.0],
            font_size=8.2,
            first_col_bold=True,
            align_center_cols=[0],
        )
        self.h2("6.3 Бэклог и оценка")
        self.table(
            ["ID", "Задача", "ч", "Зависит", "Готово, когда"],
            [
                ["M0-1", "Ревью контракта с продюсером и заказчиком", "4", "—", "Схема v1 и пример подписаны"],
                ["M0-2", "Решения по координатам и провайдеру карты", "3", "—", "WGS84 подтверждён; тайлы/план выбраны"],
                ["M1-1", "Каркас Vite + React + TS + lint/test", "3", "—", "`pnpm dev`, lint, test, build работают"],
                ["M1-2", "Оболочка, провайдеры, error boundary", "3", "M1-1", "Пустая страница без ошибок"],
                ["M2-1", "Домен + Zod-схемы + тесты", "4", "M0-1", "Валидные/битые fixture ведут себя по спецификации"],
                ["M2-2", "JsonFileFleetRepository + ошибки", "4", "M2-1", "Fetch, parse, частичный отказ, 404 покрыты"],
                ["M2-3", "useFleetSnapshot + QueryClient", "2", "M2-2", "Отладочный вывод обновляется раз в секунду"],
                ["M3-1", "Карта + маркеры станций", "5", "M1-2", "Карта центрирована; станции и подписи видны"],
                ["M3-2", "Точки тележек, статусы, точность", "5", "M3-1", "Точки двигаются; у выбранной кольцо"],
                ["M3-3", "Список, карточка, выбор", "4", "M3-2", "Карта и список выбирают один объект"],
                ["M4-1", "Состояния loading/empty/stale/error/partial", "4", "M3-3", "Каждое состояние вызывается вручную"],
                ["M4-2", "Адаптивность и доступность", "3", "M4-1", "1024 px и мобильный; клавиатура работает"],
                ["M4-3", "Панель здоровья данных", "3", "M4-1", "Источник, возраст, счётчики, пропуски"],
                ["M5-1", "Юнит/компонентные/интеграционные тесты", "5", "M2-2, M3-3", "План тестов из 9.2 покрыт"],
                ["M5-2", "Сборка, Nginx, README, runbook", "4", "M4-2", "URL задеплоен; документация проверена"],
                ["M5-3", "Демо-данные, репетиция, передача", "2", "M5-2", "Демо проходит дважды без вмешательства"],
            ],
            [1.4, 6.4, 1.2, 3.0, 4.8],
            font_size=8.0,
            first_col_bold=True,
            align_center_cols=[2],
        )
        self.p(
            "Сумма — около 58 идеальных часов. Буфер нужен для неизвестного: система координат, политика тайлов, путь "
            "деплоя, особенность браузера. Он не нужен для новых фич."
        )
        self.h2("6.4 Вехи и демо-сценарий")
        self.table(
            ["Веха", "Доказательство", "Решение"],
            [
                ["M0 — контракт заморожен", "Схема и пример проверены продюсером и UI", "Можно строить; изменения — только с версией"],
                ["M1 — первые точки", "Пять тележек из файла двигаются по карте", "Переходить к взаимодействию и отказам"],
                ["M2 — рабочий экран", "Выбор, карточка, точность, легенда, статус", "Показать диспетчеру, собрать замечания"],
                ["M3 — release candidate", "Задеплоенная сборка, тесты, README", "Заморозить объём; только багфиксы"],
                ["M4 — MVP принят", "Чек-лист подписан, демо записано", "Стартовать бэклог фазы 1"],
            ],
            [4.6, 7.4, 4.8],
            font_size=8.4,
            first_col_bold=True,
        )
        self.p("Демо на пять минут", size=12.5, color=INK, bold=True, space_before=4, space_after=4)
        self.numbered([
            "**Открыть страницу.** Назвать площадку, показать три станции, статус live и время обновления.",
            "**Показать точки.** Объяснить цвета и круг точности у выбранной тележки.",
            "**Выбрать тележку.** Сначала мышью, затем клавиатурой через список; показать карточку.",
            "**Двинуть флот.** Запустить генератор или заменить файл; точки обновляются без перезагрузки.",
            "**Сломать специально.** Переименовать файл, показать баннер и последние известные позиции; восстановить и показать recovery.",
            "**Показать шов.** Открыть диагностику, затем интерфейс `FleetRepository` и одну строку composition root. Закрыть дорожной картой фаз 1–2.",
        ])
        self.callout(
            "Репетируйте отказ, а не только happy path",
            "Демо, которое показывает только движение точек, выглядит игрушкой. Демо, которое переживает удалённый файл и "
            "объясняет устаревание, выглядит инженерным продуктом. Отрепетируйте отказ минимум дважды.",
            "info",
        )

    def ch7(self) -> None:
        self.h1("7. Риски")
        self.p(
            "Реестр короткий, потому что объём маленький. Самые высокие риски — не баги React, а несовпадение систем "
            "координат, устаревшие данные под видом live и расползание объёма в сторону позиционирования."
        )
        self.table(
            ["Риск", "В", "С", "Мера", "Триггер"],
            [
                ["Несовпадение систем координат (локальные метры vs WGS84)", "В", "В", "Зафиксировать CRS; конвертировать в продюсере; проверить по известной точке", "Точки смещены на постоянное расстояние"],
                ["Устаревший файл выглядит live", "В", "В", "Проверять `generatedAt`, а не HTTP-статус; stale-баннер; внешняя проверка возраста", "HTTP 200, но позиции замерли"],
                ["Расползание объёма в RSSI/Magma/БД", "В", "В", "Список вне границ; правило изменений; бэклог фаз", "Новая «обязательная» фича на стендапе"],
                ["Тайлы карты заблокированы в закрытой сети", "В", "С", "План площадки или свои тайлы; карта работает без тайлов", "Серые тайлы на демо"],
                ["Yandex Maps требуют поздно", "С", "В", "Изолировать Leaflet за `FleetMap`; уточнить провайдера в день 1", "Ключ API всплыл после сборки"],
                ["Неатомарная запись файла", "С", "В", "Временный файл + rename; прошлый снимок; баннер ошибки", "Периодические ошибки JSON"],
                ["Дрейф схемы между продюсером и UI", "С", "С", "Версия; Zod; ревью контракта; пример в репозитории", "Неизвестные/пропавшие поля"],
                ["Производительность на 1000+ тележек", "С", "С", "Canvas-маркеры, API/WS, кластеризация; бюджет на 100", "Просадки кадров"],
                ["Позиции открыты по URL", "С", "В", "Периметр, отсутствие секретов, HTTPS, privacy review", "Приложение доступно из гостевой сети"],
                ["Сюрпризы интеграции с Magma", "В", "С", "Серверный адаптер; запасной Open5GS; spike на фазе 2", "События не приходят / API нестабилен"],
                ["Часы и часовые пояса", "С", "С", "UTC ISO; NTP; предупреждение о будущем времени", "«-3 с назад» или «через 2 часа»"],
                ["Перфекционизм первого разработчика", "С", "С", "Один порт, без Redux и generic data source; чек-лист ревью", "Абстракций больше, чем фич"],
            ],
            [5.4, 0.9, 0.9, 6.6, 3.0],
            font_size=7.7,
            first_col_bold=True,
            align_center_cols=[1, 2],
        )
        self.p("В — вероятность, С — серьёзность. Таблица пересматривается на каждом гейте.", size=8.4, color=SUBTLE, italic=True)
        self.p("Три риска, которые заслуживают абзаца", size=12.5, color=INK, bold=True, space_before=2, space_after=4)
        self.p(
            "**Несовпадение координат.** Постоянное смещение — самый частый молчаливый отказ. Карта выглядит правдоподобно, "
            "точки двигаются, и только когда диспетчер приходит не к тому подъезду, выясняется, что весь флот смещён на "
            "200 метров. Лечение процедурное: одна эталонная точка в файле, визуальная сверка с планом, подпись CRS до "
            "первого демо."
        )
        self.p(
            "**Устаревшие данные под видом live.** Статический сервер отдаёт 200 для файла, который не менялся три часа. "
            "Если UI считает «запрос успешен» синонимом «данные свежие», он уверенно показывает замерший флот. Правило "
            "одно: свежесть берётся из `generatedAt`, а не из HTTP-статуса."
        )
        self.p(
            "**Расползание объёма.** Вокруг проекта много интересного: калибровка RSSI, события Magma, QoS MQTT, "
            "настройка Калмана, история, геозоны. Каждое может съесть две недели. Защита — таблица «вне границ» и правило "
            "«нельзя показать на демо — не входит в MVP 0.1»."
        )

    def ch8(self) -> None:
        self.h1("8. Переход к Magma без переписывания")
        self.p(
            "MVP файловый, но не тупиковый. Тот же контракт и тот же экран можно кормить HTTP-API, а затем — пайплайном "
            "Magma + MQTT. Важно понимать, что меняется, что остаётся и какие решения сегодня оставляют дверь открытой."
        )
        self.h2("8.1 Что Magma делает и чего не делает")
        self.p(
            "Magma — open-source mobile core: Access Gateway (AGW) обслуживает абонентов на площадке, Orchestrator даёт "
            "API и NMS для управления абонентами, сетями и политиками. Для проекта ценны управление SIM и сессиями, "
            "привязка тележки к соте и события attach/detach/handover."
        )
        self.p(
            "Magma **не является** движком позиционирования. Она не считает мультилатерацию и сама по себе не отдаёт "
            "RSRP/RSRQ соседних сот. Эти измерения собирает модем тележки через бортовой агент. Magma даёт сетевой "
            "контекст и авторитетный сигнал «тележка в сети и прикреплена к такой-то соте»."
        )
        self.h2("8.2 Целевая схема")
        self.table(
            ["Компонент", "Ответственность"],
            [
                ["Бортовой агент", "Читает модем (RSRP/RSRQ, соседи, TA) и публикует в MQTT"],
                ["Magma AGW / Orchestrator", "Служит LTE-сеть, отдаёт события сессий и смены соты"],
                ["Ingest", "Нормализует события и измерения, дедуплицирует, валидирует"],
                ["Движок позиционирования", "Калибровка, фильтрация, взвешенный МНК, Калман"],
                ["Snapshot publisher", "Собирает полный `FleetSnapshot`, отдаёт REST/WebSocket"],
                ["PostGIS / Timescale", "История и retention (фаза 3)"],
                ["React SPA", "Читает только `FleetSnapshot`; не знает про Magma"],
            ],
            [5.2, 11.6],
            font_size=8.4,
            first_col_bold=True,
        )
        self.p(
            "Граница между бэкендом и браузером — вертикальная линия безопасности. Браузер получает снимок по HTTPS/WSS и "
            "никогда не получает учётные данные Magma, MQTT или сырые радиоизмерения."
        )
        self.h2("8.3 Фаза 1: snapshot API")
        self.p(
            "Фаза 1 убирает статический файл из пути браузера, не меняя контракт. Небольшой бэкенд читает файл (или БД) и "
            "отдаёт `GET /api/v1/fleet/snapshot`. Тело — тот же JSON. На фронте добавляется один адаптер и меняется одна "
            "строка в composition root."
        )
        self.code(
            """// src/data/http-fleet-repository.ts
export class HttpFleetRepository implements FleetRepository {
  constructor(private readonly baseUrl: string) {}

  async loadSnapshot({ signal }: { signal?: AbortSignal } = {}): Promise<FleetLoadResult> {
    const response = await fetch(`${this.baseUrl}/api/v1/fleet/snapshot`, {
      signal, headers: { Accept: 'application/json' },
    });
    if (!response.ok) throw new FleetSourceError('http', `HTTP ${response.status}`);
    return parseFleetSnapshot(await response.json()); // тот же парсер
  }
}""",
            "UI не знает, файл это или API. В этом и смысл порта.",
        )
        self.h2("8.4 Фаза 2: Magma, MQTT и движок")
        self.numbered([
            "**Ingest.** Агент читает модем и публикует в MQTT. События Magma приходят из AGW/Orchestrator. Ingest нормализует оба потока.",
            "**Position.** Движок применяет калибровку, фильтрацию, взвешенный МНК и Калман; выдаёт координату, точность, метод и время.",
            "**Publish.** Публикатор собирает полный `FleetSnapshot`, отдаёт REST и WebSocket, пишет историю в PostGIS/Timescale, держит текущее состояние в Redis.",
            "**Consume.** React использует `WebSocketFleetRepository` (или HTTP как fallback) и рисует тот же экран.",
        ])
        self.h2("8.5 Что меняется и что остаётся")
        self.table(
            ["Область", "MVP 0.1", "Фаза 1", "Фаза 2"],
            [
                ["Источник", "Статический JSON", "HTTP API", "API + WebSocket"],
                ["Бэкенд", "Нет", "Сервис снимка", "Ingest + движок + публикатор"],
                ["БД", "Нет", "Опционально", "PostGIS + Timescale + Redis"],
                ["Радио / Magma", "Нет", "Нет", "MQTT + события Magma"],
                ["Репозиторий", "JsonFile", "Http", "WebSocket"],
                ["Контракт", "`FleetSnapshot` v1", "Тот же + поля", "Тот же + поля"],
                ["Карта / экран", "Leaflet + страница", "Без изменений", "Без изменений"],
            ],
            [3.2, 4.4, 4.2, 5.0],
            font_size=8.2,
            first_col_bold=True,
        )
        self.h2("8.6 Чек-лист готовности к Magma")
        self.bullets([
            "**Стабильные ID тележек.** В UI — ID актива; при появлении Magma добавьте необязательный `networkId`/IMSI, а не заменяйте ID.",
            "**Метод — строка, не enum.** Новые методы появляются без релиза фронта; известные подписываются, неизвестные показываются как есть.",
            "**Точность необязательна.** Отсутствие `accuracyM` значит «неизвестно», а не 0.",
            "**Время в UTC ISO.** Magma, MQTT и браузер должны жить в одной временной базе.",
            "**Контракт версионируется.** Мажорное изменение обсуждается; аддитивные поля безопасны.",
            "**Источник за портом.** Браузер не импортирует SDK Magma и не хранит её секреты.",
            "**Нет допущения 1 Гц.** Интервал опроса — конфигурация; WebSocket может push-ить чаще или реже.",
            "**Атомарность снимка сохраняется.** Сообщение WebSocket — полный снимок или документированный патч; MVP понимает только снимки.",
        ])
        self.h2("8.7 Запасной Open5GS")
        self.p(
            "Активность и поддержка Magma — проектный риск. Архитектура от неё не зависит. Если Magma не подойдёт стенду, "
            "Open5GS заменит её за теми же интерфейсами `NetworkEventSource` и `MeasurementSource`. Движок и UI не меняются. "
            "Решение принимать после короткого spike на фазе 2, а не на бумаге."
        )
        self.callout(
            "Не привязывайте домен к ядру",
            "UI не должен знать, Magma это, Open5GS или симулятор. Он знает только снимок. Это и делает требование "
            "«очень гибкая архитектура» реальным, а не лозунгом.",
            "success",
        )

    def ch9(self) -> None:
        self.h1("9. Пошаговая инструкция")
        self.p(
            "Эта глава — для разработчика, который делает MVP впервые. Это не полный учебник, но порядок работ, команды "
            "и ошибки, которые стоят дороже всего. Главное — как можно раньше получить вертикальный срез: один файл, одна "
            "точка, один клик."
        )
        self.h2("9.1 Что нужно")
        self.bullets([
            "**Node.js 20 или 22 LTS** и **pnpm** (или npm; команды ниже используют pnpm).",
            "**Git** и редактор с поддержкой TypeScript и ESLint.",
            "Современный браузер с devtools.",
            "Пример снимка и известная точка на площадке для визуальной проверки координат.",
        ])
        self.h2("9.2 Каркас приложения")
        self.code(
            """mkdir web && cd web
pnpm create vite . --template react-ts
pnpm install
pnpm add leaflet react-leaflet @tanstack/react-query zod
pnpm add -D @types/leaflet vitest @testing-library/react @testing-library/jest-dom jsdom
pnpm dev""",
            "Держите приложение в web/, чтобы документы, пример данных и будущий бэкенд жили рядом.",
        )
        self.p(
            "Сразу добавьте в `package.json` скрипты `lint`, `typecheck`, `test`, `build`. CI должен запускать все четыре. "
            "Сделать это в первый день дешевле, чем потом."
        )
        self.h2("9.3 Порядок работ")
        self.step(1, "Заморозить контракт",
                  "Скопируйте пример в `public/data/fleet.snapshot.json`. Пройдите каждое поле с продюсером. Подтвердите "
                  "WGS84, UTC, единицы и частоту. Это разговор на 30 минут, который экономит дни.")
        self.step(2, "Домен и Zod",
                  "Напишите `FleetSnapshot`, `Truck`, `BaseStation`, `Site`. Схему конверта и схемы записей. Добавьте "
                  "юнит-тесты на валидный и три битых fixture до любого UI.")
        self.step(3, "Репозиторий",
                  "Реализуйте `JsonFileFleetRepository` с fetch, `cache: 'no-store'`, проверкой HTTP, ошибками JSON и "
                  "поштучной валидацией. Тестируйте с mock fetch, а не через карту.")
        self.step(4, "Хук и отладочный вывод",
                  "Покажите количество тележек и имя первой в `<pre>` или простом списке. Это доказывает путь данных до "
                  "того, как Leaflet добавит сложность вёрстки.")
        self.step(5, "Оболочка карты",
                  "`MapContainer` с центром и зумом площадки. Слой тайлов и один жёстко заданный маркер. Сначала "
                  "исправьте высоту контейнера и импорт `leaflet/dist/leaflet.css`, потом всё остальное.")
        self.step(6, "Станции, затем тележки",
                  "Станции проще: они статичны. Затем точки с `key={truck.id}` и `center={[truck.lat, truck.lon]}`. "
                  "Помните: в Leaflet порядок — широта, долгота.")
        self.step(7, "Выбор и карточка",
                  "Поднимите `selectedTruckId` в `FleetMapPage`. Передайте в карту и карточку. Клик по фону сбрасывает "
                  "выбор. Круг точности — только у выбранной.")
        self.step(8, "Состояния",
                  "Loading, empty, stale, refresh error, fatal error, partial-invalid. Каждое вызовите вручную: "
                  "переименуйте файл, испортите запись, отмотайте `generatedAt`, удалите файл. Нельзя протестировать то, "
                  "что нельзя вызвать.")
        self.step(9, "Тесты",
                  "Покройте схему, ошибки репозитория, устаревание, карточку и баннер. Leaflet мокайте в компонентных "
                  "тестах; одну реальную проверку карты оставьте для браузера.")
        self.step(10, "Сборка и деплой",
                  "`pnpm build`, затем `dist/` с конфигурацией Nginx из приложения A. Проверьте base path, "
                  "`Cache-Control: no-store` и SPA-fallback.")
        self.step(11, "Репетиция демо",
                  "Пройдите пятиминутный сценарий дважды, включая отказ. Запишите видео. Записанное демо — лучшая "
                  "страховка от сюрпризов живой сети.")

        self.h2("9.4 Частые ошибки")
        self.table(
            ["Симптом", "Вероятная причина", "Что делать"],
            [
                ["404 на снимок", "Жёсткий `/data/...` при base path", "`${import.meta.env.BASE_URL}data/...`"],
                ["Тайлы слоями / невидимы", "Нет CSS Leaflet", "Импорт `leaflet/dist/leaflet.css`"],
                ["Карта пустая / нулевая высота", "У родителя нет высоты", "Явная высота контейнера, например `calc(100vh - 64px)`"],
                ["Точки в океане", "Перепутаны lat/lon или локальные метры", "Leaflet ждёт `[lat, lon]`; проверить CRS"],
                ["Карта мигает на каждом опросе", "`MapContainer` пересоздаётся", "Держать смонтированным, обновлять пропсы маркеров"],
                ["Запросы накапливаются", "`setInterval` в компоненте", "`refetchInterval` TanStack Query"],
                ["Устаревшие точки выглядят live", "Свежесть по HTTP-статусу", "Проверять `generatedAt`, показывать stale"],
                ["Битая запись обнуляет карту", "Падает парсинг всего снимка", "Валидировать записи по одной, собирать диагностику"],
                ["Секрет попал в бандл", "Секрет в `VITE_*`", "Убрать; переменные Vite публичны"],
                ["Локально работает, на деплое нет", "Не настроен base path / SPA", "Nginx `try_files` + корректный `base`"],
            ],
            [5.2, 5.8, 5.8],
            font_size=8.1,
        )
        self.h2("9.5 Чек-лист первого дня")
        self.bullets([
            "Репозиторий создан; `web/` запускается локально.",
            "Контракт v1 и пример снимка отревьюены с продюсером.",
            "Выбрана известная точка площадки для визуальной проверки координат.",
            "Решение по провайдеру карты зафиксировано: OSM, план площадки или оба.",
            "Известны base path и цель деплоя (корень или `/fleet/`).",
            "Согласованы порог устаревания и словарь статусов.",
            "Сценарий демо написан до того, как появилось приложение.",
        ])

    def ch10(self) -> None:
        self.h1("10. Глоссарий")
        self.table(
            ["Термин", "Значение в документе"],
            [
                ["MVP", "Минимально жизнеспособный продукт: наименьший инкремент, доказывающий ценность и архитектуру."],
                ["Снимок (snapshot)", "Полный JSON-снимок площадки, станций и тележек на один момент."],
                ["Продюсер", "Скрипт или сервис, который пишет файл снимка. Вне границ MVP."],
                ["FleetRepository", "Порт, через который UI загружает снимок. Единственный шов источника данных."],
                ["Адаптер", "Конкретная реализация порта, например `JsonFileFleetRepository`."],
                ["Порт", "Интерфейс, принадлежащий приложению и реализуемый инфраструктурой."],
                ["Домен", "Типы и чистые правила, не зависящие от React, Leaflet и сети."],
                ["WGS84", "Система широты/долготы, которую используют GPS и Leaflet."],
                ["ENU", "Локальные метрические координаты «восток–север–вверх» для расчётов позиционирования."],
                ["Мультилатерация", "Вычисление позиции по расстояниям до нескольких известных станций."],
                ["RSSI / RSRP / RSRQ", "Измерения уровня/качества радиосигнала для оценки расстояния или соты."],
                ["Timing advance", "Сетевое измерение времени, дающее грубую дистанцию до обслуживающей соты."],
                ["Cell ID", "Позиционирование только по обслуживающей соте; очень грубо."],
                ["Радиус точности", "Оценка неопределённости позиции в метрах; не гарантия."],
                ["Устаревший снимок", "Снимок, у которого `generatedAt` старше порога; продюсер мог остановиться."],
                ["Опрос (polling)", "Повторяющаяся загрузка полного снимка с фиксированным интервалом."],
                ["WebSocket", "Постоянное соединение браузер–сервер для push-обновлений; опция фазы 2."],
                ["MQTT", "Лёгкий publish/subscribe-протокол телеметрии; транспорт фазы 2."],
                ["Magma", "Open-source mobile core (AGW + Orchestrator) для частной LTE; источник фазы 2."],
                ["AGW", "Access Gateway в Magma; обслуживает абонентов и отдаёт события сессий."],
                ["Orchestrator", "API/NMS Magma для управления абонентами, сетями и политиками."],
                ["Open5GS", "Open-source ядро 4G/5G; запасной вариант за теми же адаптерами."],
                ["Leaflet", "Open-source библиотека карт, используемая в MVP."],
                ["OSM", "OpenStreetMap; данные и тайлы для разработки."],
                ["Zod", "Библиотека runtime-валидации схем на границе JSON."],
                ["TanStack Query", "Библиотека серверного состояния: опрос, кэш, повторы."],
            ],
            [4.4, 12.4],
            font_size=8.2,
            first_col_bold=True,
        )

    def appendices(self) -> None:
        self.h1("Приложение A. Конфигурация Nginx")
        self.p(
            "Конфигурация отдаёт SPA, отключает кэш снимка и надолго кэширует хешированные ассеты. Предполагается корень; "
            "для подпути настройте `base` во Vite и `location`."
        )
        self.code(
            """server {
    listen 80;
    server_name fleet.example.internal;

    root /usr/share/nginx/html;
    index index.html;

    # Живой снимок нельзя кэшировать.
    location ^~ /data/ {
        add_header Cache-Control "no-store, max-age=0" always;
        try_files $uri =404;
    }

    # Хешированные ассеты можно кэшировать надолго.
    location ^~ /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files $uri =404;
    }

    # SPA-fallback: неизвестный путь отдаёт index.html.
    location / {
        try_files $uri $uri/ /index.html;
    }

    gzip on;
    gzip_types application/json application/javascript text/css image/svg+xml;
    gzip_min_length 1024;

    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "same-origin" always;
}""",
            "Префикс `^~` не даёт регулярному location переопределить no-store для `/data/`.",
        )
        self.callout(
            "Проверяйте заголовки, а не только страницу",
            "DevTools → Network → запрос снимка. Там должно быть `Cache-Control: no-store` и 200. Если ответ пришёл из "
            "disk cache, карта может замереть, пока продюсер здоров.",
            "warning",
        )

        self.h1("Приложение B. Архитектурные решения")
        self.table(
            ["ADR", "Решение", "Следствие"],
            [
                ["ADR-001", "Файловый статический SPA для MVP 0.1", "Быстрое демо, нет бэкенда; файл — временный транспорт"],
                ["ADR-002", "Порт `FleetRepository` + файловый адаптер", "Источник меняется без правок UI"],
                ["ADR-003", "Leaflet + OpenStreetMap", "Без API-ключа; открытая лицензия; простые маркеры и круги"],
                ["ADR-004", "WGS84 — канонический контракт UI", "Нет геодезии в компонентах; метры конвертируются upstream"],
                ["ADR-005", "JSON v1 + Zod на границе", "Runtime-безопасность; версионирование"],
                ["ADR-006", "Опрос 1 Гц вместо WebSocket", "Просто, отлаживаемо, дружелюбно к прокси; апгрейд позже"],
                ["ADR-007", "Без БД и истории", "Меньше объёма; только live-точки"],
                ["ADR-008", "Magma только на сервере, фаза 2", "Нет секретов и API ядра в браузере"],
            ],
            [1.8, 7.4, 7.6],
            font_size=8.3,
            first_col_bold=True,
        )

        self.h1("Приложение C. Чек-лист приёмки")
        self.p("Отмечайте только то, что продемонстрировано, а не то, что реализовано.")
        checks = [
            "Валидный снимок с 3 станциями и 5 тележками отображается за ≤ 2 с",
            "Точки двигаются после замены файла без перезагрузки",
            "Клик по точке открывает правильную карточку",
            "Выбор с клавиатуры через список работает",
            "Круг точности и метод корректны для выбранной тележки",
            "Одна битая запись пропускается, остальные видны, счётчик показан",
            "Отсутствие файла: фатальная ошибка с «Повторить»",
            "Ошибка обновления: последние точки остаются, баннер есть",
            "Старый `generatedAt`: stale-баннер даже при HTTP 200",
            "Пустой массив тележек: пустое состояние, не ошибка",
            "Неизвестный метод показывается как есть, без падения",
            "Тайлы недоступны: точки, станции, легенда и карточка работают",
            "100 тележек: интерфейс отзывчив",
            "Base path: ассеты и данные загружаются",
            "`Cache-Control: no-store` присутствует на снимке",
            "Lint, typecheck, test и production build зелёные",
            "README описывает запуск, сборку, деплой и замену данных",
            "В бандле нет секретов; приложение за согласованным периметром",
            "Демо отрепетировано дважды, включая отказ",
            "Релиз помечен `v0.1.0`, версия сборки видна",
        ]
        self.table(["Готово", "Проверка"], [["☐", c] for c in checks], [1.6, 15.2], font_size=8.4, align_center_cols=[0])

        self.h1("Приложение D. Ссылки")
        refs = [
            ("React", "https://react.dev/", "Компоненты, состояние, эффекты."),
            ("TanStack Query", "https://tanstack.com/query/latest", "Опрос, кэш, повторы, keepPreviousData."),
            ("Zod", "https://zod.dev/", "Runtime-схемы и safeParse."),
            ("Leaflet", "https://leafletjs.com/", "Карта, маркеры, круги, image overlay."),
            ("react-leaflet", "https://react-leaflet.js.org/", "React-обёртка Leaflet."),
            ("Политика тайлов OSM", "https://operations.osmfoundation.org/policies/tiles/", "Почему публичные тайлы — для разработки."),
            ("Magma", "https://magmacore.org/", "AGW, Orchestrator, NMS."),
            ("Magma GitHub", "https://github.com/magma/magma", "Исходники, issues, активность."),
            ("Open5GS", "https://open5gs.org/", "Альтернативное open-source ядро."),
            ("RFC 3339", "https://www.rfc-editor.org/rfc/rfc3339", "Формат времени."),
            ("MDN fetch", "https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API", "AbortController, cache, ответы."),
            ("Vite", "https://vite.dev/", "Сборка, base path, переменные окружения."),
        ]
        for title, url, note in refs:
            p = self.doc.add_paragraph()
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(f"{title} — ")
            r.bold = True
            r.font.size = Pt(9.2)
            self._add_inline(p, url, size=9.0, color=BLUE)
            r = p.add_run(f". {note}")
            r.font.size = Pt(9.2)
            r.font.color.rgb = rgb("334155")
        self.callout(
            "Статус документа",
            "Это MVP 0.1, черновик для ревью. Архитектура намеренно небольшая, швы — явные. Обновляйте ADR при смене "
            "решения и держите пример снимка в синхронизации со схемой.",
            "info",
        )


def build() -> Path:
    b = RuBuilder()
    b.cover()
    b.contents()
    b.summary()
    b.ch1()
    b.ch2()
    b.ch3()
    b.ch4()
    b.ch5()
    b.ch6()
    b.ch7()
    b.ch8()
    b.ch9()
    b.ch10()
    b.appendices()
    out = ROOT / "MVP_Plan_and_Architecture_RU.docx"
    b.doc.save(out)
    print(f"Saved {out} ({out.stat().st_size / 1024:.1f} KB)")
    return out


if __name__ == "__main__":
    build()
