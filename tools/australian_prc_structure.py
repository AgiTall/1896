"""Australian colonial adaptation of the installed PRC DLC tree architecture.

References: china_communist.txt (Waking the Tiger), china_communist_sea.txt
(No Compromise, No Surrender): recovery, parallel mobilisation, political
alternatives, and converging development programmes. No PRC runtime dependency.
"""

def apply(fs, tag, add, parents, setv):
    p = 'AUC_' + tag + '_'
    root, economy, second, last = list(fs)[:4]
    positions = {}

    def node(suffix, ru, en, x, y, prerequisites, reward, rd, ed, icon='GFX_goal_generic_national_unity', other=None):
        key = p + suffix
        f = add(fs, key, ru, en, rd, ed, tuple(p+s for s in prerequisites), reward,
                p+other if other else None, icon)
        setv(f, 'cost', 5)
        positions[key] = (x, y)
        return key

    # Recovery and a choice of economic organisation converge into local industry.
    node('recovery', 'Хозяйство после кризиса', 'Recover from the Crisis', 4, 1,
         (root.removeprefix(p),), 'add_stability = 0.03 add_political_power = 25',
         'Согласовать помощь поселениям и восстановление хозяйства после кризиса: +3% стабильности и +25 политической власти.',
         'Coordinate relief and economic recovery: +3% stability and +25 political power.')
    for suffix,ru,en,x,reward,rd,ed,other in [
        ('public_works','Общественные работы','Public Works',0,'add_manpower = 750 add_stability = 0.02','Работы для безработных укрепят поселения: +750 людских ресурсов и +2% стабильности.','Employment programmes strengthen settlements: +750 manpower and +2% stability.','merchant_orders'),
        ('merchant_orders','Заказы торговых домов','Merchant Orders',8,'add_political_power = 60','Опора на торговые дома ускорит размещение заказов: +60 политической власти.','Merchant backing speeds procurement: +60 political power.','public_works')]:
        node(suffix,ru,en,x,2,('recovery',),reward,rd,ed,other=other)
    parents(fs[economy],(p+'public_works',p+'merchant_orders'))
    parents(fs[second],(p+'public_works',p+'merchant_orders'))
    parents(fs[last],(economy,),(second,))
    positions.update({economy:(0,3),second:(8,3),last:(4,4)})
    node('technical_school','Колониальное техническое училище','Colonial Technical School',4,5,
         (last.removeprefix(p),),'add_tech_bonus = { name = AUC_research bonus = 0.5 uses = 1 category = industry }',
         'Готовить мастеров для местных предприятий: одна скидка 50% на промышленное исследование.',
         'Train local specialists: one 50% industry research bonus.','GFX_goal_generic_construct_civ_factory')

    # Army recovery branches into supplies and training before converging.
    node('muster','Перепись колониального ополчения','Count the Colonial Militia',32,1,
         (root.removeprefix(p),),'army_experience = 10',
         'Проверить списки добровольцев и командиров: +10 опыта армии.',
         'Review volunteer and officer rolls: +10 army experience.','GFX_goal_generic_army_doctrines')
    parents(fs[p+'rifles'],(p+'muster',))
    node('supply_depots','Склады территориальных частей','Territorial Supply Depots',36,2,
         ('muster',),'add_equipment_to_stockpile = { type = infantry_equipment_0 amount = 150 producer = ROOT }',
         'Закупить винтовки для территориальных частей: +150 единиц базового пехотного снаряжения.',
         'Purchase rifles for territorial units: +150 basic infantry equipment.','GFX_goal_generic_army_doctrines')
    parents(fs[p+'school'],(p+'rifles',),(p+'supply_depots',))
    parents(fs[p+'harbour'],(p+'rifles',))
    node('joint_exercises','Совместные манёвры округов','Joint District Exercises',32,5,
         ('school','harbour'),'army_experience = 15 add_war_support = 0.03',
         'Штаб и береговая служба отработают общий план обороны: +15 опыта армии и +3% поддержки войны.',
         'Staff and coastal services coordinate defence: +15 army experience and +3% war support.','GFX_goal_generic_army_doctrines')
    # Separate prerequisite blocks mean both services are required.
    parents(fs[p+'joint_exercises'],(p+'school',),(p+'harbour',))
    positions.update({p+'rifles':(28,2),p+'harbour':(28,4),p+'school':(36,4)})

    # Existing constitutional outcomes remain the political spine.
    positions.update({root:(20,0),p+'opening_parliament':(16,1),p+'opening_delegates':(24,1),
        p+'demand':(20,2),p+'federal':(16,3),p+'separate':(24,3),p+'mandate':(16,5),
        p+'credit':(44,1),p+'services':(44,5)})
    node('local_civil_service','Собственная гражданская служба','Our Own Civil Service',24,5,
         ('separate',),'add_political_power = 50 add_stability = 0.03',
         'Укрепить управление самостоятельной колонии: +50 политической власти и +3% стабильности.',
         'Strengthen independent colonial administration: +50 political power and +3% stability.')
    node('district_councils','Советы удалённых округов','Outlying District Councils',20,6,
         ('mandate','local_civil_service'),'add_stability = 0.03 add_manpower = 500',
         'Представительство округов укрепит кабинет при любом конституционном устройстве: +3% стабильности и +500 людских ресурсов.',
         'District representation strengthens either constitutional settlement: +3% stability and +500 manpower.')
    node('trade_delegation','Постоянная торговая делегация','Standing Trade Delegation',44,6,
         ('services',),'add_political_power = 40 navy_experience = 5',
         'Организовать регулярные переговоры о морских поставках: +40 политической власти и +5 опыта флота.',
         'Organise regular maritime supply talks: +40 political power and +5 navy experience.')
    titles = {
        'AVC':('Мельбурнская промышленная программа','Melbourne Industrial Programme'),
        'AQL':('Программа развития северных округов','Northern District Development Programme'),
        'ASA':('Снабжение телеграфного коридора','Supply the Telegraph Corridor'),
        'AWA':('Связать прииски и побережье','Connect Goldfields and Coast'),
        'ATA':('Островная сеть снабжения','Island Supply Network')}
    ru,en=titles[tag]
    node('development_programme',ru,en,12,7,('technical_school','district_councils'),
         'capital_scope = { if = { limit = { is_owned_by = ROOT is_controlled_by = ROOT } add_extra_state_shared_building_slots = 1 add_building_construction = { type = industrial_complex level = 1 instant_build = yes } } }',
         'Объединить техническую подготовку и представительство округов. В контролируемой столице появятся дополнительная строительная ячейка и гражданская фабрика.',
         'Combine technical training and district representation. Gain one building slot and civilian factory in the owned, controlled capital.', 'GFX_goal_generic_construct_civ_factory')
    parents(fs[p+'development_programme'],(p+'technical_school',),(p+'district_councils',))
    node('prepared_colony','Колония, готовая к испытаниям','A Colony Prepared',32,8,
         ('joint_exercises','trade_delegation'),'add_stability = 0.03 add_war_support = 0.03',
         'Согласовать оборону и внешнее снабжение: +3% стабильности и +3% поддержки войны.',
         'Coordinate defence and overseas supplies: +3% stability and +3% war support.')
    parents(fs[p+'prepared_colony'],(p+'joint_exercises',),(p+'trade_delegation',))
    for key,(x,y) in positions.items():
        setv(fs[key],'x',x);setv(fs[key],'y',y)
