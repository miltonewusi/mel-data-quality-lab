FCS_COLS = ["fcs_staples", "fcs_pulses", "fcs_veg", "fcs_fruit", "fcs_meat", "fcs_dairy", "fcs_sugar", "fcs_oil"]
FCS_W = [2, 3, 1, 1, 4, 4, 0.5, 0.5]          # WFP VAM weights
RCSI_COLS = ["rcsi_less_pref", "rcsi_borrow", "rcsi_limit_portion", "rcsi_restrict_adult", "rcsi_reduce_meals"]
RCSI_W = [1, 2, 1, 3, 1]                       # standard rCSI severity weights
PRACTICE_COLS = ["prac_improved_seed", "prac_row_planting", "prac_composting", "prac_intercropping", "prac_post_harvest"]
HHS_Q = ["hhs_q1", "hhs_q2", "hhs_q3"]
HHS_F = ["hhs_f1", "hhs_f2", "hhs_f3"]

SURVEY_COLS = (
    ["submission_id", "hh_id", "round", "district", "enumerator_id", "form_version", "interview_date",
     "start_time", "duration_min", "submission_date", "gps_lat", "gps_lon", "programme_participant",
     "resp_sex", "resp_age", "hh_size", "resp_pregnant", "land_area_ha", "maize_area_ha",
     "maize_prod_kg", "maize_yield_kg_ha"]
    + FCS_COLS + ["fcs_score"] + RCSI_COLS + ["rcsi_score"]
    + ["hhs_q1", "hhs_f1", "hhs_q2", "hhs_f2", "hhs_q3", "hhs_f3", "hhs_score"]
    + PRACTICE_COLS + ["practices_n", "adopted_2plus", "income_usd_month", "vsla_member", "vsla_savings_usd"]
)
