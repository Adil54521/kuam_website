"""Rule-based classification of news by the 17 UN Sustainable Development Goals."""

from html import unescape
from functools import lru_cache
import re

from django.utils.html import strip_tags


MIN_SDG_SCORE = 8
MAX_SDG_TAGS = 3

# Keywords with weight 1 or 2 are context hints only. Their total contribution to
# one goal is capped so that words such as "student" cannot assign a goal alone.
MAX_WEAK_KEYWORD_SCORE = 3


SDG_RULES = {
    1: {
        "number": 1,
        "name": "Ликвидация нищеты",
        "color": "#E5243B",
        "keywords": {
            "ликвидация нищеты": 10,
            "борьба с бедностью": 9,
            "социальная защита малоимущих": 9,
            "адресная социальная помощь": 8,
            "малообеспеченные семьи": 6,
            "черта бедности": 7,
            "кедейлікті жою": 10,
            "кедейлікпен күрес": 9,
            "атаулы әлеуметтік көмек": 8,
            "аз қамтылған отбасылар": 6,
            "no poverty": 10,
            "poverty reduction": 9,
            "social protection for the poor": 8,
        },
    },
    2: {
        "number": 2,
        "name": "Ликвидация голода",
        "color": "#DDA63A",
        "keywords": {
            "ликвидация голода": 10,
            "продовольственная безопасность": 9,
            "борьба с недоеданием": 9,
            "устойчивое сельское хозяйство": 8,
            "школьное питание": 6,
            "банк продовольствия": 7,
            "аштықты жою": 10,
            "азық-түлік қауіпсіздігі": 9,
            "тұрақты ауыл шаруашылығы": 8,
            "мектептегі тамақтану": 6,
            "zero hunger": 10,
            "food security": 9,
            "sustainable agriculture": 8,
        },
    },
    3: {
        "number": 3,
        "name": "Хорошее здоровье и благополучие",
        "color": "#4C9F38",
        "keywords": {
            "хорошее здоровье и благополучие": 10,
            "общественное здоровье": 8,
            "профилактика заболеваний": 8,
            "психическое здоровье": 8,
            "здоровый образ жизни": 7,
            "донорство крови": 7,
            "вакцинация": 6,
            "медицинская помощь": 6,
            "жақсы денсаулық және әл-ауқат": 10,
            "қоғамдық денсаулық": 8,
            "аурулардың алдын алу": 8,
            "психикалық денсаулық": 8,
            "салауатты өмір салты": 7,
            "good health and well-being": 10,
            "disease prevention": 8,
            "mental health": 8,
            "healthcare access": 7,
            "спорт": 1,
            "sports": 1,
            "спорттық": 1,
        },
    },
    4: {
        "number": 4,
        "name": "Качественное образование",
        "color": "#C5192D",
        "keywords": {
            "качественное образование": 10,
            "день знаний": 9,
            "образовательная программа": 8,
            "инклюзивное образование": 9,
            "повышение квалификации педагогов": 8,
            "цифровая грамотность": 7,
            "академическая честность": 9,
            "доступ к образованию": 8,
            "сапалы білім": 10,
            "білім күні": 9,
            "білім беру бағдарламасы": 8,
            "инклюзивті білім беру": 9,
            "академиялық адалдық": 9,
            "білімге қолжетімділік": 8,
            "quality education": 10,
            "knowledge day": 9,
            "educational programme": 8,
            "educational program": 8,
            "inclusive education": 9,
            "academic integrity": 9,
            "student": 1,
            "студент": 1,
            "студентка": 1,
            "обучающийся": 1,
            "преподаватель": 1,
            "оқытушы": 1,
            "білім алушы": 1,
        },
    },
    5: {
        "number": 5,
        "name": "Гендерное равенство",
        "color": "#FF3A21",
        "keywords": {
            "гендерное равенство": 10,
            "равная оплата труда": 8,
            "права женщин": 8,
            "расширение прав и возможностей женщин": 9,
            "противодействие домашнему насилию": 9,
            "женщины в руководстве": 7,
            "гендерлік теңдік": 10,
            "әйелдердің құқықтары": 8,
            "тұрмыстық зорлық-зомбылыққа қарсы іс-қимыл": 9,
            "әйелдердің мүмкіндіктерін кеңейту": 9,
            "gender equality": 10,
            "women's rights": 8,
            "equal pay": 8,
            "women's empowerment": 9,
            "domestic violence prevention": 9,
        },
    },
    6: {
        "number": 6,
        "name": "Чистая вода и санитария",
        "color": "#26BDE2",
        "keywords": {
            "чистая вода": 9,
            "чистая вода и санитария": 10,
            "доступ к питьевой воде": 9,
            "очистка сточных вод": 8,
            "качество питьевой воды": 8,
            "водоснабжение и санитария": 9,
            "таза су": 9,
            "таза су және санитария": 10,
            "ауыз суға қолжетімділік": 9,
            "ағынды суларды тазарту": 8,
            "сумен жабдықтау": 6,
            "clean water and sanitation": 10,
            "access to drinking water": 9,
            "wastewater treatment": 8,
            "water quality": 7,
        },
    },
    7: {
        "number": 7,
        "name": "Недорогостоящая и чистая энергия",
        "color": "#FCC30B",
        "keywords": {
            "недорогостоящая и чистая энергия": 10,
            "возобновляемые источники энергии": 10,
            "возобновляемая энергия": 9,
            "солнечные панели": 9,
            "солнечная энергетика": 8,
            "ветровая энергетика": 8,
            "энергоэффективность": 7,
            "қолжетімді және таза энергия": 10,
            "жаңартылатын энергия көздері": 10,
            "күн панельдері": 9,
            "күн энергетикасы": 8,
            "жел энергетикасы": 8,
            "affordable and clean energy": 10,
            "renewable energy sources": 10,
            "renewable energy": 9,
            "solar panels": 9,
            "wind energy": 8,
            "energy efficiency": 7,
        },
    },
    8: {
        "number": 8,
        "name": "Достойная работа и экономический рост",
        "color": "#A21942",
        "keywords": {
            "достойная работа и экономический рост": 10,
            "трудоустройство выпускников": 10,
            "ярмарка вакансий": 9,
            "охрана труда": 7,
            "достойные условия труда": 8,
            "молодежное предпринимательство": 8,
            "создание рабочих мест": 8,
            "лайықты еңбек және экономикалық өсу": 10,
            "түлектерді жұмысқа орналастыру": 10,
            "бос орындар жәрмеңкесі": 9,
            "еңбекті қорғау": 7,
            "жұмыс орындарын құру": 8,
            "decent work and economic growth": 10,
            "graduate employment": 10,
            "job fair": 9,
            "occupational safety": 7,
            "job creation": 8,
        },
    },
    9: {
        "number": 9,
        "name": "Индустриализация, инновации и инфраструктура",
        "color": "#FD6925",
        "keywords": {
            "индустриализация, инновации и инфраструктура": 10,
            "устойчивая инфраструктура": 9,
            "промышленные инновации": 8,
            "технологический трансфер": 8,
            "цифровая инфраструктура": 8,
            "научно-технологический парк": 8,
            "индустрияландыру, инновациялар және инфрақұрылым": 10,
            "тұрақты инфрақұрылым": 9,
            "технологиялар трансфері": 8,
            "цифрлық инфрақұрылым": 8,
            "industry, innovation and infrastructure": 10,
            "sustainable infrastructure": 9,
            "technology transfer": 8,
            "digital infrastructure": 8,
            "innovation": 2,
            "инновация": 2,
            "инновациялық": 2,
        },
    },
    10: {
        "number": 10,
        "name": "Уменьшение неравенства",
        "color": "#DD1367",
        "keywords": {
            "уменьшение неравенства": 10,
            "сокращение неравенства": 10,
            "социальная интеграция": 8,
            "равные возможности": 8,
            "доступная среда": 7,
            "защита прав мигрантов": 8,
            "теңсіздікті азайту": 10,
            "әлеуметтік интеграция": 8,
            "тең мүмкіндіктер": 8,
            "қолжетімді орта": 7,
            "reduced inequalities": 10,
            "reducing inequality": 10,
            "social inclusion": 8,
            "equal opportunities": 8,
            "migrant rights": 8,
        },
    },
    11: {
        "number": 11,
        "name": "Устойчивые города и населённые пункты",
        "color": "#FD9D24",
        "keywords": {
            "устойчивые города и населённые пункты": 10,
            "устойчивые города": 9,
            "городская мобильность": 8,
            "доступное жилье": 8,
            "общественный транспорт": 7,
            "благоустройство городской среды": 8,
            "безопасность дорожного движения": 7,
            "тұрақты қалалар мен елді мекендер": 10,
            "қалалық мобильділік": 8,
            "қолжетімді тұрғын үй": 8,
            "қоғамдық көлік": 7,
            "sustainable cities and communities": 10,
            "urban mobility": 8,
            "affordable housing": 8,
            "public transport": 7,
            "road safety": 7,
        },
    },
    12: {
        "number": 12,
        "name": "Ответственное потребление и производство",
        "color": "#BF8B2E",
        "keywords": {
            "ответственное потребление и производство": 10,
            "переработка отходов": 10,
            "раздельный сбор": 9,
            "сокращение пищевых отходов": 8,
            "циркулярная экономика": 9,
            "осознанное потребление": 8,
            "жауапты тұтыну және өндіріс": 10,
            "қалдықтарды қайта өңдеу": 10,
            "қалдықтарды бөлек жинау": 9,
            "айналмалы экономика": 9,
            "responsible consumption and production": 10,
            "waste recycling": 10,
            "separate waste collection": 9,
            "circular economy": 9,
            "food waste reduction": 8,
        },
    },
    13: {
        "number": 13,
        "name": "Борьба с изменением климата",
        "color": "#3F7E44",
        "keywords": {
            "борьба с изменением климата": 10,
            "изменение климата": 10,
            "сокращение выбросов": 9,
            "углеродная нейтральность": 9,
            "парниковые газы": 8,
            "адаптация к изменению климата": 9,
            "климаттың өзгеруімен күрес": 10,
            "климаттың өзгеруі": 10,
            "шығарындыларды азайту": 9,
            "көміртегі бейтараптығы": 9,
            "парниктік газдар": 8,
            "climate action": 10,
            "climate change": 10,
            "emissions reduction": 9,
            "carbon neutrality": 9,
            "greenhouse gases": 8,
        },
    },
    14: {
        "number": 14,
        "name": "Сохранение морских экосистем",
        "color": "#0A97D9",
        "keywords": {
            "сохранение морских экосистем": 10,
            "загрязнение океана": 9,
            "загрязнение морей": 9,
            "морское биоразнообразие": 9,
            "устойчивое рыболовство": 8,
            "пластик в океане": 8,
            "теңіз экожүйелерін сақтау": 10,
            "мұхиттың ластануы": 9,
            "теңіз биоалуантүрлілігі": 9,
            "тұрақты балық аулау": 8,
            "life below water": 10,
            "marine ecosystems": 9,
            "ocean pollution": 9,
            "marine biodiversity": 9,
            "sustainable fishing": 8,
        },
    },
    15: {
        "number": 15,
        "name": "Сохранение экосистем суши",
        "color": "#56C02B",
        "keywords": {
            "сохранение экосистем суши": 10,
            "сохранение биоразнообразия": 9,
            "восстановление лесов": 9,
            "посадка деревьев": 8,
            "борьба с опустыниванием": 9,
            "охрана редких видов": 8,
            "жер экожүйелерін сақтау": 10,
            "биоалуантүрлілікті сақтау": 9,
            "ормандарды қалпына келтіру": 9,
            "ағаш отырғызу": 8,
            "шөлейттенуге қарсы күрес": 9,
            "life on land": 10,
            "biodiversity conservation": 9,
            "forest restoration": 9,
            "tree planting": 8,
            "combating desertification": 9,
        },
    },
    16: {
        "number": 16,
        "name": "Мир, правосудие и эффективные институты",
        "color": "#00689D",
        "keywords": {
            "мир, правосудие и эффективные институты": 10,
            "верховенство закона": 9,
            "доступ к правосудию": 9,
            "противодействие коррупции": 9,
            "права человека": 8,
            "академическая честность": 6,
            "мир, әділдік және тиімді институттар": 10,
            "заң үстемдігі": 9,
            "сот төрелігіне қолжетімділік": 9,
            "сыбайлас жемқорлыққа қарсы іс-қимыл": 9,
            "адам құқықтары": 8,
            "peace, justice and strong institutions": 10,
            "rule of law": 9,
            "access to justice": 9,
            "anti-corruption": 9,
            "human rights": 8,
        },
    },
    17: {
        "number": 17,
        "name": "Партнёрство в интересах устойчивого развития",
        "color": "#19486A",
        "keywords": {
            "партнёрство в интересах устойчивого развития": 10,
            "партнерство в интересах устойчивого развития": 10,
            "международное сотрудничество": 9,
            "международное партнёрство": 8,
            "международное партнерство": 8,
            "совместный меморандум": 7,
            "тұрақты даму мақсатындағы әріптестік": 10,
            "халықаралық ынтымақтастық": 9,
            "халықаралық әріптестік": 8,
            "әріптестік туралы меморандум": 7,
            "partnerships for the goals": 10,
            "international cooperation": 9,
            "international partnership": 8,
            "memorandum of cooperation": 7,
            "меморандум": 2,
            "партнёр": 1,
            "партнер": 1,
            "серіктес": 1,
            "partner": 1,
        },
    },
}


