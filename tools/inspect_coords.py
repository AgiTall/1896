import json
from pathlib import Path

wtp_map = {
    'A10W_oath': (5, 3),
    'A10W_creditors_register': (5, 4),
    'A10W_bonded_warehouses': (3, 5),
    'A10W_silver_convoy': (7, 5),
    'A10W_cable_priority': (5, 6),
    'A10W_harbour_survey': (3, 7),
    'A10W_local_shareholding': (7, 7),
    'A10W_charter_congress': (5, 8),
    'A10W_colonial_charter': (2, 9),
    'A10W_metropolitan_charter': (8, 9),
    'A10W_resident_council': (1, 10),
    'A10W_revenue_covenant': (3, 10),
    'A10W_island_registries': (7, 10),
    'A10W_merchant_assembly': (9, 10),
    'A10W_charter_constabulary': (1, 11),
    'A10W_export_estates': (3, 11),
    'A10W_duplicate_cables': (7, 11),
    'A10W_secretariat_rules': (9, 11),
    'A10W_debt_conversion': (2, 12),
    'A10W_escrow_exchange': (8, 12),
    'A10W_colony': (2, 13),
    'A10W_new_metropole': (8, 13),
    'A10W_port_welfare': (2, 14),
    'A10W_oceanic_covenant': (8, 14)
}

conf_map = {
    'A10_confederation': (15, 3),
    'A10_visayan_compact': (15, 4),
    'A10_mindanao_compact': (15, 5),
    'A10_united_command': (15, 6),
    'A10R_luzon_relief': (11, 7),
    'A10R_common_treasury': (15, 7),
    'A10R_republican_court': (13, 8),
    'A10R_language_charters': (17, 8),
    'A10_luzon_charter': (11, 9),
    'A10R_tenant_guarantees': (13, 9),
    'A10R_civilian_inspectors': (17, 9),
    'A10R_assembly_of_islands': (15, 10),
    'A10_capital_charters': (11, 11),
    'A10R_republics_forever': (13, 12),
    'A10R_federal_convention': (17, 12),
    'A10R_rotating_presidency': (11, 13),
    'A10R_customs_union': (13, 13),
    'A10R_bill_of_rights': (17, 13),
    'A10_federation': (17, 14),
    'A10R_republican_compact_end': (12, 15),
    'A10_gendarmerie': (16, 15),
    'A10_local_administration': (18, 15),
    'A10_equal_citizenship': (17, 16),
    'A10R_federal_parliament': (17, 18),
    'A10R_civilian_commonwealth': (17, 20)
}

econ_map = {
    'A10D_island_census': (22, 4),
    'A10D_municipal_roads': (20, 6),
    'A10D_mail_ferries': (24, 6),
    'A10D_abaca_cooperatives': (20, 8),
    'A10D_sugar_inspectors': (22, 8),
    'A10D_timber_and_slipways': (24, 8),
    'A10D_provincial_workshops': (20, 10),
    'A10D_rice_granaries': (22, 10),
    'A10D_district_clinics': (24, 10),
    'A10D_normal_schools': (20, 13),
    'A10D_cable_cooperatives': (22, 13),
    'A10D_sanitary_commission': (24, 13),
    'A10D_island_polytechnic': (21, 16),
    'A10D_national_market': (22, 19)
}

mil_map = {
    'A10_coastal_arsenals': (28, 4),
    'A10D_rifle_inspections': (26, 6),
    'A10D_coastal_boatyards': (30, 6),
    'A10D_common_calibres': (26, 8),
    'A10D_chart_the_straits': (30, 8),
    'A10D_field_batteries': (26, 10),
    'A10D_harbour_defences': (30, 10),
    'A10D_sappers_and_pack_trains': (26, 12),
    'A10D_merchant_reserve': (30, 12),
    'A10D_staff_college': (26, 14),
    'A10D_gunboat_school': (30, 14),
    'A10D_ammunition_toolrooms': (26, 16),
    'A10D_patrol_flotillas': (30, 16),
    'A10_landing_plans': (28, 19),
    'A10_strike_japan': (28, 21)
}

coup_map = {
    'A10M_coup': (38, 3),
    'A10M_martial_law': (38, 4),
    'A10M_recall_charters': (36, 5),
    'A10M_censor_cables': (40, 5),
    'A10M_rice_commissions': (34, 6),
    'A10M_officer_tribunal': (38, 6),
    'A10M_cadet_schools': (42, 6),
    'A10M_requisition': (36, 7),
    'A10M_levy_rolls': (42, 7),
    'A10M_compensation': (34, 8),
    'A10M_labour_battalions': (36, 8),
    'A10M_medical_corps': (42, 8),
    'A10M_quartermasters': (38, 9),
    'A10M_junta': (36, 10),
    'A10M_directorate': (42, 10),
    'A10M_revolutionary_command': (36, 11),
    'A10M_service_council': (42, 11),
    'A10M_commissars': (36, 12),
    'A10M_audited_budget': (42, 12),
    'A10M_islands_barracks': (36, 13),
    'A10M_professional_army': (42, 13),
    'A10M_red_seal': (36, 14),
    'A10M_fixed_term': (42, 14),
    'A10M_coastal_observers': (38, 15),
    'A10M_defence_plans': (38, 16),
    'A10M_veteran_settlement': (36, 17),
    'A10M_restore_markets': (40, 17),
    'A10M_iron_archipelago': (38, 19)
}

root_postwar_map = {
    'A10_island_congress': (25, 0),
    'A10R_provincial_rolls': (22, 1),
    'A10R_emergency_council': (28, 1),
    'A10R_war_accounts': (22, 21),
    'A10R_veterans_land': (20, 22),
    'A10_federal_reconstruction': (24, 22),
    'A10R_peace_generation': (22, 24)
}

all_coords = {}
for m in [wtp_map, conf_map, econ_map, mil_map, coup_map, root_postwar_map]:
    all_coords.update(m)
