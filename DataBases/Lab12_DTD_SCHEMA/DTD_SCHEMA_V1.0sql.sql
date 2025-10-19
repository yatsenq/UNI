<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE insurance_database [
<!ELEMENT insurance_database (agreements)>
<!ATTLIST insurance_database export_date CDATA #REQUIRED system CDATA #REQUIRED>

<!ELEMENT agreements (agreement*)>

<!ELEMENT agreement (conclusion_date, total_insurance_amount, duration_months, insurance_policies)>
<!ATTLIST agreement id CDATA #REQUIRED status CDATA #REQUIRED>
<!ELEMENT conclusion_date (#PCDATA)>
<!ELEMENT total_insurance_amount (#PCDATA)>
<!ELEMENT duration_months (#PCDATA)>

<!ELEMENT insurance_policies (policy*)>

<!ELEMENT policy (start_date, end_date, insurance_amount, insured_persons)>
<!ATTLIST policy id CDATA #REQUIRED>
<!ELEMENT start_date (#PCDATA)>
<!ELEMENT end_date (#PCDATA)>
<!ELEMENT insurance_amount (#PCDATA)>

<!ELEMENT insured_persons (insured*)>

<!ELEMENT insured (address?, phone_number?, email?, gender, birth_date, insurance_objects, person)>
<!ATTLIST insured id CDATA #REQUIRED person_ref CDATA #REQUIRED>
<!ELEMENT address (#PCDATA)>
<!ELEMENT phone_number (#PCDATA)>
<!ELEMENT email (#PCDATA)>
<!ELEMENT gender (#PCDATA)>
<!ELEMENT birth_date (#PCDATA)>

<!ELEMENT insurance_objects (insurance_object*)>

<!ELEMENT insurance_object (insured_ref, property_ref, property)>
<!ATTLIST insurance_object id CDATA #REQUIRED type CDATA #REQUIRED>
<!ELEMENT insured_ref (#PCDATA)>
<!ELEMENT property_ref (#PCDATA)>

<!ELEMENT property (prop)>

<!ELEMENT prop (description, value, year_of_issue?, location?)>
<!ATTLIST prop id CDATA #REQUIRED currency CDATA #REQUIRED>
<!ELEMENT description (#PCDATA)>
<!ELEMENT value (#PCDATA)>
<!ELEMENT year_of_issue (#PCDATA)>
<!ELEMENT location (#PCDATA)>

<!ELEMENT person (pers)>

<!ELEMENT pers (first_name, last_name, gender, birth_date, email?, phone_number?)>
<!ATTLIST pers id CDATA #REQUIRED>
<!ELEMENT first_name (#PCDATA)>
<!ELEMENT last_name (#PCDATA)>
]>
SELECT xmlroot(
    xmlelement(
        NAME "insurance_database",
        xmlattributes(
            CURRENT_TIMESTAMP AS "export_date",
            'Insurance System v1.0' AS "system"
        ),
        
        xmlelement(NAME "agreements",
            (SELECT xmlagg(
                xmlelement(NAME "agreement",
                    xmlattributes(
                        AGREEMENT_ID AS "id", 
                        STATUS AS "status"
                    ),
                    xmlforest(
                        CONCLUSION_DATE AS "conclusion_date", 
                        TOTAL_INSURANCE_AMOUNT AS "total_insurance_amount", 
                        DURATION AS "duration_months"
                    ),
                    
                    xmlelement(NAME "insurance_policies",
                        (SELECT xmlagg(
                            xmlelement(NAME "policy",
                                xmlattributes(POLICY_ID AS "id"),
                                xmlforest(
                                    START_DATE AS "start_date", 
                                    END_DATE AS "end_date", 
                                    INSURANCE_AMOUNT AS "insurance_amount"
                                ),
                                
                                xmlelement(NAME "insured_persons",
                                    (SELECT xmlagg(
                                        xmlelement(NAME "insured",
                                            xmlattributes(
                                                INSURED_ID AS "id", 
                                                PERSON_ID AS "person_ref"
                                            ),
                                            xmlforest(
                                                ADDRESS AS "address", 
                                                PHONE_NUMBER AS "phone_number", 
                                                EMAIL AS "email", 
                                                GENDER AS "gender", 
                                                BIRTH_DATE AS "birth_date"
                                            ),
                                            
                                            xmlelement(NAME "insurance_objects",
                                                (SELECT xmlagg(
                                                    xmlelement(NAME "insurance_object",
                                                        xmlattributes(
                                                            OBJECT_ID AS "id", 
                                                            OBJECT_TYPE AS "type"
                                                        ),
                                                        xmlforest(
                                                            INSURED_ID AS "insured_ref", 
                                                            PROPERTY_ID AS "property_ref"
                                                        ),
                                                        
                                                        xmlelement(NAME "property",
                                                            (SELECT xmlelement(NAME "prop",
                                                                xmlattributes(
                                                                    PROPERTY_ID AS "id", 
                                                                    CURRENCY AS "currency"
                                                                ),
                                                                xmlforest(
                                                                    DESCRIPTION AS "description", 
                                                                    VALUE AS "value", 
                                                                    YEAR_OF_ISSUE AS "year_of_issue", 
                                                                    LOCATION AS "location"
                                                                )
                                                            ) FROM (SELECT * FROM PROPERTY_CHARACTERISTICS LIMIT 1) sub)
                                                        )
                                                    )
                                                ) FROM (SELECT * FROM INSURANCE_OBJECT LIMIT 1) sub)
                                            ),
                                            
                                            xmlelement(NAME "person",
                                                (SELECT xmlelement(NAME "pers",
                                                    xmlattributes(PERSON_ID AS "id"),
                                                    xmlforest(
                                                        FIRST_NAME AS "first_name", 
                                                        LAST_NAME AS "last_name", 
                                                        GENDER AS "gender", 
                                                        BIRTH_DATE AS "birth_date", 
                                                        EMAIL AS "email", 
                                                        PHONE_NUMBER AS "phone_number"
                                                    )
                                                ) FROM (SELECT * FROM PERSON_CHARACTERISTICS LIMIT 1) sub)
                                            )
                                        )
                                    ) FROM (SELECT * FROM INSURED LIMIT 1) sub)
                                )
                            )
                        ) FROM (SELECT * FROM INSURANCE_POLICY LIMIT 1) sub)
                    )
                )
            ) FROM (SELECT * FROM AGREEMENT LIMIT 1) sub)
        )
    ),
    VERSION '1.0'
)::text AS xml_content;