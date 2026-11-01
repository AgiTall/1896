"""References, layout, scope and bounded lifecycle checks for the Chamber expansion."""
from collections import Counter, defaultdict
from pathlib import Path
import json
import re

from chamber_script_model import ROOT, EFFECTS, TRIGGERS, EVENTS, TAGS, World
from validate_philippines_rework import parse, value, walk

GAME = Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV')


def read(path):
    return path.read_text(encoding='utf-8-sig')


def static_checks():
    docs = {kind: set(re.findall(r'^## (\w+)\s*$', read(GAME / 'documentation' / f'{kind}_documentation.md'), re.M))
            for kind in ('effects', 'triggers', 'modifiers')}
    paths = [p for folder in ('common', 'events') for p in (ROOT / folder).rglob('*.txt') if p.name.startswith('WTN_')]
    paths += [ROOT / 'common/scripted_effects/WTC_credit.txt', ROOT / 'events/WTC_credit.txt', ROOT / 'common/decisions/WTC_credit.txt']
    trees = {p: parse(read(p)) for p in paths}
    locs = {}
    for language in ('russian', 'english'):
        entries = defaultdict(list)
        for path in (ROOT / 'localisation' / language).rglob('*.yml'):
            for key, text in re.findall(r'^\s+([^ :]+):\d+\s+"(.*)"$', read(path), re.M):
                entries[key].append(text)
        for key, texts in entries.items():
            if key.startswith(('WTN_', 'wtn_')):
                assert len(texts) == 1, (language, key, 'duplicate text')
        locs[language] = entries
    assert {k for k in locs['russian'] if k.startswith(('WTN_', 'wtn_'))} == {k for k in locs['english'] if k.startswith(('WTN_', 'wtn_'))}

    def localized(key):
        assert all(key in entries for entries in locs.values()), ('missing text', key)

    sprites = {}
    for base in (GAME, ROOT):
        for path in (base / 'interface').rglob('*.gfx'):
            for match in re.finditer(r'spriteType\s*=\s*\{\s*name\s*=\s*"?([^"\s]+)"?[^}]*?texturefile\s*=\s*"([^"]+)"', read(path), re.S | re.I):
                sprites[match[1]] = match[2]

    def sprite(name):
        assert name in sprites, ('missing sprite', name)
        assert any((base / sprites[name]).exists() for base in (ROOT, GAME)), ('missing texture', name)

    def condition(nodes):
        for key, _, node in nodes:
            if key in ('AND', 'OR', 'NOT', 'hidden_trigger') or key in TAGS | {'ROOT', 'FROM', 'PREV', 'THIS'}:
                condition(node)
            else:
                assert key in TRIGGERS or key in docs['triggers'], ('unknown condition', key)

    def effect(nodes):
        for key, _, node in nodes:
            if key in TAGS | {'ROOT', 'FROM', 'PREV', 'THIS', 'capital_scope', 'every_country'}:
                for child, op, body in node:
                    if child == 'limit':
                        condition(body)
                    else:
                        effect([(child, op, body)])
            elif key in ('if', 'else_if', 'else', 'hidden_effect'):
                for child, op, body in node:
                    condition(body) if child == 'limit' else effect([(child, op, body)])
            else:
                assert key in EFFECTS or key in docs['effects'], ('unknown effect', key)

    ideas = {key: node for p in (ROOT / 'common/ideas').glob('*.txt')
             for key, _, node in value(value(parse(read(p)), 'ideas', []), 'country', [])}
    focus_ids = {value(node, 'id') for p in (ROOT / 'common/national_focus').glob('*.txt')
                 for key, _, node in value(parse(read(p)), 'focus_tree', []) if key == 'focus'}
    equipment = '\n'.join(read(p) for p in (ROOT / 'common/units/equipment').glob('*.txt'))
    for path, tree in trees.items():
        if path.parent.name == 'scripted_effects':
            for _, _, node in tree:
                effect(node)
        if path.parent.name == 'scripted_triggers':
            for _, _, node in tree:
                condition(node)
        for key, _, node in walk(tree):
            if key in ('limit', 'trigger', 'visible', 'available', 'allowed', 'cancel_trigger', 'target_trigger') and isinstance(node, list):
                condition(node)
            if key in ('complete_effect', 'completion_reward', 'immediate', 'remove_effect', 'cancel_effect'):
                effect(node)
            if key == 'option':
                localized(value(node, 'name'))
                effect([part for part in node if part[0] not in ('name', 'trigger', 'ai_chance')])
            if key in ('title', 'desc', 'custom_effect_tooltip') and isinstance(node, str):
                localized(node)
            if key in ('add_ideas', 'remove_ideas', 'has_idea'):
                assert node in ideas, (path, 'missing idea', node)
            if key == 'add_timed_idea':
                assert value(node, 'idea') in ideas and int(value(node, 'days')) > 0
            if key == 'has_completed_focus':
                assert node in focus_ids, (path, 'missing focus', node)
            if key == 'country_event' and isinstance(node, list):
                eid = value(node, 'id')
                assert eid in EVENTS and re.fullmatch(r'[A-Za-z_]+\.\d+', eid), (path, 'invalid event id', eid)
            if key == 'add_equipment_to_stockpile':
                assert re.search(r'\b' + re.escape(value(node, 'type')) + r'\s*=\s*\{', equipment)
            if key == 'picture':
                sprite(node if node.startswith('GFX_') else 'GFX_idea_' + node)
        if path.parent.name == 'decisions':
            for _, _, category in tree:
                for did, _, node in category:
                    localized(did)
                    localized(did + '_desc')
                    sprite('GFX_decision_' + value(node, 'icon'))
        if path.parent.name == 'categories':
            for cid, _, node in tree:
                localized(cid)
                localized(cid + '_desc')
                sprite('GFX_decision_category_' + value(node, 'icon'))
    for key, node in ideas.items():
        if key.startswith('WTN_'):
            localized(key)
            localized(key + '_desc')
            for modifier, _, _ in value(node, 'modifier', []):
                assert modifier in docs['modifiers'], ('unsupported modifier', modifier)

    assigned = Counter()
    counts = {}
    for path in (ROOT / 'common/national_focus').glob('*.txt'):
        tree = value(parse(read(path)), 'focus_tree')
        for key, _, node in walk(value(tree, 'country', [])):
            if key == 'tag':
                assigned[node] += 1
        if not path.name.startswith('WTN_'):
            continue
        focuses = [node for key, _, node in tree if key == 'focus']
        counts[value(tree, 'id')] = len(focuses)
        positions = {value(f, 'id'): (int(value(f, 'x')), int(value(f, 'y'))) for f in focuses}
        assert len(positions) == len(focuses)
        assert len(set(positions.values())) == len(positions), path
        for fid, (x, y) in positions.items():
            for other, (xx, yy) in positions.items():
                if fid != other and y == yy:
                    assert abs(x - xx) >= 2, (fid, other, 'focus overlap')
        for focus in focuses:
            fid = value(focus, 'id')
            localized(fid)
            localized(fid + '_desc')
            sprite(value(focus, 'icon'))
            for key, _, group in focus:
                if key == 'prerequisite':
                    assert all(positions[parent][1] < positions[fid][1] for name, _, parent in group if name == 'focus')
    assert all(assigned[tag] == 1 for tag in TAGS - {'ZZZ'}), ('focus assignment', dict(assigned))
    # Network agreements never change sovereignty, start/end wars or seize territory.
    forbidden = {'annex_country', 'set_autonomy', 'transfer_state', 'declare_war_on', 'white_peace', 'add_to_faction'}
    assert not {key for p, tree in trees.items() if p.name.startswith('WTN_') for key, _, _ in walk(tree)} & forbidden
    for event_id, event in EVENTS.items():
        if event_id.startswith(('wtn_network.', 'wtn_relations.')) and value(event, 'hidden') != 'yes':
            assert value(event, 'timeout_days') == '20'
            first = next(n for k, _, n in event if k == 'option')
            if value(first, 'name') in {'wtn_network.ack', 'wtn_relations.ack'}:
                assert all(key == 'name' for key, _, _ in first), ('report grants gameplay rewards', event_id)
            else:
                assert value(first, 'name') in {'wtn_network.1.b', 'wtn_network.3.b', 'wtn_relations.decline'}
    bookmark = parse(read(ROOT / 'common/bookmarks/the_gathering_storm.txt'))
    for key, _, node in walk(bookmark):
        if key == 'focuses':
            assert all(fid in focus_ids for fid, _, _ in node), ('bookmark preview', node)
    return counts


