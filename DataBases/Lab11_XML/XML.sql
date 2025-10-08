SELECT xmlroot(
    xmlelement(
        NAME "insurance_database",
        xmlattributes(
            CURRENT_TIMESTAMP AS "export_date",
            'Insurance' AS "system"
        ),
        
        xmlelement(NAME "persons",
            (SELECT xmlagg(
                xmlelement(NAME "person",
                    xmlattributes(PERSON_ID AS "id"),
                    xmlforest(
                        FIRST_NAME AS "first_name", 
                        LAST_NAME AS "last_name", 
                        GENDER AS "gender", 
                        BIRTH_DATE AS "birth_date", 
                        EMAIL AS "email", 
                        PHONE_NUMBER AS "phone_number"
                    )
                )
            ) FROM PERSON_CHARACTERISTICS)
        ),
        
        xmlelement(NAME "properties",
            (SELECT xmlagg(
                xmlelement(NAME "property",
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
                )
            ) FROM PROPERTY_CHARACTERISTICS)
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
                    )
                )
            ) FROM AGREEMENT)
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
                    )
                )
            ) FROM INSURED)
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
                    )
                )
            ) FROM INSURANCE_OBJECT)
        ),
        
        xmlelement(NAME "insurance_policies",
            (SELECT xmlagg(
                xmlelement(NAME "policy",
                    xmlattributes(POLICY_ID AS "id"),
                    xmlforest(
                        START_DATE AS "start_date", 
                        END_DATE AS "end_date", 
                        INSURANCE_AMOUNT AS "insurance_amount", 
                        INSURED_ID AS "insured_ref", 
                        AGREEMENT_ID AS "agreement_ref"
                    )
                )
            ) FROM INSURANCE_POLICY)
        )
    ),
    VERSION '1.0'
)::text AS xml_content;