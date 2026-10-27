# cms/context_processors.py
from .models import (MenuItem,
                     Head,
                     Bakalavriat,
                     Meropriatia,
                     OfficeCommerse,
                     Learning,
                     LearningCarousel,
                     Research,
                     ResearchModal,
                     Organigramma,
                     Projects,
                     ProjectsModal,
                     Portfolio,
                     PortfolioCategory,
                     Main,
                     ScienceDepartmentText,
                     ScienceDepartmentImages,
                     ScienceDepartmentFile,
                     ScienceDepartmentModule,
                     ScienceDepartmentLink,
                     Accreditation,
                     Polozhenia,
                     Academic,
                     Candidates,
                     HeadHunterModel,
                     HHProfile,
                     HHLogo,
                     HHJobVacancyTitle,
                     HHJobVacancySecondTitle,
                     HHJobVacancyDropdown,
                     HHJobExperienceHeader,
                     HHJobExperienceUnderHeader,
                     HHJobExperienceSummary,
                     HHJobConditionsUnderHeader,
                     HHJobConditionsHeader,
                     HHJobConditionsSummary,
                     HHWorkHeader,
                     HHWorkUnderHeader,
                     HHEmployerHeader,
                     HHEmployerUnderHeader,
                     HeaderMain,
                     Footer)

def main_menu_processor(request):
    """
    Контекстный процессор для меню сайта.
    Возвращает список главных пунктов меню с активными детьми.
    """
    # Получаем все корневые элементы меню (parent=None), только активные
    main_menu = MenuItem.objects.filter(parent=None, is_active=True).prefetch_related('children')

    # Добавляем каждому элементу список только активных детей
    for item in main_menu:
        item.active_children = item.children.filter(is_active=True)

    return {
        'main_menu': main_menu
    }

def head_processor(request):
    """
    Контекстный процессор для меню сайта.
    Возвращает список главных пунктов меню с активными детьми.
    """
    # Получаем все корневые элементы меню (parent=None), только активные
    head = Head.objects.filter(is_active=True)

    return {
        'head': head
    }

def bakalavriat_processor(request):
    # Получаем все корневые элементы меню (parent=None), только активные
    bakalavriat = Bakalavriat.objects.filter(is_active=True)

    return {
        'bakalavriat': bakalavriat
    }

def meropriatia_processor(request):
    # Получаем все корневые элементы меню (parent=None), только активные
    meropriatia = Meropriatia.objects.filter(is_active=True)

    return {
        'meropriatia': meropriatia
    }
    
def office_processor(request):
    # Получаем все корневые элементы меню (parent=None), только активные
    office = OfficeCommerse.objects.filter(is_active=True)
        
    return {
        'office': office
    }


def learning_processor(request):
    # Получаем все корневые элементы меню (parent=None), только активные
    learning = Learning.objects.filter(is_active=True)

    return {
        'learning': learning
    }

def learning_carousel_processor(request):
    # Получаем все корневые элементы меню (parent=None), только активные
    learning_carousel = LearningCarousel.objects.filter(is_active=True)

    return {
        'learning_carousel': learning_carousel
    }

def research_processor(request):
    # Получаем все корневые элементы меню (parent=None), только активные
    research = Research.objects.filter(is_active=True)

    return {
        'research': research
    }

def research_modal_processor(request):
    # Получаем все корневые элементы меню (parent=None), только активные
    research_modal = ResearchModal.objects.filter(is_active=True)

    return {
        'research_modal': research_modal
    }

def organigramma_processor(request):
    # Получаем все корневые элементы меню (parent=None), только активные
    organigramma = Organigramma.objects.filter(is_active=True)

    return {
        'organigramma': organigramma
    }

def projects_processor(request):
    # Получаем все корневые элементы меню (parent=None), только активные
    projects = Projects.objects.filter(is_active=True)

    return {
        'projects': projects
    }

def projects_modal_processor(request):
    # Получаем все корневые элементы меню (parent=None), только активные
    projects_modal = ProjectsModal.objects.filter(is_active=True)

    return {
        'projects_modal': projects_modal
    }

def portfolio_processor(request):
    portfolio = Portfolio.objects.filter(is_active=True)

    return {
        'portfolio': portfolio
    }

def portfolio_category_processor(request):
    categories = PortfolioCategory.objects.filter(is_active=True)

    return {
        "categories": categories
    }

def main_processor(request):
    main = Main.objects.filter(is_active=True).order_by("-id")[:1]

    return {
        "main": main
    }

def main_header_processor(request):
    main_header = HeaderMain.objects.filter(is_active=True)

    return {
        "main_header": main_header
    }

def science_dep_images_processor(request):
    science_dep_images = ScienceDepartmentImages.objects.filter(is_active=True)

    return {
        "science_dep_images": science_dep_images
    }

def science_dep_text_processor(request):
    science_dep_text = ScienceDepartmentText.objects.filter(is_active=True)

    return {
        "science_dep_text": science_dep_text
    }

def science_dep_module_processor(request):
    science_dep_module = ScienceDepartmentModule.objects.filter(is_active=True)

    return {
        "science_dep_module": science_dep_module
    }

def science_dep_file_processor(request):
    science_dep_file = ScienceDepartmentFile.objects.filter(is_active=True)

    return {
        "science_dep_file": science_dep_file
    }

def science_dep_link_processor(request):
    science_dep_link = ScienceDepartmentLink.objects.filter(is_active=True)

    return {
        "science_dep_link": science_dep_link
    }

def accreditation_processor(request):
    accreditation = Accreditation.objects.filter(is_active=True)

    return {
        "accreditation": accreditation
    }

def polozhenia_processor(request):
    polozhenia = Polozhenia.objects.filter(is_active=True)

    return {
        "polozhenia": polozhenia
    }

def academicpartners_processor(request):
    academicpartners = Academic.objects.filter(is_active=True)

    return {
        "academicpartners": academicpartners
    }

def candidates_processor(request):
    candidates = Candidates.objects.filter(is_active=True).order_by('-id')

    return {
        "candidates": candidates
    }
    
#def yarmacessor_processor(request):
#    yarmacessor = Yarmarka.objects.filter(is_active=True).order_by('-id')
#    
#    return {"yarmacessor": yarmacessor}
    
#New project don't touch
def headhunter_processor(request):
    headhunter = HeadHunterModel.objects.filter(is_active=True).order_by('id')

    return {
        "headhunter": headhunter
    }

def hh_profile_processor(request):
    hh_profile = HHProfile.objects.filter(is_active=True).order_by('id')

    return {
        "hh_profile": hh_profile
    }
def logotip_processor(request):
    logo = HHLogo.objects.filter(is_active=True).order_by('id')

    return {
        "logo": logo
    }
def hh_job_vacancy_processor(request):
    title_cv = HHJobVacancyTitle.objects.filter(is_active=True).order_by('id')

    return {
        "title_cv": title_cv
    }

def hh_title_processor(request):
    second_title_cv = HHJobVacancySecondTitle.objects.filter(is_active=True).order_by('id')

    return {
        "second_title_cv": second_title_cv
    }

def dropdown_vacancy_processor(request):
    dropdown_title_cv = HHJobVacancyDropdown.objects.filter(is_active=True).order_by('id')

    return {
        "dropdown_title_cv": dropdown_title_cv
    }

def job_exp_header_processor(request):
    job_experience_header = HHJobExperienceHeader.objects.filter(is_active=True).order_by('id')

    return {
        "job_experience_header": job_experience_header
    }

def job_exp_under_header_processor(request):
    job_experience_under_header = HHJobExperienceUnderHeader.objects.filter(is_active=True).order_by('id')

    return {
        "job_experience_under_header": job_experience_under_header
    }

def jobs_processor(request):
    jobs = HHJobExperienceSummary.objects.filter(is_active=True).order_by('id')

    return {
        "jobs": jobs
    }

def job_conditions_header_processor(request):
    job_conditions_header = HHJobConditionsHeader.objects.filter(is_active=True).order_by('id')

    return {
        "job_conditions_header": job_conditions_header
    }

def job_conditions_under_header_processor(request):
    job_conditions_underheader = HHJobConditionsUnderHeader.objects.filter(is_active=True).order_by('id')

    return {
        "job_conditions_underheader": job_conditions_underheader
    }

def job_conditions_candidate_processor(request):
    job_conditions_candidate = HHJobConditionsSummary.objects.filter(is_active=True).order_by('id')

    return {
        "job_conditions_candidate": job_conditions_candidate
    }

def format_work_header_processor(request):
    format_work_header = HHWorkHeader.objects.filter(is_active=True).order_by('id')

    return {
        "format_work_header": format_work_header
    }

def format_work_under_header_processor(request):
    format_work_under_header = HHWorkUnderHeader.objects.filter(is_active=True).order_by('id')

    return {
        "format_work_under_header": format_work_under_header
    }

def form_employer_header_processor(request):
    form_employer_header = HHEmployerHeader.objects.filter(is_active=True).order_by('id')

    return {
        "form_employer_header": form_employer_header
    }

def form_employer_under_header_processor(request):
    form_employer_under_header = HHEmployerUnderHeader.objects.filter(is_active=True).order_by('id')

    return {
        "form_employer_under_header": form_employer_under_header
    }

def footer_processor(request):
    footer_processor = Footer.objects.filter(is_active=True).order_by('id')

    return {
        "footer_processor": footer_processor
    }