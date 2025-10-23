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
                        a.AGREEMENT_ID AS "id",
                        a.STATUS AS "status"
                    ),
                    xmlforest(
                        a.CONCLUSION_DATE AS "conclusion_date",
                        a.TOTAL_INSURANCE_AMOUNT AS "total_insurance_amount",
                        a.DURATION AS "duration_months"
                    ),
                    
                    xmlelement(NAME "insurance_policies",
                        (SELECT xmlagg(
                            xmlelement(NAME "policy",
                                xmlattributes(p.POLICY_ID AS "id"),
                                xmlforest(
                                    p.START_DATE AS "start_date",
                                    p.END_DATE AS "end_date",
                                    p.INSURANCE_AMOUNT AS "insurance_amount"
                                ),
                                
                                xmlelement(NAME "insured_persons",
                                    (SELECT xmlagg(
                                        xmlelement(NAME "insured",
                                            xmlattributes(
                                                ins.INSURED_ID AS "id",
                                                ins.PERSON_ID AS "person_ref"
                                            ),
                                            xmlforest(
                                                ins.ADDRESS AS "address",
                                                ins.PHONE_NUMBER AS "phone_number",
                                                ins.EMAIL AS "email",
                                                ins.GENDER AS "gender",
                                                ins.BIRTH_DATE AS "birth_date"
                                            ),
                                            
                                            xmlelement(NAME "insurance_objects",
                                                (SELECT xmlagg(
                                                    xmlelement(NAME "insurance_object",
                                                        xmlattributes(
                                                            io.OBJECT_ID AS "id",
                                                            io.OBJECT_TYPE AS "type"
                                                        ),
                                                        
                                                        xmlelement(NAME "insured_ref",
                                                            io.INSURED_ID
                                                        ),
                                                        xmlelement(NAME "property_ref",
                                                            io.PROPERTY_ID
                                                        ),
                                                        
                                                        xmlelement(NAME "property",
                                                            xmlelement(NAME "prop",
                                                                xmlattributes(
                                                                    pr.PROPERTY_ID AS "id",
                                                                    pr.CURRENCY AS "currency"
                                                                ),
                                                                xmlforest(
                                                                    pr.DESCRIPTION AS "description",
                                                                    pr.VALUE AS "value",
                                                                    pr.YEAR_OF_ISSUE AS "year_of_issue",
                                                                    pr.LOCATION AS "location"
                                                                )
                                                            )
                                                        )
                                                    )
                                                ) FROM INSURANCE_OBJECT io
                                                LEFT JOIN PROPERTY_CHARACTERISTICS pr
                                                    ON io.PROPERTY_ID = pr.PROPERTY_ID
                                                WHERE io.INSURED_ID = ins.INSURED_ID)
                                            ),
                                            
                                            xmlelement(NAME "person",
                                                xmlelement(NAME "pers",
                                                    xmlattributes(
                                                        pc.PERSON_ID AS "id"
                                                    ),
                                                    xmlforest(
                                                        pc.FIRST_NAME AS "first_name",
                                                        pc.LAST_NAME AS "last_name",
                                                        pc.GENDER AS "gender",
                                                        pc.BIRTH_DATE AS "birth_date",
                                                        pc.EMAIL AS "email",
                                                        pc.PHONE_NUMBER AS "phone_number"
                                                    )
                                                )
                                            )
                                        )
                                    ) FROM INSURED ins
                                    LEFT JOIN PERSON_CHARACTERISTICS pc
                                        ON ins.PERSON_ID = pc.PERSON_ID
                                    WHERE ins.INSURED_ID = p.INSURED_ID)
                                )
                            )
                        ) FROM INSURANCE_POLICY p
                        WHERE p.AGREEMENT_ID = a.AGREEMENT_ID)
                    )
                )
            ) FROM AGREEMENT a)
        )
    ),
    VERSION '1.0'
)::text AS xml_content;