def lifecycle_checks():
    cases = 0
    # Credit is backed by one escrow entry for every registered debtor.
    for tag in sorted(TAGS - {'A04', 'ZZZ'}):
        w = World()
        before = w.vars[tag]['WTC_debt']
        w.effect('WTN_open_offer_effect', tag)
        assert w.vars['A04']['WTN_liquidity'] == 50
        assert 'WTN_escrow_' + tag in w.flags['A04']
        w.effect('WTN_accept_offer_effect', tag)
        assert w.vars[tag]['WTC_debt'] == before + 15
        assert w.inventory(tag, 'convoy') == 15 and w.inventory(tag, 'support_equipment') == 75
        assert 'WTN_escrow_' + tag not in w.flags['A04']
        w.effect('WTN_accept_offer_effect', tag)
        w.effect('WTN_close_offer_effect', tag)
        assert w.inventory(tag, 'convoy') == 15 and w.vars['A04']['WTN_liquidity'] == 50
        cases += 3
    for reserve in (0, 9, 9.99, 10, 10.01, 60):
        for standard in (False, True):
            w = World()
            w.vars['A04']['WTN_liquidity'] = reserve
            w.effect('WTC_borrow_effect' if standard else 'WTN_open_offer_effect', 'A03')
            assert w.vars['A04']['WTN_liquidity'] == reserve - (10 if reserve >= 10 else 0)
            assert w.inventory('A03', 'convoy') == (25 if standard and reserve >= 10 else 0)
            cases += 1
    for scenario in ('decline', 'timeout', 'undelivered', 'annexed', 'creditor_gone', 'war', 'capitulation', 'autarky', 'receivership'):
        w = World()
        w.effect('WTN_open_offer_effect', 'A03')
        if scenario == 'decline':
            w.effect('WTN_close_offer_effect', 'A03')
        elif scenario == 'annexed':
            w.tags.remove('A03')
        elif scenario == 'creditor_gone':
            w.tags.remove('A04')
        elif scenario == 'war':
            w.wars.add(frozenset(('A03', 'A04')))
        elif scenario == 'capitulation':
            w.capitulated.add('A03')
        elif scenario in ('autarky', 'receivership'):
            w.flags['A03'].add('JPI_autarky' if scenario == 'autarky' else 'WTC_receivership')
        w.advance(32, deliver=scenario != 'undelivered')
        if scenario != 'creditor_gone':
            assert w.vars['A04']['WTN_liquidity'] == 60, scenario
        if scenario == 'annexed':
            w.tags.add('A03')
        if scenario == 'creditor_gone':
            w.tags.add('A04')
        w.effect('WTN_accept_offer_effect', 'A03')
        w.effect('WTN_close_offer_effect', 'A03')
        w.effect('WTN_cleanup_orphan_reserves_effect')
        assert w.inventory('A03', 'convoy') == 0
        assert w.vars['A04']['WTN_liquidity'] == 60, (scenario, 'double refund or resurrection')
        cases += 2

    for tag in ('A02', 'A09', 'A08', 'A06', 'MLT', 'A05', 'A07', 'A01', 'A03', 'A10'):
        w = World()
        w.flags[tag].add('WTN_compact_desk_open')
        debt = w.vars[tag]['WTC_debt']
        w.effect('WTN_request_compact_effect', tag)
        assert any(event == 'wtn_network.3' and receiver == 'A04' and source == tag for _, event, receiver, source in w.queue)
        w.answer('wtn_network.3', 'wtn_network.3.a', 'A04', tag)
        assert w.vars[tag]['WTC_debt'] == debt + (-5 if tag == 'A02' else 5)
        assert 'WTN_trade_partner' in w.flags[tag]
        assert len([idea for idea in w.ideas[tag] if idea.startswith('WTN_pact_')]) == 1
        after = w.vars[tag]['WTC_debt']
        w.answer('wtn_network.3', 'wtn_network.3.a', 'A04', tag)
        assert w.vars[tag]['WTC_debt'] == after
        w.advance(360)
        assert 'WTN_trade_partner' not in w.flags[tag]
        assert not [idea for idea in w.ideas[tag] if idea.startswith('WTN_pact_')]
        cases += 3
    for scenario in ('war', 'annexed', 'capitulated', 'autarky', 'debt', 'expired'):
        w = World()
        w.flags['A09'].add('WTN_compact_desk_open')
        w.effect('WTN_request_compact_effect', 'A09')
        if scenario == 'war': w.wars.add(frozenset(('A09', 'A04')))
        if scenario == 'annexed': w.tags.remove('A09')
        if scenario == 'capitulated': w.capitulated.add('A09')
        if scenario == 'autarky': w.flags['A09'].add('JPI_autarky')
        if scenario == 'debt': w.vars['A09']['WTC_debt'] = 80
        if scenario == 'expired': w.advance(31, deliver=False)
        debt = w.vars['A09']['WTC_debt']
        w.answer('wtn_network.3', 'wtn_network.3.a', 'A04', 'A09')
        assert w.vars['A09']['WTC_debt'] == debt and 'WTN_trade_partner' not in w.flags['A09']
        cases += 1

    relations = json.loads(read(ROOT / 'tools/island_relations_manifest.json'))
    for source, targets in relations['partners'].items():
        for target in targets:
            name = f'WTN_relation_{source}_{target}'
            link = 'WTN_link_' + '_'.join(sorted((source, target)))
            w = World()
            w.flags[source].add('WTN_relations_open')
            w.effect(name + '_propose_effect', source)
            assert w.queue and not w.ideas[source] and not w.ideas[target]
            w.effect(name + '_accept_effect', target)
            assert link in w.flags[source] & w.flags[target]
            assert 'WTN_island_cooperation' in w.ideas[source] & w.ideas[target]
            w.effect(name + '_accept_effect', target)
            assert len(w.ideas[source]) == len(w.ideas[target]) == (1 if relations['services']['_'.join(sorted((source, target)))] == 'maritime' else 2)
            assert w.vars[source]['WTC_debt'] == World().vars[source]['WTC_debt']
            assert not w.wars and not w.government
            w.wars.add(frozenset((source, target)))
            w.effect('WTN_refresh_links_effect', source)
            w.effect('WTN_refresh_links_effect', target)
            assert link not in w.flags[source] | w.flags[target]
            assert 'WTN_island_cooperation' not in w.ideas[source] | w.ideas[target]
            cases += 4
            for scenario in ('decline', 'annexed', 'war', 'capitulated', 'expired'):
                w = World()
                w.flags[source].add('WTN_relations_open')
                w.effect(name + '_propose_effect', source)
                if scenario == 'decline': w.effect(name + '_decline_effect', target)
                if scenario == 'annexed': w.tags.remove(source)
                if scenario == 'war': w.wars.add(frozenset((source, target)))
                if scenario == 'capitulated': w.capitulated.add(target)
                if scenario == 'expired':
                    w.flags[source].discard(name + '_pending')
                    w.flags[source].discard('WTN_relation_pending')
                w.effect(name + '_accept_effect', target)
                assert link not in w.flags[source] | w.flags[target], (source, target, scenario)
                assert not w.ideas[source] and not w.ideas[target]
                cases += 1

    for debt in (70, 70.01, 71, 90, 90.01, 99, 99.99, 100):
        w = World()
        w.vars['A03']['WTC_debt'] = debt
        w.effect('WTC_refresh_effect', 'A03')
        assert ('WTC_blacklist' in w.ideas['A03']) == (debt > 90)
        assert any(event == 'wtc_credit.3' for _, event, _, _ in w.queue) == (debt == 100)
        assert any(event == 'wtc_credit.1' for _, event, _, _ in w.queue) == (70 < debt < 100)
        cases += 1
    for option, cover in (('a', True), ('b', True), ('c', False)):
        w = World()
        w.vars['A03']['WTC_debt'] = 100
        if not cover: w.global_flags.clear()
        w.effect('WTC_refresh_effect', 'A03')
        w.answer('wtc_credit.3', 'wtc_credit.3.' + option, 'A03')
        debt = w.vars['A03']['WTC_debt']
        pp = w.pp['A03']
        w.answer('wtc_credit.3', 'wtc_credit.3.' + option, 'A03')
        assert w.vars['A03']['WTC_debt'] == debt and w.pp['A03'] == pp
        assert ('A03' in w.government) == (option == 'a')
        cases += 2
    w = World()
    w.flags['A03'].add('WTC_active_loan')
    w.vars['A03']['WTC_debt'] = 10
    w.effect('WTC_repay_effect', 'A03')
    assert w.vars['A03']['WTC_debt'] == 0 and 'WTC_active_loan' not in w.flags['A03']
    w.effect('WTC_monthly_effect', 'A03')
    assert w.vars['A03']['WTC_debt'] == 0
    assert w.vars['A04']['WTN_liquidity'] == 63
    w.effect('WTN_update_ledger_effect')
    expected = sum(w.vars[tag]['WTC_debt'] for tag in w.tags - {'A04', 'ZZZ'})
    assert w.vars['A04']['WTN_principal'] == expected
    assert w.vars['A04']['WTN_accounts'] == len(TAGS) - 3
    assert 'WTC_ledger_open' not in w.flags['ZZZ'] | w.flags['A04']
    w.effect('WTN_monthly_treasury_effect')
    assert w.vars['A04']['WTN_liquidity'] == 68
    cases += 4

    # Suspension closes new lines while honouring already reserved offers.
    w = World()
    w.effect('WTN_open_offer_effect', 'A03')
    w.flags['A04'].add('WTN_credit_suspended')
    w.effect('WTN_open_offer_effect', 'A01')
    w.effect('WTC_borrow_effect', 'A02')
    assert w.vars['A04']['WTN_liquidity'] == 50
    w.effect('WTN_accept_offer_effect', 'A03')
    assert w.inventory('A03', 'convoy') == 15
    cases += 2

    # British withdrawal immediately removes naval blacklists, not cable restrictions.
    w = World()
    w.vars['A03']['WTC_debt'] = 100
    w.effect('WTC_refresh_effect', 'A03')
    w.flags['A02'].add('WTN_cover_revoked')
    w.effect('WTC_check_cover_effect')
    assert 'WTC_british_cover' not in w.global_flags and 'WTC_blacklist' not in w.ideas['A03']
    assert 'WTC_cable_blackout' in w.ideas['A03']
    w.answer('wtc_credit.3', 'wtc_credit.3.a', 'A03')
    assert not w.government and w.vars['A03']['WTC_debt'] == 100
    w.answer('wtc_credit.3', 'wtc_credit.3.c', 'A03')
    assert w.vars['A03']['WTC_debt'] == 90
    cases += 3

    for event_id, debt, option in (('wtc_credit.1', 80, 'b'), ('wtc_credit.2', 95, 'a'), ('wtc_credit.3', 100, 'b')):
        w = World()
        w.vars['A03']['WTC_debt'] = debt
        w.effect('WTC_refresh_effect', 'A03')
        w.answer(event_id, event_id + '.' + option, 'A03')
        pp, new_debt, stability = w.pp['A03'], w.vars['A03']['WTC_debt'], w.stability['A03']
        w.answer(event_id, event_id + '.' + option, 'A03')
        assert (w.pp['A03'], w.vars['A03']['WTC_debt'], w.stability['A03']) == (pp, new_debt, stability)
        cases += 1

    # A country may receive several different services, never duplicate the same kind.
    w = World()
    for source, target in (('A02', 'A01'), ('A05', 'A02')):
        w.flags[source].add('WTN_relations_open')
        w.effect(f'WTN_relation_{source}_{target}_propose_effect', source)
        w.effect(f'WTN_relation_{source}_{target}_accept_effect', target)
    assert {'WTN_link_fuel_services', 'WTN_link_caribbean_services', 'WTN_island_cooperation'} <= w.ideas['A02']
    w.wars.add(frozenset(('A02', 'A01')))
    w.effect('WTN_refresh_links_effect', 'A02')
    assert 'WTN_link_fuel_services' not in w.ideas['A02'] and 'WTN_island_cooperation' in w.ideas['A02']
    w.advance(360, deliver=False)
    assert not w.ideas['A02'] and not w.ideas['A05']
    cases += 3

    # Cancelling an external contract must preserve workshop work funded at home.
    w = World()
    w.ideas['A09'].add('WTN_osaka_contract')
    w.flags['A09'].update(('WTN_compact_desk_open', 'WTN_compact_pending'))
    w.effect('WTN_sign_compact_effect', 'A09')
    w.effect('WTN_cancel_compact_effect', 'A09')
    assert w.ideas['A09'] == {'WTN_osaka_contract'}
    cases += 1

    # Execute every new focus reward in its own eligible country and controlled capital.
    for path in (ROOT / 'common/national_focus').glob('WTN*_focus.txt'):
        tree = value(parse(read(path)), 'focus_tree')
        tags = [node for key, _, node in walk(value(tree, 'country')) if key == 'tag']
        if not tags:
            continue  # Legacy trees retained for saves may have no country assignment.
        tag = tags[0]
        for key, _, focus in tree:
            if key != 'focus': continue
            w = World()
            w.states[1] = dict(owner=tag, controller=tag, slots=0, industry=0)
            w.capitals[tag] = 1
            w.run(value(focus, 'completion_reward'), tag)
            if value(focus, 'id').endswith('_local_service') or value(focus, 'id') == 'WTN_common_registry':
                assert w.states[1]['industry'] == w.states[1]['slots'] == 1
            cases += 1
    for owner, controller in (('A01', 'A04'), ('A04', 'A01')):
        w = World()
        w.states[697].update(owner=owner, controller=controller)
        w.effect('WTN_local_workshops_effect')
        assert w.states[697]['industry'] == w.states[697]['slots'] == 0
        w.effect('WTN_armourer_workshops_effect')
        assert w.states[697].get('arms', 0) == 0 and w.states[697]['slots'] == 0
        cases += 1

    # One reachable route funds a usable civilian base, including initially empty capitals.
    for path in (ROOT / 'common/national_focus').glob('WTN*_focus.txt'):
        tree = value(parse(read(path)), 'focus_tree')
        tags = [node for key, _, node in walk(value(tree, 'country')) if key == 'tag']
        if not tags:
            continue  # No new campaign can select this compatibility tree.
        tag = tags[0]
        w = World()
        w.states[1] = dict(owner=tag, controller=tag, slots=0, industry=0)
        w.capitals[tag] = 1
        completed = set()
        pending=[focus for key,_,focus in tree if key=='focus']
        while pending:
            progress=False
            for focus in list(pending):
                excluded = {fid for k, _, group in focus if k == 'mutually_exclusive' for name, _, fid in group if name == 'focus'}
                groups = [{fid for name, _, fid in group if name == 'focus'} for k, _, group in focus if k == 'prerequisite']
                if excluded & completed:pending.remove(focus);continue
                if any(not group & completed for group in groups):continue
                fid=value(focus,'id');completed.add(fid);pending.remove(focus);progress=True
                w.focuses[tag].add(fid);w.run(value(focus,'completion_reward'),tag)
            if not progress:break
        assert w.states[1]['industry'] == 2, (path.name, 'civilian programme')
        assert w.states[1].get('arms', 0) == (1 if tag in ('A08', 'PCF') else 0)
        cases += 1

    w = World()
    w.vars['A04']['WTN_liquidity'] = 20
    for tag in ('A01', 'A03', 'A09'): w.effect('WTN_open_offer_effect', tag)
    assert w.vars['A04']['WTN_liquidity'] == 0 and 'WTN_offer_reserved' not in w.flags['A09']
    w.effect('WTN_accept_offer_effect', 'A01')
    w.effect('WTN_close_offer_effect', 'A03')
    assert w.vars['A04']['WTN_liquidity'] == 10 and w.inventory('A01', 'convoy') == 15
    cases += 2

    naval_service = value(parse(read(ROOT / 'common/decisions/WTC_credit.txt')), 'WTC_debt_ledger')
    naval_service = value(naval_service, 'WTC_naval_service')
    for convoys, rifles in ((9.99, 500), (10, 499.99), (10, 500)):
        w = World()
        w.wars.add(frozenset(('A02', 'A05')))
        w.stock['A03'].update(convoy_1=convoys, infantry_equipment_0=rifles)
        assert w.test(value(naval_service, 'available'), 'A03') == (convoys >= 10 and rifles >= 500)
        assert not w.test(value(naval_service, 'available'), 'A02'), 'British self-transfer cannot discharge debt'
        cases += 1

    # Run the real country-scoped monthly hooks once for every country.
    w = World()
    for name in ('WTC_credit', 'WTN_network'):
        hooks = value(parse(read(ROOT / f'common/on_actions/{name}.txt')), 'on_actions')
        monthly = value(value(hooks, 'on_monthly'), 'effect')
        for tag in sorted(w.tags): w.run(monthly, tag)
    assert w.vars['A04']['WTN_liquidity'] == 65
    assert all(w.pp[tag] == 498 for tag in TAGS - {'A04', 'ZZZ'})
    assert w.pp['A04'] == w.pp['ZZZ'] == 500
    cases += 1
    return cases


def main():
    counts = static_checks()
    cases = lifecycle_checks()
    report = dict(status='passed', added_focus_trees=counts, added_focuses=sum(counts.values()),
                  lifecycle_scenarios=cases, covered_tags=sorted(TAGS - {'ZZZ'}),
                  limitations=['Static definitions and bounded script execution; no HOI4 engine launch.',
                               'No campaign balance, diplomatic AI or native UI verification.'])
    (ROOT / 'tools/chamber_network_validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'PASS: {sum(counts.values())} focuses in {len(counts)} trees; {cases} lifecycle scenarios; all country assignments, references, bilingual text and focus positions.')


if __name__ == '__main__':
    main()
