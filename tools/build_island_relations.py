"""Generate explicit bilateral links and a recoverable country-by-country escrow book."""
import json
import re
from build_chamber_network import ROOT, write

COLONIES = ["A07", "AVC", "AQL", "ASA", "AWA", "ATA"]
PARTNERS = {
    "A04": ["A02", "A01", "A03", "A06", "A09", "A05", "MLT", "A10"],
    "A01": ["A02", "A05", "A11", "A12", "A13", "A14"],
    "A02": ["A01", "A05", "MLT"] + COLONIES,
    "A03": ["A08", "A09"],
    "A05": ["A02", "A01"],
    "A06": ["MLT", "A02"],
    "A08": ["A03", "A09"],
    "A09": ["A03", "A08"],
    "A10": ["A11", "A12", "A13", "MLT"],
    "MLT": ["A02", "A06", "A04"],
    "PCF": ["A02", "A01", "A04"],
    "PAZ": ["A02", "A01", "A04"],
    "PHR": ["A02", "A01", "A04"],
    "PHW": ["A02", "A03", "A04"],
    "PSY": ["A02", "A04", "PZN", "PPE"],
    "PTG": ["A02", "PHW"],
    "PKR": ["A08", "A06"],
    "PPM": ["A06", "A02"],
    "PZN": ["PSY", "PPE"],
    "PPE": ["PSY", "PZN"],
}
for tag in COLONIES:
    PARTNERS[tag] = ["A02"] + [other for other in COLONIES if other != tag]
for tag in ["A11", "A12", "A13", "A14"]:
    PARTNERS[tag] = ["A01", "A03", "A10"]
for tag in ["PLS", "PSL", "PCB", "PPN", "PVI", "PSM", "PMD", "PNM", "PNL", "PML", "PBT"]:
    PARTNERS[tag] = ["A10", "A04", "MLT"]


def service_kind(a, b):
    pair = {a, b}
    if pair == {'A06', 'MLT'}:
        return 'research'
    if pair == {'A03', 'A09'}:
        return 'workshop'
    if pair in ({'A03', 'A08'}, {'A08', 'A09'}):
        return 'northern'
    if pair == {'A01', 'A02'}:
        return 'fuel'
    if pair & set(COLONIES) and pair <= set(COLONIES + ['A02']):
        return 'colonial'
    if pair & {'A05', 'PCF', 'PAZ', 'PHR'}:
        return 'caribbean'
    return 'maritime'


