<?xml version="1.0" encoding="UTF-8"?>
<!-- Це оголошення XML документа. Вказує версію XML (1.0) та кодування (UTF-8) -->

<!DOCTYPE insurance_database [
<!-- DOCTYPE - це оголошення типу документа. 
     Воно каже: "Зараз я опишу правила для документа з кореневим елементом insurance_database"
     Квадратні дужки [ ] - всередині них пишуться всі правила DTD -->

<!-- ==================== КОРЕНЕВИЙ ЕЛЕМЕНТ ==================== -->

<!ELEMENT insurance_database (agreements)>
<!-- ELEMENT - це ключове слово, яке означає "Оголошую елемент"
     insurance_database - назва елемента, який ми оголошуємо
     (agreements) - у круглих дужках вказується, ЩО має бути всередині цього елемента
     Читається так: "Елемент insurance_database ПОВИНЕН містити всередині один елемент agreements"
     Це як правило: якщо є <insurance_database>, то всередині ОБОВ'ЯЗКОВО має бути <agreements> -->

<!ATTLIST insurance_database export_date CDATA #REQUIRED system CDATA #REQUIRED>
<!-- ATTLIST - це "Attribute List" - список атрибутів
     Читається: "Для елемента insurance_database оголошую атрибути"

     insurance_database - для якого елемента ці атрибути

     export_date - назва першого атрибута
     CDATA - тип даних атрибута (Character Data - будь-який текст)
     #REQUIRED - цей атрибут ОБОВ'ЯЗКОВИЙ (без нього елемент недійсний)

     system - назва другого атрибута
     CDATA - теж текст
     #REQUIRED - теж обов'язковий

     Приклад використання:
     <insurance_database export_date="2025-10-20" system="Insurance System v1.0"> -->

<!-- ==================== КОЛЕКЦІЯ ДОГОВОРІВ ==================== -->

<!ELEMENT agreements (agreement*)>
<!-- agreements - назва елемента
     (agreement*) - всередині можуть бути елементи agreement
     * (зірочка) - означає "нуль або більше"

     Тобто може бути:
     - <agreements></agreements>  ← порожній, без жодного agreement (0 разів)
     - <agreements><agreement>...</agreement></agreements>  ← один agreement (1 раз)
     - <agreements><agreement>...</agreement><agreement>...</agreement></agreements>  ← багато (∞ разів) -->

<!-- ==================== ДОГОВІР ==================== -->

<!ELEMENT agreement (conclusion_date, total_insurance_amount, duration_months, insurance_policies)>
<!-- agreement - елемент договору
     (conclusion_date, total_insurance_amount, duration_months, insurance_policies) -
     КОМИ між елементами означають ПОСЛІДОВНІСТЬ

     Читається: "Всередині agreement мають бути САМЕ ЦІ елементи САМЕ В ЦЬОМУ ПОРЯДКУ":
     1. Спочатку conclusion_date
     2. Потім total_insurance_amount
     3. Потім duration_months
     4. І в кінці insurance_policies

     Жодного іншого елемента бути не може!
     Змінювати порядок не можна! -->

<!ATTLIST agreement id CDATA #REQUIRED status CDATA #REQUIRED>
<!-- Для елемента agreement два обов'язкові атрибути:
     id - ідентифікатор (текст, обов'язковий)
     status - статус (текст, обов'язковий)

     Приклад:
     <agreement id="5" status="Cancelled"> -->

<!-- ==================== ПРОСТІ ЕЛЕМЕНТИ ДОГОВОРУ ==================== -->

<!ELEMENT conclusion_date (#PCDATA)>
<!-- conclusion_date - дата укладення договору
     #PCDATA - "Parsed Character Data" - текстові дані, які парсяться (обробляються)
     Це означає: всередині цього елемента просто текст, ніяких інших елементів

     Різниця між PCDATA і CDATA:
     - #PCDATA використовується для ВМІСТУ елементів (між тегами)
     - CDATA використовується для АТРИБУТІВ

     Приклад:
     <conclusion_date>2022-04-02</conclusion_date> -->

<!ELEMENT total_insurance_amount (#PCDATA)>
<!-- Загальна сума страхування - просто текст (число)
     Приклад: <total_insurance_amount>430371.97</total_insurance_amount> -->

<!ELEMENT duration_months (#PCDATA)>
<!-- Тривалість у місяцях - просто текст (число)
     Приклад: <duration_months>24</duration_months> -->

<!-- ==================== ПОЛІСИ ==================== -->

<!ELEMENT insurance_policies (policy*)>
<!-- insurance_policies - колекція полісів
     (policy*) - може містити нуль або більше елементів policy
     Аналогічно до agreements -->

<!ELEMENT policy (start_date, end_date, insurance_amount, insured_persons)>
<!-- policy - окремий поліс
     Послідовність з 4 обов'язкових елементів (через кому = порядок важливий):
     1. start_date - дата початку
     2. end_date - дата закінчення
     3. insurance_amount - сума страхування
     4. insured_persons - застраховані особи -->

<!ATTLIST policy id CDATA #REQUIRED>
<!-- У полісу один обов'язковий атрибут - id
     Приклад: <policy id="680"> -->

<!ELEMENT start_date (#PCDATA)>
<!ELEMENT end_date (#PCDATA)>
<!ELEMENT insurance_amount (#PCDATA)>
<!-- Три прості елементи з текстовим вмістом
     Приклад:
     <start_date>2022-10-27</start_date>
     <end_date>2023-10-22</end_date>
     <insurance_amount>5019054.65</insurance_amount> -->

<!-- ==================== ЗАСТРАХОВАНІ ОСОБИ ==================== -->

<!ELEMENT insured_persons (insured*)>
<!-- insured_persons - колекція застрахованих осіб
     (insured*) - нуль або більше осіб -->

<!ELEMENT insured (address?, phone_number?, email?, gender, birth_date, insurance_objects, person)>
<!-- insured - застрахована особа

     ВАЖЛИВО! Знак питання (?) означає "необов'язковий елемент" (0 або 1 раз):
     address? - адреса може бути, а може не бути
     phone_number? - телефон може бути, а може не бути
     email? - email може бути, а може не бути

     БЕЗ знаку питання = ОБОВ'ЯЗКОВИЙ елемент (рівно 1 раз):
     gender - стать (обов'язково)
     birth_date - дата народження (обов'язково)
     insurance_objects - об'єкти страхування (обов'язково, але може бути порожнім)
     person - дані про персону (обов'язково)

     Приклад:
     <insured>
       <address>...</address>      ← може не бути
       <phone_number>...</phone_number>  ← може не бути
       <email>...</email>          ← може не бути
       <gender>M</gender>          ← ОБОВ'ЯЗКОВО
       <birth_date>1972-07-15</birth_date>  ← ОБОВ'ЯЗКОВО
       <insurance_objects>...</insurance_objects>  ← ОБОВ'ЯЗКОВО
       <person>...</person>        ← ОБОВ'ЯЗКОВО
     </insured> -->

<!ATTLIST insured id CDATA #REQUIRED person_ref CDATA #REQUIRED>
<!-- Два обов'язкові атрибути:
     id - ідентифікатор застрахованої особи
     person_ref - посилання на елемент person (зв'язок)

     Приклад: <insured id="80" person_ref="382"> -->

<!ELEMENT address (#PCDATA)>
<!ELEMENT phone_number (#PCDATA)>
<!ELEMENT email (#PCDATA)>
<!ELEMENT gender (#PCDATA)>
<!ELEMENT birth_date (#PCDATA)>
<!-- П'ять простих текстових елементів
     Приклад:
     <address>Одеса, вул. Петлюри, 29, кв. 20</address>
     <phone_number>+380999289334</phone_number>
     <email>client80@example.com</email>
     <gender>M</gender>
     <birth_date>1972-07-15</birth_date> -->

<!-- ==================== ОБ'ЄКТИ СТРАХУВАННЯ ==================== -->

<!ELEMENT insurance_objects (insurance_object*)>
<!-- insurance_objects - колекція об'єктів страхування
     (insurance_object*) - нуль або більше об'єктів
     Може бути порожнім: <insurance_objects></insurance_objects> або <insurance_objects/> -->

<!ELEMENT insurance_object (insured_ref, property_ref, property)>
<!-- insurance_object - окремий застрахований об'єкт
     Три обов'язкові елементи по порядку:
     1. insured_ref - посилання на застраховану особу
     2. property_ref - посилання на майно
     3. property - дані про майно -->

<!ATTLIST insurance_object id CDATA #REQUIRED type CDATA #REQUIRED>
<!-- Два обов'язкові атрибути:
     id - ідентифікатор об'єкта
     type - тип страхування (Health, Vehicle, Life, Property, Liability)

     Приклад: <insurance_object id="317" type="Health"> -->

<!ELEMENT insured_ref (#PCDATA)>
<!ELEMENT property_ref (#PCDATA)>
<!-- Два прості елементи - посилання (зазвичай містять ID)
     Приклад:
     <insured_ref>80</insured_ref>
     <property_ref>234</property_ref> -->

<!-- ==================== МАЙНО ==================== -->

<!ELEMENT property (prop)>
<!-- property - обгортка для майна
     (prop) - всередині ОБОВ'ЯЗКОВО один елемент prop
     Чому така структура? Це дозволяє розширювати схему в майбутньому -->

<!ELEMENT prop (description, value, year_of_issue?, location?)>
<!-- prop - власне майно
     Чотири елементи:
     description - опис (ОБОВ'ЯЗКОВИЙ)
     value - вартість (ОБОВ'ЯЗКОВА)
     year_of_issue? - рік випуску (НЕОБОВ'ЯЗКОВИЙ, може не бути)
     location? - місцезнаходження (НЕОБОВ'ЯЗКОВЕ, може не бути)

     Чому year_of_issue і location необов'язкові?
     Бо, наприклад, для нерухомості year_of_issue не завжди актуальний -->

<!ATTLIST prop id CDATA #REQUIRED currency CDATA #REQUIRED>
<!-- Два обов'язкові атрибути:
     id - ідентифікатор майна
     currency - валюта (UAH, USD, EUR)

     Приклад: <prop id="234" currency="UAH"> -->

<!ELEMENT description (#PCDATA)>
<!ELEMENT value (#PCDATA)>
<!ELEMENT year_of_issue (#PCDATA)>
<!ELEMENT location (#PCDATA)>
<!-- Чотири прості текстові елементи
     Приклад:
     <description>Nissan Qashqai, 2020 року випуску</description>
     <value>5638672.28</value>
     <year_of_issue>2008</year_of_issue>
     <location>Ірпінь, район ЖК "Затишний"</location> -->

<!-- ==================== ПЕРСОНАЛЬНІ ДАНІ ==================== -->

<!ELEMENT person (pers)>
<!-- person - обгортка для персональних даних
     (pers) - всередині ОБОВ'ЯЗКОВО один елемент pers -->

<!ELEMENT pers (first_name, last_name, gender, birth_date, email?, phone_number?)>
<!-- pers - персональна інформація
     Шість елементів (4 обов'язкові, 2 необов'язкові):
     first_name - ім'я (ОБОВ'ЯЗКОВЕ)
     last_name - прізвище (ОБОВ'ЯЗКОВЕ)
     gender - стать (ОБОВ'ЯЗКОВА)
     birth_date - дата народження (ОБОВ'ЯЗКОВА)
     email? - email (НЕОБОВ'ЯЗКОВИЙ)
     phone_number? - телефон (НЕОБОВ'ЯЗКОВИЙ)

     Чому email і phone_number необов'язкові?
     Можливо, у базі є застарілі записи без контактів -->

<!ATTLIST pers id CDATA #REQUIRED>
<!-- Один обов'язковий атрибут:
     id - ідентифікатор персони

     Приклад: <pers id="382"> -->

<!ELEMENT first_name (#PCDATA)>
<!ELEMENT last_name (#PCDATA)>
<!-- Два прості текстові елементи
     Приклад:
     <first_name>Іван</first_name>
     <last_name>Кравченко</last_name> -->

]>

<!-- Кінець DTD - закриваємо квадратну дужку -->

<!-- ==================== РЕЗЮМЕ СИМВОЛІВ ==================== -->
<!--
* (зірочка) = 0 або більше разів
    Приклад: (agreement*) означає жоден, один або багато agreement

? (знак питання) = 0 або 1 раз (необов'язковий)
    Приклад: email? означає email може бути, а може не бути

+ (плюс) = 1 або більше разів (не використовується в цій схемі)
    Приклад: (item+) означає хоча б один item, але може бути більше

БЕЗ СИМВОЛУ = рівно 1 раз (обов'язковий)
    Приклад: (gender) означає gender має бути ОБОВ'ЯЗКОВО і РІВНО ОДИН РАЗ

, (кома) = послідовність (елементи мають йти саме в цьому порядку)
    Приклад: (first_name, last_name) означає спочатку first_name, потім last_name

| (вертикальна риска) = вибір (або один, або інший) - не використовується тут
    Приклад: (email | phone) означає або email, або phone (один з двох)
-->

<!-- ==================== ТИПИ ДАНИХ ==================== -->
<!--
#PCDATA - Parsed Character Data
    - Використовується для ВМІСТУ елементів (між відкриваючим і закриваючим тегом)
    - Текст, який обробляється парсером XML
    - Приклад: <name>Іван</name>  ← "Іван" це PCDATA

CDATA - Character Data
    - Використовується для АТРИБУТІВ
    - Будь-який текст
    - Приклад: <person id="123">  ← "123" це CDATA

#REQUIRED - обов'язковий атрибут
    - Елемент недійсний без цього атрибута

#IMPLIED - необов'язковий атрибут (не використовується в цій схемі)
    - Атрибут може бути або не бути
-->

<!-- ==================== НАВІЩО ВСЕ ЦЕ ПОТРІБНО? ==================== -->
<!--
1. ВАЛІДАЦІЯ - перевірка правильності XML
   Якщо хтось створить XML, який не відповідає DTD, парсер видасть помилку

2. ДОКУМЕНТАЦІЯ - DTD це документація структури даних
   Розробник дивиться на DTD і одразу розуміє, як має виглядати XML

3. СТАНДАРТИЗАЦІЯ - всі XML файли мають однакову структуру
   Всі системи знають, чого очікувати

4. АВТОДОПОВНЕННЯ - редактори коду можуть підказувати елементи
   Якщо ви пишете XML і є DTD, редактор знає, які елементи дозволені

5. КОНТРОЛЬ ЯКОСТІ - помилки виявляються автоматично
   Не треба вручну перевіряти тисячі рядків XML
-->
