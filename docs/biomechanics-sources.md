# Biomechanics Reference Sources

Biomechanical and injury-biomechanics references used across the project - the kinematics plausibility scoring in `src/henryk_simulations/corridor/references.py` and the back-impact dynamics model in `src/henryk_simulations/corridor/impact.py`. Citations are grouped by topic. Population-distribution values are means and between-subject standard deviations for adult males (recreationally active unless noted); injury-biomechanics values are tolerance corridors from cadaver and sled testing.

## Push and grip forces

- **Daams, B.J. (1994).** *Human force exertion in user-product interaction.* Delft University Press. Tabulates standing two-arm and single-arm push at various stances. Reported mean two-arm push force for an unloaded standing subject 800 N with between-subject SD 200 N; single-arm dominant 400 N, SD 100 N.
- **Mital, A. & Kumar, S. (1995).** *Human muscle strength definitions, measurement, and usage.* International Journal of Industrial Ergonomics, 16(4), 237-256. Confirms the Daams numbers and adds a fatigue qualification (sustained 30 s force ~60% of peak).
- **Chaffin, D.B. & Andersson, G.B.J. (1991).** *Occupational Biomechanics* (2nd ed.). Wiley. Reference work for ergonomic force budgets used in occupational health.

## Sprint and standing acceleration

- **Mero, A., Komi, P.V. & Gregor, R.J. (1992).** *Biomechanics of sprint running.* Sports Medicine, 13(6), 376-392. Reports peak horizontal centre-of-mass acceleration of 3.0 m/s^2 (recreational male) and 5.0 m/s^2 (elite sprinter) within the first 0.2 s of a standing start, with between-subject SD ~0.8 and 0.5 m/s^2 respectively.
- **di Prampero, P.E. et al. (2005).** *Sprint running: a new energetic approach.* J. Exp. Biol., 208, 2809-2816. Cross-checks Mero with energy-based estimates.

## Throwing kinematics

- **Cross, R. (2004).** *Physics of overarm throwing.* American Journal of Physics, 72(3), 305-312. Release-velocity and KE budgets for hand-thrown objects ranging 0.15-5 kg; the 5 kg figure (8 m/s release, SD 2.5; 160 J KE, SD 80) is interpolated from his population sample.
- **Atwater, A.E. (1979).** *Biomechanics of overarm throwing movements and of throwing injuries.* Exercise and Sport Sciences Reviews, 7, 43-86. Foundational reference for overarm throw kinematics.
- **van den Tillaar, R. & Ettema, G. (2004).** *Effect of body size and gender in overarm throwing performance.* Eur. J. Appl. Physiol., 91(4), 413-418. Provides between-subject variance estimates.

## Standing pivot and yaw kinematics

- **Hodgson, A.J., Lewis, J. & Drury, C.G. (2008).** *A turning-while-walking task with cognitive load.* Applied Ergonomics, 39(3), 386-396. Peak yaw angular velocity during voluntary 180 deg standing pivot 3.5 rad/s, SD 1.0 rad/s.
- **Crenshaw, S.J. et al. (2006).** *The contributions of the foot to the body's rotation during turning.* J. Biomech., 39(1), 89-96. Cross-reference for foot-pivot mechanics during yaw rotation.

## Body segment inertia parameters

- **Plagenhoef, S., Evans, F.G. & Abdelnour, T. (1983).** *Anatomical data for analyzing human motion.* Research Quarterly for Exercise and Sport, 54(2), 169-178. Standard tabulation of body-segment masses and moments of inertia. Whole-body yaw inertia about CoM for a 75 kg standing male 1.5 kg m^2, SD 0.4.
- **de Leva, P. (1996).** *Adjustments to Zatsiorsky-Seluyanov's segment inertia parameters.* Journal of Biomechanics, 29(9), 1223-1230. Adjusted male segment mass fractions, centres of mass and radii of gyration; used to build the body-segment model and the effective impacting mass for the back-impact analysis.

## Reaching kinematics

- **Marteniuk, R.G., MacKenzie, C.L. & Leavitt, J.L. (1990).** *Functional relationships between grasp and transport in prehension movements.* Hum. Movement Sci., 9(2), 149-176. Hand peak velocity during goal-directed reach 2.5 m/s, SD 0.8 m/s, for adult subjects extending the arm 0.4-0.7 m.

## Rate of force development and movement jerk

- **Aagaard, P., Simonsen, E.B., Andersen, J.L., Magnusson, P. & Dyhre-Poulsen, P. (2002).** *Increased rate of force development and neural drive of human skeletal muscle following resistance training.* Journal of Applied Physiology, 93(4), 1318-1326. Contractile rate of force development of the knee extensors measured over 30, 50, 100 and 200 ms windows from contraction onset, values roughly 1,100-2,200 N m s^-1, rising 25-33% after 14 weeks of heavy-resistance training. Establishes that explosive voluntary force is developed progressively over tens to hundreds of milliseconds, not instantaneously.
- **Maffiuletti, N.A., Aagaard, P., Blazevich, A.J., Folland, J., Tillin, N. & Duchateau, J. (2016).** *Rate of force development: physiological and methodological considerations.* European Journal of Applied Physiology, 116(6), 1091-1116. Review. Early-phase rate of force development (first 50-75 ms) is governed by motor-unit recruitment and discharge rate, force in the first 40 ms of a rapid contraction is about 60% below the tetanic value, and athletic explosive tasks have contraction times of 50-250 ms. Used here to floor the start-ramp "give" - the centre-of-mass acceleration cannot ramp from zero to peak faster than the neuromuscular system develops propulsive force. Peak jerk of the centre of mass equals the net force rate divided by body mass, so the rate-of-force-development limit also bounds jerk.

## Thoracic impact response

The lumped-parameter modelling behind the 5-DOF posterior-thorax chain in the back-impact analysis - the mass-spring-damper form, the force-deflection corridors, and the tensed-versus-relaxed stiffness scaling.

- **Lobdell, T.E., Kroell, C.K., Schneider, D.C., Hering, W.E. & Nahum, A.M. (1973).** *Impact response of the human thorax.* In Human Impact Response: Measurement and Simulation, Plenum Press. The lumped mass-spring-damper model of the thorax under blunt impact - the structural form of the 5-DOF posterior-thorax chain.
- **Kroell, C.K., Schneider, D.C. & Nahum, A.M. (1971).** *Impact tolerance and response of the human thorax.* 15th Stapp Car Crash Conference, SAE 710851. Cadaver chest force-deflection corridors and the 5-7 cm chest-compression range over which rib fracture progresses.
- **Stalnaker, R.L., McElhaney, J.H., Roberts, V.L. & Trollope, M.L. (1973).** *Human torso response to blunt trauma.* In Human Impact Response: Measurement and Simulation, Plenum Press. Muscle tension raises thoracic stiffness by roughly 2.2-4.4x the relaxed baseline - the tensed-posterior scaling behind the chain interface stiffnesses.

## Rib and thoracic injury thresholds

The fracture corridors the computed impact peaks are scored against - rib fracture force, the AIS deflection criterion, and the posterior-thorax tolerance band.

- **Viano, D.C. (1989).** *Biomechanical responses and injuries in blunt lateral impact.* 33rd Stapp Car Crash Conference, SAE 892432. Thoracic blunt-impact injury criteria on the AIS scale; roughly 1.6 kN per loaded rib at AIS 2+.
- **Cavanaugh, J.M. et al. (1990).** *Biomechanical response and injury tolerance of the thorax in twelve sled side impacts.* 34th Stapp Car Crash Conference, SAE 902307. AIS 3+ thoracic injury at about 25 mm chest deflection; relaxed anterior chest stiffness baseline ~50 N/mm.
- **Kemper, A.R. et al. (2014).** *Rear-torso impact biomechanics: dynamic response and injury tolerance of the posterior thorax.* Journal of Biomechanics, article PII S0021929015003772. Posterior-thorax tolerance band 6.9-10.5 kN, producing rib fractures and costo-vertebral / costo-transverse joint injuries. The article PII indicates 2015; the project cites it as 2014, a discrepancy left for a project-wide citation reconciliation.

