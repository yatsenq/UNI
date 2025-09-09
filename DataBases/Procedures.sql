-- ==============================
-- 1. Підрахунок полісів за типом
-- ==============================
CREATE OR REPLACE PROCEDURE count_policies_by_type(
    INOUT type_param insurance_type,
    INOUT total_count INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_record RECORD;
    cur CURSOR FOR
        SELECT ip.POLICY_ID
        FROM INSURANCE_POLICY ip
        JOIN INSURANCE_OBJECT io ON ip.INSURED_ID = io.INSURED_ID
        WHERE io.OBJECT_TYPE = type_param;
BEGIN
    total_count := 0;
    PERFORM 1
    FROM INSURANCE_POLICY ip
    JOIN INSURANCE_OBJECT io ON ip.INSURED_ID = io.INSURED_ID
    WHERE io.OBJECT_TYPE = type_param;

    IF NOT FOUND THEN
        RAISE NOTICE 'Полісів типу % не знайдено', type_param;
        RETURN;
    END IF;

    OPEN cur;
    LOOP
        FETCH cur INTO v_record;
        EXIT WHEN NOT FOUND;
        total_count := total_count + 1;
    END LOOP;
    CLOSE cur;

    RAISE NOTICE 'Кількість полісів типу %: %', type_param, total_count;

EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'Сталася помилка у count_policies_by_type: %', SQLERRM;
END;
$$;

-- ==============================
-- 2. Призупинення договорів з малою сумою (без EXECUTE)
-- ==============================
CREATE OR REPLACE PROCEDURE suspend_low_amount_agreements(
    IN min_amount money_amount
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_agreement RECORD;
    cur CURSOR FOR
        SELECT a.AGREEMENT_ID, SUM(ip.INSURANCE_AMOUNT) AS total_sum
        FROM AGREEMENT a
        JOIN INSURANCE_POLICY ip ON a.AGREEMENT_ID = ip.AGREEMENT_ID
        GROUP BY a.AGREEMENT_ID;
BEGIN
    OPEN cur;
    LOOP
        FETCH cur INTO v_agreement;
        EXIT WHEN NOT FOUND;

        IF v_agreement.total_sum < min_amount THEN
            -- звичайний UPDATE без EXECUTE
            UPDATE AGREEMENT
            SET STATUS = 'Suspended'
            WHERE AGREEMENT_ID = v_agreement.AGREEMENT_ID;

            RAISE NOTICE 'Договір % призупинено (сума = %)',
                v_agreement.AGREEMENT_ID, v_agreement.total_sum;
        END IF;
    END LOOP;
    CLOSE cur;

EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'Сталася помилка у suspend_low_amount_agreements: %', SQLERRM;
END;
$$;


-- ==============================
-- 3. Середня сума полісів за типом
-- ==============================
CREATE OR REPLACE PROCEDURE avg_policy_amount_by_type(
    IN insurance_type_param insurance_type,
    OUT avg_amount money_amount
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_policy RECORD;
    v_total NUMERIC := 0;
    v_count INTEGER := 0;
    cur CURSOR FOR
        SELECT p.INSURANCE_AMOUNT
        FROM INSURANCE_POLICY p
        JOIN INSURANCE_OBJECT io ON p.INSURED_ID = io.INSURED_ID
        WHERE io.OBJECT_TYPE = insurance_type_param;
BEGIN
    PERFORM 1
    FROM INSURANCE_POLICY p
    JOIN INSURANCE_OBJECT io ON p.INSURED_ID = io.INSURED_ID
    WHERE io.OBJECT_TYPE = insurance_type_param;

    IF NOT FOUND THEN
        RAISE NOTICE 'Полісів типу % не знайдено', insurance_type_param;
        avg_amount := 0;
        RETURN;
    END IF;

    OPEN cur;
    LOOP
        FETCH cur INTO v_policy;
        EXIT WHEN NOT FOUND;

        v_total := v_total + v_policy.INSURANCE_AMOUNT;
        v_count := v_count + 1;
    END LOOP;
    CLOSE cur;

    avg_amount := v_total / v_count;
    RAISE NOTICE 'Середня сума полісів типу % = %', insurance_type_param, avg_amount;

EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'Сталася помилка у avg_policy_amount_by_type: %', SQLERRM;
END;
$$;

-- 1. Підрахунок полісів
DO $$
DECLARE
    insurance_type_var insurance_type := 'Vehicle';
    count_var INTEGER := 0;
BEGIN
    CALL count_policies_by_type(insurance_type_var, count_var);
    RAISE NOTICE 'Результат INOUT: %', count_var;
END;
$$;

-- 2. Призупинення договорів менше 200000
CALL suspend_low_amount_agreements(200000);

SELECT AGREEMENT_ID, STATUS, TOTAL_INSURANCE_AMOUNT
FROM AGREEMENT
--WHERE STATUS = 'Suspended'
ORDER BY AGREEMENT_ID;


-- 3. Середня сума полісів за типом
DO $$
DECLARE
    avg_result money_amount;
BEGIN
    CALL avg_policy_amount_by_type('Vehicle', avg_result);
    RAISE NOTICE 'Середня сума Vehicle = %', avg_result;
END;
$$;


