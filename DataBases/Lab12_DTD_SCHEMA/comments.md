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
     Це як правило: якщо є <insurance_database>, то всередині ОБОВ'ЯЗКОВО має бути <agreements>

     У ВАШОМУ XML:
     <insurance_database export_date="2025-10-20T17:52:58.325835+03:00" system="Insurance System v1.0">
       <agreements>...</agreements>  ← Ось цей елемент agreements обов'язковий
     </insurance_database> -->

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
     <insurance_database export_date="2025-10-20" system="Insurance System v1.0">

     У ВАШОМУ XML:
     <insurance_database
       export_date="2025-10-20T17:52:58.325835+03:00"  ← Перший атрибут
       system="Insurance System v1.0">                 ← Другий атрибут -->

<!-- ==================== КОЛЕКЦІЯ ДОГОВОРІВ ==================== -->

<!ELEMENT agreements (agreement*)>
<!-- agreements - назва елемента
     (agreement*) - всередині можуть бути елементи agreement
     * (зірочка) - означає "нуль або більше"

     Тобто може бути:
     - <agreements></agreements>  ← порожній, без жодного agreement (0 разів)
     - <agreements><agreement>...</agreement></agreements>  ← один agreement (1 раз)
     - <agreements><agreement>...</agreement><agreement>...</agreement></agreements>  ← багато (∞ разів)

     У ВАШОМУ XML:
     <agreements>
       <agreement id="5" status="Cancelled">...</agreement>   ← Перший agreement
       <agreement id="10" status="Active">...</agreement>     ← Другий agreement
     </agreements>
     Тут 2 договори, що валідно завдяки зірочці * -->

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
     Змінювати порядок не можна!

     У ВАШОМУ XML (перший договір):
     <agreement id="5" status="Cancelled">
       <conclusion_date>2022-04-02</conclusion_date>                    ← 1. Перший елемент
       <total_insurance_amount>430371.97</total_insurance_amount>       ← 2. Другий елемент
       <duration_months>24</duration_months>                            ← 3. Третій елемент
       <insurance_policies>...</insurance_policies>                     ← 4. Четвертий елемент
     </agreement>
     Порядок точно збігається з DTD! -->