def _normalize_text(value):
    """Return plain, lowercase text with normalized whitespace."""
    if value is None:
        return ""
    text_with_tag_separators = re.sub(r"<[^>]+>", " ", str(value))
    plain_text = unescape(strip_tags(text_with_tag_separators)).lower().replace("ё", "е")
    return " ".join(plain_text.split())


@lru_cache(maxsize=None)
def _keyword_pattern(keyword):
    return re.compile(rf"(?<!\w){re.escape(keyword)}(?!\w)", flags=re.IGNORECASE)


def _contains_keyword(text, keyword):
    """Match a complete keyword/phrase without matching it inside another word."""
    return _keyword_pattern(keyword).search(text) is not None


def classify_news(title="", content_rus="", content_kaz="", content_eng=""):
    """Return up to three SDGs whose weighted keywords match the news text."""
    normalized_title = _normalize_text(title)
    normalized_content = _normalize_text(
        " ".join(
            str(value or "")
            for value in (content_rus, content_kaz, content_eng)
        )
    )

    results = []

    for rule in SDG_RULES.values():
        score = 0
        weak_score = 0
        matched_keywords = []

        for raw_keyword, weight in rule["keywords"].items():
            keyword = _normalize_text(raw_keyword)
            title_match = _contains_keyword(normalized_title, keyword)
            content_match = _contains_keyword(normalized_content, keyword)

            if not title_match and not content_match:
                continue

            # A keyword found in both places is counted once, at its maximum
            # (title) value rather than being added twice.
            keyword_score = weight * 3 if title_match else weight
            if weight <= 2:
                allowed = max(0, MAX_WEAK_KEYWORD_SCORE - weak_score)
                contribution = min(keyword_score, allowed)
                weak_score += contribution
                score += contribution
            else:
                score += keyword_score

            matched_keywords.append(raw_keyword)

        if score >= MIN_SDG_SCORE:
            results.append(
                {
                    "number": rule["number"],
                    "name": rule["name"],
                    "score": score,
                    "color": rule["color"],
                    "matched_keywords": matched_keywords,
                }
            )

    results.sort(key=lambda item: (-item["score"], item["number"]))
    return results[:MAX_SDG_TAGS]


def attach_sdg_tags(news_object):
    """Attach transient SDG tags to a News-like object and return the object."""
    title = getattr(news_object, "title", "") or ""
    if not title.strip():
        for content_field in ("content_rus", "content_kaz", "content_eng"):
            content = getattr(news_object, content_field, "") or ""
            heading_match = re.search(
                r"<h[1-3]\b[^>]*>(.*?)</h[1-3]\s*>",
                content,
                flags=re.IGNORECASE | re.DOTALL,
            )
            if heading_match:
                title = unescape(strip_tags(heading_match.group(1)))
                break

    news_object.sdg_tags = classify_news(
        title=title,
        content_rus=getattr(news_object, "content_rus", ""),
        content_kaz=getattr(news_object, "content_kaz", ""),
        content_eng=getattr(news_object, "content_eng", ""),
    )
    return news_object


def get_sdg_goals():
    """Return template-safe public data for all SDGs without classification rules."""
    return [
        {
            "number": rule["number"],
            "name": rule["name"],
            "color": rule["color"],
        }
        for rule in SDG_RULES.values()
    ]
