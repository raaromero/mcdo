"""Titles, bullets, figures, equations and speaker notes of slides of the 2CE meeting deck of 2026-10-29
(scripts/make_lim2002_progress_deck.py -> output/08_two_color/decks/2ce_meeting_cambaliza.pptx, frozen), copied word for
word from its manifest (2ce_meeting_manifest.json) on 2026-11-18. The user reviewed these slides; decks that carry
one of them over take its text from here. Key: the slide title. n: the slide number in that deck. figs: paths
under output/.
"""

SLIDES = {'Two-color excitation with two confocal beams at an angle θ': {'n': 5,
                                                                'items': ['2CE: “two excitation photons of different '
                                                                          'wavelengths,” with 1/λe = 1/λ1 + 1/λ2 (p. '
                                                                          '26).',
                                                                          'The two beams “do not interfere with each '
                                                                          'other” (p. 26).',
                                                                          'θ = angle between the two lens axes: θ = '
                                                                          '0 is single-beam 2PE, θ = π is 4Pi 2PE '
                                                                          '(p. 26).'],
                                                                'figs': ['08_two_color/setup_model.png'],
                                                                'eqs': [],
                                                                'main': 'Two lenses focus two colors onto one point, '
                                                                        'at an angle theta.',
                                                                'notes': 'pp. 26-27: 2PE is the special case lambda1 '
                                                                         '= lambda2 = 2 lambda_e = lambda_2p. L1 '
                                                                         'defines the z-axis; at theta = 0 only one '
                                                                         'lens is needed. Detector: large area, '
                                                                         'along the z-axis of L1.'},
 'Fluorescence from two colors (2CE) and from two photons of one color (2PE)': {'n': 7,
                                                                                'items': ['At each point P, the '
                                                                                          'fluorescence depends on '
                                                                                          'how the two focused beams '
                                                                                          'combine.',
                                                                                          '2CE absorbs one photon of '
                                                                                          'each color, so the signal '
                                                                                          'is the product of the two '
                                                                                          'intensities.',
                                                                                          'It is generated “only in '
                                                                                          'regions where there is a '
                                                                                          'simultaneous presence of '
                                                                                          'I1(P) and I2(P; θ)” (p. '
                                                                                          '28).',
                                                                                          '2PE uses one color in '
                                                                                          'both beams, so the two '
                                                                                          'fields add first: the '
                                                                                          'excitation has '
                                                                                          'interference terms (p. '
                                                                                          '28).',
                                                                                          '2PE absorbs two photons, '
                                                                                          'so the signal is the '
                                                                                          'square of the excitation: '
                                                                                          'the fourth power of the '
                                                                                          'summed field.',
                                                                                          '2PE is “possible even '
                                                                                          'with only one excitation '
                                                                                          'beam” (p. 28): I12 and '
                                                                                          'I22 remain where the '
                                                                                          'other beam is absent.'],
                                                                                'figs': [],
                                                                                'eqs': ['F_{2c}(P;\\theta) = '
                                                                                        '\\kappa\\,|U_1(P)|^2\\,|U_2(P;\\theta)|^2 '
                                                                                        '= \\kappa\\, I_1(P)\\, '
                                                                                        'I_2(P;\\theta)',
                                                                                        '|U_1(P) + U_2(P;\\theta)|^2 '
                                                                                        '= I_1 + I_2 + '
                                                                                        '2\\,\\mathrm{Re}\\left[U_1 '
                                                                                        'U_2^{*}\\right]',
                                                                                        'F_{2p}(P;\\theta) = '
                                                                                        "\\kappa'\\,|U_1(P) + "
                                                                                        'U_2(P;\\theta)|^4'],
                                                                                'main': 'Eqs. (2)-(3): 2CE '
                                                                                        'multiplies two intensities; '
                                                                                        '2PE squares the summed '
                                                                                        'intensity of two '
                                                                                        'interfering beams.',
                                                                                'notes': "kappa, kappa' = "
                                                                                         'fluorescence '
                                                                                         'cross-sections. 2CE: '
                                                                                         'lambda1 = 0.750 um on L1, '
                                                                                         'lambda2 = 0.656 um on L2. '
                                                                                         '2PE: lambda_2p = 0.7 um on '
                                                                                         'both.'},
 'Summary: high NA': {'n': 34,
                      'items': ['The conclusions of Cambaliza & Saloma hold at high NA, but the differences between '
                                '2PE and 2CE shrink.',
                                '2PE at θ = π/2 stays the sharpest distribution at all NA: its spot is one '
                                'interference fringe, 0.26 µm in air, while the 2CE spot shrinks with NA, from 2.9 '
                                'times the 2PE spot at NA 0.5 to 2.0 at NA 0.7.',
                                'The 2PE side lobes weaken with NA, from 0.11 to 0.04 of the peak at θ = π/2 (NA 0.5 '
                                'to 0.7) and from 0.97 to 0.42 at θ = π (NA 0.5 to 0.9), so 2PE images gain '
                                'contrast.',
                                'Crossed lenses (θ = π/2) fit only up to NA 0.71 in air and 0.94 in water, the limit '
                                'of NA 0.7 noted on p. 34.',
                                'The paraxial Eq. (1) gives the right spot width up to NA 0.86 in air, but '
                                'overestimates the depth of focus above NA 0.43 (by 36% at NA 0.9).'],
                      'figs': [],
                      'eqs': [],
                      'main': 'High NA: main points.',
                      'notes': 'Vector = Richards-Wolf, both beams polarized along y. Paraxial DOF error grows as '
                               'tan^2(alpha/2); in water it is about half that in air at the same NA. Annular '
                               'pupils: paraxial DOF 2.2x too long at NA 0.9 in air.'},
 'Central spot and depth of focus against NA: 2CE, θ = 0 and π': {'n': 35,
                                                                  'items': ['As NA increases both widths shrink, but '
                                                                            'the paraxial depth of focus shrinks '
                                                                            'more slowly than the vector one and '
                                                                            'becomes too long.',
                                                                            'The paraxial DOF of F2c(0, 0, z; 0) is '
                                                                            '5% longer from NA 0.43 in air (0.57 in '
                                                                            'water), below the NA 0.7 stated on p. '
                                                                            '27; the central spot stays within 5% up '
                                                                            'to NA 0.86.',
                                                                            'Eq. (1) uses sin²α/2 for 1 − cos α, '
                                                                            'which lengthens the DOF by the factor 1 '
                                                                            '+ tan²(α/2).'],
                                                                  'figs': ['08_two_color/cambaliza2000/high_na/cfg_2ce_0.png'],
                                                                  'eqs': [],
                                                                  'main': 'Scalar against vector widths, 2CE, θ = 0 '
                                                                          'and π.',
                                                                  'notes': 'Solid: vector (Richards-Wolf), beams '
                                                                           'along y; dashed: paraxial scalar. Blue: '
                                                                           'air; green: water. Linear axes. Gap '
                                                                           'numbers from high_na/split.txt.'},
 'Central spot and depth of focus against NA: 2CE, θ = π/2': {'n': 36,
                                                              'items': ['As NA increases both widths of F2c at θ = '
                                                                        'π/2 shrink, and the paraxial model follows '
                                                                        'the vector focus within 4% wherever crossed '
                                                                        'lenses fit (NA 0.71 in air, 0.94 in water).',
                                                                        'Each width is set by the narrow transverse '
                                                                        'spot of the other beam, which Eq. (1) '
                                                                        'reproduces.'],
                                                              'figs': ['08_two_color/cambaliza2000/high_na/cfg_2ce_pi2.png'],
                                                              'eqs': [],
                                                              'main': 'Scalar against vector widths, 2CE, θ = π/2.',
                                                              'notes': 'Solid: vector (Richards-Wolf), beams along '
                                                                       'y; dashed: paraxial scalar. Blue: air; '
                                                                       'green: water. Linear axes. Gap numbers from '
                                                                       'high_na/split.txt.'},
 'Central spot and depth of focus against NA: 2PE, θ = 0': {'n': 37,
                                                            'items': ['F2p at θ = 0 is identical with F2c at θ = 0, '
                                                                      'so it changes with NA in the same way: the '
                                                                      'paraxial DOF is 5% longer from NA 0.43 in '
                                                                      'air.'],
                                                            'figs': ['08_two_color/cambaliza2000/high_na/cfg_2pe_0.png'],
                                                            'eqs': [],
                                                            'main': 'Scalar against vector widths, 2PE, θ = 0.',
                                                            'notes': 'Solid: vector (Richards-Wolf), beams along y; '
                                                                     'dashed: paraxial scalar. Blue: air; green: '
                                                                     'water. Linear axes. Gap numbers from '
                                                                     'high_na/split.txt.'},
 'Central spot and depth of focus against NA: 2PE, θ = π/2': {'n': 38,
                                                              'items': ['As NA increases the central spot of F2p at '
                                                                        'θ = π/2 keeps its width, 0.26 µm in air and '
                                                                        '0.19 µm in water, in both models (within '
                                                                        '0.4%).',
                                                                        'The spot is one interference fringe of the '
                                                                        'two crossed beams, so its width is set by '
                                                                        'the wavelength in the medium, λ2p/n (n = 1 '
                                                                        'air, 1.33 water), not by the NA.',
                                                                        'It stays the sharpest distribution at every '
                                                                        'NA, as at NA 0.5 (p. 28).'],
                                                              'figs': ['08_two_color/cambaliza2000/high_na/cfg_2pe_pi2.png'],
                                                              'eqs': [],
                                                              'main': 'Scalar against vector widths, 2PE, θ = π/2.',
                                                              'notes': 'Solid: vector (Richards-Wolf), beams along '
                                                                       'y; dashed: paraxial scalar. Blue: air; '
                                                                       'green: water. Linear axes. Gap numbers from '
                                                                       'high_na/split.txt.'},
 'Central spot and depth of focus against NA: 2PE, θ = π': {'n': 39,
                                                            'items': ['Across the axis, F2p(x, 0, 0; π) is identical '
                                                                      'with F2p(x, 0, 0; 0).',
                                                                      'As NA increases fewer fringes fit inside the '
                                                                      'focus, about 9 at NA 0.5 and 2 at NA 0.9 in '
                                                                      'air: the focus shortens as 1/NA², while the '
                                                                      'fringes stay about λ/2n apart, half the '
                                                                      'wavelength in the medium (0.37 µm at NA 0.5, '
                                                                      '0.44 µm at NA 0.9; λ/2n = 0.35 µm in air).',
                                                                      'The fringes spread slightly with NA because '
                                                                      'the converging waves cross the axis at an '
                                                                      'angle; the central fringe widens from 0.13 to '
                                                                      '0.17 µm, and paraxial and vector agree within '
                                                                      '5% up to NA 0.91 in air.'],
                                                            'figs': ['08_two_color/cambaliza2000/high_na/cfg_2pe_pi.png'],
                                                            'eqs': [],
                                                            'main': 'Scalar against vector widths, 2PE, θ = π.',
                                                            'notes': 'Solid: vector (Richards-Wolf), beams along y; '
                                                                     'dashed: paraxial scalar. Blue: air; green: '
                                                                     'water. Linear axes. Gap numbers from '
                                                                     'high_na/split.txt. Facing lenses: the two '
                                                                     'beams form a standing wave with peaks about '
                                                                     'lambda/2n apart (n = refractive index; '
                                                                     'lambda/2n = 0.35 um in air, 0.26 um in water): '
                                                                     '0.37 um at NA 0.5 and 0.44 um at NA 0.9 in '
                                                                     'air. The spacing grows a little with NA '
                                                                     'because the converging waves cross the axis at '
                                                                     'an angle. Fringes inside the focus (its length '
                                                                     'over the spacing): air about 9 at NA 0.5, 4 at '
                                                                     '0.7, 2 at 0.9; water about 17 at NA 0.5, 4 at '
                                                                     '0.9, 2 at 1.2. The focus shortens as 1/NA^2 '
                                                                     'while the spacing stays near lambda/2n.'},
 'Paraxial over vector widths of 2CE against NA': {'n': 40,
                                                   'items': ['As NA increases the paraxial 2CE widths become larger '
                                                             'than the vector ones, first along the axis.',
                                                             'Along the axis at θ = 0 and π the difference reaches '
                                                             '5% at NA 0.43 in air (0.57 in water); across the axis '
                                                             'at NA 0.86 (1.14); with crossed lenses it stays within '
                                                             '4%.'],
                                                   'figs': ['08_two_color/cambaliza2000/high_na/gap_2ce.png'],
                                                   'eqs': [],
                                                   'main': 'Where the paraxial 2CE widths depart from the vector '
                                                           'ones.',
                                                   'notes': 'Gap = scalar / vector - 1. Diamonds: NA where the gap '
                                                            'reaches 5% (interpolated).'},
 'Paraxial over vector widths of 2PE against NA': {'n': 41,
                                                   'items': ['As NA increases the paraxial 2PE widths at θ = 0 '
                                                             'depart as the 2CE ones; with crossed lenses they stay '
                                                             'within 0.4%.',
                                                             'At θ = π the paraxial central fringe becomes narrower '
                                                             'than the vector one, by 5% at NA 0.91 in air (1.21 in '
                                                             'water).'],
                                                   'figs': ['08_two_color/cambaliza2000/high_na/gap_2pe.png'],
                                                   'eqs': [],
                                                   'main': 'Where the paraxial 2PE widths depart from the vector '
                                                           'ones.',
                                                   'notes': 'Gap = scalar / vector - 1. 2PE across the axis at theta '
                                                            '= pi equals theta = 0 and is not drawn twice.'},
 'Whole-profile measures: NRMSE and Linfoot’s F, C, Q': {'n': 42,
                                                         'items': ['Both profiles scaled to the same energy, so side '
                                                                   'lobes and tails count, not only the width.',
                                                                   'NRMSE: the root-mean-square difference of the '
                                                                   'two profiles; 0 when they are identical.',
                                                                   'Fidelity F, structural content C, correlation '
                                                                   'quality Q: 1 for identical profiles; C < 1 for a '
                                                                   'flatter, longer focus.',
                                                                   'F, C and Q are linked; NRMSE carries the same '
                                                                   'information as F.'],
                                                         'figs': [],
                                                         'eqs': ['\\sum_k a_k\\,\\Delta s = \\sum_k r_k\\,\\Delta s '
                                                                 '= 1',
                                                                 '\\mathrm{NRMSE} = \\sqrt{\\frac{\\sum_k (a_k - '
                                                                 'r_k)^2}{\\sum_k r_k^2}}',
                                                                 'F = 1 - \\frac{\\sum_k (a_k - r_k)^2}{\\sum_k '
                                                                 'r_k^2}, \\qquad C = \\frac{\\sum_k a_k^2}{\\sum_k '
                                                                 'r_k^2}, \\qquad Q = \\frac{\\sum_k a_k\\, '
                                                                 'r_k}{\\sum_k r_k^2}',
                                                                 'F = 2Q - C, \\qquad \\mathrm{NRMSE} = \\sqrt{1 - '
                                                                 'F}'],
                                                         'main': 'Whole-profile measures and their equations.',
                                                         'notes': 'Linfoot (1956) criteria with the vector profile '
                                                                  'as reference. Unit energy over the window: a '
                                                                  'profile that is longer but lower is not counted '
                                                                  'as better. The dashboard shows these on the '
                                                                  'profile (How it is measured).'},
 'Whole-profile difference of 2CE, paraxial against vector': {'n': 43,
                                                              'items': ['As NA increases the paraxial F2c departs '
                                                                        'from the vector one along the axis much '
                                                                        'more than across it.',
                                                                        'Along the axis at θ = 0 and π: 6% at NA 0.5 '
                                                                        'and 25% at NA 0.9 in air; across the axis '
                                                                        '1% and 5%; with crossed lenses 3% or less.'],
                                                              'figs': ['08_two_color/cambaliza2000/high_na/nrmse_2ce.png'],
                                                              'eqs': [],
                                                              'main': 'Whole profiles: the same picture as the '
                                                                      'widths.',
                                                              'notes': 'r = vector profile, a = scalar profile, both '
                                                                       'normalized to unit area over the plotted '
                                                                       'window (x +-1 um x 0.5/NA, z +-5 um x n '
                                                                       '(0.5/NA)^2), 401 points. NRMSE = sqrt(1 - '
                                                                       'F), F = Linfoot fidelity.'},
 'Whole-profile difference of 2PE, paraxial against vector': {'n': 44,
                                                              'items': ['As NA increases the paraxial F2p departs as '
                                                                        'F2c at θ = 0; along the axis at θ = π by 7% '
                                                                        'at NA 0.5 and 29% at NA 0.9 in air.',
                                                                        'With crossed lenses it differs by 5% or '
                                                                        'less: the fringes are set by the wavelength '
                                                                        'in both models.'],
                                                              'figs': ['08_two_color/cambaliza2000/high_na/nrmse_2pe.png'],
                                                              'eqs': [],
                                                              'main': 'Whole 2PE profiles, scalar against vector.',
                                                              'notes': 'Same normalization as the 2CE slide. 2PE '
                                                                       'across the axis at theta = pi equals theta = '
                                                                       '0.'},
 'Summary: Linfoot’s criteria': {'n': 46,
                                 'items': ['As NA increases the paraxial profiles keep their shape across the axis: '
                                           'F ≥ 0.996 for both signals and all θ.',
                                           'Along the axis with facing lenses they become longer and lower than the '
                                           'vector ones: C < 0.95 from NA 0.44 in air (0.58 in water), where the DOF '
                                           'departs by 5%.',
                                           'With crossed lenses (θ = π/2), F ≥ 0.997 and C ≥ 0.9 wherever the lenses '
                                           'fit.',
                                           'F falls below 0.99 from NA 0.6 in air; C responds first, because the '
                                           'paraxial focus is longer and lower.'],
                                 'figs': [],
                                 'eqs': [],
                                 'main': 'Linfoot’s criteria: main points.',
                                 'notes': 'F = 1 - sum (a-r)^2 / sum r^2, C = sum a^2 / sum r^2, Q = sum a r / sum '
                                          'r^2, with r = vector, a = scalar, each normalized to unit energy over the '
                                          'window (circular pupils, uniform input). All cases, also annular and '
                                          'Gaussian: '
                                          'output/08_two_color/cambaliza2000/high_na/linfoot/linfoot_<signal>_<pupil>_<input>.png '
                                          'and the dashboard.'},
 'Linfoot’s criteria against NA: 2CE, θ = 0 and π': {'n': 47,
                                                     'items': ['As NA increases the paraxial F2c(0, 0, z; π) becomes '
                                                               'longer and lower than the vector one, so C falls '
                                                               'first: below 0.95 from NA 0.44 in air (0.58 in '
                                                               'water).',
                                                               'F stays above 0.99 up to NA 0.63 (0.84 in water); '
                                                               'across the axis F ≥ 0.996 at all NA.'],
                                                     'figs': ['08_two_color/cambaliza2000/high_na/linfoot/linfoot_na_2ce_0.png'],
                                                     'eqs': [],
                                                     'main': 'F changes least; C and Q show the split first, along '
                                                             'the axis.',
                                                     'notes': 'Why C falls first: with unit energy, the longer '
                                                              'scalar focus has a lower peak, so sum a^2 drops below '
                                                              'sum r^2.'},
 'Linfoot’s criteria against NA: 2CE, θ = π/2': {'n': 48,
                                                 'items': ['As NA increases the paraxial and vector F2c at θ = π/2 '
                                                           'stay alike: F ≥ 0.999, C ≥ 0.97 and Q ≥ 0.98 wherever '
                                                           'crossed lenses fit (NA 0.71 in air, 0.94 in water).',
                                                           'With crossed lenses, Eq. (1) gives the profiles of the '
                                                           'vector focus.'],
                                                 'figs': ['08_two_color/cambaliza2000/high_na/linfoot/linfoot_na_2ce_pi2.png'],
                                                 'eqs': [],
                                                 'main': 'Crossed lenses: scalar and vector profiles agree.',
                                                 'notes': 'Same normalization; crossed lenses fit up to NA = n sin '
                                                          '45 degrees.'},
 'Linfoot’s criteria against NA: 2PE, θ = 0': {'n': 49,
                                               'items': ['As NA increases F2p at θ = 0 departs as F2c at θ = 0: '
                                                         'along the axis C < 0.95 from NA 0.44 in air and F < 0.99 '
                                                         'from NA 0.63.',
                                                         'Across the axis F ≥ 0.996 at all NA.'],
                                               'figs': ['08_two_color/cambaliza2000/high_na/linfoot/linfoot_na_2pe_0.png'],
                                               'eqs': [],
                                               'main': '2PE at theta = 0: as 2CE.',
                                               'notes': 'Same normalization.'},
 'Linfoot’s criteria against NA: 2PE, θ = π/2': {'n': 50,
                                                 'items': ['As NA increases the paraxial F2p at θ = π/2 keeps F ≥ '
                                                           '0.997 wherever the lenses fit.',
                                                           'Along the axis C falls to 0.91; across the axis F, C and '
                                                           'Q stay above 0.97.'],
                                                 'figs': ['08_two_color/cambaliza2000/high_na/linfoot/linfoot_na_2pe_pi2.png'],
                                                 'eqs': [],
                                                 'main': '2PE with crossed lenses: close agreement.',
                                                 'notes': 'Same normalization.'},
 'Linfoot’s criteria against NA: 2PE, θ = π': {'n': 51,
                                               'items': ['As NA increases the paraxial envelope of the F2p(0, 0, z; '
                                                         'π) fringes becomes too long: C < 0.95 from NA 0.44 in air '
                                                         '(0.58 in water), F < 0.99 from NA 0.58 (0.78).',
                                                         'At NA 0.95 in air F = 0.85, the lowest of all cases.'],
                                               'figs': ['08_two_color/cambaliza2000/high_na/linfoot/linfoot_na_2pe_pi.png'],
                                               'eqs': [],
                                               'main': '2PE with facing lenses: the envelope sets the difference.',
                                               'notes': 'Same normalization.'},
 'Side lobes of 2PE against NA: distance from the peak and height': {'n': 52,
                                                                     'items': ['As NA increases the 2PE side lobes '
                                                                               'weaken: at θ = π/2 from 0.11 of the '
                                                                               'peak at NA 0.5 to 0.04 at NA 0.7 '
                                                                               '(air); at θ = π from 0.97 to 0.42 at '
                                                                               'NA 0.9.',
                                                                               'Their distance from the peak follows '
                                                                               'the wavelength in the medium (n = 1 '
                                                                               'air, 1.33 water): λ/2n with facing '
                                                                               'lenses (the standing-wave fringe) '
                                                                               'and λ/n with crossed lenses, at low '
                                                                               'NA.',
                                                                               'Weaker side lobes give images of '
                                                                               'higher contrast, so the drawback of '
                                                                               '2PE reported at NA 0.5 (pp. 28–29) '
                                                                               'shrinks at high NA.'],
                                                                     'figs': ['08_two_color/cambaliza2000/high_na/sidelobes.png'],
                                                                     'eqs': [],
                                                                     'main': 'The 2PE side lobes follow the '
                                                                             'wavelength: lambda/2n facing, lambda/n '
                                                                             'crossed.',
                                                                     'notes': 'At theta = pi/2 the side lobe rides '
                                                                              'on the narrow spot of the other beam, '
                                                                              'which narrows with NA, so it moves in '
                                                                              'and drops. First local maximum beyond '
                                                                              'the first minimum, vector (solid) and '
                                                                              'scalar (dashed); lambda = 0.7 um. At '
                                                                              'theta = pi the vector side lobe is '
                                                                              'lower than the scalar one at high NA '
                                                                              '(0.42 against 0.65 at NA 0.9 in air), '
                                                                              'because the vector focus, which sets '
                                                                              'the fringe envelope, is shorter. 2CE '
                                                                              'side lobes stay below 1e-3 of the '
                                                                              'peak.'},
 '2PE and 2CE central spots against NA, circular pupils': {'n': 53,
                                                           'items': ['As NA increases the 2CE spot at θ = π/2 '
                                                                     'shrinks while the 2PE spot keeps its width: '
                                                                     '2.9 times the 2PE spot at NA 0.5, 2.0 at NA '
                                                                     '0.7 in air.',
                                                                     'Relative to θ = 0, the 2PE spot at θ = π/2 is '
                                                                     '0.50 times as wide at NA 0.5 and 0.71 at NA '
                                                                     '0.7.',
                                                                     '2PE at θ = π/2 stays the sharpest distribution '
                                                                     'at every NA, as on p. 28; scalar and vector '
                                                                     'agree within 4%.'],
                                                           'figs': ['08_two_color/cambaliza2000/high_na/ratios_x.png'],
                                                           'eqs': [],
                                                           'main': 'The 2CE-2PE comparisons hold at high NA; their '
                                                                   'size depends on NA.',
                                                           'notes': 'Within 4% to NA 0.7 (air) and 0.9 (water). 2CE '
                                                                    'over 2PE at theta = pi/2: 2.9x at NA 0.5, 2.0x '
                                                                    'at NA 0.7 in air. 2PE crossed over facing: 0.50 '
                                                                    'at NA 0.5, 0.71 at NA 0.7 in air.'},
 '2CE and 2PE depth of focus against NA, θ = π/2': {'n': 54,
                                                    'items': ['As NA increases the 2CE DOF shortens while the 2PE '
                                                              'DOF stays one fringe: 2.6 times the 2PE DOF at NA '
                                                              '0.5, 1.8 at NA 0.7 in air.',
                                                              'The “broader DOF” of 2CE at θ = π/2 (p. 30) remains '
                                                              'at high NA, but the difference shrinks.'],
                                                    'figs': ['08_two_color/cambaliza2000/high_na/ratios_z.png'],
                                                    'eqs': [],
                                                    'main': 'The DOF comparison holds at high NA.',
                                                    'notes': 'DOF of 2CE over 2PE at theta = pi/2: 2.6 at NA 0.5, '
                                                             '1.8 at NA 0.7 in air; 3.5 at 0.5, 1.9 at 0.9 in water. '
                                                             'Scalar and vector within 4%. The 2PE width is that of '
                                                             'the central fringe, which does not change with NA, so '
                                                             'the ratio falls as the 2CE focus shortens.'},
 'Annular pupils: depth of focus against NA, air': {'n': 55,
                                                    'items': ['As NA increases the paraxial annular DOF departs '
                                                              'sooner than the circular one: 15% too long at NA 0.5 '
                                                              'and 2.2 times at NA 0.9 in air.',
                                                              'A thin ring uses the edge of the pupil, where the '
                                                              'paraxial phase error is largest.'],
                                                    'figs': ['08_two_color/cambaliza2000/high_na/pupils/annular_widths_air_z.png'],
                                                    'eqs': [],
                                                    'main': 'Along the axis the paraxial model departs sooner with '
                                                            'annular pupils.',
                                                    'notes': 'Vector (Richards-Wolf) with the annulus sin(theta) >= '
                                                             'eps sin(alpha) (sine condition), beams polarized along '
                                                             'y. Annular DOF (2CE, theta = 0), vector / scalar: 155 '
                                                             '/ 179 um at NA 0.5 (scalar 15% longer), 65 / 91 um at '
                                                             '0.7 (39%), 25 / 55 um at 0.9 (125%). Water: 221 / 238 '
                                                             'at 0.5, 54 / 73 at 0.9, 18 / 41 at 1.2. Annular over '
                                                             'circular DOF: 47x at NA 0.5, 42x at 0.7, 31x at 0.9 '
                                                             '(paraxial: 1/(1 - eps^2) = 50). Spot across the axis: '
                                                             '0.70x the circular one at all NA. theta = pi/2: set by '
                                                             'the narrow transverse spot of the other beam, so '
                                                             'scalar and vector agree within 2%.'},
 'Annular central spots against NA: the comparisons of p. 31': {'n': 56,
                                                                'items': ['As NA increases the annular 2CE spot at θ '
                                                                          '= 0 stays 0.67 of that at θ = π/2, and '
                                                                          'the annular 2PE spot loses its lead over '
                                                                          '2CE: 53% narrower at NA 0.5, 34% at NA '
                                                                          '0.7 in air.',
                                                                          'Star: value stated on p. 31; cross: the '
                                                                          'same ratio on the published curves. 0.82 '
                                                                          'stated, 0.67 on Fig. 6b; 35% stated, 34% '
                                                                          'on Fig. 6a, which plots the excitation '
                                                                          '(Eq. (6) gives 53%).'],
                                                                'figs': ['08_two_color/cambaliza2000/high_na/pupils/annular_quoted_x.png'],
                                                                'eqs': [],
                                                                'main': 'Annular comparisons across the axis.',
                                                                'notes': 'Stars: values quoted at NA 0.5. Solid: '
                                                                         'vector; dashed: paraxial scalar; filled: '
                                                                         'air; open: water. The replication gives '
                                                                         '0.67 at NA 0.5 for the Fig. 6b ratio.'},
 'Annular depth of focus against NA: the comparisons of p. 32': {'n': 57,
                                                                 'items': ['As NA increases the annular 2CE DOF at θ '
                                                                           '= π/2 stays about 30% shorter than the '
                                                                           'circular one, and its lead over the 2PE '
                                                                           'DOF shrinks: 85% longer at NA 0.5.',
                                                                           'Star: value stated on p. 32; cross: the '
                                                                           'same ratio on the published curves. 40% '
                                                                           'stated, 30% on the curves; 20% stated, '
                                                                           '85%.'],
                                                                 'figs': ['08_two_color/cambaliza2000/high_na/pupils/annular_quoted_z.png'],
                                                                 'eqs': [],
                                                                 'main': 'Annular comparisons along the axis.',
                                                                 'notes': 'Stars: values quoted at NA 0.5. Solid: '
                                                                          'vector; dashed: paraxial scalar; filled: '
                                                                          'air; open: water.'},
 '2CE response to the wavelength gap Δλ against NA, θ = π/2': {'n': 58,
                                                               'items': ['As NA increases the effect of Δλ stays the '
                                                                         'same: from 10 to 94 nm the central spot '
                                                                         'grows by about 6% and the DOF shrinks by '
                                                                         'about 5%, from NA 0.3 to 0.9, in air and '
                                                                         'water.',
                                                                         'At θ = π/2 the central spot follows λ1 and '
                                                                         'the DOF follows λ2 at all NA, so the '
                                                                         'trade-off of p. 30 holds.'],
                                                               'figs': ['08_two_color/cambaliza2000/high_na/pupils/dlambda_vs_na.png'],
                                                               'eqs': [],
                                                               'main': 'The wavelength gap changes the 2CE response '
                                                                       'by the same fraction at all NA.',
                                                               'notes': '2CE, theta = pi/2, circular pupils; '
                                                                        '1/lambda1 + 1/lambda2 = 1/350 nm. From 10 '
                                                                        'to 94 nm the FWHM grows by 6.3% at NA 0.3, '
                                                                        '6.1% at 0.5, 5.7% at 0.7 (air), 5.8% at 0.9 '
                                                                        '(water); the DOF shrinks by 5.5% to 5.2%. '
                                                                        'Vector (y), unpolarized and scalar within '
                                                                        '0.3% of each other in this relative '
                                                                        'change.'}}