## Sex and age effects on injury tolerance

The demographic scaling in `src/henryk_simulations/corridor/injuries.py` - the `tolerance_factor` that shifts each injury onset for a given sex and age. The literature is consistent on two points: age is the dominant factor and acts on bone, and the sex difference is structural (rib geometry) rather than material.

- **The effect of age on the structural properties of human ribs (2014).** *Journal of the Mechanical Behavior of Biomedical Materials*, article PII S1751616114002860. https://www.sciencedirect.com/science/article/abs/pii/S1751616114002860 . Ultimate tensile strength, tensile strain, elastic modulus, fracture toughness and energy-to-fracture of rib cortical bone all decrease across adult age; force at fracture peaks in the young-adult years (25-40).
- **Rib cortical bone fracture risk as a function of age and rib strain (2021).** *Frontiers in Bioengineering and Biotechnology*, PMC8181138. https://pmc.ncbi.nlm.nih.gov/articles/PMC8181138/ . Rib cortical bone loses about 12.2% of its failure strain per decade of ageing - far steeper than the 5.1% earlier models assumed. At a 50% fracture-risk threshold a 30-year-old tolerates 69 km/h frontal delta-v against 48 km/h for a 70-year-old. Sex was not a significant covariate of failure strain (p = 0.335): the bone material itself is not sex-different.
- **Effects of sex, age and loading rate on rib cortical bone tensile properties (2020).** *Journal of the Mechanical Behavior of Biomedical Materials*, article PII S1751616119305880. https://www.sciencedirect.com/science/article/abs/pii/S1751616119305880 . Confirms the age decline in rib cortical bone material properties; sex effects on the material are minor.
- **Holcombe, S.A. et al. (2022).** *Rib cortical bone thickness variation in adults by age and sex.* *Journal of Anatomy*, PMC9644965. https://pmc.ncbi.nlm.nih.gov/articles/PMC9644965/ . Female ribs thin faster than male - 0.035-0.043 mm/decade against 0.011-0.032 mm/decade - so a female ribcage fractures at a lower force than a male one through geometry (thinner, smaller cross-section), not weaker bone material.
- **Kent, R. et al. (2005).** *Chest deflection tolerance to blunt anterior loading is sensitive to age but not load distribution.* *Forensic Science International*, article PII S0379073804003524. https://www.sciencedirect.com/science/article/abs/pii/S0379073804003524 . Whole-chest deflection tolerance falls with age.
- **Forman, J. et al. (2012).** *Predicting rib fracture risk with whole-body finite element models.* The rib injury risk function is strongly dependent on age and not on the loading condition.
- **Increased thorax injury in aged females (2024).** *Frontiers in Public Health*, article 10.3389/fpubh.2024.1336518. https://www.frontiersin.org/journals/public-health/articles/10.3389/fpubh.2024.1336518/full . Aged females show a large rise in severe thorax injury in side impact - the age-by-sex interaction, driven by age-specific geometry and material properties.
- **Vertebral bone, age and bone mineral density.** *New Osteoporotic / Vertebral Compression Fractures*, Endotext (NBK279035), https://www.ncbi.nlm.nih.gov/books/NBK279035/ ; *Vertebral Compression Fractures*, StatPearls (NBK448171). Vertebral bone mineral density declines steadily with age and faster after the menopause; fracture risk roughly doubles for every standard deviation of BMD below the young-adult mean.

These sources set the per-tissue `tolerance_factor` slopes in `injuries.py`: a steep age slope and a moderate, geometric sex gap for bone; smaller slopes for cartilage and joint/ligament; near-flat for muscle, soft tissue, viscera and neural/vascular tissue.

## Notes on use

Distributions in `references.py` are modelled as normal with the reported population means and SDs. This is appropriate for healthy adult subjects with motor-skill quantities that are approximately bell-shaped; the CIs computed at 95% therefore reflect between-subject biological variation, not measurement uncertainty. Where the original literature reports asymmetric or bounded distributions (e.g. yaw inertia, which cannot be negative), the normal approximation is adequate over the relevant range but should be replaced with a log-normal if extreme tail probabilities matter for a future analysis.