def main():
    triggers, effects, decisions, events = [], [], [], ["add_namespace = wtn_relations"]
    local = {"russian": {}, "english": {}}
    links = {}
    for source, targets in PARTNERS.items():
        for target in targets:
            event_id = f"wtn_relations.{len(decisions) + 1}"
            service = service_kind(source, target)
            links.setdefault(tuple(sorted((source, target))), set()).update((source, target))
            name = f"WTN_relation_{source}_{target}"
            link = "WTN_link_" + "_".join(sorted((source, target)))
            pending = name + "_pending"
            ready = f"exists = yes has_capitulated = no country_exists = {target} NOT = {{ has_war_with = {target} }} {target} = {{ has_capitulated = no }}"
            triggers.append(f"{name}_can_propose = {{ tag = {source} {ready} OR = {{ has_country_flag = WTN_relations_open tag = A01 tag = A03 tag = A10 }} NOT = {{ has_country_flag = WTN_relation_pending }} NOT = {{ has_country_flag = WTN_relation_cooldown }} NOT = {{ has_country_flag = {link} }} }}")
            answer = f"tag = {target} exists = yes has_capitulated = no country_exists = {source} NOT = {{ has_war_with = {source} }} NOT = {{ has_country_flag = {link} }} {source} = {{ has_capitulated = no has_country_flag = {pending} has_country_flag = WTN_relation_pending }}"
            triggers.append(f"{name}_can_answer = {{ {answer} }}")
            effects.append(f"{name}_propose_effect = {{ if = {{ limit = {{ {name}_can_propose = yes }} set_country_flag = {{ flag = {pending} days = 30 }} set_country_flag = {{ flag = WTN_relation_pending days = 30 }} set_country_flag = WTN_relation_waiting_reply set_country_flag = {{ flag = WTN_relation_cooldown days = 180 }} country_event = {{ id = wtn_relations.1003 days = 31 }} {target} = {{ country_event = {{ id = {event_id} days = 2 }} }} }} }}")
            effects.append(f"{name}_accept_effect = {{ if = {{ limit = {{ {name}_can_answer = yes }} hidden_effect = {{ set_country_flag = {{ flag = {link} days = 360 }} {source} = {{ clr_country_flag = {pending} clr_country_flag = WTN_relation_pending clr_country_flag = WTN_relation_waiting_reply set_country_flag = {{ flag = WTN_relation_accepted_notice days = 15 }} country_event = {{ id = wtn_relations.1001 days = 1 }} set_country_flag = {{ flag = {link} days = 360 }} WTN_refresh_links_effect = yes }} WTN_refresh_links_effect = yes }} custom_effect_tooltip = WTN_relation_{service}_tt }} }}")
            effects.append(f"{name}_decline_effect = {{ if = {{ limit = {{ country_exists = {source} {source} = {{ has_country_flag = {pending} }} }} {source} = {{ clr_country_flag = {pending} clr_country_flag = WTN_relation_pending clr_country_flag = WTN_relation_waiting_reply set_country_flag = {{ flag = WTN_relation_declined_notice days = 15 }} country_event = {{ id = wtn_relations.1002 days = 1 }} }} }} }}")
            decisions.append(f" {name} = {{ icon = generic_political_discourse cost = 25 allowed = {{ original_tag = {source} }} targets = {{ {target} }} target_trigger = {{ FROM = {{ exists = yes }} }} visible = {{ tag = {source} OR = {{ has_country_flag = WTN_relations_open tag = A01 tag = A03 tag = A10 }} }} available = {{ {name}_can_propose = yes }} complete_effect = {{ {name}_propose_effect = yes }} ai_will_do = {{ base = 1 }} }}")
            events.append(f"country_event = {{ id = {event_id} title = wtn_relations.title desc = wtn_relations.desc picture = GFX_1896_event_trade is_triggered_only = yes timeout_days = 20 trigger = {{ {name}_can_answer = yes }} option = {{ name = wtn_relations.decline ai_chance = {{ factor = 35 }} {name}_decline_effect = yes }} option = {{ name = wtn_relations.accept ai_chance = {{ factor = 65 }} {name}_accept_effect = yes }} }}")
            for lang in local:
                local[lang][name] = "Соглашение морских служб: [FROM.GetName]" if lang == "russian" else "Voyage Services Agreement: [FROM.GetName]"
                local[lang][name + "_desc"] = "Предложить обмен морскими ведомостями на год. Партнёр вправе отказать. Соглашение сохраняет отдельные правительства и не прекращает чужих войн; несколько соглашений не складывают один и тот же бонус." if lang == "russian" else "Propose a one-year exchange of maritime records. The partner may refuse. Both governments remain separate, and other wars continue; multiple agreements do not stack the same bonus."
    live_checks, cleanup = [], []
    service_checks = {}
    for (a, b) in links:
        flag = f"WTN_link_{a}_{b}"
        for source, target in ((a, b), (b, a)):
            live_checks.append(f"AND = {{ tag = {source} has_country_flag = {flag} country_exists = {target} has_capitulated = no NOT = {{ has_war_with = {target} }} {target} = {{ has_capitulated = no }} }}")
            service = service_kind(source, target)
            if service != 'maritime':
                service_checks.setdefault(service, []).append(live_checks[-1])
            cleanup.append(f"if = {{ limit = {{ tag = {source} has_country_flag = {flag} OR = {{ NOT = {{ country_exists = {target} }} has_capitulated = yes has_war_with = {target} {target} = {{ has_capitulated = yes }} }} }} clr_country_flag = {flag} if = {{ limit = {{ country_exists = {target} }} {target} = {{ clr_country_flag = {flag} }} }} }}")
    triggers.append("WTN_has_live_link = { OR = { " + " ".join(live_checks) + " } }")
    service_effects = []
    for service, checks in service_checks.items():
        triggers.append(f"WTN_has_{service}_link = {{ OR = {{ " + " ".join(checks) + " } }")
        service_effects.append(f"if = {{ limit = {{ WTN_has_{service}_link = yes }} add_ideas = WTN_link_{service}_services }} else = {{ remove_ideas = WTN_link_{service}_services }}")
    effects.append("WTN_refresh_links_effect = { hidden_effect = { " + " ".join(cleanup) + " if = { limit = { WTN_has_live_link = yes } add_ideas = WTN_island_cooperation } else = { remove_ideas = WTN_island_cooperation } " + " ".join(service_effects) + " } }")
    write("common/scripted_triggers/WTN_relations.txt", "\n".join(triggers))
    write("common/scripted_effects/WTN_relations.txt", "\n".join(effects))
    write("common/decisions/WTN_relations.txt", "WTN_island_relations = {\n" + "\n".join(decisions) + "\n}")
    write("common/decisions/categories/WTN_relations.txt", "WTN_island_relations = { icon = generic_foreign_policy allowed = { NOT = { original_tag = ZZZ } } visible = { OR = { has_country_flag = WTN_relations_open tag = A01 tag = A03 tag = A10 } } }")
    events += [
        'country_event = { id = wtn_relations.1001 title = wtn_relations.accepted.t desc = wtn_relations.accepted.d picture = GFX_1896_event_trade is_triggered_only = yes timeout_days = 20 trigger = { has_country_flag = WTN_relation_accepted_notice } option = { name = wtn_relations.ack } }',
        'country_event = { id = wtn_relations.1002 title = wtn_relations.declined.t desc = wtn_relations.declined.d picture = GFX_1896_event_trade is_triggered_only = yes timeout_days = 20 trigger = { has_country_flag = WTN_relation_declined_notice } option = { name = wtn_relations.ack } }',
        'country_event = { id = wtn_relations.1003 hidden = yes is_triggered_only = yes trigger = { has_country_flag = WTN_relation_waiting_reply NOT = { has_country_flag = WTN_relation_pending } } immediate = { clr_country_flag = WTN_relation_waiting_reply set_country_flag = { flag = WTN_relation_declined_notice days = 15 } country_event = { id = wtn_relations.1002 days = 1 } } }',
    ]
    write("events/WTN_relations.txt", "\n".join(events))
    shared = {
        "WTN_relation_maritime_tt": ("Обе стороны получают морскую координацию +2% на срок соглашения. Одинаковые услуги нескольких партнёров не складываются.", "Both governments gain +2% naval coordination for the agreement's duration. Identical services from several partners do not stack."),
        "WTN_relation_research_tt": ("Обе стороны получают морскую координацию +2% и скорость исследований +2% на срок соглашения.", "Both governments gain +2% naval coordination and +2% research speed for the agreement's duration."),
        "WTN_relation_workshop_tt": ("Обе стороны получают морскую координацию +2% и рост эффективности производства +2% на срок соглашения.", "Both governments gain +2% naval coordination and +2% production efficiency growth for the agreement's duration."),
        "WTN_relation_northern_tt": ("Обе стороны получают морскую координацию +2% и расход снабжения −2% на срок соглашения.", "Both governments gain +2% naval coordination and −2% supply consumption for the agreement's duration."),
        "WTN_relation_fuel_tt": ("Обе стороны получают морскую координацию +2% и морской расход снабжения −3% на срок соглашения. Нефть и регионы не передаются.", "Both governments gain +2% naval coordination and −3% naval supply consumption for the agreement's duration. No oil or states are transferred."),
        "WTN_relation_colonial_tt": ("Обе стороны получают морскую координацию +2% и скорость строительства +2% на срок соглашения. Колонии сохраняют отдельные кабинеты.", "Both governments gain +2% naval coordination and +2% construction speed for the agreement's duration. Colonies retain separate cabinets."),
        "WTN_relation_caribbean_tt": ("Обе стороны получают морскую координацию +2% и эффективность эскортов +2% на срок соглашения.", "Both governments gain +2% naval coordination and +2% convoy escort efficiency for the agreement's duration."),
        "WTN_island_relations": ("Островная дипломатия", "Island Diplomacy"),
        "WTN_island_relations_desc": ("Прямые соглашения морских служб дополняют отношения с Палатой. Обе стороны должны подтвердить условия; долг, власть и границы соглашением не передаются.", "Direct voyage-services agreements complement relations with the Chamber. Both governments must confirm the terms; agreements transfer no debt, authority or territory."),
        "wtn_relations.title": ("Представители [FROM.GetName]", "Delegates from [FROM.GetName]"),
        "wtn_relations.desc": ("Прибывшие представители предлагают обмениваться портовыми ведомостями, сверять места встречи судов и согласовать передачу торговых грузов. Они готовы подписать ограниченное соглашение морских служб, оставляющее политические вопросы за пределами договора.", "The visiting delegates propose exchanging harbour records, checking ship rendezvous and coordinating merchant cargo handovers. They are prepared to sign a limited voyage-services agreement leaving political questions outside the treaty."),
        "wtn_relations.decline": ("Сейчас мы не готовы принять эти условия", "We cannot accept these terms at present"),
        "wtn_relations.accept": ("Согласовать работу морских служб", "Coordinate our voyage services"),
        "wtn_relations.accepted.t": ("Морские службы договорились", "Voyage Services Agreed"),
        "wtn_relations.accepted.d": ("Посланники прислали подтверждённые условия. Портовые команды обоих правительств могут согласовывать рейсы и обмениваться проверенными ведомостями.", "Our envoys have sent confirmed terms. Harbour crews of both governments can coordinate voyages and exchange verified records."),
        "wtn_relations.declined.t": ("Предложение осталось без соглашения", "The Proposal Yields No Agreement"),
        "wtn_relations.declined.d": ("Представители вернулись без подтверждённых условий. Нашим морским службам предстоит поддерживать рейсы своими средствами и искать другие возможности договориться.", "Our delegates have returned without confirmed terms. Our maritime services must sustain voyages from their own resources and seek other opportunities to agree."),
        "wtn_relations.ack": ("Принять донесение к сведению", "Acknowledge the report"),
    }
    for key, (ru, en) in shared.items():
        local["russian"][key] = ru
        local["english"][key] = en
    for lang, entries in local.items():
        write(f"localisation/{lang}/WTN_relations_l_{lang}.yml", f"l_{lang}:\n" + "\n".join(f' {k}:0 "{v}"' for k, v in entries.items()), bom=True)

    tags = sorted({tag for p in (ROOT / "common/country_tags").glob("*.txt") for tag in re.findall(r'^\s*([A-Z0-9]{3})\s*=', p.read_text(encoding="utf-8-sig"), re.M)} - {"A04", "ZZZ"})
    mark, release, consume, held, orphan = [], [], [], [], []
    for tag in tags:
        flag = "WTN_escrow_" + tag
        mark.append(f"if = {{ limit = {{ tag = {tag} }} A04 = {{ set_country_flag = {flag} }} }}")
        held.append(f"AND = {{ tag = {tag} A04 = {{ has_country_flag = {flag} }} }}")
        release.append(f"if = {{ limit = {{ tag = {tag} country_exists = A04 A04 = {{ has_country_flag = {flag} }} }} A04 = {{ clr_country_flag = {flag} add_to_variable = {{ WTN_liquidity = 10 }} WTN_clamp_treasury_effect = yes }} }}")
        consume.append(f"if = {{ limit = {{ tag = {tag} country_exists = A04 }} A04 = {{ clr_country_flag = {flag} }} }}")
        orphan.append(f"if = {{ limit = {{ has_country_flag = {flag} OR = {{ NOT = {{ country_exists = {tag} }} {tag} = {{ NOT = {{ has_country_flag = WTN_offer_reserved }} }} }} }} clr_country_flag = {flag} add_to_variable = {{ WTN_liquidity = 10 }} }}")
    write("common/scripted_triggers/WTN_escrow.txt", "WTN_has_reservation = { country_exists = A04 OR = { " + " ".join(held) + " } }\nWTN_registered_customer = { OR = { " + " ".join("tag = " + t for t in tags) + " } }")
    escrow = {
        'WTN_mark_reservation_effect': ' '.join(mark),
        'WTN_release_reservation_effect': ' '.join(release),
        'WTN_consume_reservation_effect': ' '.join(consume),
        'WTN_cleanup_orphan_reserves_effect': ' '.join(orphan) + ' WTN_clamp_treasury_effect = yes',
    }
    write("common/scripted_effects/WTN_escrow.txt", '\n'.join(f'{name} = {{ hidden_effect = {{ {body} }} }}' for name, body in escrow.items()))
    write("tools/island_relations_manifest.json", json.dumps(dict(partners=PARTNERS, bilateral_pairs=[list(p) for p in links], services={"_".join(p):service_kind(*p) for p in links}, escrow_tags=tags), indent=2))
    print(f"Built {sum(map(len, PARTNERS.values()))} proposals across {len(links)} bilateral pairs; {len(tags)} recoverable escrow accounts.")


if __name__ == "__main__":
    main()
