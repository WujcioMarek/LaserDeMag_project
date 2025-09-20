Module LaserDeMag.visual.plotter
================================
Moduł przygotowujący dane do wizualizacji wyników symulacji 3TM.

Ten moduł zawiera funkcję `plot_results`, która przetwarza dane wyjściowe modelu 3TM
(temperatury elektronów, fononów oraz magnetyzacji) w celu przygotowania ich do wykresów
przestrzennych i czasowych.

---
3TM simulation results plotting module.

This module includes the `plot_results` function, which processes the 3TM model output
(electron, phonon temperatures and magnetization) to prepare it for spatial and temporal plots.

Functions
---------

`plot_results(S, delays, temp_map, material_name)`
: