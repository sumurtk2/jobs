"""
Build Spanish market data for the AI exposure treemap.

Reads occupations.csv and scores.json, adapts data for the Spanish market:
- Translates titles and rationales to Spanish
- Scales salaries to EUR (Spanish market levels)
- Scales employment to Spain's ~21M workforce
- Maps education levels to Spanish equivalents
- Translates outlook descriptions

Usage:
    uv run python build_spain_data.py
"""

import csv
import json
import time

# ── Spanish title overrides (better than machine translation) ──────────

TITLE_ES = {
    "Accountants and auditors": "Contables y auditores",
    "Actors": "Actores",
    "Actuaries": "Actuarios",
    "Administrative services and facilities managers": "Directores de servicios administrativos e instalaciones",
    "Adult basic and secondary education and ESL teachers": "Profesores de educación para adultos y español para extranjeros",
    "Advertising sales agents": "Agentes de ventas de publicidad",
    "Advertising, promotions, and marketing managers": "Directores de publicidad, promociones y marketing",
    "Aerospace engineering and operations technologists and technicians": "Técnicos en ingeniería aeroespacial",
    "Aerospace engineers": "Ingenieros aeroespaciales",
    "Agricultural and food science technicians": "Técnicos en ciencias agrícolas y alimentarias",
    "Agricultural and food scientists": "Científicos agrícolas y alimentarios",
    "Agricultural engineers": "Ingenieros agrícolas",
    "Agricultural workers": "Trabajadores agrícolas",
    "Air traffic controllers": "Controladores de tráfico aéreo",
    "Aircraft and avionics equipment mechanics and technicians": "Mecánicos y técnicos de aviación",
    "Airline and commercial pilots": "Pilotos de líneas aéreas y comerciales",
    "Animal care and service workers": "Trabajadores de cuidado de animales",
    "Announcers and DJs": "Locutores y DJs",
    "Anthropologists and archeologists": "Antropólogos y arqueólogos",
    "Arbitrators, mediators, and conciliators": "Árbitros, mediadores y conciliadores",
    "Architects": "Arquitectos",
    "Architectural and engineering managers": "Directores de arquitectura e ingeniería",
    "Archivists, curators, and museum workers": "Archiveros, conservadores y trabajadores de museos",
    "Art directors": "Directores de arte",
    "Assemblers and fabricators": "Ensambladores y montadores",
    "Athletes and sports competitors": "Atletas y deportistas profesionales",
    "Athletic trainers": "Preparadores físicos",
    "Atmospheric scientists, including meteorologists": "Científicos atmosféricos y meteorólogos",
    "Audiologists": "Audiólogos",
    "Automotive body and glass repairers": "Chapistas y cristaleros de automóviles",
    "Automotive service technicians and mechanics": "Mecánicos de automóviles",
    "Bakers": "Panaderos",
    "Barbers, hairstylists, and cosmetologists": "Peluqueros y estilistas",
    "Bartenders": "Camareros de barra (barman)",
    "Bill and account collectors": "Cobradores de facturas y cuentas",
    "Biochemists and biophysicists": "Bioquímicos y biofísicos",
    "Bioengineers and biomedical engineers": "Bioingenieros e ingenieros biomédicos",
    "Biological technicians": "Técnicos en biología",
    "Boilermakers": "Caldereros",
    "Bookkeeping, accounting, and auditing clerks": "Auxiliares de contabilidad y auditoría",
    "Broadcast, sound, and video technicians": "Técnicos de sonido, imagen y emisión",
    "Budget analysts": "Analistas presupuestarios",
    "Bus drivers": "Conductores de autobús",
    "Butchers": "Carniceros",
    "Calibration technologists and technicians": "Técnicos de calibración",
    "Cardiovascular technologists and technicians": "Técnicos cardiovasculares",
    "Career and technical education teachers": "Profesores de formación profesional",
    "Carpenters": "Carpinteros",
    "Cartographers and photogrammetrists": "Cartógrafos y fotogrametristas",
    "Cashiers": "Cajeros",
    "Chefs and head cooks": "Chefs y jefes de cocina",
    "Chemical engineers": "Ingenieros químicos",
    "Chemical technicians": "Técnicos químicos",
    "Chemists and materials scientists": "Químicos y científicos de materiales",
    "Childcare workers": "Cuidadores infantiles",
    "Chiropractors": "Quiroprácticos",
    "Civil engineering technologists and technicians": "Técnicos en ingeniería civil",
    "Civil engineers": "Ingenieros civiles",
    "Claims adjusters, appraisers, examiners, and investigators": "Peritos, tasadores e investigadores de seguros",
    "Clinical laboratory technologists and technicians": "Técnicos de laboratorio clínico",
    "Coaches and scouts": "Entrenadores y ojeadores deportivos",
    "Community health workers": "Trabajadores de salud comunitaria",
    "Compensation and benefits managers": "Directores de compensación y beneficios",
    "Compensation, benefits, and job analysis specialists": "Especialistas en compensación y análisis de puestos",
    "Compliance officers": "Oficiales de cumplimiento normativo",
    "Computer and information research scientists": "Investigadores en informática",
    "Computer and information systems managers": "Directores de sistemas informáticos",
    "Computer hardware engineers": "Ingenieros de hardware informático",
    "Computer network architects": "Arquitectos de redes informáticas",
    "Computer programmers": "Programadores informáticos",
    "Computer support specialists": "Técnicos de soporte informático",
    "Computer systems analysts": "Analistas de sistemas informáticos",
    "Concierges": "Conserjes de hotel",
    "Conservation scientists and foresters": "Científicos de conservación e ingenieros forestales",
    "Construction and building inspectors": "Inspectores de construcción y edificación",
    "Construction equipment operators": "Operadores de maquinaria de construcción",
    "Construction laborers and helpers": "Peones y ayudantes de construcción",
    "Construction managers": "Directores de obra",
    "Cooks": "Cocineros",
    "Correctional officers and bailiffs": "Funcionarios de prisiones y alguaciles",
    "Cost estimators": "Estimadores de costes",
    "Court reporters and simultaneous captioners": "Taquígrafos judiciales y subtituladores",
    "Craft and fine artists": "Artistas plásticos y artesanos",
    "Credit counselors": "Asesores de crédito",
    "Customer service representatives": "Agentes de atención al cliente",
    "Dancers and choreographers": "Bailarines y coreógrafos",
    "Data scientists": "Científicos de datos",
    "Database administrators and architects": "Administradores y arquitectos de bases de datos",
    "Delivery truck drivers and driver/sales workers": "Conductores de reparto",
    "Dental and ophthalmic laboratory technicians and medical appliance technicians": "Técnicos de laboratorio dental y óptico",
    "Dental assistants": "Auxiliares de odontología",
    "Dental hygienists": "Higienistas dentales",
    "Dentists": "Dentistas",
    "Desktop publishers": "Maquetadores",
    "Diagnostic medical sonographers": "Ecografistas médicos",
    "Diesel service technicians and mechanics": "Mecánicos de vehículos diésel",
    "Dietitians and nutritionists": "Dietistas y nutricionistas",
    "Drafters": "Delineantes",
    "Drywall installers, ceiling tile installers, and tapers": "Instaladores de paneles de yeso y falsos techos",
    "Economists": "Economistas",
    "Editors": "Editores",
    "Electrical and electronic engineering technologists and technicians": "Técnicos en ingeniería eléctrica y electrónica",
    "Electrical and electronics engineers": "Ingenieros eléctricos y electrónicos",
    "Electrical and electronics installers and repairers": "Instaladores y reparadores eléctricos y electrónicos",
    "Electrical power-line installers and repairers": "Instaladores y reparadores de líneas eléctricas",
    "Electricians": "Electricistas",
    "Electro-mechanical and mechatronics technologists and technicians": "Técnicos en electromecánica y mecatrónica",
    "Elementary, middle, and high school principals": "Directores de centros educativos",
    "Elevator and escalator installers and repairers": "Instaladores y reparadores de ascensores",
    "Emergency management directors": "Directores de gestión de emergencias",
    "EMTs and paramedics": "Técnicos de emergencias sanitarias",
    "Entertainment and recreation managers": "Directores de entretenimiento y ocio",
    "Environmental engineering technologists and technicians": "Técnicos en ingeniería ambiental",
    "Environmental engineers": "Ingenieros ambientales",
    "Environmental science and protection technicians": "Técnicos de protección ambiental",
    "Environmental scientists and specialists": "Científicos y especialistas ambientales",
    "Epidemiologists": "Epidemiólogos",
    "Exercise physiologists": "Fisiólogos del ejercicio",
    "Farmers, ranchers, and other agricultural managers": "Agricultores, ganaderos y directores de explotaciones agrarias",
    "Fashion designers": "Diseñadores de moda",
    "Film and video editors and camera operators": "Editores de vídeo y operadores de cámara",
    "Financial analysts": "Analistas financieros",
    "Financial clerks": "Auxiliares financieros",
    "Financial examiners": "Inspectores financieros",
    "Financial managers": "Directores financieros",
    "Fire inspectors": "Inspectores de prevención de incendios",
    "Firefighters": "Bomberos",
    "Fishing and hunting workers": "Trabajadores de pesca y caza",
    "Fitness trainers and instructors": "Monitores y entrenadores de fitness",
    "Flight attendants": "Auxiliares de vuelo",
    "Flooring installers and tile and stone setters": "Instaladores de suelos, alicatadores y soladores",
    "Floral designers": "Floristas",
    "Food and beverage serving and related workers": "Camareros y personal de hostelería",
    "Food preparation workers": "Ayudantes de cocina",
    "Food processing equipment workers": "Operadores de equipos de procesamiento de alimentos",
    "Food service managers": "Directores de restauración",
    "Forensic science technicians": "Técnicos en ciencia forense",
    "Forest and conservation workers": "Trabajadores forestales y de conservación",
    "Fundraisers": "Recaudadores de fondos",
    "Funeral service workers": "Trabajadores de servicios funerarios",
    "Gambling services workers": "Trabajadores de casinos y juegos de azar",
    "General maintenance and repair workers": "Trabajadores de mantenimiento general",
    "General office clerks": "Auxiliares administrativos",
    "Genetic counselors": "Asesores genéticos",
    "Geographers": "Geógrafos",
    "Geological and hydrologic technicians": "Técnicos geológicos e hidrológicos",
    "Geoscientists": "Geocientíficos",
    "Glaziers": "Cristaleros",
    "Graphic designers": "Diseñadores gráficos",
    "Grounds maintenance workers": "Trabajadores de mantenimiento de jardines",
    "Hand laborers and material movers": "Peones y mozos de almacén",
    "Hazardous materials removal workers": "Trabajadores de retirada de materiales peligrosos",
    "Health and safety engineers": "Ingenieros de seguridad y salud laboral",
    "Health education specialists": "Especialistas en educación sanitaria",
    "Health information technologists and medical registrars": "Técnicos en información sanitaria",
    "Heating, air conditioning, and refrigeration mechanics and installers": "Técnicos en climatización y refrigeración",
    "Heavy and tractor-trailer truck drivers": "Conductores de camión y vehículos pesados",
    "Heavy vehicle and mobile equipment service technicians": "Técnicos de mantenimiento de maquinaria pesada",
    "High school teachers": "Profesores de educación secundaria y bachillerato",
    "Historians": "Historiadores",
    "Home health and personal care aides": "Auxiliares de ayuda a domicilio",
    "Human resources managers": "Directores de recursos humanos",
    "Human resources specialists": "Especialistas en recursos humanos",
    "Hydrologists": "Hidrólogos",
    "Industrial designers": "Diseñadores industriales",
    "Industrial engineering technologists and technicians": "Técnicos en ingeniería industrial",
    "Industrial engineers": "Ingenieros industriales",
    "Industrial machinery mechanics, machinery maintenance workers, and millwrights": "Mecánicos de maquinaria industrial",
    "Industrial production managers": "Directores de producción industrial",
    "Information clerks": "Auxiliares de información",
    "Information security analysts": "Analistas de seguridad informática",
    "Instructional coordinators": "Coordinadores pedagógicos",
    "Insulation workers": "Instaladores de aislamiento",
    "Insurance sales agents": "Agentes de seguros",
    "Insurance underwriters": "Suscriptores de seguros",
    "Interior designers": "Diseñadores de interiores",
    "Interpreters and translators": "Intérpretes y traductores",
    "Ironworkers": "Ferrallistas y estructuristas metálicos",
    "Janitors and building cleaners": "Personal de limpieza",
    "Jewelers and precious stone and metal workers": "Joyeros y orfebres",
    "Judges and hearing officers": "Jueces y magistrados",
    "Kindergarten and elementary school teachers": "Profesores de educación infantil y primaria",
    "Labor relations specialists": "Especialistas en relaciones laborales",
    "Landscape architects": "Arquitectos paisajistas",
    "Lawyers": "Abogados",
    "Librarians and library media specialists": "Bibliotecarios",
    "Library technicians and assistants": "Auxiliares de biblioteca",
    "Licensed practical and licensed vocational nurses": "Enfermeros prácticos",
    "Loan officers": "Gestores de préstamos",
    "Lodging managers": "Directores de establecimientos hoteleros",
    "Logging workers": "Trabajadores forestales madereros",
    "Logisticians": "Logísticos",
    "Machinists and tool and die makers": "Maquinistas y matriceros",
    "Management analysts": "Consultores de gestión",
    "Manicurists and pedicurists": "Manicuristas y pedicuristas",
    "Marine engineers and naval architects": "Ingenieros navales",
    "Market research analysts": "Analistas de investigación de mercados",
    "Marriage and family therapists": "Terapeutas de pareja y familia",
    "Masonry workers": "Albañiles",
    "Massage therapists": "Masajistas terapéuticos",
    "Material moving machine operators": "Operadores de maquinaria de transporte de materiales",
    "Material recording clerks": "Auxiliares de registro de materiales",
    "Materials engineers": "Ingenieros de materiales",
    "Mathematicians and statisticians": "Matemáticos y estadísticos",
    "Mechanical engineering technologists and technicians": "Técnicos en ingeniería mecánica",
    "Mechanical engineers": "Ingenieros mecánicos",
    "Medical and health services managers": "Directores de servicios sanitarios",
    "Medical assistants": "Auxiliares de medicina",
    "Medical dosimetrists": "Dosimetristas médicos",
    "Medical equipment repairers": "Técnicos de reparación de equipos médicos",
    "Medical records specialists": "Especialistas en registros médicos",
    "Medical scientists": "Científicos médicos",
    "Medical transcriptionists": "Transcriptores médicos",
    "Meeting, convention, and event planners": "Organizadores de eventos y congresos",
    "Metal and plastic machine workers": "Operadores de máquinas de metal y plástico",
    "Microbiologists": "Microbiólogos",
    "Middle school teachers": "Profesores de educación secundaria (ESO)",
    "Military careers": "Carreras militares",
    "Mining and geological engineers": "Ingenieros de minas y geológicos",
    "Models": "Modelos",
    "Music directors and composers": "Directores musicales y compositores",
    "Musicians and singers": "Músicos y cantantes",
    "Natural sciences managers": "Directores de ciencias naturales",
    "Network and computer systems administrators": "Administradores de redes y sistemas informáticos",
    "News analysts, reporters, and journalists": "Periodistas, reporteros y analistas de noticias",
    "Nuclear engineers": "Ingenieros nucleares",
    "Nuclear medicine technologists": "Técnicos en medicina nuclear",
    "Nuclear technicians": "Técnicos nucleares",
    "Nurse anesthetists, nurse midwives, and nurse practitioners": "Enfermeros especializados (anestesia, matronas, enfermería avanzada)",
    "Nursing assistants and orderlies": "Auxiliares de enfermería y celadores",
    "Occupational health and safety specialists and technicians": "Técnicos en prevención de riesgos laborales",
    "Occupational therapists": "Terapeutas ocupacionales",
    "Occupational therapy assistants and aides": "Auxiliares de terapia ocupacional",
    "Oil and gas workers": "Trabajadores del petróleo y gas",
    "Operations research analysts": "Analistas de investigación operativa",
    "Opticians": "Ópticos",
    "Optometrists": "Optometristas",
    "Orthotists and prosthetists": "Ortopedas y protésicos",
    "Painters, construction and maintenance": "Pintores de construcción y mantenimiento",
    "Painting and coating workers": "Operadores de pintura y recubrimiento industrial",
    "Paralegals and legal assistants": "Asistentes jurídicos y paralegales",
    "Personal financial advisors": "Asesores financieros personales",
    "Pest control workers": "Técnicos de control de plagas",
    "Petroleum engineers": "Ingenieros de petróleo",
    "Pharmacists": "Farmacéuticos",
    "Pharmacy technicians": "Técnicos de farmacia",
    "Phlebotomists": "Flebotomistas",
    "Photographers": "Fotógrafos",
    "Physical therapist assistants and aides": "Auxiliares de fisioterapia",
    "Physical therapists": "Fisioterapeutas",
    "Physician assistants": "Asistentes médicos",
    "Physicians and surgeons": "Médicos y cirujanos",
    "Physicists and astronomers": "Físicos y astrónomos",
    "Plumbers, pipefitters, and steamfitters": "Fontaneros e instaladores de tuberías",
    "Podiatrists": "Podólogos",
    "Police and detectives": "Policías e investigadores",
    "Political scientists": "Politólogos",
    "Postal service workers": "Trabajadores de correos",
    "Postsecondary education administrators": "Administradores de educación superior",
    "Postsecondary teachers": "Profesores universitarios",
    "Power plant operators, distributors, and dispatchers": "Operadores de centrales eléctricas",
    "Preschool and childcare center directors": "Directores de centros de educación infantil",
    "Preschool teachers": "Profesores de educación infantil",
    "Private detectives and investigators": "Detectives privados e investigadores",
    "Probation officers and correctional treatment specialists": "Oficiales de libertad condicional",
    "Producers and directors": "Productores y directores",
    "Project management specialists": "Especialistas en gestión de proyectos",
    "Property appraisers and assessors": "Tasadores de inmuebles",
    "Property, real estate, and community association managers": "Administradores de fincas e inmuebles",
    "Psychiatric technicians and aides": "Técnicos y auxiliares de psiquiatría",
    "Psychologists": "Psicólogos",
    "Public relations and fundraising managers": "Directores de relaciones públicas y captación de fondos",
    "Public relations specialists": "Especialistas en relaciones públicas",
    "Public safety telecommunicators": "Teleoperadores de emergencias",
    "Purchasing managers, buyers, and purchasing agents": "Directores de compras y compradores",
    "Quality control inspectors": "Inspectores de control de calidad",
    "Radiation therapists": "Radioterapeutas",
    "Radiologic and MRI technologists": "Técnicos en radiología y resonancia magnética",
    "Railroad workers": "Trabajadores ferroviarios",
    "Real estate brokers and sales agents": "Agentes inmobiliarios",
    "Receptionists": "Recepcionistas",
    "Recreation workers": "Monitores de ocio y tiempo libre",
    "Recreational therapists": "Terapeutas recreativos",
    "Registered nurses": "Enfermeros diplomados",
    "Rehabilitation counselors": "Consejeros de rehabilitación",
    "Respiratory therapists": "Terapeutas respiratorios",
    "Retail sales workers": "Vendedores minoristas",
    "Roofers": "Techadores",
    "Sales engineers": "Ingenieros de ventas",
    "Sales managers": "Directores de ventas",
    "School and career counselors and advisors": "Orientadores escolares y profesionales",
    "Secretaries and administrative assistants": "Secretarios y asistentes administrativos",
    "Securities, commodities, and financial services sales agents": "Agentes de bolsa y servicios financieros",
    "Security guards and gambling surveillance officers": "Guardias de seguridad y vigilantes",
    "Semiconductor processing technicians": "Técnicos de procesamiento de semiconductores",
    "Set and exhibit designers": "Diseñadores de escenarios y exposiciones",
    "Sheet metal workers": "Chapistas industriales",
    "Skincare specialists": "Especialistas en cuidado de la piel (esteticistas)",
    "Small engine mechanics": "Mecánicos de pequeños motores",
    "Social and community service managers": "Directores de servicios sociales y comunitarios",
    "Social and human service assistants": "Asistentes de servicios sociales",
    "Social workers": "Trabajadores sociales",
    "Sociologists": "Sociólogos",
    "Software developers, quality assurance analysts, and testers": "Desarrolladores de software y analistas de calidad",
    "Solar photovoltaic installers": "Instaladores de paneles solares fotovoltaicos",
    "Special education teachers": "Profesores de educación especial",
    "Special effects artists and animators": "Artistas de efectos especiales y animadores",
    "Speech-language pathologists": "Logopedas",
    "Stationary engineers and boiler operators": "Operadores de calderas y equipos fijos",
    "Substance abuse, behavioral disorder, and mental health counselors": "Consejeros de adicciones y salud mental",
    "Surgical assistants and technologists": "Asistentes y técnicos quirúrgicos",
    "Survey researchers": "Investigadores de encuestas",
    "Surveying and mapping technicians": "Técnicos en topografía y cartografía",
    "Surveyors": "Topógrafos",
    "Tax examiners and collectors, and revenue agents": "Inspectores y recaudadores de impuestos",
    "Taxi drivers, shuttle drivers, and chauffeurs": "Taxistas y conductores de VTC",
    "Teacher assistants": "Auxiliares de educación",
    "Technical writers": "Redactores técnicos",
    "Telecommunications technicians": "Técnicos de telecomunicaciones",
    "Tellers": "Cajeros de banca",
    "Top executives": "Altos directivos",
    "Tour and travel guides": "Guías turísticos",
    "Training and development managers": "Directores de formación y desarrollo",
    "Training and development specialists": "Especialistas en formación y desarrollo",
    "Transportation, storage, and distribution managers": "Directores de transporte, almacenamiento y distribución",
    "Travel agents": "Agentes de viajes",
    "Tutors": "Profesores particulares",
    "Umpires, referees, and other sports officials": "Árbitros y jueces deportivos",
    "Urban and regional planners": "Urbanistas y planificadores territoriales",
    "Veterinarians": "Veterinarios",
    "Veterinary assistants and laboratory animal caretakers": "Auxiliares de veterinaria",
    "Veterinary technologists and technicians": "Técnicos veterinarios",
    "Waiters and waitresses": "Camareros",
    "Water and wastewater treatment plant and system operators": "Operadores de plantas de tratamiento de aguas",
    "Water transportation workers": "Trabajadores de transporte marítimo",
    "Web developers and digital designers": "Desarrolladores web y diseñadores digitales",
    "Welders, cutters, solderers, and brazers": "Soldadores y cortadores",
    "Wholesale and manufacturing sales representatives": "Representantes de ventas al por mayor",
    "Wind turbine technicians": "Técnicos de aerogeneradores",
    "Woodworkers": "Ebanistas y trabajadores de la madera",
    "Writers and authors": "Escritores y autores",
    "Zoologists and wildlife biologists": "Zoólogos y biólogos de fauna silvestre",
}

# ── Education mapping ──────────────────────────────────────────────────

EDUCATION_ES = {
    "No formal educational credential": "Sin titulación formal",
    "High school diploma or equivalent": "ESO / Bachillerato",
    "Postsecondary nondegree award": "Certificado de profesionalidad",
    "Some college, no degree": "Formación no reglada",
    "Associate's degree": "FP Grado Superior",
    "Bachelor's degree": "Grado universitario",
    "Master's degree": "Máster",
    "Doctoral or professional degree": "Doctorado",
    "See How to Become One": "Ver requisitos de acceso",
    "": "",
}

# ── Outlook description mapping ────────────────────────────────────────

OUTLOOK_ES = {
    "Much faster than average": "Mucho más rápido que la media",
    "Faster than average": "Más rápido que la media",
    "As fast as average": "Tan rápido como la media",
    "Slower than average": "Más lento que la media",
    "Little or no change": "Poco o ningún cambio",
    "Decline": "Descenso",
    "": "",
}

# ── Salary scaling ─────────────────────────────────────────────────────
# US median ~$60K, Spain median ~€26K → factor ~0.43
# But we also apply sector-specific adjustments and floor at minimum wage

SPAIN_MINIMUM_WAGE = 15876  # €/year (2024)
SALARY_SCALE = 0.43  # general USD→EUR factor for Spain

def scale_salary(us_pay):
    """Convert US annual pay to realistic Spanish EUR salary."""
    if us_pay is None:
        return None
    eur = us_pay * SALARY_SCALE
    # Floor at minimum wage
    eur = max(eur, SPAIN_MINIMUM_WAGE)
    # Round to nearest 100
    return round(eur / 100) * 100


# ── Employment scaling ─────────────────────────────────────────────────
# US ~160M employed, Spain ~21M → factor ~0.131

EMPLOYMENT_SCALE = 0.131

def scale_employment(us_jobs):
    """Scale US employment numbers to Spain's workforce."""
    if us_jobs is None:
        return None
    es_jobs = us_jobs * EMPLOYMENT_SCALE
    # Round to nearest 100, minimum 100
    result = round(es_jobs / 100) * 100
    return max(result, 100)


# ── Rationale translation ──────────────────────────────────────────────

def translate_rationales(rationales):
    """Translate rationale texts to Spanish using deep_translator."""
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='en', target='es')

        translated = {}
        total = len(rationales)
        for i, (slug, text) in enumerate(rationales.items()):
            if not text:
                translated[slug] = ""
                continue
            try:
                # deep_translator has a 5000 char limit, split if needed
                if len(text) > 4500:
                    parts = [text[:len(text)//2], text[len(text)//2:]]
                    result = ""
                    for part in parts:
                        result += translator.translate(part)
                        time.sleep(0.1)
                else:
                    result = translator.translate(text)
                translated[slug] = result
                if (i + 1) % 50 == 0:
                    print(f"  Translated {i+1}/{total} rationales...")
                time.sleep(0.05)  # rate limiting
            except Exception as e:
                print(f"  Warning: Could not translate rationale for {slug}: {e}")
                translated[slug] = text  # fallback to English
        return translated
    except ImportError:
        print("  Warning: deep_translator not available, keeping English rationales")
        return rationales


def main():
    # Load AI exposure scores
    with open("scores.json") as f:
        scores_list = json.load(f)
    scores = {s["slug"]: s for s in scores_list}

    # Load CSV stats
    with open("occupations.csv") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Loaded {len(rows)} occupations from CSV")
    print(f"Loaded {len(scores)} scores from scores.json")

    # Collect rationales for translation
    print("Translating rationales to Spanish...")
    rationales_en = {}
    for row in rows:
        slug = row["slug"]
        score = scores.get(slug, {})
        rationales_en[slug] = score.get("rationale", "")
    rationales_es = translate_rationales(rationales_en)
    print(f"  Done translating rationales")

    # Build Spanish data
    data = []
    missing_titles = []
    for row in rows:
        slug = row["slug"]
        score = scores.get(slug, {})
        title_en = row["title"]

        # Title translation
        title_es = TITLE_ES.get(title_en)
        if not title_es:
            missing_titles.append(title_en)
            title_es = title_en  # fallback

        # Pay conversion
        us_pay = int(row["median_pay_annual"]) if row["median_pay_annual"] else None
        es_pay = scale_salary(us_pay)

        # Employment scaling
        us_jobs = int(row["num_jobs_2024"]) if row["num_jobs_2024"] else None
        es_jobs = scale_employment(us_jobs)

        # Education mapping
        edu_en = row["entry_education"]
        edu_es = EDUCATION_ES.get(edu_en, edu_en)

        # Outlook translation
        outlook_en = row["outlook_desc"]
        outlook_es = OUTLOOK_ES.get(outlook_en, outlook_en)

        data.append({
            "title": title_es,
            "slug": slug,
            "category": row["category"],
            "pay": es_pay,
            "jobs": es_jobs,
            "outlook": int(row["outlook_pct"]) if row["outlook_pct"] else None,
            "outlook_desc": outlook_es,
            "education": edu_es,
            "exposure": score.get("exposure"),
            "exposure_rationale": rationales_es.get(slug, ""),
            "url": row.get("url", ""),
        })

    if missing_titles:
        print(f"\nWarning: {len(missing_titles)} titles had no Spanish translation (using English):")
        for t in missing_titles:
            print(f"  - {t}")

    import os
    os.makedirs("site", exist_ok=True)
    with open("site/data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    print(f"\nWrote {len(data)} occupations to site/data.json")
    total_jobs = sum(d["jobs"] for d in data if d["jobs"])
    print(f"Total jobs represented: {total_jobs:,}")
    total_wages = sum(d["jobs"] * d["pay"] for d in data if d["jobs"] and d["pay"])
    print(f"Total annual wages: €{total_wages:,.0f}")

    # Sanity checks
    pays = [d["pay"] for d in data if d["pay"]]
    print(f"Pay range: €{min(pays):,} - €{max(pays):,}")
    print(f"Median pay: €{sorted(pays)[len(pays)//2]:,}")


if __name__ == "__main__":
    main()
