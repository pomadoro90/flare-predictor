"""Unified standalone Blender build script for the flare predictor scene.

This file inlines flare_install.py with separator_new.py, scene_build_clean.py,
and flare_tip_final.py so it can be run directly with:
    blender --background --python build_all.py
"""
"""
ФАКЕЛЬНАЯ УСТАНОВКА НПЗ — low-poly модель для курсовой работы.
Версия: v29 | Полигонов: ~25K | Blender 5.1.1 | Рендер: EEVEE/Workbench

═══════════════════════════════════════════════════════════
                    АННОТАЦИЯ ОБЪЕКТОВ
═══════════════════════════════════════════════════════════

СЕКЦИИ КОДА (по номерам ═══):
  0. ЗЕМЛЯ + ПЛОЩАДКА — Ground (зелёный plane 60×60), Pad (бетон 48×36×0.12)
  1. СТВОЛ — три секции: красная 0-12м (Ø2.2), белая 12-28м (Ø2.2), красная 28-38м (Ø2.2)
  2. ПЛАТФОРМЫ — 3 шт. на стыках 12/28м + верхняя 37м, R=2.0, перила h=1.3
  3. ЛЕСТНИЦА — Н-образная (2 рейки + перекладины), 3 секции со сдвигом 90°, защитная клетка
  4. ОТТЯЖКИ — 12 тросов (3 яруса × 4 направления), анкеры 1.4×1.4×0.8м на расстоянии 20м
  5. ГОРЕЛКА — Burner_B + сопло + пламя (конус 7м) + дежурные горелки (3) + паровой коллектор + газовый коллектор
  6. ДАТЧИКИ НА СТВОЛЕ — P_flare, Q_flare, P_purge, Q_purge (давление), T_flame (темп.), Steam_Q
  7. СЕПАРАТОР — горизонтальный 7.5×Ø2.8м, опоры, уровнемер, манометр, лестница-клетка
  8. ДРЕНАЖ — вертикальная ёмкость Ø0.9×2.4м, уровнемер
  9. ТРУБОПРОВОДНАЯ ЭСТАКАДА — П-образные рамы на фундаментах, линии: сброс, продувка, конденсат, пар
 9a. ДАТЧИК РАСХОДА НА ПРОДУВОЧНОЙ ЛИНИИ — корпус + измерительный элемент (X=-3, Y=RY+0.3)
 9b. ДАТЧИКИ НА ОПОРЫ ЭСТАКАДЫ — 3 вибродатчика на левых стойках рам X∈{-12,-6,0}
 9c. ФУНДАМЕНТНАЯ ПЛИТА СЕПАРАТОРА — бетонная плита 8.5×3.4×0.12 под сепаратором
 10. СВЕТ — Sun (25,-20,35), energy=4.5
 11. КАМЕРА — lens=18, позиция (28,-30,22), цель (-4,-3,15)
 12. РЕНДЕР — EEVEE, 1920×1080, голубое небо, exposure=1.2

МАТЕРИАЛЫ (префиксы):
  MR — Red (#C62828) ствол, опоры эстакады
  MW — White ствол, сепаратор, анкерные блоки
  MS — Steel ролики, валы, лестница, клетка, перила
  MY — Yellow трубы, датчики давления
  MB — Burner тёмный металл горелок
  MF — Flame оранжевое пламя
  MC — Cable чёрные тросы оттяжек
  MN — Concrete фундаменты, бетонная площадка
  MG — Ground зелёная земля
  MM — Sensor тёмные головки датчиков

ПРОСТРАНСТВЕННАЯ СХЕМА (вид сверху, ось X→, Y↑):
                    N (Y+)
            anc(20,19)  anc(20,19)
             /              \
            /                \
    W --sep(-7,-4.5)====эстакада(Y=-7)====[СТВОЛ(0,-1)]--  E (X+)
            \                /
             \              /
            anc(-20,-21) anc(-20,-21)
                    S (Y-)

  Ствол:    X=0, Y=-1, H=38м
  Сепаратор: X=-7, Y=-4.5, 7.5×Ø2.8
  Дренаж:   X=-11.5, Y=-5, Ø0.9×2.4
  Эстакада: Y=-7, X∈[-12;3], трубы на z≈2.9
  Анкеры:   R=20м от ствола, высоты крепления 10/20/34м

ЗАПУСК:
  blender --background --python flare_install.py
  blender --background flare_install.blend --python render_views.py
  bash render_all.sh
"""
import bpy, math, os
from mathutils import Vector, Matrix

# ═══════ INLINE MODULE: flare_tip_final.py ═══════