<!ATTLIST agreement id CDATA #REQUIRED status CDATA #REQUIRED>
<!-- Для елемента agreement два обов'язкові атрибути:
     id - ідентифікатор (текст, обов'язковий)
     status - статус (текст, обов'язковий)

     Приклад:
     <agreement id="5" status="Cancelled">

     У ВАШОМУ XML:
     <agreement id="5" status="Cancelled">   ← Перший договір: id=5, status=Cancelled
     <agreement id="10" status="Active">     ← Другий договір: id=10, status=Active -->

<!-- ==================== ПРОСТІ ЕЛЕМЕНТИ ДОГОВОРУ ==================== -->

<!ELEMENT conclusion_date (#PCDATA)>
<!-- conclusion_date - дата укладення договору
     #PCDATA - "Parsed Character Data" - текстові дані, які парсяться (обробляються)
     Це означає: всередині цього елемента просто текст, ніяких інших елементів

     Різниця між PCDATA і CDATA:
     - #PCDATA використовується для ВМІСТУ елементів (між тегами)
     - CDATA використовується для АТРИБУТІВ

     Приклад:
     <conclusion_date>2022-04-02</conclusion_date>

     У ВАШОМУ XML:
     <conclusion_date>2022-04-02</conclusion_date>  ← Договір 1
     <conclusion_date>2023-10-16</conclusion_date>  ← Договір 2 -->

<!ELEMENT total_insurance_amount (#PCDATA)>
<!-- Загальна сума страхування - просто текст (число)
     Приклад: <total_insurance_amount>430371.97</total_insurance_amount>

     У ВАШОМУ XML:
     <total_insurance_amount>430371.97</total_insurance_amount>   ← Договір 1
     <total_insurance_amount>1000853.76</total_insurance_amount>  ← Договір 2 -->

<!ELEMENT duration_months (#PCDATA)>
<!-- Тривалість у місяцях - просто текст (число)
     Приклад: <duration_months>24</duration_months>

     У ВАШОМУ XML:
     <duration_months>24</duration_months>  ← Договір 1: 24 місяці
     <duration_months>36</duration_months>  ← Договір 2: 36 місяців -->

<!-- ==================== ПОЛІСИ ==================== -->

<!ELEMENT insurance_policies (policy*)>
<!-- insurance_policies - колекція полісів
     (policy*) - може містити нуль або більше елементів policy
     Аналогічно до agreements

     У ВАШОМУ XML:
     Договір 1:
     <insurance_policies>
       <policy id="680">...</policy>  ← Один поліс
     </insurance_policies>

     Договір 2:
     <insurance_policies>
       <policy id="213">...</policy>  ← Один поліс
     </insurance_policies> -->

<!ELEMENT policy (start_date, end_date, insurance_amount, insured_persons)>
<!-- policy - окремий поліс
     Послідовність з 4 обов'язкових елементів (через кому = порядок важливий):
     1. start_date - дата початку
     2. end_date - дата закінчення
     3. insurance_amount - сума страхування
     4. insured_persons - застраховані особи

     У ВАШОМУ XML (поліс 680):
     <policy id="680">
       <start_date>2022-10-27</start_date>                    ← 1. Дата початку
       <end_date>2023-10-22</end_date>                        ← 2. Дата закінчення
       <insurance_amount>5019054.65</insurance_amount>        ← 3. Сума
       <insured_persons>...</insured_persons>                 ← 4. Застраховані особи
     </policy> -->

<!ATTLIST policy id CDATA #REQUIRED>
<!-- У полісу один обов'язковий атрибут - id
     Приклад: <policy id="680">

     У ВАШОМУ XML:
     <policy id="680">  ← Перший поліс
     <policy id="213">  ← Другий поліс -->

<!ELEMENT start_date (#PCDATA)>
<!ELEMENT end_date (#PCDATA)>
<!ELEMENT insurance_amount (#PCDATA)>
<!-- Три прості елементи з текстовим вмістом
     Приклад:
     <start_date>2022-10-27</start_date>
     <end_date>2023-10-22</end_date>
     <insurance_amount>5019054.65</insurance_amount>

     У ВАШОМУ XML:
     Поліс 680:
     <start_date>2022-10-27</start_date>
     <end_date>2023-10-22</end_date>
     <insurance_amount>5019054.65</insurance_amount>

     Поліс 213:
     <start_date>2022-10-30</start_date>
     <end_date>2027-10-04</end_date>
     <insurance_amount>1335706.11</insurance_amount> -->

<!-- ==================== ЗАСТРАХОВАНІ ОСОБИ ==================== -->

<!ELEMENT insured_persons (insured*)>
<!-- insured_persons - колекція застрахованих осіб
     (insured*) - нуль або більше осіб

     У ВАШОМУ XML:
     Поліс 680:
     <insured_persons>
       <insured id="80" person_ref="382">...</insured>  ← Одна особа
     </insured_persons>

     Поліс 213:
     <insured_persons>
       <insured id="798" person_ref="75">...</insured>  ← Одна особа
     </insured_persons> -->

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
     </insured>

     У ВАШОМУ XML (особа 80):
     <insured id="80" person_ref="382">
       <address>Одеса, вул. Петлюри, 29, кв. 20</address>        ← Є (необов'язковий)
       <phone_number>+380999289334</phone_number>                ← Є (необов'язковий)
       <email>client80@example.com</email>                       ← Є (необов'язковий)
       <gender>M</gender>                                        ← Є (обов'язковий)
       <birth_date>1972-07-15</birth_date>                       ← Є (обов'язковий)
       <insurance_objects>...</insurance_objects>                ← Є (обов'язковий)
       <person>...</person>                                      ← Є (обов'язковий)
     </insured>

     У ВАШОМУ XML (особа 798):
     <insured id="798" person_ref="75">
       <address>Дніпро, вул. Центральна, 134, кв. 52</address>   ← Є (необов'язковий)
       <phone_number>+380996546783</phone_number>                ← Є (необов'язковий)
       <email>client798@example.com</email>                      ← Є (необов'язковий)
       <gender>F</gender>                                        ← Є (обов'язковий)
       <birth_date>1976-03-16</birth_date>                       ← Є (обов'язковий)
       <insurance_objects/>                                      ← Є, але ПОРОЖНІЙ (обов'язковий)
       <person>...</person>                                      ← Є (обов'язковий)
     </insured>

     ЧИ МОЖНА ПРИБРАТИ ЗНАК "?"?
     У вашому XML ВСІ необов'язкові поля (address, phone_number, email) присутні в обох записах,
     тому ТЕХНІЧНО можна прибрати ?, і ваш XML залишиться валідним.

     АЛЕ це ПОГАНА ІДЕЯ, тому що:
     1. У майбутньому може з'явитися клієнт без email
     2. Старі записи можуть не мати телефону
     3. Система стане негнучкою

     Приклад, що стане НЕМОЖЛИВИМ без "?":
     <insured id="999" person_ref="123">
       <gender>M</gender>
       <birth_date>1990-01-01</birth_date>
       <insurance_objects/>
       <person>...</person>
     </insured>
     ↑ Без address, phone_number, email - валідно ТІЛЬКИ завдяки "?" -->

<!ATTLIST insured id CDATA #REQUIRED person_ref CDATA #REQUIRED>
<!-- Два обов'язкові атрибути:
     id - ідентифікатор застрахованої особи
     person_ref - посилання на елемент person (зв'язок)

     Приклад: <insured id="80" person_ref="382">

     У ВАШОМУ XML:
     <insured id="80" person_ref="382">    ← person_ref вказує на <pers id="382"> далі
     <insured id="798" person_ref="75">    ← person_ref вказує на <pers id="75"> далі -->

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
     <birth_date>1972-07-15</birth_date>

     У ВАШОМУ XML:
     Особа 80:
     <address>Одеса, вул. Петлюри, 29, кв. 20</address>
     <phone_number>+380999289334</phone_number>
     <email>client80@example.com</email>
     <gender>M</gender>
     <birth_date>1972-07-15</birth_date>

     Особа 798:
     <address>Дніпро, вул. Центральна, 134, кв. 52</address>
     <phone_number>+380996546783</phone_number>
     <email>client798@example.com</email>
     <gender>F</gender>
     <birth_date>1976-03-16</birth_date> -->

<!-- ==================== ОБ'ЄКТИ СТРАХУВАННЯ ==================== -->

<!ELEMENT insurance_objects (insurance_object*)>
<!-- insurance_objects - колекція об'єктів страхування
     (insurance_object*) - нуль або більше об'єктів
     Може бути порожнім: <insurance_objects></insurance_objects> або <insurance_objects/>

     У ВАШОМУ XML:
     Особа 80 - є один об'єкт:
     <insurance_objects>
       <insurance_object id="317" type="Health">...</insurance_object>
     </insurance_objects>

     Особа 798 - НЕМАЄ об'єктів (порожній):
     <insurance_objects/>  ← Це валідно завдяки зірочці * (нуль об'єктів) -->

<!ELEMENT insurance_object (insured_ref, property_ref, property)>
<!-- insurance_object - окремий застрахований об'єкт
     Три обов'язкові елементи по порядку:
     1. insured_ref - посилання на застраховану особу
     2. property_ref - посилання на майно
     3. property - дані про майно

     У ВАШОМУ XML:
     <insurance_object id="317" type="Health">
       <insured_ref>80</insured_ref>          ← 1. Посилання на <insured id="80">
       <property_ref>234</property_ref>       ← 2. Посилання на <prop id="234">
       <property>...</property>               ← 3. Деталі майна
     </insurance_object> -->

<!ATTLIST insurance_object id CDATA #REQUIRED type CDATA #REQUIRED>
<!-- Два обов'язкові атрибути:
     id - ідентифікатор об'єкта
     type - тип страхування (Health, Vehicle, Life, Property, Liability)

     Приклад: <insurance_object id="317" type="Health">

     У ВАШОМУ XML:
     <insurance_object id="317" type="Health">
                       ↑        ↑
                       |        └─ Тип: Health (медичне страхування)
                       └────────── ID об'єкта: 317

     ДЕ ЦЕ Є В КОДІ:
     Знаходиться всередині <insurance_objects> особи з id="80":
     <insured id="80" person_ref="382">
       ...
       <insurance_objects>
         <insurance_object id="317" type="Health">  ← ОСЬ ТУТ!
           ...
         </insurance_object>
       </insurance_objects>
     </insured> -->

<!ELEMENT insured_ref (#PCDATA)>
<!ELEMENT property_ref (#PCDATA)>
<!-- Два прості елементи - посилання (зазвичай містять ID)
     Приклад:
     <insured_ref>80</insured_ref>
     <property_ref>234</property_ref>

     У ВАШОМУ XML:
     <insured_ref>80</insured_ref>      ← Посилання на <insured id="80">
     <property_ref>234</property_ref>   ← Посилання на <prop id="234"> -->

<!-- ==================== МАЙНО ==================== -->

<!ELEMENT property (prop)>
<!-- property - обгортка для майна
     (prop) - всередині ОБОВ'ЯЗКОВО один елемент prop
     Чому така структура? Це дозволяє розширювати схему в майбутньому

     У ВАШОМУ XML:
     <property>
       <prop id="234" currency="UAH">...</prop>
     </property> -->

<!ELEMENT prop (description, value, year_of_issue?, location?)>
<!-- prop - власне майно
     Чотири елементи:
     description - опис (ОБОВ'ЯЗКОВИЙ)
     value - вартість (ОБОВ'ЯЗКОВА)
     year_of_issue? - рік випуску (НЕОБОВ'ЯЗКОВИЙ, може не бути)
     location? - місцезнаходження (НЕОБОВ'ЯЗКОВЕ, може не бути)

     Чому year_of_issue і location необов'язкові?
     Бо, наприклад, для нерухомості year_of_issue не завжди актуальний

     У ВАШОМУ XML:
     <prop id="234" currency="UAH">
       <description>Nissan Qashqai, 2020 року випуску</description>  ← Обов'язковий
       <value>5638672.28</value>                                     ← Обов'язковий
       <year_of_issue>2008</year_of_issue>                           ← Є (необов'язковий)
       <location>Ірпінь, район ЖК "Затишний"</location>              ← Є (необов'язковий)
     </prop>

     ЧИ МОЖНА ПРИБРАТИ ЗНАК "?"?
     У вашому XML обидва поля (year_of_issue і location) присутні,
     тому ТЕХНІЧНО можна прибрати ?, і ваш XML залишиться валідним.

     АЛЕ це ПОГАНА ІДЕЯ, тому що:
     - Для медичного страхування немає "року випуску" і "локації"
     - Для страхування життя немає фізичного об'єкта
     - Транспорт переміщується (немає постійної локації)

     Приклад, що стане НЕМОЖЛИВИМ без "?":
     <prop id="500" currency="UAH">
       <description>Медичний поліс премію класу</description>
       <value>50000.00</value>
     </prop>
     ↑ Без year_of_issue і location - валідно ТІЛЬКИ завдяки "?" -->

<!ATTLIST prop id CDATA #REQUIRED currency CDATA #REQUIRED>
<!-- Два обов'язкові атрибути:
     id - ідентифікатор майна
     currency - валюта (UAH, USD, EUR)

     Приклад: <prop id="234" currency="UAH">

     У ВАШОМУ XML:
     <prop id="234" currency="UAH">
           ↑        ↑
           |        └─ Валюта: UAH (гривня)
           └────────── ID майна: 234 -->

<!ELEMENT description (#PCDATA)>
<!ELEMENT value (#PCDATA)>
<!ELEMENT year_of_issue (#PCDATA)>
<!ELEMENT location (#PCDATA)>
<!-- Чотири прості текстові елементи
     Приклад:
     <description>Nissan Qashqai, 2020 року випуску</description>
     <value>5638672.28</value>
     <year_of_issue>2008</year_of_issue>
     <location>Ірпінь, район ЖК "Затишний"</location>

     У ВАШОМУ XML:
     <description>Nissan Qashqai, 2020 року випуску</description>
     <value>5638672.28</value>
     <year_of_issue>2008</year_of_issue>
     <location>Ірпінь, район ЖК "Затишний"</location>

     ⚠️ ЦІКАВИЙ МОМЕНТ:
     В description написано "2020 року випуску", але year_of_issue каже "2008"
     Це суперечність у даних! Можлива помилка. -->

<!-- ==================== ПЕРСОНАЛЬНІ ДАНІ ==================== -->

<!ELEMENT person (pers)>
<!-- person - обгортка для персональних даних
     (pers) - всередині ОБОВ'ЯЗКОВО один елемент pers

     У ВАШОМУ XML:
     <person>
       <pers id="382">...</pers>
     </person> -->

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
     Можливо, у базі є застарілі записи без контактів

     У ВАШОМУ XML (персона 382):
     <pers id="382">
       <first_name>Іван</first_name>                           ← Обов'язковий
       <last_name>Кравченко</last_name>                        ← Обов'язковий
       <gender>M</gender>                                      ← Обов'язковий
       <birth_date>1992-03-03</birth_date>                     ← Обов'язковий
       <email>ivan.kravchenko@outlook.com</email>              ← Є (необов'язковий)
       <phone_number>+380997386167</phone_number>              ← Є (необов'язковий)
     </pers>

     У ВАШОМУ XML (персона 75):
     <pers id="75">
       <first_name>Сергій</first_name>                         ← Обов'язковий
       <last_name>Павленко</last_name>                         ← Обов'язковий
       <gender>M</gender>                                      ← Обов'язковий
       <birth_date>1975-12-06</birth_date>                     ← Обов'язковий
       <email>sergiy.pavlenko@example.com</email>              ← Є (необов'язковий)
       <phone_number>+380991343442</phone_number>              ← Є (необов'язковий)
     </pers>

     ЧИ МОЖНА ПРИБРАТИ ЗНАК "?"?
     У вашому XML обидві персони мають email і phone_number,
     тому ТЕХНІЧНО можна прибрати ?, і ваш XML залишиться валідним.

     АЛЕ це ПОГАНА ІДЕЯ, тому що:
     - Старі записи можуть не мати контактів
     - Клієнт може не хотіти надавати email/телефон -->

<!ATTLIST pers id CDATA #REQUIRED>
<!-- Один обов'язковий атрибут:
     id - ідентифікатор персони

     Приклад: <pers id="382">

     У ВАШОМУ XML:
     <pers id="382">  ← Перша персона (Іван Кравченко)
     <pers id="75">   ← Друга персона (Сергій Павленко)

     ЗВ'ЯЗОК:
     <insured id="80" person_ref="382">  ← Посилається на <pers id="382">
     <insured id="798" person_ref="75">  ← Посилається на <pers id="75"> -->

<!ELEMENT first_name (#PCDATA)>
<!ELEMENT last_name (#PCDATA)>
<!-- Два прості текстові елементи
     Приклад:
     <first_name>Іван</first_name>
     <last_name>Кравченко</last_name>

     У ВАШОМУ XML:
     Персона 382:
     <first_name>Іван</first_name>
     <last_name>Кравченко</last_name>

     Персона 75:
     <first_name>Сергій</first_name>
     <last_name>Павленко</last_name> -->

]>

<!-- Кінець DTD - закриваємо квадратну дужку -->

<!-- ==================== РЕЗЮМЕ СИМВОЛІВ ==================== -->
<!--
* (зірочка) = 0 або більше разів
    Приклад: (agreement*) означає жоден, один або багато agreement
    У ВАШОМУ XML: <agreements> містить 2 agreement - валідно!

? (знак питання) = 0 або 1 раз (необов'язковий)
    Приклад: email? означає email може бути, а може не бути
    У ВАШОМУ XML: Всі email присутні, але ? дає гнучкість на майбутнє

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
