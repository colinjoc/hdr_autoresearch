# Feature candidates — PL-1 cohort study

| feature | source column(s) | transform | domain rationale |
|---|---|---|---|
| grant_year | CN_Date_Granted | year(date) | regime shifts (BCAR, SHD, COVID, HfA) |
| grant_month | CN_Date_Granted | month(date) | seasonality, winter-grant effects |
| grant_quarter | CN_Date_Granted | quarter(date) | aligns with CSO BHQ cadence |
| is_dublin | LocalAuthority | bool membership | regulatory & market concentration |
| la_category | LocalAuthority | map to urban/rural/dublin | Dublin / other cities / urban / rural |
| apartment_flag | CN_Proposed_use_of_building, CN_Sub_Group | bool contains "apartment/flat/maisonette" | apartment viability bottleneck |
| one_off_flag | CN_Sub_Group | == "1_dwelling_house" AND units==1 | rural self-builds |
| oneoff_no_garage | CN_Sub_Group, CN_Number_of_Buildings | composite | one-off no-garage variant |
| log_units | CN_Total_Number_of_Dwelling_Units | log1p | scheme size |
| log_floor_area | CN_Total_floor_area_of_building | log1p | scheme size alternative |
| multi_building | CN_Number_of_New_Buildings | >1 bool | economies of scale |
| multi_phase | CN_Total_Number_of_Phases | >1 bool | phased delivery |
| ahb_flag | CN_Approved_housing_body | == "yes" | pre-funded projects |
| la_own_flag | CN_Behalf_local_authority | == "yes" | LA direct |
| seven_day_flag | CN_Project_type | == "Seven_Day_Notice" | rapid-build non-residential comparator |
| opt_out_flag | CN_Project_type | == "Opt_Out_Comm_Notice" | one-off self-build route |
| protected_flag | CN_Protected_structure | == "yes" | heritage works slow |
| foul_water_type | CN_Foul_water | categorical | proxy for infrastructure complexity |
| mmc_flag | CN_Main_Method_of_Construction | startswith "MMC" | modern methods of construction |
| material_category | CN_Main_Construction_Material | categorical | concrete vs steel vs timber |
| lat | CN_LAT | float | geocoord |
| lng | CN_LNG | float | geocoord |
| dist_to_dublin | lat, lng | haversine to 53.349,-6.260 | periphery indicator |
| units_completed_ratio | CCC_Units_Completed / CN_Total_Number_of_Dwelling_Units | ratio | over/under-delivery flag |
| pre_2015_flag | grant_year | <2015 | data-quality ramp-up |
| shd_era_flag | grant_year | 2017 ≤ y ≤ 2021 | SHD regime window |
| covid_commence_flag | CN_Commencement_Date | 2020-03 ≤ date ≤ 2021-04 | COVID-shutdown window |
| post_hfa_flag | grant_year | ≥2022 | Housing for All era |
| permission_near_expiry | CN_Date_Granted, CN_Date_Expiry, CN_Commencement_Date | commencement within 6 months of expiry | option-value "commence before expiry" |
| section_42_flag | CN_Date_Expiry - CN_Date_Granted | >5 years ⇒ extension probable | planning extension proxy |

## Target variables

| target | definition | cohort |
|---|---|---|
| duration_perm_to_comm | days(CN_Commencement_Date - CN_Date_Granted) | permission granted AND commencement populated |
| duration_comm_to_ccc | days(CCC_Date_Validated - CN_Commencement_Date) | commencement populated AND CCC validated |
| duration_perm_to_ccc | days(CCC_Date_Validated - CN_Date_Granted) | complete-timeline subcohort |
| dark_permission | bool (no commencement within 72 months of grant) | permission granted ≥ 6 years ago |
| completes_within_24m | bool (CCC within 24 months of commence) | commenced ≥ 2 years ago |
| completes_within_48m | bool (CCC within 48 months of commence) | commenced ≥ 4 years ago |
| completes_within_72m | bool (CCC within 72 months of commence) | commenced ≥ 6 years ago |