# Object state transcribed from /tmp/blender-agent-3/execute/model_state.json.
OBJECTS = [{'dims': [208.0, 208.0, 195.0],
  'loc': [0.0, 0.0, 3.835],
  'material': 'mat_beacon',
  'name': 'geo_beacon',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 96},
 {'dims': [39.0, 39.0, 390.0],
  'loc': [0.0, 0.0, 3.575],
  'material': 'mat_beacon_bracket',
  'name': 'geo_beacon_bracket',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [1014.0, 1014.0, 2860.0],
  'loc': [0.0, 0.0, 1.4885],
  'material': 'mat_body',
  'name': 'geo_body',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 384},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [0.507, 0.0, 0.0975],
  'material': 'mat_flange',
  'name': 'geo_bolt_01',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [0.48217, 0.15665, 0.0975],
  'material': 'mat_flange',
  'name': 'geo_bolt_02',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [0.41015, 0.29796, 0.0975],
  'material': 'mat_flange',
  'name': 'geo_bolt_03',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [0.29796, 0.41015, 0.0975],
  'material': 'mat_flange',
  'name': 'geo_bolt_04',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [0.15665, 0.48217, 0.0975],
  'material': 'mat_flange',
  'name': 'geo_bolt_05',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [0.0, 0.507, 0.0975],
  'material': 'mat_flange',
  'name': 'geo_bolt_06',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [-0.15665, 0.48217, 0.0975],
  'material': 'mat_flange',
  'name': 'geo_bolt_07',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [-0.29796, 0.41015, 0.0975],
  'material': 'mat_flange',
  'name': 'geo_bolt_08',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [-0.41015, 0.29796, 0.0975],
  'material': 'mat_flange',
  'name': 'geo_bolt_09',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [-0.48217, 0.15665, 0.0975],
  'material': 'mat_flange',
  'name': 'geo_bolt_10',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [-0.507, 0.0, 0.0975],
  'material': 'mat_flange',
  'name': 'geo_bolt_11',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [-0.48217, -0.15665, 0.0975],
  'material': 'mat_flange',
  'name': 'geo_bolt_12',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [-0.41015, -0.29796, 0.0975],
  'material': 'mat_flange',
  'name': 'geo_bolt_13',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [-0.29796, -0.41015, 0.0975],
  'material': 'mat_flange',
  'name': 'geo_bolt_14',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [-0.15665, -0.48217, 0.0975],
  'material': 'mat_flange',
  'name': 'geo_bolt_15',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [0.0, -0.507, 0.0975],
  'material': 'mat_flange',
  'name': 'geo_bolt_16',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [0.15665, -0.48217, 0.0975],
  'material': 'mat_flange',
  'name': 'geo_bolt_17',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [0.29796, -0.41015, 0.0975],
  'material': 'mat_flange',
  'name': 'geo_bolt_18',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [0.41015, -0.29796, 0.0975],
  'material': 'mat_flange',
  'name': 'geo_bolt_19',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [0.48217, -0.15665, 0.0975],
  'material': 'mat_flange',
  'name': 'geo_bolt_20',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [195.0, 195.0, 2600.0],
  'loc': [0.0, 0.0, 1.43],
  'material': 'mat_steam_headers',
  'name': 'geo_central_steam_pipe',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 384},
 {'dims': [58.5, 15.6, 156.0],
  'loc': [0.078, 0.0, 2.73],
  'material': 'mat_vortex_vane',
  'name': 'geo_central_vortex_vane_01',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, 45.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 8},
 {'dims': [58.5, 15.6, 156.0],
  'loc': [0.039, 0.0676, 2.73],
  'material': 'mat_vortex_vane',
  'name': 'geo_central_vortex_vane_02',
  'parent': 'geo_flare_tip_assembly',
  'rot': [-0.0, 45.0, 60.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 8},
 {'dims': [58.5, 15.6, 156.0],
  'loc': [-0.039, 0.0676, 2.73],
  'material': 'mat_vortex_vane',
  'name': 'geo_central_vortex_vane_03',
  'parent': 'geo_flare_tip_assembly',
  'rot': [-0.0, 45.0, 120.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 8},
 {'dims': [58.5, 15.6, 156.0],
  'loc': [-0.078, 0.0, 2.73],
  'material': 'mat_vortex_vane',
  'name': 'geo_central_vortex_vane_04',
  'parent': 'geo_flare_tip_assembly',
  'rot': [-0.0, 45.0, -180.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 8},
 {'dims': [58.5, 15.6, 156.0],
  'loc': [-0.039, -0.0676, 2.73],
  'material': 'mat_vortex_vane',
  'name': 'geo_central_vortex_vane_05',
  'parent': 'geo_flare_tip_assembly',
  'rot': [-0.0, 45.0, -120.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 8},
 {'dims': [58.5, 15.6, 156.0],
  'loc': [0.039, -0.0676, 2.73],
  'material': 'mat_vortex_vane',
  'name': 'geo_central_vortex_vane_06',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, 45.0, -60.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 8},
 {'dims': [611.0, 611.0, 15.6],
  'loc': [0.0, 0.0, 3.445],
  'material': 'mat_vortex_vane',
  'name': 'geo_deflector',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 192},
 {'dims': [65.0, 65.0, 520.0],
  'loc': [0.0, 0.0, 3.185],
  'material': 'mat_vortex_vane',
  'name': 'geo_deflector_stalk',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 96},
 {'dims': [1170.0, 1170.0, 58.5],
  'loc': [0.0, 0.0, 0.02925],
  'material': 'mat_flange',
  'name': 'geo_flange',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 1366},
 {'dims': [52.0, 52.0, 156.0],
  'loc': [0.663, 0.0, 0.26],
  'material': 'mat_pilot',
  'name': 'geo_fuel_inlet',
  'parent': 'grp_pilot_burners',
  'rot': [90.0, -0.0, 90.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 128},
 {'dims': [11.7, 11.7, 23.4],
  'loc': [0.7488, 0.039, 0.26],
  'material': 'mat_flange',
  'name': 'geo_fuel_inlet_bolt_01',
  'parent': 'grp_pilot_burners',
  'rot': [90.0, -0.0, 90.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [11.7, 11.7, 23.4],
  'loc': [0.7488, 0.0195, 0.2938],
  'material': 'mat_flange',
  'name': 'geo_fuel_inlet_bolt_02',
  'parent': 'grp_pilot_burners',
  'rot': [90.0, -0.0, 90.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [11.7, 11.7, 23.4],
  'loc': [0.7488, -0.0195, 0.2938],
  'material': 'mat_flange',
  'name': 'geo_fuel_inlet_bolt_03',
  'parent': 'grp_pilot_burners',
  'rot': [90.0, -0.0, 90.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [11.7, 11.7, 23.4],
  'loc': [0.7488, -0.039, 0.26],
  'material': 'mat_flange',
  'name': 'geo_fuel_inlet_bolt_04',
  'parent': 'grp_pilot_burners',
  'rot': [90.0, -0.0, 90.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [11.7, 11.7, 23.4],
  'loc': [0.7488, -0.0195, 0.2262],
  'material': 'mat_flange',
  'name': 'geo_fuel_inlet_bolt_05',
  'parent': 'grp_pilot_burners',
  'rot': [90.0, -0.0, 90.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [11.7, 11.7, 23.4],
  'loc': [0.7488, 0.0195, 0.2262],
  'material': 'mat_flange',
  'name': 'geo_fuel_inlet_bolt_06',
  'parent': 'grp_pilot_burners',
  'rot': [90.0, -0.0, 90.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [104.0, 104.0, 15.6],
  'loc': [0.741, 0.0, 0.26],
  'material': 'mat_flange',
  'name': 'geo_fuel_inlet_flange',
  'parent': 'grp_pilot_burners',
  'rot': [90.0, -0.0, 90.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 128},
 {'dims': [1170.0, 1170.0, 52.0],
  'loc': [0.0, 0.0, 0.26],
  'material': 'mat_pilot',
  'name': 'geo_fuel_manifold',
  'parent': 'grp_pilot_burners',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 3200},
 {'dims': [31.2, 31.2, 65.0],
  'loc': [0.559, 0.0, 0.26],
  'material': 'mat_pilot',
  'name': 'geo_fuel_tee_1',
  'parent': 'grp_pilot_burners',
  'rot': [90.0, -0.0, 90.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 96},
 {'dims': [31.2, 31.2, 65.0],
  'loc': [-0.28002, 0.48373, 0.26],
  'material': 'mat_pilot',
  'name': 'geo_fuel_tee_2',
  'parent': 'grp_pilot_burners',
  'rot': [90.0, 0.0, -149.93],
  'scale': [1.0, 1.0, 1.0],
  'verts': 96},
 {'dims': [31.2, 31.2, 65.0],
  'loc': [-0.28002, -0.48373, 0.26],
  'material': 'mat_pilot',
  'name': 'geo_fuel_tee_3',
  'parent': 'grp_pilot_burners',
  'rot': [90.0, 0.0, -30.07],
  'scale': [1.0, 1.0, 1.0],
  'verts': 96},
 {'dims': [884.0, 884.0, 26.0],
  'loc': [0.0, 0.0, 0.078],
  'material': 'mat_body',
  'name': 'geo_gas_seal',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 384},
 {'dims': [58.5, 67.6, 32.5],
  'loc': [0.507, 0.0, 0.15275],
  'material': 'mat_flange',
  'name': 'geo_hex_nut_01',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 12},
 {'dims': [58.5, 67.6, 32.5],
  'loc': [0.48217, 0.15665, 0.15275],
  'material': 'mat_flange',
  'name': 'geo_hex_nut_02',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 12},
 {'dims': [58.5, 67.6, 32.5],
  'loc': [0.41015, 0.29796, 0.15275],
  'material': 'mat_flange',
  'name': 'geo_hex_nut_03',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 12},
 {'dims': [58.5, 67.6, 32.5],
  'loc': [0.29796, 0.41015, 0.15275],
  'material': 'mat_flange',
  'name': 'geo_hex_nut_04',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 12},
 {'dims': [58.5, 67.6, 32.5],
  'loc': [0.15665, 0.48217, 0.15275],
  'material': 'mat_flange',
  'name': 'geo_hex_nut_05',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 12},
 {'dims': [58.5, 67.6, 32.5],
  'loc': [0.0, 0.507, 0.15275],
  'material': 'mat_flange',
  'name': 'geo_hex_nut_06',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 12},
 {'dims': [58.5, 67.6, 32.5],
  'loc': [-0.15665, 0.48217, 0.15275],
  'material': 'mat_flange',
  'name': 'geo_hex_nut_07',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 12},
 {'dims': [58.5, 67.6, 32.5],
  'loc': [-0.29796, 0.41015, 0.15275],
  'material': 'mat_flange',
  'name': 'geo_hex_nut_08',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 12},
 {'dims': [58.5, 67.6, 32.5],
  'loc': [-0.41015, 0.29796, 0.15275],
  'material': 'mat_flange',
  'name': 'geo_hex_nut_09',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 12},
 {'dims': [58.5, 67.6, 32.5],
  'loc': [-0.48217, 0.15665, 0.15275],
  'material': 'mat_flange',
  'name': 'geo_hex_nut_10',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 12},
 {'dims': [58.5, 67.6, 32.5],
  'loc': [-0.507, 0.0, 0.15275],
  'material': 'mat_flange',
  'name': 'geo_hex_nut_11',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 12},
 {'dims': [58.5, 67.6, 32.5],
  'loc': [-0.48217, -0.15665, 0.15275],
  'material': 'mat_flange',
  'name': 'geo_hex_nut_12',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 12},
 {'dims': [58.5, 67.6, 32.5],
  'loc': [-0.41015, -0.29796, 0.15275],
  'material': 'mat_flange',
  'name': 'geo_hex_nut_13',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 12},
 {'dims': [58.5, 67.6, 32.5],
  'loc': [-0.29796, -0.41015, 0.15275],
  'material': 'mat_flange',
  'name': 'geo_hex_nut_14',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 12},
 {'dims': [58.5, 67.6, 32.5],
  'loc': [-0.15665, -0.48217, 0.15275],
  'material': 'mat_flange',
  'name': 'geo_hex_nut_15',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 12},
 {'dims': [58.5, 67.6, 32.5],
  'loc': [0.0, -0.507, 0.15275],
  'material': 'mat_flange',
  'name': 'geo_hex_nut_16',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 12},
 {'dims': [58.5, 67.6, 32.5],
  'loc': [0.15665, -0.48217, 0.15275],
  'material': 'mat_flange',
  'name': 'geo_hex_nut_17',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 12},
 {'dims': [58.5, 67.6, 32.5],
  'loc': [0.29796, -0.41015, 0.15275],
  'material': 'mat_flange',
  'name': 'geo_hex_nut_18',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 12},
 {'dims': [58.5, 67.6, 32.5],
  'loc': [0.41015, -0.29796, 0.15275],
  'material': 'mat_flange',
  'name': 'geo_hex_nut_19',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 12},
 {'dims': [58.5, 67.6, 32.5],
  'loc': [0.48217, -0.15665, 0.15275],
  'material': 'mat_flange',
  'name': 'geo_hex_nut_20',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 12},
 {'dims': [195.0, 156.0, 104.0],
  'loc': [0.546, 0.325, 0.65],
  'material': 'mat_instrument',
  'name': 'geo_junction_box',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 30.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 8},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [0.481, 0.0, 1.04],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_lower_01',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, -0.0, 90.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [0.45201, 0.16445, 1.04],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_lower_02',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, -0.0, 110.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [0.36842, 0.30914, 1.04],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_lower_03',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, -0.0, 130.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [0.2405, 0.41652, 1.04],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_lower_04',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, -0.0, 150.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [0.08346, 0.47372, 1.04],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_lower_05',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, 0.0, 170.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [-0.08346, 0.47372, 1.04],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_lower_06',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, -0.0, -170.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [-0.2405, 0.41652, 1.04],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_lower_07',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, 0.0, -150.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [-0.36842, 0.30914, 1.04],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_lower_08',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, 0.0, -130.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [-0.45201, 0.16445, 1.04],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_lower_09',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, 0.0, -110.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [-0.481, 0.0, 1.04],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_lower_10',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, 0.0, -90.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [-0.45201, -0.16445, 1.04],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_lower_11',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, 0.0, -70.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [-0.36842, -0.30914, 1.04],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_lower_12',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, -0.0, -50.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [-0.2405, -0.41652, 1.04],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_lower_13',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, 0.0, -30.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [-0.08346, -0.47372, 1.04],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_lower_14',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, 0.0, -10.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [0.08346, -0.47372, 1.04],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_lower_15',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, -0.0, 10.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [0.2405, -0.41652, 1.04],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_lower_16',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, -0.0, 30.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [0.36842, -0.30914, 1.04],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_lower_17',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, 0.0, 50.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [0.45201, -0.16445, 1.04],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_lower_18',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, -0.0, 70.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [0.47372, 0.08346, 1.82],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_upper_01',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, -0.0, 100.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [0.41652, 0.2405, 1.82],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_upper_02',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, -0.0, 120.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [0.30914, 0.36842, 1.82],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_upper_03',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, 0.0, 140.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [0.16445, 0.45201, 1.82],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_upper_04',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, -0.0, 160.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [0.0, 0.481, 1.82],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_upper_05',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, -0.0, -180.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [-0.16445, 0.45201, 1.82],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_upper_06',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, 0.0, -160.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [-0.30914, 0.36842, 1.82],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_upper_07',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, -0.0, -140.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [-0.41652, 0.2405, 1.82],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_upper_08',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, 0.0, -120.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [-0.47372, 0.08346, 1.82],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_upper_09',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, 0.0, -100.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [-0.47372, -0.08346, 1.82],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_upper_10',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, 0.0, -80.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [-0.41652, -0.2405, 1.82],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_upper_11',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, 0.0, -60.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [-0.30914, -0.36842, 1.82],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_upper_12',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, -0.0, -40.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [-0.16445, -0.45201, 1.82],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_upper_13',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, 0.0, -20.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [-0.0, -0.481, 1.82],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_upper_14',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, 0.0, -0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [0.16445, -0.45201, 1.82],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_upper_15',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, -0.0, 20.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [0.30914, -0.36842, 1.82],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_upper_16',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, 0.0, 40.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [0.41652, -0.2405, 1.82],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_upper_17',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, -0.0, 60.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [83.2, 83.2, 104.0],
  'loc': [0.47372, -0.08346, 1.82],
  'material': 'mat_nozzle',
  'name': 'geo_nozzle_upper_18',
  'parent': 'grp_gas_nozzles',
  'rot': [15.0, -0.0, 80.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [49.4, 49.4, 2470.0],
  'loc': [0.559, 0.0, 1.495],
  'material': 'mat_pilot',
  'name': 'geo_pilot_burner_1',
  'parent': 'none',
  'rot': [0.0, 0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [49.4, 49.4, 2470.0],
  'loc': [-0.2795, 0.4836, 1.495],
  'material': 'mat_pilot',
  'name': 'geo_pilot_burner_2',
  'parent': 'none',
  'rot': [0.0, 0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [49.4, 49.4, 2470.0],
  'loc': [-0.2795, -0.4836, 1.495],
  'material': 'mat_pilot',
  'name': 'geo_pilot_burner_3',
  'parent': 'none',
  'rot': [0.0, 0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [57.2, 57.2, 52.0],
  'loc': [0.559, 0.0, 2.756],
  'material': 'mat_pilot',
  'name': 'geo_pilot_head_1',
  'parent': 'grp_pilot_burners',
  'rot': [8.0, 0.0, -90.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [57.2, 57.2, 52.0],
  'loc': [-0.28002, 0.48373, 2.756],
  'material': 'mat_pilot',
  'name': 'geo_pilot_head_2',
  'parent': 'grp_pilot_burners',
  'rot': [8.0, 0.0, 30.07],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [57.2, 57.2, 52.0],
  'loc': [-0.28002, -0.48373, 2.756],
  'material': 'mat_pilot',
  'name': 'geo_pilot_head_3',
  'parent': 'grp_pilot_burners',
  'rot': [8.0, 0.0, -210.07],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [1170.0, 1170.0, 65.0],
  'loc': [0.0, 0.0, 2.08],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_collector',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 3200},
 {'dims': [83.2, 83.2, 188.5],
  'loc': [-0.65325, 0.20852, 0.13],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_inlet',
  'parent': 'grp_service_pipes',
  'rot': [90.0, -0.0, -107.7],
  'scale': [1.0, 1.0, 1.0],
  'verts': 128},
 {'dims': [13.0, 13.0, 31.2],
  'loc': [-0.77649, 0.18369, 0.13],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_inlet_bolt_01',
  'parent': 'grp_service_pipes',
  'rot': [90.0, 0.0, -107.7],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [13.0, 13.0, 31.2],
  'loc': [-0.77103, 0.20072, 0.17316],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_inlet_bolt_02',
  'parent': 'grp_service_pipes',
  'rot': [90.0, 0.0, -107.7],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [13.0, 13.0, 31.2],
  'loc': [-0.7579, 0.24193, 0.1911],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_inlet_bolt_03',
  'parent': 'grp_service_pipes',
  'rot': [90.0, 0.0, -107.7],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [13.0, 13.0, 31.2],
  'loc': [-0.74477, 0.28301, 0.17316],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_inlet_bolt_04',
  'parent': 'grp_service_pipes',
  'rot': [90.0, 0.0, -107.7],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [13.0, 13.0, 31.2],
  'loc': [-0.73931, 0.30004, 0.13],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_inlet_bolt_05',
  'parent': 'grp_service_pipes',
  'rot': [90.0, 0.0, -107.7],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [13.0, 13.0, 31.2],
  'loc': [-0.74477, 0.28301, 0.08684],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_inlet_bolt_06',
  'parent': 'grp_service_pipes',
  'rot': [90.0, 0.0, -107.7],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [13.0, 13.0, 31.2],
  'loc': [-0.7579, 0.24193, 0.0689],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_inlet_bolt_07',
  'parent': 'grp_service_pipes',
  'rot': [90.0, 0.0, -107.7],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [13.0, 13.0, 31.2],
  'loc': [-0.77103, 0.20072, 0.08684],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_inlet_bolt_08',
  'parent': 'grp_service_pipes',
  'rot': [90.0, 0.0, -107.7],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [156.0, 156.0, 23.4],
  'loc': [-0.74308, 0.23712, 0.13],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_inlet_flange',
  'parent': 'grp_service_pipes',
  'rot': [90.0, 0.0, -107.7],
  'scale': [1.0, 1.0, 1.0],
  'verts': 128},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [0.5525, 0.0, 2.145],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_nozzle_01',
  'parent': 'grp_steam_nozzles',
  'rot': [8.0, 0.0, -90.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [0.51922, 0.18902, 2.145],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_nozzle_02',
  'parent': 'grp_steam_nozzles',
  'rot': [8.0, 0.0, -70.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [0.42328, 0.35516, 2.145],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_nozzle_03',
  'parent': 'grp_steam_nozzles',
  'rot': [8.0, 0.0, -50.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [0.27625, 0.47853, 2.145],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_nozzle_04',
  'parent': 'grp_steam_nozzles',
  'rot': [8.0, 0.0, -30.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [0.09594, 0.54405, 2.145],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_nozzle_05',
  'parent': 'grp_steam_nozzles',
  'rot': [8.0, 0.0, -10.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [-0.09594, 0.54405, 2.145],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_nozzle_06',
  'parent': 'grp_steam_nozzles',
  'rot': [8.0, 0.0, 10.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [-0.27625, 0.47853, 2.145],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_nozzle_07',
  'parent': 'grp_steam_nozzles',
  'rot': [8.0, 0.0, 30.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [-0.42328, 0.35516, 2.145],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_nozzle_08',
  'parent': 'grp_steam_nozzles',
  'rot': [8.0, 0.0, 50.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [-0.51922, 0.18902, 2.145],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_nozzle_09',
  'parent': 'grp_steam_nozzles',
  'rot': [8.0, 0.0, 70.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [-0.5525, 0.0, 2.145],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_nozzle_10',
  'parent': 'grp_steam_nozzles',
  'rot': [8.0, 0.0, 90.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [-0.51922, -0.18902, 2.145],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_nozzle_11',
  'parent': 'grp_steam_nozzles',
  'rot': [8.0, 0.0, -250.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [-0.42328, -0.35516, 2.145],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_nozzle_12',
  'parent': 'grp_steam_nozzles',
  'rot': [8.0, 0.0, -230.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [-0.27625, -0.47853, 2.145],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_nozzle_13',
  'parent': 'grp_steam_nozzles',
  'rot': [8.0, 0.0, -210.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [-0.09594, -0.54405, 2.145],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_nozzle_14',
  'parent': 'grp_steam_nozzles',
  'rot': [8.0, 0.0, -190.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [0.09594, -0.54405, 2.145],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_nozzle_15',
  'parent': 'grp_steam_nozzles',
  'rot': [8.0, 0.0, -170.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [0.27625, -0.47853, 2.145],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_nozzle_16',
  'parent': 'grp_steam_nozzles',
  'rot': [8.0, 0.0, -150.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [0.42328, -0.35516, 2.145],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_nozzle_17',
  'parent': 'grp_steam_nozzles',
  'rot': [8.0, 0.0, -130.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [0.51922, -0.18902, 2.145],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_nozzle_18',
  'parent': 'grp_steam_nozzles',
  'rot': [8.0, 0.0, -110.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 48},
 {'dims': [83.2, 83.2, 2015.0],
  'loc': [-0.56355, 0.17979, 1.1375],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_pipe_main',
  'parent': 'grp_service_pipes',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 256},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [0.5915, 0.0, 0.819],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_riser_nozzle_01',
  'parent': 'grp_steam_nozzles',
  'rot': [8.0, 0.0, -90.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [0.29575, 0.5122, 0.819],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_riser_nozzle_02',
  'parent': 'grp_steam_nozzles',
  'rot': [8.0, 0.0, -30.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [-0.29575, 0.5122, 0.819],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_riser_nozzle_03',
  'parent': 'grp_steam_nozzles',
  'rot': [8.0, -0.0, 30.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [-0.5915, 0.0, 0.819],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_riser_nozzle_04',
  'parent': 'grp_steam_nozzles',
  'rot': [8.0, -0.0, 90.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [-0.29575, -0.5122, 0.819],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_riser_nozzle_05',
  'parent': 'grp_steam_nozzles',
  'rot': [8.0, -0.0, 150.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [39.0, 39.0, 78.0],
  'loc': [0.29575, -0.5122, 0.819],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_riser_nozzle_06',
  'parent': 'grp_steam_nozzles',
  'rot': [8.0, 0.0, -150.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 64},
 {'dims': [1235.0, 1235.0, 52.0],
  'loc': [0.0, 0.0, 0.78],
  'material': 'mat_steam_headers',
  'name': 'geo_steam_riser_ring',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 3200},
 {'dims': [18.2, 18.2, 2080.0],
  'loc': [0.50245, 0.24505, 1.17],
  'material': 'mat_instrument',
  'name': 'geo_tc_cable',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, 0.0, -180.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 32},
 {'dims': [15.6, 15.6, 78.0],
  'loc': [0.5135, 0.0, 0.975],
  'material': 'mat_instrument',
  'name': 'geo_tc_probe_01',
  'parent': 'geo_flare_tip_assembly',
  'rot': [90.0, -0.0, 90.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 32},
 {'dims': [15.6, 15.6, 78.0],
  'loc': [0.42068, 0.29458, 1.365],
  'material': 'mat_instrument',
  'name': 'geo_tc_probe_02',
  'parent': 'geo_flare_tip_assembly',
  'rot': [90.0, 0.0, 125.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 32},
 {'dims': [15.6, 15.6, 78.0],
  'loc': [0.17563, 0.48256, 1.755],
  'material': 'mat_instrument',
  'name': 'geo_tc_probe_03',
  'parent': 'geo_flare_tip_assembly',
  'rot': [90.0, 0.0, 160.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 32},
 {'dims': [15.6, 15.6, 78.0],
  'loc': [-0.17563, 0.48256, 2.21],
  'material': 'mat_instrument',
  'name': 'geo_tc_probe_04',
  'parent': 'geo_flare_tip_assembly',
  'rot': [90.0, -0.0, -160.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 32},
 {'dims': [15.6, 15.6, 78.0],
  'loc': [0.42068, -0.29458, 2.6],
  'material': 'mat_instrument',
  'name': 'geo_tc_probe_05',
  'parent': 'geo_flare_tip_assembly',
  'rot': [90.0, 0.0, 55.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 32},
 {'dims': [852.8, 852.8, 20.54],
  'loc': [0.0, 0.0, 2.795],
  'material': 'mat_vortex_vane',
  'name': 'geo_vortex_ring',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 2592},
 {'dims': [104.0, 156.0, 6.5],
  'loc': [0.416, 0.0, 2.795],
  'material': 'mat_vortex_vane',
  'name': 'geo_vortex_vane_01',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 37.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 8},
 {'dims': [104.0, 156.0, 6.5],
  'loc': [0.33657, 0.24453, 2.795],
  'material': 'mat_vortex_vane',
  'name': 'geo_vortex_vane_02',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 73.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 8},
 {'dims': [104.0, 156.0, 6.5],
  'loc': [0.12857, 0.39559, 2.795],
  'material': 'mat_vortex_vane',
  'name': 'geo_vortex_vane_03',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 109.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 8},
 {'dims': [104.0, 156.0, 6.5],
  'loc': [-0.12857, 0.39559, 2.795],
  'material': 'mat_vortex_vane',
  'name': 'geo_vortex_vane_04',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 145.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 8},
 {'dims': [104.0, 156.0, 6.5],
  'loc': [-0.33657, 0.24453, 2.795],
  'material': 'mat_vortex_vane',
  'name': 'geo_vortex_vane_05',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, 0.0, -179.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 8},
 {'dims': [104.0, 156.0, 6.5],
  'loc': [-0.416, 0.0, 2.795],
  'material': 'mat_vortex_vane',
  'name': 'geo_vortex_vane_06',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, 0.0, -143.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 8},
 {'dims': [104.0, 156.0, 6.5],
  'loc': [-0.33657, -0.24453, 2.795],
  'material': 'mat_vortex_vane',
  'name': 'geo_vortex_vane_07',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, 0.0, -107.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 8},
 {'dims': [104.0, 156.0, 6.5],
  'loc': [-0.12857, -0.39559, 2.795],
  'material': 'mat_vortex_vane',
  'name': 'geo_vortex_vane_08',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, 0.0, -71.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 8},
 {'dims': [104.0, 156.0, 6.5],
  'loc': [0.12857, -0.39559, 2.795],
  'material': 'mat_vortex_vane',
  'name': 'geo_vortex_vane_09',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, 0.0, -35.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 8},
 {'dims': [104.0, 156.0, 6.5],
  'loc': [0.33657, -0.24453, 2.795],
  'material': 'mat_vortex_vane',
  'name': 'geo_vortex_vane_10',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 1.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 8},
 {'dims': [1456.0, 1456.0, 31.2],
  'loc': [0.0, 0.0, 0.78],
  'material': 'mat_windshield_scale',
  'name': 'geo_windshield_ring_bottom',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 3200},
 {'dims': [1456.0, 1456.0, 31.2],
  'loc': [0.0, 0.0, 3.12],
  'material': 'mat_windshield_scale',
  'name': 'geo_windshield_ring_top',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 3200},
 {'dims': [1495.0, 1495.0, 26.0],
  'loc': [0.0, 0.0, 3.159],
  'material': 'mat_windshield_scale',
  'name': 'geo_windshield_ring_top_canted_flange',
  'parent': 'geo_flare_tip_assembly',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 3200},
 {'dims': [1456.0, 1456.0, 2340.0],
  'loc': [0.0, 0.0, 1.95],
  'material': 'mat_windshield_scale',
  'name': 'geo_windshield_sleeve',
  'parent': 'grp_windshield',
  'rot': [0.0, -0.0, 0.0],
  'scale': [1.0, 1.0, 1.0],
  'verts': 512}]

# PBR values from the source scene material definitions. model_state.json stores material names only.
MATERIAL_SPECS = {'mat_beacon': ((1.0, 0.02, 0.0, 1.0), 0.0, 0.16),
 'mat_beacon_bracket': ((0.62, 0.64, 0.61, 1.0), 1.0, 0.38),
 'mat_body': ((0.58, 0.6, 0.57, 1.0), 1.0, 0.36),
 'mat_flange': ((0.47, 0.48, 0.47, 1.0), 1.0, 0.52),
 'mat_gas_seal': ((0.08, 0.08, 0.075, 1.0), 1.0, 0.68),
 'mat_instrument': ((0.42, 0.44, 0.44, 1.0), 0.75, 0.48),
 'mat_nozzle': ((0.2, 0.19, 0.17, 1.0), 1.0, 0.44),
 'mat_pilot': ((0.45, 0.43, 0.39, 1.0), 1.0, 0.42),
 'mat_steam_headers': ((0.56, 0.36, 0.2, 1.0), 1.0, 0.46),
 'mat_vortex_vane': ((0.78, 0.79, 0.76, 1.0), 1.0, 0.18),
 'mat_windshield_scale': ((0.08, 0.08, 0.075, 1.0), 1.0, 0.68)}


def principled_node(material):
    material.use_nodes = True
    node = material.node_tree.nodes.get('Principled BSDF')
    if node is not None:
        return node
    for candidate in material.node_tree.nodes:
        if candidate.type == 'BSDF_PRINCIPLED':
            return candidate
    return material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')


def set_input(node, name, value):
    if name in node.inputs:
        node.inputs[name].default_value = value


def make_materials():
    materials = {}
    for name, (color, metallic, roughness) in MATERIAL_SPECS.items():
        mat = bpy.data.materials.new(name)
        mat.use_fake_user = True
        mat.diffuse_color = color
        bsdf = principled_node(mat)
        set_input(bsdf, 'Base Color', color)
        set_input(bsdf, 'Metallic', metallic)
        set_input(bsdf, 'Roughness', roughness)
        materials[name] = mat
    return materials


def deg_tuple(values):
    return tuple(math.radians(v) for v in values)


def meters(values):
    return tuple(v / 1000.0 for v in values)


def set_exact_transform(obj, rec):
    obj.location = tuple(rec['loc'])
    obj.rotation_euler = deg_tuple(rec['rot'])
    obj.scale = tuple(rec['scale'])


def apply_exact_dimensions_before_rotation(obj, dims_m):
    # Dimensions in JSON are millimetres. Set them before Euler rotation so they describe local model size.
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.dimensions = dims_m
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.select_set(False)


def assign_and_shade(obj, mat, smooth=True):
    if mat is not None:
        obj.data.materials.append(mat)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    if smooth:
        bpy.ops.object.shade_smooth()
    else:
        bpy.ops.object.shade_flat()
    obj.select_set(False)


def create_cube(rec, mat):
    dims = meters(rec['dims'])
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=tuple(rec['loc']))
    obj = bpy.context.object
    obj.name = rec['name']
    obj.data.name = rec['name'] + '_mesh'
    apply_exact_dimensions_before_rotation(obj, dims)
    set_exact_transform(obj, rec)
    assign_and_shade(obj, mat, smooth=False)
    return obj


def create_cylinder(rec, mat, vertices=32, smooth=True):
    dims = meters(rec['dims'])
    radius = max(dims[0], dims[1]) / 2.0
    depth = dims[2]
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=tuple(rec['loc']))
    obj = bpy.context.object
    obj.name = rec['name']
    obj.data.name = rec['name'] + '_mesh'
    apply_exact_dimensions_before_rotation(obj, dims)
    set_exact_transform(obj, rec)
    assign_and_shade(obj, mat, smooth=smooth)
    return obj


def create_torus(rec, mat):
    dims = meters(rec['dims'])
    outer_radius = max(dims[0], dims[1]) / 2.0
    minor_radius = dims[2] / 2.0
    major_radius = outer_radius - minor_radius
    bpy.ops.mesh.primitive_torus_add(major_segments=160, minor_segments=20, major_radius=major_radius, minor_radius=minor_radius, location=tuple(rec['loc']))
    obj = bpy.context.object
    obj.name = rec['name']
    obj.data.name = rec['name'] + '_mesh'
    apply_exact_dimensions_before_rotation(obj, dims)
    set_exact_transform(obj, rec)
    assign_and_shade(obj, mat, smooth=True)
    return obj


def create_hollow_windshield_sleeve(rec, mat):
    dims = meters(rec['dims'])
    outer_r = 0.560
    inner_r = 0.500
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=outer_r, depth=dims[2], location=tuple(rec['loc']))
    outer = bpy.context.object
    outer.name = rec['name']
    outer.data.name = rec['name'] + '_mesh'
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=inner_r, depth=dims[2] + 0.02, location=tuple(rec['loc']))
    inner = bpy.context.object
    inner.name = rec['name'] + '_inner_boolean'
    mod = outer.modifiers.new('hollow_inner_cut', 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = inner
    bpy.context.view_layer.objects.active = outer
    outer.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(inner, do_unlink=True)
    apply_exact_dimensions_before_rotation(outer, dims)
    set_exact_transform(outer, rec)
    assign_and_shade(outer, mat, smooth=True)
    return outer


def create_hollow_body(rec, mat):
    dims = meters(rec['dims'])
    outer_r = max(dims[0], dims[1]) / 2.0
    inner_r = outer_r * 0.82
    vertices = rec.get('verts', 384)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=outer_r, depth=dims[2], location=tuple(rec['loc']))
    outer = bpy.context.object
    outer.name = rec['name']
    outer.data.name = rec['name'] + '_mesh'
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=inner_r, depth=dims[2] + 0.02, location=tuple(rec['loc']))
    inner = bpy.context.object
    inner.name = rec['name'] + '_inner_boolean'
    mod = outer.modifiers.new('hollow_inner_cut', 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = inner
    bpy.context.view_layer.objects.active = outer
    outer.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(inner, do_unlink=True)
    apply_exact_dimensions_before_rotation(outer, dims)
    set_exact_transform(outer, rec)
    assign_and_shade(outer, mat, smooth=True)
    return outer


def is_torus_name(name):
    explicit = ('geo_steam_collector', 'geo_steam_riser_ring', 'geo_fuel_manifold')
    return name in explicit or name in ('geo_vortex_ring', 'geo_windshield_ring_bottom', 'geo_windshield_ring_top', 'geo_windshield_ring_top_canted_flange')


def create_object(rec, materials):
    name = rec['name']
    mat_name = rec['material']
    if mat_name == 'mat_windshield_scale' and mat_name not in materials:
        mat_name = 'mat_gas_seal'
    mat = materials.get(mat_name)

    if name == 'geo_windshield_sleeve':
        return create_hollow_windshield_sleeve(rec, mat)
    if name == 'geo_body':
        return create_hollow_body(rec, mat)
    if is_torus_name(name):
        return create_torus(rec, mat)
    if rec.get('verts') == 8 or 'vane' in name and not ('nozzle' in name):
        return create_cube(rec, mat)
    if 'hex_nut' in name or name.startswith('geo_nut_'):
        return create_cylinder(rec, mat, vertices=6, smooth=False)
    if 'bolt' in name:
        return create_cylinder(rec, mat, vertices=8, smooth=False)
    return create_cylinder(rec, mat, vertices=32, smooth=True)


def make_assembly_empty():
    empty = bpy.data.objects.new('geo_flare_tip_assembly', None)
    empty.empty_display_type = 'PLAIN_AXES'
    empty.empty_display_size = 0.25
    bpy.context.collection.objects.link(empty)
    return empty


def parent_keep_world(obj, parent):
    world = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_world = world


def setup_camera_and_lighting():
    bpy.ops.object.light_add(type='SUN', location=(0.0, 0.0, 5.0), rotation=(math.radians(45.0), 0.0, math.radians(45.0)))
    sun = bpy.context.object
    sun.name = 'key_sun_45deg'
    sun.data.energy = 2.0

    bpy.ops.object.light_add(type='AREA', location=(2.8, -3.5, 4.2))
    area = bpy.context.object
    area.name = 'soft_area_light'
    area.data.energy = 450.0
    area.data.size = 4.0

    bpy.ops.object.camera_add(location=(3.2, -4.2, 2.6), rotation=(math.radians(62.0), 0.0, math.radians(38.0)))
    cam = bpy.context.object
    cam.name = 'Camera'
    cam.data.lens = 45.0
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 4.2
    cam.data.dof.aperture_fstop = 8.0
    bpy.context.scene.camera = cam


# ═══════ INLINE MODULE: separator_new.py ═══════
"""
Detailed horizontal separator (knockout drum) for flare-predictor project.
Blender 4.0.2 compatible, low-poly (~2000-3000 faces).
Coordinate system matches flare_install.py: SX=-7.0, SY=-4.5, SZ=2.8, SL=7.5, SR=1.4.

Function: create_separator(bpy, math, MW, MS, MY, MM, MN, MR)
"""

def create_separator(bpy, math_mod, MW, MS, MY, MM, MN, MR):
    """
    Creates a complete horizontal separator vessel with all fittings.
    
    Parameters:
        bpy: Blender Python API module
        math_mod: Python math module (may be different from built-in in bpy context)
        MW: white/light grey material for body
        MS: steel material for structure
        MY: yellow material for indicators
        MM: dark material for sensors/gauges
        MN: concrete material for bases
        MR: red material for warnings
    """
    # Use the passed math module (or fallback to built-in)
    if math_mod is None:
        math_mod = math
    
    from mathutils import Vector

    # ─── Constants ────────────────────────────────────────────
    SX, SY, SZ, SL, SR = -10.0, -6.0, 2.8, 7.5, 1.4
    GROUND_Z = 0.0

    # ─── Helper functions ─────────────────────────────────────
    def assign_mat(obj, mat):
        obj.data.materials.clear()
        obj.data.materials.append(mat)

    def make_circle_disk(loc, radius, normal_axis='Y', name="Disk",
                         material=MS, segs=48):
        """Create a flat circle mesh facing along the specified axis."""
        # Create in XY plane (normal +Z), then rotate to desired axis
        bpy.ops.mesh.primitive_circle_add(
            vertices=segs, radius=radius, fill_type='NGON',
            location=(0, 0, 0))
        obj = bpy.context.active_object
        obj.name = name
        assign_mat(obj, material)
        bpy.ops.object.shade_flat()
        if normal_axis == 'Y':
            obj.rotation_euler = (math_mod.radians(-90), 0, 0)
        elif normal_axis == 'X':
            obj.rotation_euler = (0, math_mod.radians(90), 0)
        elif normal_axis == 'neg_X':
            obj.rotation_euler = (0, math_mod.radians(-90), 0)
        # else Z: no rotation needed
        obj.location = loc
        return obj

    def make_cylinder(loc, radius, depth, rot=(0, 0, 0), name="Cyl",
                      material=MS, segs=20):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=segs, radius=radius, depth=depth,
            location=loc, rotation=rot)
        obj = bpy.context.active_object
        obj.name = name
        assign_mat(obj, material)
        bpy.ops.object.shade_smooth()
        return obj

    def make_box(loc, scale, name="Box", material=MS):
        bpy.ops.mesh.primitive_cube_add(location=loc)
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = scale
        assign_mat(obj, material)
        bpy.ops.object.shade_smooth()
        return obj

    def make_torus(loc, major_r, minor_r, name="Torus",
                   material=MS, m_segs=20, r_segs=8):
        bpy.ops.mesh.primitive_torus_add(
            major_radius=major_r, minor_radius=minor_r,
            location=loc, major_segments=m_segs, minor_segments=r_segs)
        obj = bpy.context.active_object
        obj.name = name
        assign_mat(obj, material)
        bpy.ops.object.shade_smooth()
        return obj

    def make_uvsphere(loc, radius, name="Sphere", material=MS, segs=16):
        rings = max(8, segs // 2)
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=radius, location=loc,
            segments=segs, ring_count=rings)
        obj = bpy.context.active_object
        obj.name = name
        assign_mat(obj, material)
        bpy.ops.object.shade_smooth()
        return obj

    def make_pipe(p1, p2, radius=0.04, material=MS, segs=8, name="Pipe"):
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        dz = p2[2] - p1[2]
        length = math_mod.sqrt(dx*dx + dy*dy + dz*dz)
        if length < 0.001:
            return None
        mid = ((p1[0] + p2[0]) / 2,
               (p1[1] + p2[1]) / 2,
               (p1[2] + p2[2]) / 2)
        obj = make_cylinder(mid, radius, length, name=name,
                            material=material, segs=segs)
        direction = Vector((dx, dy, dz))
        obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
        return obj

    def make_disc_flange(end_pos, direction_vec, radius, name_prefix,
                         flange_scale=1.5, material=MS):
        """Create a blind flange assembly: bored flange, cap, nuts, studs."""
        flange_disc_radius = radius * 1.75
        flange_body_radius = radius * 1.9
        bore_radius = radius * 1.05
        bolt_circle_radius = flange_disc_radius * 0.82
        bolt_radius = 0.012
        nut_radius = bolt_radius * 1.8
        nut_depth = bolt_radius * 1.5
        stud_radius = bolt_radius * 0.6
        stud_protrusion = bolt_radius * 0.8
        n_bolts = max(8, int(flange_disc_radius / (bolt_radius * 2.5)))
        bottom_flange_thickness = 0.04
        blind_cap_thickness = 0.05
        bore_depth = bottom_flange_thickness
        raised_face_radius = radius * 1.1
        raised_face_thickness = 0.006
        bolt_hole_depth = bottom_flange_thickness + blind_cap_thickness + 0.004

        direction = Vector(direction_vec).normalized()
        rotation = direction.to_track_quat('Z', 'Y').to_euler()

        def point_along(dist, offset=None):
            base = Vector(end_pos) + direction * dist
            if offset is not None:
                base += offset
            return (base.x, base.y, base.z)

        bottom_flange_dist = bottom_flange_thickness / 2
        blind_cap_dist = bottom_flange_thickness + blind_cap_thickness / 2
        cap_top_dist = bottom_flange_thickness + blind_cap_thickness
        bore_dist = bottom_flange_thickness - bore_depth / 2

        # --- Bottom flange disc: flat shading for crisp 90° edges ---
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=48, radius=flange_body_radius,
            depth=bottom_flange_thickness,
            location=point_along(bottom_flange_dist))
        bottom_flange = bpy.context.active_object
        bottom_flange.name = name_prefix + "_BottomFlange"
        bottom_flange.rotation_euler = rotation
        assign_mat(bottom_flange, material)
        # Flat shading = no smooth vertex normals = sharp 90° edges
        bpy.ops.object.shade_flat()

        bore = make_cylinder(
            point_along(bore_dist), bore_radius, bore_depth,
            name=name_prefix + "_BottomFlangeBore", material=MM, segs=24)
        bore.rotation_euler = rotation

        # --- Blind cap disc: flat shading for crisp 90° edges ---
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=48, radius=flange_body_radius,
            depth=blind_cap_thickness,
            location=point_along(blind_cap_dist))
        blind_cap = bpy.context.active_object
        blind_cap.name = name_prefix + "_BlindCap"
        blind_cap.rotation_euler = rotation
        assign_mat(blind_cap, material)
        bpy.ops.object.shade_flat()

        raised_face = make_torus(
            point_along(cap_top_dist + raised_face_thickness / 2),
            raised_face_radius, raised_face_thickness,
            name=name_prefix + "_RaisedFaceRing", material=material,
            m_segs=32, r_segs=8)
        raised_face.rotation_euler = rotation

        reference = Vector((0, 0, 1))
        if abs(direction.dot(reference)) > 0.95:
            reference = Vector((0, 1, 0))
        local_x = direction.cross(reference).normalized()
        local_y = direction.cross(local_x).normalized()

        for i in range(n_bolts):
            angle = i * 2 * math_mod.pi / n_bolts
            offset = (local_x * (math_mod.cos(angle) * bolt_circle_radius) +
                      local_y * (math_mod.sin(angle) * bolt_circle_radius))

            hole = make_cylinder(
                point_along(bolt_hole_depth / 2 - 0.002, offset),
                bolt_radius * 0.9, bolt_hole_depth,
                name=name_prefix + "_BoltHole_" + str(i),
                material=MM, segs=12)
            hole.rotation_euler = rotation

            bpy.ops.mesh.primitive_cylinder_add(
                vertices=6, radius=nut_radius, depth=nut_depth,
                location=point_along(cap_top_dist + nut_depth / 2, offset),
                rotation=rotation)
            nut = bpy.context.active_object
            nut.name = name_prefix + "_FlangeNut_" + str(i)
            assign_mat(nut, material)
            nut.rotation_euler = rotation
            bpy.ops.object.shade_flat()

            stud_dist = cap_top_dist + nut_depth + stud_protrusion / 2
            stud = make_cylinder(
                point_along(stud_dist, offset), stud_radius,
                stud_protrusion,
                name=name_prefix + "_Stud_" + str(i),
                material=material, segs=12)
            stud.rotation_euler = rotation
            make_uvsphere(
                point_along(cap_top_dist + nut_depth + stud_protrusion, offset),
                stud_radius,
                name=name_prefix + "_StudTop_" + str(i),
                material=material, segs=12)

    def make_nozzle(pos, radius, length, direction_vec, name_prefix,
                    flange_scale=1.5, flange_r=0.04, material=MS):
        """Create a nozzle cylinder + flat bolted flange pointing in direction_vec."""
        dz = direction_vec
        end_pos = (pos[0] + dz[0] * length,
                   pos[1] + dz[1] * length,
                   pos[2] + dz[2] * length)
        mid_pos = ((pos[0] + end_pos[0]) / 2,
                   (pos[1] + end_pos[1]) / 2,
                   (pos[2] + end_pos[2]) / 2)
        # Cylinder
        cyl_obj = make_cylinder(mid_pos, radius, length,
                                name=name_prefix + "_Nozzle",
                                material=material, segs=12)
        direction = Vector(dz)
        cyl_obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
        make_disc_flange(end_pos, dz, radius, name_prefix,
                         flange_scale=flange_scale, material=material)
        return cyl_obj

    def make_polyline(points, radius=0.02, material=MS, segs=8,
                      name="Polyline"):
        if len(points) < 2:
            return None
        pipe_objects = []
        for i in range(len(points) - 1):
            p1, p2 = points[i], points[i + 1]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            dz = p2[2] - p1[2]
            length = (dx*dx + dy*dy + dz*dz) ** 0.5
            if length < 0.001:
                continue
            mid = ((p1[0] + p2[0]) / 2,
                   (p1[1] + p2[1]) / 2,
                   (p1[2] + p2[2]) / 2)
            obj = make_cylinder(
                mid, radius, length,
                name=name + "_seg_" + str(i),
                material=material, segs=segs)
            direction = Vector((dx, dy, dz))
            obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
            pipe_objects.append(obj)
        if not pipe_objects:
            return None

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = pipe_objects[0]
        for obj in pipe_objects:
            obj.select_set(True)
        bpy.ops.object.join()
        joined = bpy.context.active_object
        joined.name = name
        joined.data.name = name + "_data"
        # Merge overlapping vertices at segment junctions and recalculate normals
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=0.001)
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.shade_smooth()
        bpy.ops.object.select_all(action='DESELECT')
        return joined

    def make_curve_tube(points, radius=0.02, material=MS,
                        name="CurveTube"):
        if len(points) < 2:
            return None
        curve = bpy.data.curves.new(name + "_data", type='CURVE')
        curve.dimensions = '3D'
        curve.fill_mode = 'FULL'
        curve.bevel_depth = radius
        curve.bevel_resolution = 8
        curve.resolution_u = 64

        spline = curve.splines.new(type='POLY')
        spline.points.add(len(points) - 1)
        for point, coord in zip(spline.points, points):
            point.co = (coord[0], coord[1], coord[2], 1.0)

        obj = bpy.data.objects.new(name, curve)
        bpy.context.collection.objects.link(obj)
        assign_mat(obj, material)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.shade_smooth()
        obj.select_set(False)
        return obj

    # ═══════════════════════════════════════════════════════════
    # 1. MAIN BODY
    # ═══════════════════════════════════════════════════════════
    # Horizontal cylinder (rotated to X-axis)
    body = make_cylinder((SX, SY, SZ), SR, SL,
                         rot=(0, math_mod.radians(90), 0),
                         name="Sep_Body", material=MW, segs=30)

    # Elliptical heads at both ends (elongated UV hemispheres)
    head_scale_x = 0.6  # elliptical head depth ~0.6 * SR
    vessel_parts = [body]
    for side_label, x_offset in [("L", -SL / 2), ("R", SL / 2)]:
        head = make_uvsphere(
            (SX + x_offset, SY, SZ), SR,
            name="Sep_Head_Temp_" + side_label,
            material=MW, segs=20)
        head.scale = (head_scale_x, 1.0, 1.0)

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = head
        head.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        threshold = 0.01 * SR
        for vertex in head.data.vertices:
            if side_label == "L":
                vertex.select = vertex.co.x > threshold
            else:
                vertex.select = vertex.co.x < -threshold

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')
        vessel_parts.append(head)

    bpy.ops.object.select_all(action='DESELECT')
    for part in vessel_parts:
        part.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.join()
    vessel = bpy.context.active_object
    vessel.name = "Sep_Body"
    vessel.data.name = "Sep_Body_Mesh"
    assign_mat(vessel, MW)
    bpy.ops.object.shade_smooth()

    # ═══════════════════════════════════════════════════════════
    # 2. MASSIVE STEEL BEAM SUPPORTS
    # ═══════════════════════════════════════════════════════════
    sx_positions = [SX - SL * 0.3, SX + SL * 0.3]
    support_y_l = SY - SR * 0.65
    support_y_r = SY + SR * 0.65
    support_top_z = SZ - SR - 0.05

    for i, sx in enumerate(sx_positions):
        make_box(
            (sx, support_y_l, SZ / 2),
            (0.15 / 2, 0.15 / 2, SZ / 2),
            name="Sep_Support_Column_L_" + str(i), material=MS)
        make_box(
            (sx, support_y_r, SZ / 2),
            (0.15 / 2, 0.15 / 2, SZ / 2),
            name="Sep_Support_Column_R_" + str(i), material=MS)

        make_pipe(
            (sx, support_y_l, support_top_z),
            (sx, support_y_r, support_top_z),
            radius=0.04, material=MS, segs=8,
            name="Sep_Support_CrossBeam_" + str(i))

        make_pipe(
            (sx, support_y_l, 0.1),
            (sx, support_y_r, SZ - SR - 0.1),
            radius=0.025, material=MS, segs=8,
            name="Sep_Support_Diag_L_" + str(i))
        make_pipe(
            (sx, support_y_r, 0.1),
            (sx, support_y_l, SZ - SR - 0.1),
            radius=0.025, material=MS, segs=8,
            name="Sep_Support_Diag_R_" + str(i))

        make_box(
            (sx, support_y_l, GROUND_Z + 0.04),
            (0.25, 0.25, 0.04),
            name="Sep_Support_Base_L_" + str(i), material=MN)
        make_box(
            (sx, support_y_r, GROUND_Z + 0.04),
            (0.25, 0.25, 0.04),
            name="Sep_Support_Base_R_" + str(i), material=MN)

        cradle = make_cylinder(
            (sx, SY, SZ), SR + 0.03, 0.45,
            rot=(0, math_mod.radians(90), 0),
            name="Sep_Support_Cradle_" + str(i),
            material=MS, segs=24)
        cradle.scale = (1.0, 1.0, 0.85)

        make_pipe(
            (sx, support_y_l, GROUND_Z + 0.08),
            (sx, support_y_r, GROUND_Z + 0.08),
            radius=0.04, material=MS, segs=8,
            name="Sep_Support_BaseBeam_" + str(i))

    make_pipe(
        (sx_positions[0], support_y_l, GROUND_Z + 0.08),
        (sx_positions[1], support_y_l, GROUND_Z + 0.08),
        radius=0.04, material=MS, segs=8,
        name="Sep_Support_LongBeam_L")
    make_pipe(
        (sx_positions[0], support_y_r, GROUND_Z + 0.08),
        (sx_positions[1], support_y_r, GROUND_Z + 0.08),
        radius=0.04, material=MS, segs=8,
        name="Sep_Support_LongBeam_R")

    # ═══════════════════════════════════════════════════════════
    # 3. NOZZLES AND FITTINGS
    # ═══════════════════════════════════════════════════════════

    # ── Inlet nozzle (large, top-left, slightly angled) ──
    inlet_x = SX - SL * 0.25
    inlet_z = SZ + SR
    make_nozzle(
        (inlet_x, SY, inlet_z), 0.18, 0.55, (0, 0, 1),
        "Sep_Inlet", flange_scale=1.6, flange_r=0.045,
        material=MS)

    # ── Vent nozzle (medium, top-right, pointing up) ──
    vent_x = SX + SL * 0.28
    vent_z = SZ + SR
    make_nozzle(
        (vent_x, SY, vent_z), 0.14, 0.50, (0, 0, 1),
        "Sep_Vent", flange_scale=1.5, flange_r=0.04,
        material=MS)

    # ── Drain nozzle (small, bottom-center, pointing down) ──
    drain_x = SX
    drain_z = SZ - SR
    make_nozzle(
        (drain_x, SY, drain_z), 0.10, 0.55, (0, 0, -1),
        "Sep_Drain", flange_scale=1.5, flange_r=0.035,
        material=MS)

    # ── Drain/valve nozzle on left head bottom ──
    # Small nozzle port on the lower portion of the left elliptical head,
    # pointing outward at an angle (left and slightly down)
    head_center_x = SX - SL / 2
    head_a = head_scale_x * SR
    head_b = SR
    head_drain_angle = math_mod.radians(240)
    head_drain_x = head_center_x + head_a * math_mod.cos(head_drain_angle)
    head_drain_z = SZ + head_b * math_mod.sin(head_drain_angle)
    make_nozzle(
        (head_drain_x, SY, head_drain_z), 0.08, 0.35, (-0.5, 0, -0.866),
        "Sep_HeadDrain", flange_scale=1.4, flange_r=0.03,
        material=MS)

    # ── (Manhole removed from left head per reference — no manhole on left end cap) ──

    # ── Pressure gauge assembly: nozzle, valve, detailed dial ──
    pg_x = SX - SL * 0.15
    pg_y = SY + SR * 0.3     # slight Y-offset
    pg_z = SZ + SR + 1.0

    # Flange anchor: all above-flange elements positioned relative to flange_top
    flange_z = pg_z - 0.08
    flange_top = flange_z + 0.10    # flange body 0.04 + cap 0.05 + raised face 0.006 + margin

    # Vertical connecting pipe from separator shell to flange base
    make_pipe(
        (pg_x, pg_y, SZ + SR), (pg_x, pg_y, flange_z),
        radius=0.025, material=MS, segs=8,
        name="Sep_PG_ConnPipe")

    # Flange at junction
    make_disc_flange(
        (pg_x, pg_y, flange_z), (0, 0, 1), 0.045,
        name_prefix="Sep_PG_Base", flange_scale=1.5, material=MS)

    # Riser pipe: visible section from flange top to gauge (same dia as ConnPipe)
    riser_top = flange_top + 0.12
    make_pipe(
        (pg_x, pg_y, flange_top), (pg_x, pg_y, riser_top),
        radius=0.025, material=MS, segs=8,
        name="Sep_PG_RiserPipe")

    # Hex nut connector below pressure gauge dial
    nut = make_cylinder(
        (pg_x, pg_y, riser_top + 0.02), 0.025, 0.035,
        name="Sep_PG_NutConnector", material=MM, segs=6)
    bpy.context.view_layer.objects.active = nut
    nut.select_set(True)
    bpy.ops.object.shade_flat()

    make_pipe(
        (pg_x, pg_y, riser_top), (pg_x, pg_y, riser_top + 0.04),
        radius=0.015, material=MS, segs=8,
        name="Sep_PG_StemPipe")

    # Pressure gauge case, bezel, face, scale, and needle
    dial_z = riser_top + 0.06
    make_cylinder(
        (pg_x, pg_y, dial_z), 0.125, 0.06,
        rot=(0, math_mod.radians(-90), 0),
        name="Sep_PG_DialCase", material=MM, segs=48)
    bezel = make_cylinder(
        (pg_x - 0.032, pg_y, dial_z), 0.128, 0.006,
        rot=(0, math_mod.radians(-90), 0),
        name="Sep_PG_FrontBezel", material=MM, segs=48)
    dial_face = make_circle_disk(
        (pg_x - 0.036, pg_y, dial_z), 0.118,
        normal_axis='neg_X', name="Sep_PG_DialFace", material=MW, segs=48)
    dial_face.data.materials[0].diffuse_color = (1.0, 1.0, 1.0, 1.0)

    dial_cx = pg_x
    dial_cz = dial_z
    tick_x = dial_cx - 0.037
    label_x = dial_cx - 0.038
    needle_x = dial_cx - 0.039
    pivot_x = dial_cx - 0.040
    arc_start = -45
    arc_end = 225

    def dial_rotation(angle):
        return (angle - math_mod.radians(90), 0, 0)

    for i in range(10):
        angle = math_mod.radians(arc_start + i * (arc_end - arc_start) / 9)
        tick_r = 0.10
        ty = pg_y + tick_r * math_mod.cos(angle)
        tz = dial_cz + tick_r * math_mod.sin(angle)
        tick = make_box(
            (tick_x, ty, tz), (0.001, 0.001, 0.015),
            name="Sep_PG_TickM_{}".format(i), material=MM)
        tick.rotation_euler = dial_rotation(angle)

    for i in range(40):
        angle = math_mod.radians(arc_start + i * (arc_end - arc_start) / 39)
        tick_r = 0.105
        ty = pg_y + tick_r * math_mod.cos(angle)
        tz = dial_cz + tick_r * math_mod.sin(angle)
        tick = make_box(
            (tick_x, ty, tz), (0.0005, 0.001, 0.008),
            name="Sep_PG_TickS_{}".format(i), material=MM)
        tick.rotation_euler = dial_rotation(angle)

    text_values = [("0", -45), ("20", 9), ("40", 63), ("60", 117), ("80", 171), ("100", 225)]
    for txt_str, angle_deg in text_values:
        angle = math_mod.radians(angle_deg)
        lr = 0.07
        ly = pg_y + lr * math_mod.cos(angle)
        lz = dial_cz + lr * math_mod.sin(angle)
        bpy.ops.object.text_add(location=(label_x, ly, lz))
        txt_obj = bpy.context.active_object
        txt_obj.name = "Sep_PG_Text_" + txt_str
        txt_obj.data.body = txt_str
        txt_obj.data.size = 0.012
        txt_obj.data.align_x = 'CENTER'
        txt_obj.data.align_y = 'CENTER'
        txt_obj.rotation_euler = (0, math_mod.radians(-90), 0)
        assign_mat(txt_obj, MM)

    needle_angle = math_mod.radians(-45)
    needle = make_box(
        (needle_x, pg_y, dial_cz), (0.003, 0.001, 0.06),
        name="Sep_PG_Needle", material=MM)
    needle.rotation_euler = dial_rotation(needle_angle)
    make_cylinder(
        (pivot_x, pg_y, dial_cz), 0.008, 0.003,
        rot=(0, math_mod.radians(-90), 0),
        name="Sep_PG_PivotDot", material=MM, segs=16)

    # Face elements face -X directly (no rotation needed)

    # ── Pipe stubs connecting to FlareGas route ──
    # Small horizontal pipe from top of separator toward the gas pipe route
    stub_x = SX + SL * 0.3
    stub_z = SZ + SR + 0.35
    make_cylinder(
        (stub_x, SY + 0.3, stub_z), 0.06, 0.6,
        rot=(0, 0, math_mod.radians(90)),  # along Y
        name="Sep_GasStub", material=MY, segs=10)
    # Flange on stub
    make_disc_flange(
        (stub_x, SY + 0.6, stub_z), (0, 1, 0), 0.06,
        name_prefix="Sep_GasStub", flange_scale=1.5, material=MY)

    # ═══════════════════════════════════════════════════════════
    # 4. SERVICE PLATFORM ON TOP
    # ═══════════════════════════════════════════════════════════
    plat_len = SL * 0.65         # ~65% of cylinder length
    plat_w = SR * 2.4            # extends beyond diameter
    plat_z = SZ + SR             # on top of cylinder
    plat_thick = 0.06
    rail_h = 0.90                # railing height

    # Platform boundaries (computed first — ladder position depends on them)
    p_x_min = SX - plat_len / 2
    p_x_max = SX + plat_len / 2
    p_y_min = SY - plat_w / 2
    p_y_max = SY + plat_w / 2

    # Ladder coordinates (aligned with front edge of platform grating)
    lad_x = SX + SL * 0.15              # ladder X center (stringers along X)
    lad_y = p_y_max                     # ladder Y = front edge of platform (was SY + SR + 0.10)
    lad_z_top = plat_z                  # top of ladder = platform level (flush with grating)
    lad_z_bot = GROUND_Z + 0.4          # above ground

    # No hole in the platform — grating is continuous under the ladder.
    # The cage sits above the platform surface and does NOT cut through it.

    bar_r = 0.02      # pipe radius for grating
    bar_spacing = 0.18 # gap between bars

    # ── Longitudinal bars along Y axis (running front-to-back) ──
    # All bars are full-length — no hole around ladder.
    bar_idx = 0
    n_bars_x = int(round((p_x_max - p_x_min) / bar_spacing)) + 1
    for bi in range(n_bars_x):
        bar_x = p_x_min + bi * bar_spacing
        if bar_x > p_x_max + 0.01:
            break
        make_pipe(
            (bar_x, p_y_min + 0.02, plat_z + bar_r),
            (bar_x, p_y_max - 0.02, plat_z + bar_r),
            radius=bar_r, material=MS, segs=6,
            name="Sep_Grat_Y_{}".format(bar_idx))
        bar_idx += 1

    # ── Transverse bars along X axis (running left-to-right) ──
    # All bars are full-length — no hole around ladder.
    n_bars_y = int(round((p_y_max - p_y_min) / bar_spacing)) + 1
    for bi in range(n_bars_y):
        bar_y = p_y_min + bi * bar_spacing
        if bar_y > p_y_max + 0.01:
            break
        make_pipe(
            (p_x_min + 0.02, bar_y, plat_z),
            (p_x_max - 0.02, bar_y, plat_z),
            radius=bar_r, material=MS, segs=6,
            name="Sep_Grat_X_{}".format(bar_idx))
        bar_idx += 1

    # ── Toe plate (thin box around perimeter) ──
    toe_h = 0.08
    toe_t = 0.02
    
    # Front and back edges (along X)
    for y_edge, y_name in [(p_y_max, "Front"), (p_y_min, "Back")]:
        make_box(
            (SX, y_edge, plat_z + toe_h / 2),
            (plat_len / 2, toe_t / 2, toe_h / 2),
            name="Sep_Plat_Toe_{}".format(y_name), material=MS)
    # Left and right edges (along Y)
    for x_edge, x_name in [(p_x_min, "L"), (p_x_max, "R")]:
        make_box(
            (x_edge, SY, plat_z + toe_h / 2),
            (toe_t / 2, plat_w / 2, toe_h / 2),
            name="Sep_Plat_Toe_{}".format(x_name), material=MS)

    # (No hole frame — platform has no cutout, grating is continuous)

    # ── Railing posts (thin cylinders at ~1m intervals) ──
    post_r = 0.025
    n_posts_x = max(2, int(round(plat_len / 0.9)) + 1)
    n_posts_y = max(2, int(round(plat_w / 0.9)) + 1)

    # Access opening on front edge (where ladder meets)
    opening_x = SX + SL * 0.15   # aligned with ladder hole
    opening_half = 0.35

    post_index = 0
    # Posts along X-edges (front and back)
    for y_edge in [p_y_min, p_y_max]:
        for pi in range(n_posts_x):
            px = p_x_min + plat_len * pi / (n_posts_x - 1)
            # Skip posts on front edge in the access opening area
            if y_edge == p_y_max and abs(px - opening_x) < opening_half:
                continue
            make_cylinder(
                (px, y_edge, plat_z + rail_h / 2),
                post_r, rail_h,
                name="Sep_Plat_Post_{}".format(post_index),
                material=MS, segs=6)
            post_index += 1

    # Posts along Y-edges (left and right) - solid, no opening
    for x_edge in [p_x_min, p_x_max]:
        for pi in range(n_posts_y):
            py = p_y_min + plat_w * pi / (n_posts_y - 1)
            # Skip corner posts already created by X-edges
            if pi == 0 or pi == n_posts_y - 1:
                continue
            make_cylinder(
                (x_edge, py, plat_z + rail_h / 2),
                post_r, rail_h,
                name="Sep_Plat_Post_{}".format(post_index),
                material=MS, segs=6)
            post_index += 1

    # ── Cage dimensions (needed early for platform rail clipping) ──
    rail_spacing = 0.35
    cage_r = 0.40            # forward reach of the cage (Y radius)
    cage_rx = rail_spacing / 2          # cage X-radius matches ladder stringers (no side gap)
    cage_ry = cage_r                     # 0.40m  — forward reach
    cage_bar_r = 0.014       # thickness of cage bars
    cage_start_z = lad_z_bot + 0.5   # start ~0.5m above ground
    cage_end_z = plat_z + rail_h         # cage extends to railing top

    # ── Horizontal rails (3 levels: top, middle, bottom) ──
    rail_radius = 0.018
    rail_heights = [0.15, 0.50, 0.85]  # fraction of rail_h from floor
    
    for rh_frac in rail_heights:
        rh = plat_z + rh_frac
        # Front rail — with gap for ladder access opening
        # Rails extend to exact post positions (no 0.05 offset) so they touch corner posts
        rail_tag = int(rh_frac * 100)
        make_pipe(
            (p_x_min, p_y_max, rh),
            (lad_x - cage_rx, p_y_max, rh),
            radius=rail_radius, material=MS, segs=6,
            name="Sep_Plat_Rail_FL_{}".format(rail_tag))
        make_pipe(
            (lad_x + cage_rx, p_y_max, rh),
            (p_x_max, p_y_max, rh),
            radius=rail_radius, material=MS, segs=6,
            name="Sep_Plat_Rail_FR_{}".format(rail_tag))
        # Back rail (solid, no opening)
        make_pipe(
            (p_x_min, p_y_min, rh),
            (p_x_max, p_y_min, rh),
            radius=rail_radius, material=MS, segs=6,
            name="Sep_Plat_Rail_B_{}".format(int(rh_frac * 100)))
        # Left rail (solid, no opening)
        make_pipe(
            (p_x_min, p_y_min, rh),
            (p_x_min, p_y_max, rh),
            radius=rail_radius, material=MS, segs=6,
            name="Sep_Plat_Rail_L_{}".format(int(rh_frac * 100)))
        # Right rail (solid, no opening)
        make_pipe(
            (p_x_max, p_y_min, rh),
            (p_x_max, p_y_max, rh),
            radius=rail_radius, material=MS, segs=6,
            name="Sep_Plat_Rail_R_{}".format(int(rh_frac * 100)))

    # ═══════════════════════════════════════════════════════════
    # 5. LADDER (vertical, right side)
    # ═══════════════════════════════════════════════════════════
    # ── Ladder coordinates already defined above (section 4) ──
    # lad_x, lad_y, lad_z_top, lad_z_bot are set in the platform section

    # Side rails (thin pipes) — rotated 90°: rails along X, rungs along X too
    # rail_spacing already defined above (cage dimensions section)
    rail_r_lad = 0.02
    lad_x_l = lad_x - rail_spacing / 2   # left rail in X
    lad_x_r = lad_x + rail_spacing / 2   # right rail in X

    make_pipe(
        (lad_x_l, lad_y, lad_z_bot), (lad_x_l, lad_y, lad_z_top),
        radius=rail_r_lad, material=MS, segs=6,
        name="Sep_Ladder_Rail_L")
    make_pipe(
        (lad_x_r, lad_y, lad_z_bot), (lad_x_r, lad_y, lad_z_top),
        radius=rail_r_lad, material=MS, segs=6,
        name="Sep_Ladder_Rail_R")

    # Rungs at 0.3m intervals — along X (connecting left and right rails)
    rung_r = 0.015
    n_rungs = int((lad_z_top - lad_z_bot) / 0.30)
    for ri in range(n_rungs):
        rz = lad_z_bot + (ri + 0.5) * (lad_z_top - lad_z_bot) / n_rungs
        make_pipe(
            (lad_x_l, lad_y, rz), (lad_x_r, lad_y, rz),
            radius=rung_r, material=MS, segs=6,
            name="Sep_Ladder_Rung_{}".format(ri))

    # Ladder top remains open inside the safety cage for unobstructed exit.
    
    # ── Ladder safety cage (proper semicircular cage) ──
    # The cage forms a semicircular arch AROUND the front of the ladder,
    # from the left rail to the right rail, curving forward (Y+).
    # cage_rx, cage_ry, cage_bar_r, cage_start_z, cage_end_z already defined above

    if cage_end_z > cage_start_z:
        # ── Vertical cage bars (7 bars forming a semicircular arch) ──
        # Arc from π (left side at lad_x - cage_rx, lad_y) through π/2 (center front)
        # to 0 (right side at lad_x + cage_rx, lad_y), wrapping around the front.
        n_vert = 7
        for vi in range(n_vert):
            frac = vi / (n_vert - 1)  # 0.0 to 1.0
            angle = math_mod.pi * (1.0 - frac)  # π → 0 (left → right through front)
            bar_x = lad_x + math_mod.cos(angle) * cage_rx
            bar_y = lad_y + math_mod.sin(angle) * cage_ry
            make_pipe(
                (bar_x, bar_y, cage_start_z), (bar_x, bar_y, cage_end_z),
                radius=cage_bar_r, material=MS, segs=6,
                name="Sep_Ladder_CageV_{}".format(vi))

        # ── Horizontal semicircular rings at regular intervals (curve tubes) ──
        n_rings = int((cage_end_z - cage_start_z) / 0.40) + 1
        n_arc_pts = 32  # number of arc segments per ring (more = smoother)
        for ri in range(n_rings):
            rz = cage_start_z + ri * 0.40
            if rz > cage_end_z + 0.01:
                break
            ring_pts = []
            for si in range(n_arc_pts + 1):
                t = si / n_arc_pts
                angle = math_mod.pi * (1.0 - t)  # π → 0
                px = lad_x + math_mod.cos(angle) * cage_rx
                py = lad_y + math_mod.sin(angle) * cage_ry
                ring_pts.append((px, py, rz))
            make_curve_tube(
                ring_pts, radius=cage_bar_r, material=MS,
                name="Sep_Ladder_CageR_" + str(ri))

        # Top ring — full semicircular arc, same style as regular rings
        top_ring_pts = []
        for si in range(n_arc_pts + 1):
            t = si / n_arc_pts
            angle = math_mod.pi * (1.0 - t)  # π → 0
            px = lad_x + math_mod.cos(angle) * cage_rx
            py = lad_y + math_mod.sin(angle) * cage_ry
            top_ring_pts.append((px, py, cage_end_z))
        make_curve_tube(
            top_ring_pts, radius=cage_bar_r, material=MS,
            name="Sep_Ladder_CageR_Top")

    # ═══════════════════════════════════════════════════════════
    # 6. SMALL DETAILS
    # ═══════════════════════════════════════════════════════════

    # ── Warning stripes (red bands) on inlet and vent nozzles ──
    for stripe_info in [
        ("Sep_Inlet_Warn", SX - SL * 0.25, SY, SZ + SR + 0.45, 0.20, 0.015),
        ("Sep_Vent_Warn", SX + SL * 0.28, SY, SZ + SR + 0.40, 0.16, 0.015),
    ]:
        s_name, sx_s, sy_s, sz_s, s_r, s_h = stripe_info
        make_cylinder(
            (sx_s, sy_s, sz_s), s_r, s_h,
            name=s_name, material=MR, segs=12)

    # ── Platform support beams and diagonal shell braces ──
    beam_w = 0.15
    beam_h = 0.10
    beam_len = p_x_max - p_x_min
    beam_z = plat_z - beam_h / 2
    beam_y_positions = [SY - SR * 0.30, SY + SR * 0.30]

    for bi, beam_y in enumerate(beam_y_positions):
        make_box(
            (SX, beam_y, beam_z),
            (beam_len / 2, beam_w / 2, beam_h / 2),
            name="Sep_Plat_SupportBeam_{}".format(bi), material=MS)

    def make_square_brace(p1, p2, width, name):
        start = Vector(p1)
        end = Vector(p2)
        span = end - start
        length = span.length
        if length < 0.001:
            return None
        bpy.ops.mesh.primitive_cube_add(location=((p1[0] + p2[0]) / 2,
                                                  (p1[1] + p2[1]) / 2,
                                                  (p1[2] + p2[2]) / 2))
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = (length / 2, width / 2, width / 2)
        obj.rotation_euler = span.to_track_quat('X', 'Z').to_euler()
        assign_mat(obj, MS)
        bpy.ops.object.shade_smooth()
        return obj

    brace_w = 0.05
    brace_x_positions = [SX - plat_len * 0.25, SX + plat_len * 0.25]
    shell_y_offset = SR * 0.72
    shell_z = SZ + math_mod.sqrt(max(0.0, SR * SR - shell_y_offset * shell_y_offset))
    for side_sgn, side_name, y_edge in [(-1, "L", p_y_min), (1, "R", p_y_max)]:
        shell_y = SY + side_sgn * shell_y_offset
        for xi, x_br in enumerate(brace_x_positions):
            make_square_brace(
                (x_br, y_edge, plat_z - plat_thick / 2),
                (x_br, shell_y, shell_z),
                brace_w,
                "Sep_Plat_DiagBrace_{}_{}".format(side_name, xi))

# ═══════ INLINE MODULE: scene_build_clean.py ═══════
"""scene_build_clean.py - Clean rebuild: geometry -> materials -> cameras/lights -> save.
No double execution. Cameras and lights created AFTER geometry+materials.
"""


# Cabinet dimensions are meters: 900 x 500 x 1500 mm.
CABINET_W = 0.90
CABINET_D = 0.50
CABINET_H = 1.50
PANEL_THICKNESS = 0.024
FRONT_Y = -CABINET_D / 2
BACK_Y = CABINET_D / 2
LEFT_X = -CABINET_W / 2
RIGHT_X = CABINET_W / 2
FACE_ROT_Y_AXIS = (math.radians(90), 0.0, 0.0)
CABINET_MOUNT_Z_OFFSET = 0.70


def shifted(loc, x_offset=0.0):
    """Return location shifted along X for a duplicated cabinet."""
    return (loc[0] + x_offset, loc[1], loc[2])


def suffixed(name, suffix=""):
    """Return object name with duplicate suffix when building the second cabinet."""
    return f"{name}{suffix}"


def move_objects_z(objects, z_offset):
    """Lift a completed cabinet assembly without changing its local geometry."""
    for obj in objects:
        obj.location.z += z_offset

# -------------------------------------------------------------------
# GEOMETRY
# -------------------------------------------------------------------

def make_box(name, loc, size, bevel_segments=0, bevel_depth=0):
    """Create a box mesh at location with given dimensions (x, y, z)."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel_segments > 0 and bevel_depth > 0:
        mod = obj.modifiers.new("Bevel", "BEVEL")
        mod.segments = bevel_segments
        mod.width = bevel_depth
        mod.limit_method = "ANGLE"
        mod.angle_limit = math.radians(45)
    return obj


def make_cylinder(name, loc, radius, depth, rot=(0.0, 0.0, 0.0), segments=32):
    """Create a cylinder mesh at location with radius and depth."""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=segments,
        radius=radius,
        depth=depth,
        location=loc,
        rotation=rot,
    )
    obj = bpy.context.active_object
    obj.name = name
    return obj


def shade_flat(obj):
    """Set flat shading on object."""
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_flat()
    obj.select_set(False)


def build_cabinet_body(x_offset=0.0, suffix=""):
    """Hollow painted-steel cabinet shell with visible open front."""
    parts = []
    parts.append(make_box(
        suffixed("geo_cabinet_body_left_side", suffix),
        shifted((LEFT_X + PANEL_THICKNESS / 2, 0.0, CABINET_H / 2), x_offset),
        (PANEL_THICKNESS, CABINET_D, CABINET_H),
        bevel_segments=2,
        bevel_depth=0.008,
    ))
    parts.append(make_box(
        suffixed("geo_cabinet_body_right_side", suffix),
        shifted((RIGHT_X - PANEL_THICKNESS / 2, 0.0, CABINET_H / 2), x_offset),
        (PANEL_THICKNESS, CABINET_D, CABINET_H),
        bevel_segments=2,
        bevel_depth=0.008,
    ))
    parts.append(make_box(
        suffixed("geo_cabinet_body_top", suffix),
        shifted((0.0, 0.0, CABINET_H - PANEL_THICKNESS / 2), x_offset),
        (CABINET_W, CABINET_D, PANEL_THICKNESS),
        bevel_segments=2,
        bevel_depth=0.008,
    ))
    parts.append(make_box(
        suffixed("geo_cabinet_body_bottom", suffix),
        shifted((0.0, 0.0, PANEL_THICKNESS / 2), x_offset),
        (CABINET_W, CABINET_D, PANEL_THICKNESS),
        bevel_segments=2,
        bevel_depth=0.008,
    ))
    parts.append(make_box(
        suffixed("geo_cabinet_body_back", suffix),
        shifted((0.0, BACK_Y - PANEL_THICKNESS / 2, CABINET_H / 2), x_offset),
        (CABINET_W, PANEL_THICKNESS, CABINET_H),
        bevel_segments=2,
        bevel_depth=0.008,
    ))
    return parts


def build_interior_back_wall(x_offset=0.0, suffix=""):
    """Light-gray interior mounting plate on the inside back wall."""
    return make_box(
        suffixed("geo_interior_back_wall", suffix),
        shifted((0.0, 0.236, 0.764), x_offset),
        (0.790, 0.012, 1.350),
        bevel_segments=1,
        bevel_depth=0.004,
    )


def build_cabinet_door(x_offset=0.0, suffix=""):
    """Open left-hinged front door, swung about 100 degrees around left edge."""
    door_w = 0.86
    door_t = 0.006
    door_h = 1.46
    hinge_x = LEFT_X + x_offset
    hinge_y = FRONT_Y - 0.012

    obj = make_box(
        suffixed("geo_cabinet_door", suffix),
        (hinge_x + door_w / 2, hinge_y, door_h / 2 + 0.020),
        (door_w, door_t, door_h),
        bevel_segments=2,
        bevel_depth=0.008,
    )

    # Move origin to the left hinge edge, then rotate the door open.
    bpy.context.scene.cursor.location = (hinge_x, hinge_y, door_h / 2 + 0.020)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")
    obj.rotation_euler[2] = math.radians(-100.0)
    return obj


def hinge_point_for_z(z, x_offset=0.0):
    return (LEFT_X - 0.008 + x_offset, FRONT_Y - 0.012, z)


def build_door_hinges(x_offset=0.0, suffix=""):
    """Three vertical barrel hinges on the cabinet's left front edge."""
    hinges = []
    for hinge_suffix, z in [("bot", 0.230), ("mid", 0.750), ("top", 1.270)]:
        hinge = make_cylinder(
            suffixed(f"geo_door_hinge_{hinge_suffix}", suffix),
            hinge_point_for_z(z, x_offset),
            0.016,
            0.110,
            segments=18,
        )
        hinges.append(hinge)
    return hinges


def open_door_local_to_world(local_x, local_y, local_z, x_offset=0.0):
    """Convert closed-door local coordinates to world after the 100 degree swing."""
    hinge = Vector((LEFT_X + x_offset, FRONT_Y - 0.012, 0.0))
    angle = math.radians(-100.0)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    x = hinge.x + local_x * cos_a - local_y * sin_a
    y = hinge.y + local_x * sin_a + local_y * cos_a
    return (x, y, local_z)


def build_door_locks(x_offset=0.0, suffix=""):
    """Two screw-type locks on the opened door's free edge."""
    locks = []
    for lock_suffix, z in [("bot", 0.330), ("top", 1.200)]:
        loc = open_door_local_to_world(0.790, -0.008, z, x_offset)
        lock = make_cylinder(
            suffixed(f"geo_door_lock_{lock_suffix}", suffix),
            loc,
            0.014,
            0.030,
            rot=FACE_ROT_Y_AXIS,
            segments=16,
        )
        lock.rotation_euler[2] = math.radians(-100.0)
        locks.append(lock)
    return locks


def build_latch_handle(x_offset=0.0, suffix=""):
    """Black latch handle on the opened door."""
    loc = open_door_local_to_world(0.740, -0.012, 1.160, x_offset)
    obj = make_box(suffixed("geo_latch_handle", suffix), loc, (0.052, 0.012, 0.028), bevel_segments=1, bevel_depth=0.004)
    obj.rotation_euler[2] = math.radians(-100.0)
    return obj


def build_panel_controls(side, x_off, panel_y, panel_z, x_offset=0.0, suffix=""):
    """Add screws, indicators and switches to one internal controller face."""
    controls = []
    for index, (sx, sz) in enumerate([(-0.100, 0.060), (-0.100, -0.060), (0.100, 0.060), (0.100, -0.060)]):
        controls.append(make_cylinder(
            suffixed(f"geo_panel_screw_{side}_{index + 1}", suffix),
            shifted((x_off + sx, panel_y - 0.052, panel_z + sz), x_offset),
            0.0044,
            0.008,
            rot=FACE_ROT_Y_AXIS,
            segments=6,
        ))

    indicators = [
        ("flame_1", -0.060, 0.040),
        ("flame_2", -0.020, 0.040),
        ("flame_3", 0.020, 0.040),
        ("flame_4", 0.060, 0.040),
        ("ignition", 0.040, 0.008),
    ]
    for index, (iname, ix, iz) in enumerate(indicators):
        label = "flame" if "flame" in iname else "ignition"
        controls.append(make_cylinder(
            suffixed(f"geo_indicator_{side}_{label}_{index + 1}", suffix),
            shifted((x_off + ix, panel_y - 0.052, panel_z + iz), x_offset),
            0.006,
            0.006,
            rot=FACE_ROT_Y_AXIS,
            segments=16,
        ))

    controls.append(make_cylinder(
        suffixed(f"geo_rotary_switch_{side}", suffix),
        shifted((x_off, panel_y - 0.052, panel_z - 0.040), x_offset),
        0.024,
        0.020,
        rot=FACE_ROT_Y_AXIS,
        segments=24,
    ))
    controls.append(make_box(
        suffixed(f"geo_switch_pointer_{side}", suffix),
        shifted((x_off, panel_y - 0.052, panel_z - 0.052), x_offset),
        (0.008, 0.006, 0.040),
    ))
    controls.append(make_box(
        suffixed(f"geo_toggle_switch_{side}", suffix),
        shifted((x_off - 0.070, panel_y - 0.052, panel_z - 0.090), x_offset),
        (0.016, 0.014, 0.024),
        bevel_segments=1,
        bevel_depth=0.002,
    ))
    return controls


def build_control_panels(x_offset=0.0, suffix=""):
    """Two identical controller blocks inside the cabinet on the upper DIN rail."""
    panels = []
    panel_y = 0.190
    panel_z = 1.120
    for side, x_off in [("L", -0.140), ("R", 0.140)]:
        frame = make_box(
            suffixed(f"geo_panel_frame_{side}", suffix),
            shifted((x_off, panel_y, panel_z), x_offset),
            (0.250, 0.100, 0.170),
            bevel_segments=1,
            bevel_depth=0.006,
        )
        face = make_box(
            suffixed(f"geo_control_panel_{side}", suffix),
            shifted((x_off, panel_y - 0.050, panel_z), x_offset),
            (0.230, 0.008, 0.150),
            bevel_segments=1,
            bevel_depth=0.004,
        )
        panels.extend([frame, face])
        panels.extend(build_panel_controls(side, x_off, panel_y, panel_z, x_offset, suffix))
    return panels


def build_upper_din_rail(x_offset=0.0, suffix=""):
    """DIN rail supporting the two controller blocks."""
    rail = make_box(suffixed("geo_din_rail_upper", suffix), shifted((0.0, 0.216, 1.120), x_offset), (0.660, 0.020, 0.070))
    shade_flat(rail)
    return rail


def build_din_rail(x_offset=0.0, suffix=""):
    """Scaled Omega-profile DIN rail in the middle zone."""
    rail = make_box(suffixed("geo_din_rail", suffix), shifted((0.0, 0.208, 0.840), x_offset), (0.700, 0.020, 0.070))
    shade_flat(rail)
    return rail


def build_terminal_blocks(x_offset=0.0, suffix=""):
    """Twelve WAGO-style terminal blocks on the middle DIN rail."""
    blocks = []
    for i in range(12):
        x = -0.330 + i * 0.060
        block = make_box(
            suffixed(f"geo_terminal_block_{i + 1:02d}", suffix),
            shifted((x, 0.174, 0.840), x_offset),
            (0.048, 0.060, 0.080),
            bevel_segments=1,
            bevel_depth=0.004,
        )
        blocks.append(block)
    return blocks


def make_tube(name, points, radius=0.0030, bevel_resolution=4):
    """Create a tube (bevelled curve) from a list of (x,y,z) points.
       Uses Bezier curves with automatic handles for smooth bends."""
    curve_data = bpy.data.curves.new(name, type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = radius
    curve_data.bevel_resolution = bevel_resolution
    curve_data.use_fill_caps = True

    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    for i, (px, py, pz) in enumerate(points):
        pt = spline.bezier_points[i]
        pt.co = (px, py, pz)
        pt.handle_left_type = 'AUTO'
        pt.handle_right_type = 'AUTO'

    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)
    return obj


def build_panel_wires(x_offset=0.0, suffix=""):
    """Wiring: each relay has 2 colored wires coming DOWN from the panel,
       which SMOOTHLY MERGE into a single black trunk over a length (not a sharp Y).
       The colored wires start offset, gradually converge inward over ~60mm,
       then run alongside the trunk for another ~20mm before disappearing into it.
       Plus a main bundle from cable gland rising up the left wall."""

    left_x = -0.450  # cabinet left wall
    panel_y = 0.190  # panel center depth
    panel_bottom_z = 1.036  # bottom edge of panel frames (relay output)
    trunk_start_z = 0.970  # where the trunk begins (higher, closer to panel)
    trunk_end_z = 0.680  # shared merge point for the two black trunks
    merge_complete_z = 0.940  # where colored wires fully converge to trunk center

    # === Main wire bundle: cable exit → up left wall → connect to trunk merge point ===
    bundle_pts = [
        shifted((left_x + 0.040, 0.190, 0.200), x_offset),  # cable exit on left wall
        shifted((left_x + 0.040, 0.190, 0.400), x_offset),  # running up left wall
        shifted((left_x + 0.040, 0.190, 0.560), x_offset),  # still on left wall
        shifted((-0.200, 0.190, 0.620), x_offset),          # curving inward and upward
        shifted((0.0, 0.190, trunk_end_z), x_offset),       # connects directly to trunk merge point
    ]
    make_tube(suffixed("geo_wire_bundle", suffix), bundle_pts, radius=0.014, bevel_resolution=6)

    # === Two colored wires per relay → smooth merge into black trunk ===
    # Each colored wire:
    #   1. Starts offset from panel center (±24mm)
    #   2. Gradually curves inward over ~60mm height
    #   3. Runs alongside the trunk for ~20mm (nearly touching)
    #   4. Disappears into the trunk at merge_complete_z
    #
    # The trunk starts higher and the colored wires merge into it smoothly.

    panel_specs = [
        # (panel_x, trunk_name, w1_name, w1_mat, w1_dx, w2_name, w2_mat, w2_dx)
        (-0.140, "geo_wire_trunk_L", "geo_wire_L1", "mat_wire_red", -0.024, "geo_wire_L2", "mat_wire_blue", 0.024),
        ( 0.140, "geo_wire_trunk_R", "geo_wire_R1", "mat_wire_green", -0.024, "geo_wire_R2", "mat_wire_yellow", 0.024),
    ]

    for panel_x, trunk_name, w1_name, w1_mat, w1_dx, w2_name, w2_mat, w2_dx in panel_specs:
        # Wire 1 (colored): starts offset, gradually curves inward, then merges
        w1_pts = [
            shifted((panel_x + w1_dx, panel_y, panel_bottom_z), x_offset),  # start offset on panel
            shifted((panel_x + w1_dx * 0.65, panel_y, panel_bottom_z - 0.024), x_offset),  # curving inward
            shifted((panel_x + w1_dx * 0.25, panel_y, merge_complete_z + 0.016), x_offset),  # almost at center
            shifted((panel_x, panel_y, merge_complete_z), x_offset),  # merged into trunk
        ]
        make_tube(suffixed(w1_name, suffix), w1_pts, radius=0.0030)

        # Wire 2 (colored): same path on the other side
        w2_pts = [
            shifted((panel_x + w2_dx, panel_y, panel_bottom_z), x_offset),  # start offset on panel
            shifted((panel_x + w2_dx * 0.65, panel_y, panel_bottom_z - 0.024), x_offset),  # curving inward
            shifted((panel_x + w2_dx * 0.25, panel_y, merge_complete_z + 0.016), x_offset),  # almost at center
            shifted((panel_x, panel_y, merge_complete_z), x_offset),  # merged into trunk
        ]
        make_tube(suffixed(w2_name, suffix), w2_pts, radius=0.0030)

        # Trunk (black): starts higher, colored wires merge into it along the way
        trunk_pts = [
            shifted((panel_x, panel_y, trunk_start_z), x_offset),  # top of trunk (near panel bottom)
            shifted((panel_x, panel_y, 0.840), x_offset),          # starts as a relay-specific trunk
            shifted((panel_x * 0.45, panel_y, 0.730), x_offset),   # curves inward toward common merge
            shifted((0.0, panel_y, trunk_end_z), x_offset),        # merged into common trunk
        ]
        make_tube(suffixed(trunk_name, suffix), trunk_pts, radius=0.006)


def build_cable(x_offset=0.0, suffix=""):
    """Black rubber cable exits left wall lower third and descends to pedestal."""
    exit_obj = make_cylinder(
        suffixed("geo_cable_exit", suffix),
        shifted((LEFT_X - 0.008, 0.200, 0.200), x_offset),
        0.018,
        0.036,
        rot=(0.0, math.radians(90), 0.0),
        segments=18,
    )
    hose = make_cylinder(
        suffixed("geo_cable_hose", suffix),
        shifted((LEFT_X - 0.036, 0.200, 0.060), x_offset),
        0.016,
        0.280,
        segments=18,
    )
    rings = []
    for i in range(8):
        z = -0.064 + i * 0.036
        ring = make_cylinder(
            suffixed(f"geo_cable_hose_corrugation_{i + 1:02d}", suffix),
            shifted((LEFT_X - 0.036, 0.200, z), x_offset),
            0.0190,
            0.008,
            segments=18,
        )
        rings.append(ring)
    return [exit_obj, hose] + rings


def build_cabinet(x_offset=0.0, suffix=""):
    """Build one complete cabinet at the requested X offset."""
    existing = set(bpy.data.objects)
    build_cabinet_body(x_offset, suffix)
    build_interior_back_wall(x_offset, suffix)
    build_cabinet_door(x_offset, suffix)
    build_door_hinges(x_offset, suffix)
    build_door_locks(x_offset, suffix)
    build_latch_handle(x_offset, suffix)
    build_upper_din_rail(x_offset, suffix)
    build_control_panels(x_offset, suffix)
    build_din_rail(x_offset, suffix)
    build_terminal_blocks(x_offset, suffix)
    build_panel_wires(x_offset, suffix)
    build_cable(x_offset, suffix)
    move_objects_z([obj for obj in bpy.data.objects if obj not in existing], CABINET_MOUNT_Z_OFFSET)


def duplicate_cabinet(offset_x):
    """Duplicate the cabinet by rebuilding every part with a suffix and X offset."""
    build_cabinet(offset_x, "_2")


def build_support_structure():
    """Outdoor support posts, crossbars, foundations, and ground plane."""
    foundation_size = (0.40, 0.30, 0.30)
    foundation_z = foundation_size[2] / 2
    post_width = 0.10
    post_height = 1.80
    post_z = foundation_size[2] + post_height / 2
    left_post_x = LEFT_X
    right_post_x = RIGHT_X + 1.00
    support_y = 0.30
    crossbar_size = 0.12
    crossbar_x = (left_post_x + right_post_x) / 2
    crossbar_length = right_post_x - left_post_x

    make_box("geo_ground", (0.0, 0.0, -0.010), (4.0, 4.0, 0.02))
    for name, x in [("left", left_post_x), ("right", right_post_x)]:
        make_box(
            f"geo_concrete_foundation_{name}",
            (x, support_y, foundation_z),
            foundation_size,
            bevel_segments=1,
            bevel_depth=0.008,
        )
        make_box(
            f"geo_support_post_{name}",
            (x, support_y, post_z),
            (post_width, post_width, post_height),
            bevel_segments=1,
            bevel_depth=0.006,
        )
    make_box(
        "geo_crossbar_upper",
        (crossbar_x, support_y, 1.60),
        (crossbar_length, crossbar_size, crossbar_size),
        bevel_segments=1,
        bevel_depth=0.006,
    )
    make_box(
        "geo_crossbar_lower",
        (crossbar_x, support_y, 0.80),
        (crossbar_length, crossbar_size, crossbar_size),
        bevel_segments=1,
        bevel_depth=0.006,
    )


def build_geometry():
    """Build all geometry objects."""
    build_support_structure()
    build_cabinet()
    duplicate_cabinet(1.00)
    print(f"GEOMETRY_DONE: {len([o for o in bpy.data.objects if o.type in ('MESH', 'CURVE')])} meshes+curves created")


# -------------------------------------------------------------------
# MATERIALS
# -------------------------------------------------------------------

def create_principled(name, color_hex, roughness=0.45, metallic=0.0):
    """Create a Principled BSDF material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    r = int(color_hex[1:3], 16) / 255.0
    g = int(color_hex[3:5], 16) / 255.0
    b = int(color_hex[5:7], 16) / 255.0
    bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def create_bump_material(name, color_hex, roughness=0.45, metallic=0.0, bump_strength=0.035):
    """Create a material with noise bump for painted steel."""
    mat = create_principled(name, color_hex, roughness, metallic)
    if bump_strength > 0:
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bump = mat.node_tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = bump_strength
        noise = mat.node_tree.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 50.0
        noise.inputs["Detail"].default_value = 4.0
        mat.node_tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        mat.node_tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def make_all_materials():
    """Create all PBR materials for the cabinet."""
    materials = {}
    materials["mat_painted_steel"] = create_bump_material(
        "mat_painted_steel", "#D4E4F0", roughness=0.45, metallic=0.3, bump_strength=0.035)
    materials["mat_painted_steel_door"] = create_principled(
        "mat_painted_steel_door", "#D6DBE0", roughness=0.45, metallic=0.3)
    materials["mat_interior_back_wall"] = create_principled(
        "mat_interior_back_wall", "#ECEFF1", roughness=0.42, metallic=0.15)
    materials["mat_galvanized_hinge"] = create_principled(
        "mat_galvanized_hinge", "#888888", roughness=0.3, metallic=0.8)
    materials["mat_black_latch"] = create_principled(
        "mat_black_latch", "#1A1A1A", roughness=0.4, metallic=0.5)
    materials["mat_blue_abs"] = create_principled(
        "mat_blue_abs", "#0033A0", roughness=0.3, metallic=0.1)
    materials["mat_white_faceplate"] = create_principled(
        "mat_white_faceplate", "#F0F0F0", roughness=0.4, metallic=0.0)
    materials["mat_silver_screw"] = create_principled(
        "mat_silver_screw", "#C0C0C0", roughness=0.25, metallic=0.9)
    materials["mat_black_lens"] = create_principled(
        "mat_black_lens", "#1A1A1A", roughness=0.5, metallic=0.0)
    materials["mat_black_knob"] = create_principled(
        "mat_black_knob", "#222222", roughness=0.4, metallic=0.0)
    materials["mat_red_pointer"] = create_principled(
        "mat_red_pointer", "#CC0000", roughness=0.3, metallic=0.1)
    materials["mat_galvanized_rail"] = create_principled(
        "mat_galvanized_rail", "#A8A8A0", roughness=0.35, metallic=0.85)
    materials["mat_terminal_wago"] = create_principled(
        "mat_terminal_wago", "#E0E0DC", roughness=0.5, metallic=0.0)
    materials["mat_black_rubber"] = create_principled(
        "mat_black_rubber", "#1A1A1A", roughness=0.8, metallic=0.0)
    materials["mat_corrugated"] = create_principled(
        "mat_corrugated", "#2A2A2A", roughness=0.7, metallic=0.1)
    materials["mat_black_steel"] = create_principled(
        "mat_black_steel", "#222222", roughness=0.4, metallic=0.3)
    materials["mat_concrete"] = create_principled(
        "mat_concrete", "#808080", roughness=0.95, metallic=0.0)
    materials["mat_ground"] = create_principled(
        "mat_ground", "#4A4A4A", roughness=0.95, metallic=0.0)
    materials["mat_wire_red"] = create_principled(
        "mat_wire_red", "#CC0000", roughness=0.6, metallic=0.0)
    materials["mat_wire_blue"] = create_principled(
        "mat_wire_blue", "#0044AA", roughness=0.6, metallic=0.0)
    materials["mat_wire_green"] = create_principled(
        "mat_wire_green", "#00AA44", roughness=0.6, metallic=0.0)
    materials["mat_wire_yellow"] = create_principled(
        "mat_wire_yellow", "#DDAA00", roughness=0.6, metallic=0.0)
    return materials


def assign_materials(materials):
    """Assign materials to geometry objects by naming convention."""
    mapping = {
        "geo_cabinet_body": "mat_painted_steel",
        "geo_cabinet_door": "mat_painted_steel_door",
        "geo_interior_back_wall": "mat_interior_back_wall",
        "geo_door_hinge": "mat_galvanized_hinge",
        "geo_door_lock": "mat_black_latch",
        "geo_latch_handle": "mat_black_latch",
        "geo_panel_frame": "mat_blue_abs",
        "geo_control_panel": "mat_white_faceplate",
        "geo_panel_screw": "mat_silver_screw",
        "geo_indicator": "mat_black_lens",
        "geo_rotary_switch": "mat_black_knob",
        "geo_switch_pointer": "mat_red_pointer",
        "geo_toggle_switch": "mat_black_knob",
        "geo_din_rail": "mat_galvanized_rail",
        "geo_terminal_block": "mat_terminal_wago",
        "geo_wire_trunk_L": "mat_black_rubber",
        "geo_wire_trunk_R": "mat_black_rubber",
        "geo_wire_L1": "mat_wire_red",
        "geo_wire_L2": "mat_wire_blue",
        "geo_wire_R1": "mat_wire_green",
        "geo_wire_R2": "mat_wire_yellow",
        "geo_wire_bundle": "mat_black_rubber",
        "geo_cable_exit": "mat_black_rubber",
        "geo_cable_hose": "mat_corrugated",
        "geo_support_post": "mat_black_steel",
        "geo_crossbar": "mat_black_steel",
        "geo_concrete_foundation": "mat_concrete",
        "geo_ground": "mat_ground",
    }

    assigned = 0
    for obj in bpy.data.objects:
        if obj.type not in ("MESH", "CURVE"):
            continue
        mat_name = None
        for prefix, candidate in mapping.items():
            if obj.name.startswith(prefix):
                mat_name = candidate
                break
        if mat_name and mat_name in materials:
            obj.data.materials.clear()
            obj.data.materials.append(materials[mat_name])
            assigned += 1
            if obj.name.startswith("geo_din_rail"):
                shade_flat(obj)

    print(f"MATERIALS_ASSIGNED: {assigned}")
    return assigned


# -------------------------------------------------------------------
# CAMERAS & LIGHTS
# -------------------------------------------------------------------

FOCUS_POINT = Vector((0.25, 0.0, 0.55))
CAMERA_FOCAL_LENGTH = 50.0


def create_camera(name, location, target=None):
    """Create a camera with TRACK_TO constraint pointing at target."""
    if target is None:
        target = bpy.data.objects.get("camera_focus_target")

    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = CAMERA_FOCAL_LENGTH
    cam = bpy.data.objects.new(name, cam_data)
    cam.location = location
    bpy.context.collection.objects.link(cam)

    if target:
        constraint = cam.constraints.new(type="TRACK_TO")
        constraint.target = target
        constraint.track_axis = "TRACK_NEGATIVE_Z"
        constraint.up_axis = "UP_Y"

    return cam


def create_lights():
    """Sun + fill light."""
    sun_data = bpy.data.lights.new("light_sun", type="SUN")
    sun_data.energy = 3.0
    sun = bpy.data.objects.new("light_sun", sun_data)
    sun.location = (3.0, -2.0, 5.0)
    sun.rotation_euler = (0.785, 0.0, 0.785)
    bpy.context.collection.objects.link(sun)

    fill_data = bpy.data.lights.new("light_fill", type="POINT")
    fill_data.energy = 1.5
    fill = bpy.data.objects.new("light_fill", fill_data)
    fill.location = (-2.0, 3.0, 4.0)
    bpy.context.collection.objects.link(fill)


def setup_world():
    """Set world background color."""
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.color = (0.15, 0.15, 0.15)


def build_cameras_and_lights():
    """Create scene cameras and lights."""
    target = bpy.data.objects.new("camera_focus_target", None)
    target.empty_display_type = "PLAIN_AXES"
    target.empty_display_size = 0.1
    target.location = FOCUS_POINT
    bpy.context.collection.objects.link(target)

    create_camera("cam_front", (0.25, -2.5, 0.38), target)
    create_camera("cam_fr45", (1.8, -2.0, 0.42), target)
    create_camera("cam_side", (2.5, 0.025, 0.38), target)
    create_camera("cam_top", (0.25, 0.025, 2.8), target)
    create_camera("cam_persp", (1.3, -2.0, 1.1), target)

    bpy.context.scene.camera = bpy.data.objects["cam_persp"]
    create_lights()
    setup_world()
    print("SCENE_DONE")



bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

# ═══════ МАТЕРИАЛЫ ═══════
def mat(name, rgb, rough=0.45, metal=0.25):
    m = bpy.data.materials.new(name=name)
    m.diffuse_color = (*rgb, 1.0)
    m.roughness = rough
    m.metallic = metal
    return m

MR = mat(name="Red",       rgb=(0.82, 0.15, 0.10), metal=0.30)
MW = mat(name="White",     rgb=(0.92, 0.91, 0.87))
MS = mat(name="Steel",     rgb=(0.55, 0.58, 0.62), metal=0.80, rough=0.30)
MY = mat(name="Yellow",    rgb=(0.95, 0.82, 0.05))
MB = mat(name="Burner",    rgb=(0.28, 0.30, 0.35), metal=0.90, rough=0.20)
MF = mat(name="Flame",     rgb=(1.00, 0.55, 0.05))
MC = mat(name="Cable",     rgb=(0.06, 0.08, 0.12), metal=0.65, rough=0.35)  # почти чёрный трос
MN = mat(name="Concrete",  rgb=(0.72, 0.68, 0.63), rough=0.88)  # светлый бетон анкеров
MG = mat(name="Ground",    rgb=(0.30, 0.45, 0.18), rough=0.95)  # зелёная земля
MM = mat(name="Sensor",    rgb=(0.06, 0.08, 0.16), metal=0.70, rough=0.30)

def sm(obj, m):
    obj.data.materials.clear()
    obj.data.materials.append(m)

# ═══════ ПРИМИТИВЫ ═══════
def cyl(loc, r, d, rot=(0,0,0), name="C", m=MS, seg=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=seg, radius=r, depth=d, location=loc, rotation=rot)
    o = bpy.context.active_object; o.name = name; sm(obj=o, m=m)
    bpy.ops.object.shade_smooth()
    return o

def cube(loc, scale, name="Q", m=MS):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.active_object; o.name = name; o.scale = scale; sm(obj=o, m=m)
    bpy.ops.object.shade_smooth()
    return o

def torus(loc, R, r, name="T", m=MS, seg=20, rseg=8):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc,
                                      major_segments=seg, minor_segments=rseg)
    o = bpy.context.active_object; o.name = name; sm(obj=o, m=m)
    bpy.ops.object.shade_smooth()
    return o

def pipe(p1, p2, r=0.04, m=MS, seg=12, name="P"):
    dx = p2[0] - p1[0]; dy = p2[1] - p1[1]; dz = p2[2] - p1[2]
    L = math.sqrt(dx*dx + dy*dy + dz*dz)
    if L < 0.001: return None
    mid = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2)
    c = cyl(mid, r, L, rot=(0,0,0), name=name, m=m, seg=seg)
    direction = Vector((dx, dy, dz))
    c.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    return c

def joint(loc, pipe_r, v_in, v_out, name="J", m=MS):
    """DEBUG: два цилиндра-порта в позициях стыков. Потом заменим на elbow."""
    R = pipe_r * 1.5
    # Входной порт: loc - R·v_in, смотрит по v_in
    c_in = loc - R * v_in
    p_in = cyl(c_in, pipe_r, 0.06, name=name + "_IN", m=m, seg=16)
    p_in.rotation_euler = v_in.to_track_quat('Z', 'Y').to_euler()
    # Выходной порт: loc + R·v_out, смотрит по v_out
    c_out = loc + R * v_out
    p_out = cyl(c_out, pipe_r, 0.06, name=name + "_OUT", m=m, seg=16)
    p_out.rotation_euler = v_out.to_track_quat('Z', 'Y').to_euler()
    return p_in

def elbow(loc, v_in, v_out, pipe_r, name="Elbow", m=MS, seg=24):
    """Четверть тора (90° изгиб). Вход по v_in, выход по v_out."""
    import bmesh
    loc_v = Vector(loc)
    v_in = Vector(v_in).normalized()
    v_out = Vector(v_out).normalized()

    Re = pipe_r * 1.5      # радиус изгиба по центральной линии
    rt = pipe_r             # радиус трубы

    # --- локальная геометрия четверти тора ---
    # Дуга: старт (0,0,-Re) касат. +Z → конец (Re,0,0) касат. +X
    # Параметризация: x=Re*(1-cos u), z=Re*sin u - Re, u∈[0,π/2]
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    rings = []
    for i in range(seg + 1):
        u = (i / seg) * math.pi / 2
        cx = Re * (1 - math.cos(u))
        cz = Re * math.sin(u) - Re
        tx = math.sin(u)
        tz = math.cos(u)
        ring = []
        for j in range(seg):
            v = (j / seg) * 2 * math.pi
            x = cx + rt * math.cos(v) * tz
            y = rt * math.sin(v)
            z = cz - rt * math.cos(v) * tx
            ring.append(bm.verts.new((x, y, z)))
        rings.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(seg):
        for j in range(seg):
            jn = (j + 1) % seg
            bm.faces.new((rings[i][j], rings[i][jn], rings[i+1][jn], rings[i+1][j]))
    bm.to_mesh(mesh)
    bm.free()
    # Сглаживание: выставляем use_smooth на всех гранях напрямую
    for p in mesh.polygons:
        p.use_smooth = True

    # --- матрица: локальная +Z→v_in, локальная +X→v_out ---
    mz = v_in
    mx = v_out
    my = mz.cross(mx)
    if my.length < 1e-6:
        my = Vector((0, 1, 0))
    my.normalize()
    mz = mx.cross(my)
    mz.normalize()
    M = Matrix((mx, my, mz)).to_4x4()
    obj.matrix_world = Matrix.Translation(loc_v) @ M

    # --- порты в мировых координатах ---
    port_in  = loc_v + M @ Vector((0, 0, -Re))
    port_out = loc_v + M @ Vector((Re, 0, 0))

    sm(obj=obj, m=m)

    return obj, tuple(port_in), tuple(port_out)

def route(points, r, m=MS, seg=12, name="R", joint_m=None):
    """Прокладывает трубу по ломаной с elbow-коленами в вершинах поворота."""
    if joint_m is None:
        joint_m = m
    n = len(points)
    if n < 2:
        return
    current_start = Vector(points[0])
    seg_idx = 0
    for pivot_idx in range(1, n - 1):
        p_prev  = Vector(points[pivot_idx - 1])
        p_pivot = Vector(points[pivot_idx])
        p_next  = Vector(points[pivot_idx + 1])
        v_in  = (p_pivot - p_prev).normalized()
        v_out = (p_next - p_pivot).normalized()
        if abs(v_in.dot(v_out)) > 0.999:
            continue  # прямой участок — без колена
        # колено в точке поворота
        _, port_in, port_out = elbow(
            p_pivot, v_in, v_out, r, seg=24,
            name="{}_E{}".format(name, pivot_idx), m=joint_m)
        # труба от предыдущего старта до входного порта колена
        if (current_start - Vector(port_in)).length > 0.001:
            pipe(tuple(current_start), port_in, r=r, m=m, seg=seg,
                 name="{}_{}".format(name, seg_idx))
            seg_idx += 1
        current_start = Vector(port_out)
    # последний прямой сегмент
    if (current_start - Vector(points[-1])).length > 0.001:
        pipe(tuple(current_start), points[-1], r=r, m=m, seg=seg,
             name="{}_{}".format(name, seg_idx))

# ═══════ ЗЕМЛЯ + ПЛОЩАДКА ═══════
# Земля ниже, площадка толще и выше — чтобы не было наложения
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, -2, -0.03))
sm(obj=bpy.context.active_object, m=MG)
bpy.context.active_object.name = "Ground"
cube((0, -2, 0.06), (24, 18, 0.06), name="Pad", m=MN)

# ═══════ 1. СТВОЛ ═══════
H, R, FX, FY = 38.0, 0.65, 0.0, -1.0
cyl((FX, FY, 6.1),  R, 12.0, name="Stack_L", m=MR, seg=30)
cyl((FX, FY, 20.1), R, 16.0, name="Stack_M", m=MW, seg=30)
cyl((FX, FY, 33.1), R, 10.0, name="Stack_U", m=MR, seg=30)
cyl((FX, FY, 0.25), 1.35, 0.5, name="Stack_Base", m=MS, seg=30)

# ═══════ 2. ПЛАТФОРМЫ — только на стыках секций + верхняя ═══════
PR, RH, POST_R = 1.5, 0.05, 0.045
LR = R + 0.25           # радиус лестницы (нужен для отверстий в платформах)
# Платформы: стык красный-белый (12м), стык белый-красный (28м), верхняя (37м)
for pz, pname in [(12.0, "Joint_LM"), (28.0, "Joint_MU"), (37.0, "Top")]:
    cyl((FX, FY, pz), PR, 0.12, name="{}_D".format(pname), m=MS, seg=48)
    for rh in [0.40, 0.90, 1.30]:
        torus((FX, FY, pz+rh), PR-0.18, RH, name="{}_R{}".format(pname, rh), m=MS, seg=48, rseg=12)
    for a in range(0, 360, 45):
        ang = math.radians(a)
        sx = FX + math.cos(ang) * (PR - 0.22)
        sy = FY + math.sin(ang) * (PR - 0.22)
        # Стойка: от чуть ниже нижнего поручня (pz+0.30) до верхнего (pz+1.30)
        cyl((sx, sy, pz+0.68), POST_R, 1.24, name="{}_P{}".format(pname, a), m=MS, seg=6)

# ── Отверстия (круглые люки) в платформах над лестницей ──
HATCH_R = 0.35  # радиус круглого люка (достаточно для прохода человека)
for pz, pname, az_deg in [(12.0, "Joint_LM", 0), (28.0, "Joint_MU", 90), (37.0, "Top", 0)]:
    az = math.radians(az_deg)
    hx = FX + math.cos(az) * LR
    hy = FY + math.sin(az) * LR
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32, radius=HATCH_R, depth=0.20,
        location=(hx, hy, pz))
    cutter = bpy.context.active_object; cutter.name = "{}_Hole".format(pname)
    disc = bpy.data.objects["{}_D".format(pname)]
    bpy.context.view_layer.objects.active = disc
    mod = disc.modifiers.new(name="Hole", type='BOOLEAN')
    mod.object = cutter; mod.operation = 'DIFFERENCE'
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)

# ═══════ 3. ЛЕСТНИЦА: Н-образная, только на красных секциях, у ствола ═══════
LR = R + 0.25          # радиус — прямо у ствола
RAIL_R = 0.025         # радиус реек
STEP_W = 0.45          # ширина лестницы
CAGE_R = LR + 0.28     # радиус клетки
CAGE_BAR_R = 0.014     # тонкие прутья

# Три секции лестницы: нижняя красная, белая, верхняя красная
LADDER_SECTIONS = [
    (0.6, 12.0, 0),      # нижняя красная
    (12.0, 28.0, 90),    # белая ← возвращаю!
    (28.0, 37.5, 0),     # верхняя красная
]

for sec_idx, (z0, z1, az_deg) in enumerate(LADDER_SECTIONS):
    az = math.radians(az_deg)
    ox = FX + math.cos(az) * LR
    oy = FY + math.sin(az) * LR
    px = -math.sin(az)
    py = math.cos(az)

    # Координаты реек
    lx = ox - px * STEP_W/2
    ly = oy - py * STEP_W/2
    rx = ox + px * STEP_W/2
    ry = oy + py * STEP_W/2

    # Рейки — СТАЛЬНЫЕ серые
    pipe((lx, ly, z0), (lx, ly, z1), r=RAIL_R, m=MS, seg=12,
         name="Rail_L_{}".format(sec_idx))
    pipe((rx, ry, z0), (rx, ry, z1), r=RAIL_R, m=MS, seg=12,
         name="Rail_R_{}".format(sec_idx))

    # Ступени: одна перекладина на шаг
    STEP_H = 0.30
    n_steps = int((z1 - z0) / STEP_H)
    sh = (z1 - z0) / n_steps
    for si in range(n_steps):
        z = z0 + si * sh + sh/2
        pipe((lx, ly, z), (rx, ry, z), r=RAIL_R*0.7, m=MS, seg=6,
             name="Rung_{}_{}".format(sec_idx, si))

    # Защитная клетка
    cage_n = 8
    for ci in range(cage_n):
        ca = math.radians(ci * 360 / cage_n)
        cx = ox + math.cos(ca) * (CAGE_R - LR)
        cy = oy + math.sin(ca) * (CAGE_R - LR)
        pipe((cx, cy, z0), (cx, cy, z1), r=CAGE_BAR_R, m=MS, seg=6,
             name="CageV_{}_{}".format(sec_idx, ci))

    # Кольца клетки + радиальные распорки к стволу
    n_rings = int((z1 - z0) / 1.5) + 1
    for ri in range(n_rings):
        ring_z = z0 + ri * 1.5
        if ring_z > z1: ring_z = z1
        torus((ox, oy, ring_z), CAGE_R - LR, CAGE_BAR_R,
              name="CageR_{}_{}".format(sec_idx, int(ring_z)), m=MS, seg=36, rseg=12)
        # Боковые распорки от кольца клетки к стволу (левая + правая)
        for ra in [90, 270]:
            rang = math.radians(az_deg + ra)
            csx = ox + math.cos(rang) * (CAGE_R - LR)
            csy = oy + math.sin(rang) * (CAGE_R - LR)
            pipe((csx, csy, ring_z), (FX+math.cos(rang)*LR*0.6, FY+math.sin(rang)*LR*0.6, ring_z),
                 r=CAGE_BAR_R*0.8, m=MS, seg=6,
                 name="Brkt_{}_{}_{}".format(sec_idx, int(ring_z), ra))
    # Гарантируем кольцо на самом верху (z1) — если ещё не создано
    if z0 + (n_rings - 1) * 1.5 < z1 - 0.01:
        torus((ox, oy, z1), CAGE_R - LR, CAGE_BAR_R,
              name="CageR_{}_{}".format(sec_idx, int(z1)), m=MS, seg=36, rseg=12)
        for ra in [90, 270]:
            rang = math.radians(az_deg + ra)
            csx = ox + math.cos(rang) * (CAGE_R - LR)
            csy = oy + math.sin(rang) * (CAGE_R - LR)
            pipe((csx, csy, z1), (FX+math.cos(rang)*LR*0.6, FY+math.sin(rang)*LR*0.6, z1),
                 r=CAGE_BAR_R*0.8, m=MS, seg=6,
                 name="Brkt_{}_{}_top".format(sec_idx, int(z1), ra))

# ═══════ 4. ОТТЯЖКИ — НА КРАСНЫХ СЕКЦИЯХ, АНКЕРЫ 1.4×1.4×0.8м ═══════
GH = [10.0, 20.0, 34.0]
GA = [45, 135, 225, 315]
GR = 20.0
for h in GH:
    r = 0.09 if h == 20.0 else 0.08
    for ga in GA:
        ang = math.radians(ga)
        ax = FX + math.cos(ang) * GR
        ay = FY + math.sin(ang) * GR
        # Анкерный блок: центр z=0.40, scale=0.70 → верх z=0.80
        cube((ax, ay, 0.40), (0.70, 0.70, 0.40), 
             name="Anc_{}_{}".format(int(h), ga), m=MN)
        # Трос от ствола к вершине анкера
        pipe((FX, FY, h), (ax, ay, 0.80), r=r, m=MC, seg=14,
             name="Guy_{}_{}".format(int(h), ga))

# ═══════ 5. ГОРЕЛКА + ПАР + ГАЗОВЫЙ КОЛЛЕКТОР ═══════
BZ = H + 0.3
cyl((FX, FY, BZ), 0.80, 1.0, name="Burner_B", m=MB, seg=26)
NOZZLE_Z = BZ + 0.5
_flare_tip_materials = make_materials()
_flare_tip_assembly = make_assembly_empty()
_flare_tip_created = []
for _flare_tip_rec in OBJECTS:
    _flare_tip_obj = create_object(_flare_tip_rec, _flare_tip_materials)
    _flare_tip_created.append(_flare_tip_obj)
for _flare_tip_obj in _flare_tip_created:
    parent_keep_world(_flare_tip_obj, _flare_tip_assembly)
_flare_tip_assembly.location = (FX, FY, NOZZLE_Z)

# Дежурные горелки: газ подаётся изнутри ствола через маленькие патрубки
# (основной сбросной газ идёт внутри ствола — подводится от сепаратора через эстакаду)

# ПАР: внешний стояк вдоль ствола, посекционная окраска как у ствола, крепления-хомуты
# Стояк сзади-слева (азимут ~220°), от уровня эстакады до парового кольца
STEAM_Z = BZ + 0.5          # высота парового кольца
STEAM_R = R + 0.35          # отступ от центра ствола
STEAM_AZ = math.radians(210)  # азимут стояка (сзади-слева)
STEAM_PIPE_R = 0.12
SX0 = FX + math.cos(STEAM_AZ) * STEAM_R
SY0 = FY + math.sin(STEAM_AZ) * STEAM_R
SS_Z = 2.7  # уровень эстакады (SHOE_Z, секция 9) — начало стояка
# Стояк: только от эстакады вверх (нижний конец на эстакаде, не на земле)
pipe((SX0, SY0, SS_Z),  (SX0, SY0, 12.0), r=STEAM_PIPE_R, m=MR, seg=16, name="SteamRise_L")
pipe((SX0, SY0, 12.0), (SX0, SY0, 28.0), r=STEAM_PIPE_R, m=MW, seg=16, name="SteamRise_M")
pipe((SX0, SY0, 28.0), (SX0, SY0, STEAM_Z), r=STEAM_PIPE_R, m=MR, seg=16, name="SteamRise_U")

# Крепления-хомуты каждые 2 метра (torus вокруг стояка + стержень к стволу)
CLAMP_R = STEAM_PIPE_R * 1.5
# Начинаем от SS_Z + 0.5 (чуть выше joint-а), чтобы не накладываться на стык
for cz in [z/10.0 for z in range(int(SS_Z*10+5), int(STEAM_Z*10), 20)]:  # каждые 2.0м
    # Хомут — torus вокруг стояка
    torus((SX0, SY0, cz), CLAMP_R, 0.012, name="SCL_T_{}".format(int(cz*10)), m=MS, seg=24, rseg=12)
    # Стержень от хомута к стволу
    pipe((SX0+math.cos(STEAM_AZ)*CLAMP_R, SY0+math.sin(STEAM_AZ)*CLAMP_R, cz),
         (FX+math.cos(STEAM_AZ)*R, FY+math.sin(STEAM_AZ)*R, cz),
         r=0.012, m=MS, seg=6, name="SCL_B_{}".format(int(cz*10)))

# ═══════ 6. ДАТЧИКИ НА СТВОЛЕ ═══════
# Датчик давления: корпус на кронштейне + стержень к стволу
def pressure_sensor(loc, name):
    # Направление к стволу: от датчика к поверхности (центр ствола (FX,FY), радиус R)
    dx, dy = loc[0] - FX, loc[1] - FY
    dist = math.sqrt(dx*dx + dy*dy)
    ux, uy = dx/dist, dy/dist  # единичный вектор от ствола к датчику
    stem_r = 0.015
    cube((loc[0], loc[1], loc[2]-0.08), (0.06, 0.06, 0.04), name=name+"_Brkt", m=MS)
    # Стержень от кронштейна к поверхности ствола
    pipe((FX + ux*R, FY + uy*R, loc[2]-0.08), (loc[0]-ux*0.06, loc[1]-uy*0.06, loc[2]-0.08),
         r=stem_r, m=MS, seg=8, name=name+"_Stem")
    cyl(loc, 0.05, 0.10, name=name+"_Body", m=MY, seg=12)
    cyl((loc[0], loc[1], loc[2]+0.07), 0.03, 0.04, name=name+"_Top", m=MM, seg=10)

# Датчик температуры: длинный зонд в гильзе + стержень к стволу
def temp_sensor(loc, name):
    dx, dy = loc[0] - FX, loc[1] - FY
    dist = math.sqrt(dx*dx + dy*dy)
    ux, uy = dx/dist, dy/dist
    stem_r = 0.015
    cube((loc[0], loc[1], loc[2]-0.06), (0.05, 0.05, 0.03), name=name+"_Brkt", m=MS)
    # Стержень от кронштейна к поверхности ствола
    pipe((FX + ux*R, FY + uy*R, loc[2]-0.06), (loc[0]-ux*0.05, loc[1]-uy*0.05, loc[2]-0.06),
         r=stem_r, m=MS, seg=8, name=name+"_Stem")
    cyl(loc, 0.04, 0.18, name=name+"_Probe", m=MR, seg=10)
    cyl((loc[0], loc[1], loc[2]+0.12), 0.05, 0.05, name=name+"_Head", m=MM, seg=12)

# На нижней красной секции: P_flare, Q_flare
pressure_sensor((FX, FY+1.2, 3.5), "PS_Pflare")
pressure_sensor((FX, FY-1.2, 3.5), "PS_Qflare")
# На белой секции: P_purge, Q_purge
pressure_sensor((FX, FY+1.2, 18.0), "PS_Ppurge")
pressure_sensor((FX, FY-1.2, 18.0), "PS_Qpurge")
# На верхней красной секции: T_flame, Steam_Q
temp_sensor((FX, FY+1.2, 30.0), "TS_Tflame")
pressure_sensor((FX, FY-1.2, 30.0), "PS_SteamQ")

# ═══════ 7. СЕПАРАТОР ═══════
# Подробная модель: эллиптические днища, седловидные опоры, площадка с ограждениями,
# лестница с клеткой, патрубки с фланцами, люк, уровнемер, манометр, предупреждающие полосы
# Координаты (используются также в секциях 9, 9a, 9c):
SX, SY, SZ, SL, SR = -10.0, -6.0, 2.8, 7.5, 1.4
create_separator(bpy, math, MW, MS, MY, MM, MN, MR)

# ═══════ 7a. ШКАФЫ УПРАВЛЕНИЯ ═══════
# Добавляем шкафы с опорами (столбики + рейки), без грунта (он уже есть)
_cabinet_existing = set(bpy.data.objects)
build_support_structure()
# Remove the small ground plane — the flare scene has its own
_ground = bpy.data.objects.get('geo_ground')
if _ground:
    bpy.data.objects.remove(_ground, do_unlink=True)
build_cabinet()
duplicate_cabinet(1.00)
_cabinet_created = [obj for obj in bpy.data.objects if obj not in _cabinet_existing]
_cabinet_dx = SX - 4.5
_cabinet_dy = SY - 2.0
for _cabinet_obj in _cabinet_created:
    _cabinet_obj.location.x += _cabinet_dx
    _cabinet_obj.location.y += _cabinet_dy

_cabinet_materials = make_all_materials()
assign_materials(_cabinet_materials)

# ═══════ 8. ДРЕНАЖ ═══════

# ═══════ 9. ТРУБОПРОВОДНАЯ ЭСТАКАДА (УСИЛЕННАЯ) ═══════
RY = -7.0
RACK_SPAN = 3     # int — для range()
BEAM_Z = 2.6        # верх балки (centre + half scale)
COL_W = 0.12         # толщина стоек УВЕЛИЧЕНА
SHOE_Z = BEAM_Z + 0.08
FLARE_Z = SHOE_Z + 0.17 + 0.03
PURGE_Z = SHOE_Z + 0.12 + 0.03

# СБРОСНОЙ ГАЗ (FlareGas): сепаратор → эстакада → ствол (горизонтально, прямой угол)
# От сепаратора горизонтально до эстакады, спуск у эстакады, дальше горизонтально до ствола

# ПРОДУВОЧНЫЙ ГАЗ (Purge): подаётся через внутренний стояк, отдельная наружная труба не нужна

# КОНДЕНСАТ: сбрасывается внутри сепаратора, отдельная труба не нужна
# (жидкость отводится через дренажный патрубок Sep_Drain на корпусе)

# ПАР (Steam): магистраль скрыта внутри ствола, снаружи только паровое кольцо + форсунки
# Внешняя паровая труба не нужна — пар подаётся по внутреннему стояку
# (см. секцию 5 — SteamRing + Nozzles)

# (датчик расхода убран вместе с продувочной линией)

# ═══════ 9c. ФУНДАМЕНТНАЯ ПЛИТА ПОД СЕПАРАТОР ═══════
# Бетонная плита под всем сепаратором, выступает за габариты

# ═══════ 10. СВЕТ ═══════
bpy.ops.object.light_add(type='SUN', location=(25, -20, 35))
bpy.context.active_object.data.energy = 4.5

# ═══════ 10. КАМЕРА ═══════
bpy.ops.object.camera_add()
cam = bpy.context.active_object
cam.name = "Camera"
cam.data.lens = 18
cam.location = Vector((28, -30, 22))
tgt = Vector((-4, -3, 15))
cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam

# ═══════ 11. EEVEE + ГОЛУБОЕ НЕБО ═══════
s = bpy.context.scene
s.render.engine = 'BLENDER_EEVEE'
s.eevee.taa_render_samples = 32
s.view_settings.exposure = 1.2
s.render.resolution_x = 1920
s.render.resolution_y = 1080
s.render.image_settings.file_format = 'PNG'

# Голубое небо
w = bpy.data.worlds['World']
w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.45, 0.68, 0.90, 1.0)
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.2

# ── СОХРАНЕНИЕ + РЕНДЕР ──
blend_path = "/home/pomadoro/projects/flare-predictor/blender/flare_install.blend"
render_path = "/home/pomadoro/projects/flare-predictor/blender/0001.png"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
s.render.filepath = render_path
bpy.ops.render.render(write_still=True)
print("✅ v14 сохранена + рендер: {}".format(render_path))
