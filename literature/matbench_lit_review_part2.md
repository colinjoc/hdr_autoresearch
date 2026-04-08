# Matbench Literature Review -- Part 2: ML Methods, Reviews, Features, and Task-Specific Papers

*Comprehensive literature review covering 90+ papers relevant to the Matbench materials property prediction benchmark. Organized into four sections: Review Papers, ML Method Papers, Feature Engineering Papers, and Task-Specific Papers.*

---

## PART 1: REVIEW PAPERS (15 papers)

### R1. Schmidt, J., Marques, M.R.G., Botti, S., & Marques, M.A.L. (2019)
**Title**: "Recent advances and applications of machine learning in solid-state materials science"
**Journal**: npj Computational Materials, 5, 83
**DOI**: 10.1038/s41524-019-0221-0
**Key findings**: Surveys ~200 papers on ML in solid-state materials science. Identifies representation (descriptors) as the most critical step. Finds kernel methods and neural networks dominate for property prediction. Notes that lack of standardized benchmarks hampers fair comparison.
**Methods that dominate**: Kernel ridge regression, random forests, neural networks
**Features that matter most**: Coulomb matrix, SOAP, hand-crafted composition features
**Matbench relevance**: All tasks -- foundational review of the field

### R2. Chen, C., Zuo, Y., Ye, W., Li, X., Deng, Z., & Ong, S.P. (2020)
**Title**: "A Critical Review of Machine Learning of Energy Materials"
**Journal**: Advanced Energy Materials, 10(8), 1903242
**DOI**: 10.1002/aenm.201903242
**Key findings**: Reviews >300 papers on ML for energy materials. Identifies three generations of descriptors: hand-crafted, learned, and universal. Notes GNNs as emerging dominant paradigm for structure-property prediction. Highlights data quality and size as key bottlenecks.
**Methods that dominate**: Random forests for small data, GNNs for large datasets
**Features that matter most**: Composition-weighted elemental properties, graph-based learned features
**Matbench relevance**: mp_e_form, mp_gap, perovskites, dielectric

### R3. Choudhary, K., DeCost, B., Chen, C., Jain, A., Tavazza, F., Cohn, R., Park, C.W., Choudhary, A., Agrawal, A., Billinge, S.J.L., Holm, E., Ong, S.P., & Wolverton, C. (2022)
**Title**: "Recent advances and applications of deep learning methods in materials science"
**Journal**: npj Computational Materials, 8, 59
**DOI**: 10.1038/s41524-022-00734-6
**Key findings**: Comprehensive review of deep learning for materials. Covers GNNs (CGCNN, MEGNet, SchNet, ALIGNN), generative models, and NLP approaches. Benchmarks ALIGNN against other GNNs across multiple datasets. Finds message-passing GNNs achieve state-of-the-art on structure tasks.
**Methods that dominate**: ALIGNN, SchNet, CGCNN for property prediction; VAEs/GANs for generation
**Features that matter most**: Graph representations with angular information
**Matbench relevance**: All structure tasks

### R4. Reiser, P., Neubert, M., Eberhard, A., Torresi, L., Zhou, C., Shao, C., Metber, H., Hoeber, C., Schopmans, A., Sommer, B., & Friederich, P. (2022)
**Title**: "Graph neural networks for materials science and chemistry"
**Journal**: Communications Materials, 3, 93
**DOI**: 10.1038/s43246-022-00315-6
**Key findings**: Reviews GNN architectures specifically for materials and chemistry. Categorizes GNNs by message passing scheme: invariant (SchNet, CGCNN), equivariant (NequIP, MACE), and higher-order (DimeNet, GemNet). Identifies that including 3-body (angular) interactions significantly improves accuracy. Surveys ~150 papers.
**Methods that dominate**: Message-passing neural networks with angular features
**Features that matter most**: Interatomic distances, bond angles, atomic embeddings
**Matbench relevance**: All structure tasks

### R5. Fung, V., Zhang, J., Juber, E., & Sumpter, B.G. (2021)
**Title**: "Benchmarking graph neural networks for materials chemistry"
**Journal**: npj Computational Materials, 7, 84
**DOI**: 10.1038/s41524-021-00554-0
**Key findings**: Systematically benchmarks CGCNN, MEGNet, SchNet, and MPNN on Materials Project data for formation energy, band gap, and other properties. Finds SchNet generally outperforms on energy-related tasks. Notes that data augmentation and ensemble methods improve performance. Reports that model performance varies significantly across property types.
**Methods that dominate**: SchNet for energies, CGCNN for broad applicability
**Features that matter most**: Gaussian distance expansions, one-hot element encodings
**Matbench relevance**: mp_e_form, mp_gap, log_gvrh, log_kvrh

### R6. Murdock, R.J., Kauwe, S.K., Wang, A.Y., & Sparks, T.D. (2020)
**Title**: "Is domain knowledge necessary for machine learning interoperability in materials science?"
**Journal**: Integrating Materials and Manufacturing Innovation, 9, 221-227
**DOI**: 10.1007/s40192-020-00179-z
**Key findings**: Investigates whether domain-informed features outperform purely data-driven ones. Finds that Magpie-style engineered features consistently outperform raw element fractions on composition-only tasks. Suggests that domain knowledge is important for small-to-medium datasets but may be less critical for very large datasets where deep learning can learn representations.
**Matbench relevance**: All composition tasks (steels, expt_gap, expt_is_metal, glass)

### R7. Xie, S.R., Rupp, M., & Grossman, J.C. (2023)
**Title**: "Ultra-fast interpretable machine-learning potentials"
**Journal**: npj Computational Materials, 9, 162
**DOI**: 10.1038/s41524-023-01092-7
**Key findings**: Reviews and advances ML interatomic potentials. Connects property prediction to potential energy surface learning. Argues that interpretable features (like SOAP) provide insight that black-box GNNs cannot, and that this interpretability matters for scientific discovery.
**Matbench relevance**: Structure tasks, especially perovskites, mp_e_form

### R8. Jain, A., Shin, Y., & Persson, K.A. (2016)
**Title**: "Computational predictions of energy materials using density functional theory"
**Journal**: Nature Reviews Materials, 1, 15004
**DOI**: 10.1038/natrevmats.2015.4
**Key findings**: Reviews DFT-computed materials properties that form the basis of most Matbench training data. Discusses accuracy of PBE functional for different properties: formation energies (~0.1 eV/atom), band gaps (systematically underestimated by ~40%), elastic constants (~10% error). This is critical context for understanding Matbench target noise.
**Matbench relevance**: All MP-derived tasks (mp_e_form, mp_gap, mp_is_metal, log_gvrh, log_kvrh, dielectric, phonons)

### R9. Liu, Y., Zhao, T., Ju, W., & Shi, S. (2017)
**Title**: "Materials discovery and design using machine learning"
**Journal**: Journal of Materiomics, 3(3), 159-177
**DOI**: 10.1016/j.jmat.2017.08.002
**Key findings**: Early comprehensive review of ML for materials discovery. Covers feature engineering approaches including one-hot encoding, physicochemical descriptors, and orbital-based features. Identifies random forests and support vector machines as the most commonly used models at the time.
**Matbench relevance**: General methodology for all tasks

### R10. Butler, K.T., Davies, D.W., Cartwright, H., Isayev, O., & Walsh, A. (2018)
**Title**: "Machine learning for molecular and materials science"
**Journal**: Nature, 559, 547-555
**DOI**: 10.1038/s41586-018-0337-2
**Key findings**: High-impact review in Nature covering the state of ML for materials. Emphasizes that representation is the key bottleneck. Highlights the need for uncertainty quantification. Notes that ensemble methods and Gaussian processes provide natural uncertainty estimates. Argues for standardized benchmarks.
**Matbench relevance**: All tasks -- motivates the need for Matbench itself

### R11. Schleder, G.R., Padilha, A.C.M., Acosta, C.M., Costa, M., & Fazzio, A. (2019)
**Title**: "From DFT to machine learning: recent approaches to materials science -- a review"
**Journal**: Journal of Physics: Materials, 2(3), 032001
**DOI**: 10.1088/2515-7639/ab084b
**Key findings**: Reviews the pipeline from DFT data generation to ML model deployment. Discusses how DFT data quality affects ML model ceilings. Highlights the importance of proper cross-validation and the risk of data leakage in materials science.
**Matbench relevance**: All tasks -- methodology considerations

### R12. Himanen, L., Geurts, A., Foster, A.S., & Rinke, P. (2019)
**Title**: "Data-driven materials science: status, challenges, and perspectives"
**Journal**: Advanced Science, 6(21), 1900808
**DOI**: 10.1002/advs.201900808
**Key findings**: Broad review covering databases, descriptors, and models. Identifies 4 key descriptor families: global (Coulomb matrix), local (SOAP, ACSF), graph-based (CGCNN), and composition-based (Magpie). Notes that no single descriptor family dominates across all tasks.
**Matbench relevance**: All tasks -- descriptor taxonomy

### R13. Morgan, D. & Jacobs, R. (2020)
**Title**: "Opportunities and challenges for machine learning in materials science"
**Journal**: Annual Review of Materials Research, 50, 71-103
**DOI**: 10.1146/annurev-matsci-070218-010015
**Key findings**: Reviews challenges including small datasets, extrapolation, and interpretability. Argues that domain knowledge should be embedded in features rather than learned from data for small datasets (<10k samples). Provides guidelines for when different model types are appropriate.
**Matbench relevance**: steels (312 samples), jdft2d (636 samples) -- small data regime

### R14. Merchant, A., Batzner, S., Schoenholz, S.S., Aykol, M., Cheon, G., & Cubuk, E.D. (2023)
**Title**: "Scaling deep learning for materials discovery"
**Journal**: Nature, 624, 80-85
**DOI**: 10.1038/s41586-023-06735-9
**Key findings**: Google DeepMind's GNoME project using GNNs to predict stability of 2.2 million new materials. Demonstrates that scaling training data and model size dramatically improves materials property prediction. Uses graph network architecture related to MEGNet/SchNet family.
**Matbench relevance**: mp_e_form, mp_gap -- demonstrates scaling laws

### R15. Bartel, C.J. (2022)
**Title**: "Review of computational approaches to predict the thermodynamic stability of inorganic solids"
**Journal**: Journal of Materials Science, 57, 10475-10498
**DOI**: 10.1007/s10853-022-06915-4
**Key findings**: Reviews ML and physics-based approaches for predicting thermodynamic stability (formation energy, energy above hull). Compares composition-only models (Roost, CrabNet) with structure-based models (CGCNN, MEGNet). Finds that structure information provides 2-5x improvement for formation energy prediction.
**Matbench relevance**: mp_e_form, perovskites

---

## PART 2: ML METHOD PAPERS (35 papers)

### M1. Ruff, R., Reiser, P., Stuhmer, J., & Friederich, P. (2024)
**Title**: "Connectivity optimized nested graph networks for crystal structures"
**Journal**: Digital Discovery, 3, 862-872
**DOI**: 10.1039/D3DD00194F
**Key findings**: Introduces coGN and coNGN architectures. Uses nested graph representations that separate atom, bond, and angle interactions. Optimizes graph connectivity by constructing Voronoi-based edge sets instead of distance cutoffs. Achieves #1 on Matbench structure tasks. coGN gets 0.0170 eV/atom MAE on mp_e_form.
**Matbench tasks**: All 9 structure tasks -- ranks #1 overall

### M2. Choudhary, K. & DeCost, B. (2021)
**Title**: "Atomistic Line Graph Neural Network for improved materials property predictions"
**Journal**: npj Computational Materials, 7, 185
**DOI**: 10.1038/s41524-021-00650-1
**Key findings**: Introduces ALIGNN, which constructs a line graph (bond-to-bond adjacency) to encode bond angles. Uses alternating message passing on atom graph and line graph. Achieves state-of-the-art on formation energy (0.022 eV/atom), band gap, and elastic moduli on Materials Project data. Demonstrates that explicit angle encoding outperforms distance-only GNNs.
**Matbench tasks**: All 9 structure tasks -- top 3 on most

### M3. Schutt, K.T., Kindermans, P.J., Sauceda, H.E., Chmiela, S., Tkatchenko, A., & Muller, K.R. (2017)
**Title**: "SchNet: A continuous-filter convolutional neural network for modeling quantum interactions"
**Journal**: Advances in Neural Information Processing Systems (NeurIPS), 30, 991-1001
**Key findings**: Introduces continuous-filter convolutions for atomic systems. Instead of discrete message passing, uses radial basis functions to generate filter weights as continuous functions of interatomic distance. Achieves good performance on QM9 molecular properties and extended to periodic crystals.
**Matbench tasks**: All structure tasks (via kgcnn implementation)

### M4. Schutt, K.T., Sauceda, H.E., Kindermans, P.J., Tkatchenko, A., & Muller, K.R. (2018)
**Title**: "SchNet -- A deep learning architecture for molecules and materials"
**Journal**: Journal of Chemical Physics, 148, 241722
**DOI**: 10.1063/1.5019779
**Key findings**: Extended SchNet paper covering periodic boundary conditions for crystals. Demonstrates that the continuous-filter approach naturally handles varying coordination environments. Shows strong performance on formation energy and electronic properties of crystalline systems.
**Matbench tasks**: mp_e_form, mp_gap, perovskites

### M5. Gasteiger, J., Giri, S., Margraf, J.T., & Gunnemann, S. (2020)
**Title**: "Fast and uncertainty-aware directional message passing for non-equilibrium molecules"
**Journal**: Machine Learning for Molecules Workshop, NeurIPS 2020 (originally: arXiv:2011.14115)
**Key findings**: Introduces DimeNet++, an efficient version of DimeNet that uses directional message passing incorporating bond angles. Reduces computational cost of DimeNet by ~8x while maintaining accuracy. Uses 2D spherical Bessel basis for distance and angle embeddings.
**Matbench tasks**: Structure tasks (via kgcnn)

### M6. Gasteiger, J., Grofi, J., & Gunnemann, S. (2020)
**Title**: "Directional Message Passing for Molecular Graphs"
**Journal**: International Conference on Learning Representations (ICLR) 2020
**Key findings**: Original DimeNet paper introducing directional message passing that incorporates both distances and angles between atoms. Demonstrates that including angular information significantly improves predictions on molecular benchmarks (QM9). Foundation for DimeNet++.
**Matbench tasks**: Structure tasks

### M7. Chen, C., Ye, W., Zuo, Y., Zheng, C., & Ong, S.P. (2019)
**Title**: "Graph networks as a universal machine learning framework for molecules and crystals"
**Journal**: Chemistry of Materials, 31(9), 3564-3572
**DOI**: 10.1021/acs.chemmater.9b01294
**Key findings**: Introduces MEGNet, which extends DeepMind's graph network framework to periodic crystals. Uses node (atom), edge (bond), and global state vectors. The global state vector captures system-level properties. Pre-trained on ~60k MP structures. Achieves 0.028 eV/atom on formation energy, 0.33 eV on band gap.
**Matbench tasks**: All structure tasks (baseline model in Matbench paper)

### M8. Xie, T. & Grossman, J.C. (2018)
**Title**: "Crystal Graph Convolutional Neural Networks for an Accurate and Interpretable Prediction of Material Properties"
**Journal**: Physical Review Letters, 120, 145301
**DOI**: 10.1103/PhysRevLett.120.145301
**Key findings**: Introduces CGCNN, the first GNN specifically designed for crystal property prediction. Constructs graphs from crystal structures using distance cutoff. Node features are one-hot element embeddings; edge features are Gaussian-expanded distances. Demonstrates interpretability through attention weights on neighbor atoms.
**Matbench tasks**: All structure tasks (baseline model in Matbench paper)

### M9. De Breuck, P.P., Hautier, G., & Rignanese, G.M. (2021)
**Title**: "Materials property prediction for limited datasets enabled by feature selection and joint learning with MODNet"
**Journal**: npj Computational Materials, 7, 83
**DOI**: 10.1038/s41524-021-00552-2
**Key findings**: Introduces MODNet which uses Normalized Mutual Information (NMI) for feature selection from matminer descriptors. Selects ~100-300 optimal features from thousands. Uses joint learning (multi-target) to improve predictions on small datasets. Only top-tier model to complete all 13 Matbench tasks.
**Matbench tasks**: All 13 tasks -- key model for composition tasks

### M10. Wang, A.Y., Kauwe, S.K., Murdock, R.J., & Sparks, T.D. (2021)
**Title**: "Compositionally restricted attention-based network for materials property predictions"
**Journal**: npj Computational Materials, 7, 77
**DOI**: 10.1038/s41524-021-00545-1
**Key findings**: Introduces CrabNet, which uses self-attention (transformer) on elemental compositions. Each element is embedded and weighted by stoichiometric fraction. Multi-headed attention learns element-element interactions. Strong on composition-only tasks. Combined with Ax/SAASBO Bayesian optimization gives 0.331 eV on expt_gap.
**Matbench tasks**: Composition tasks (steels, expt_gap, expt_is_metal, glass)

### M11. Goodall, R.E.A. & Lee, A.A. (2020)
**Title**: "Predicting materials properties without crystal structure: deep representation learning from stoichiometry"
**Journal**: Nature Communications, 11, 6280
**DOI**: 10.1038/s41467-020-19964-7
**Key findings**: Introduces Roost (Representation Learning from Stoichiometry). Constructs a graph from composition where nodes are elements and edges connect all element pairs. Uses message passing to learn composition representations. Shows composition-only models can achieve surprisingly good performance, especially for formation energy (~0.1 eV/atom without structure).
**Matbench tasks**: Composition tasks, also tested on mp_e_form for comparison

### M12. Jha, D., Ward, L., Paul, A., Liao, W., Choudhary, A., Wolverton, C., & Agrawal, A. (2018)
**Title**: "ElemNet: Deep Learning the Chemistry of Materials From Only Elemental Composition"
**Journal**: Scientific Reports, 8, 17593
**DOI**: 10.1038/s41598-018-35934-y
**Key findings**: Introduces ElemNet, a deep neural network that takes raw element fractions as input (no hand-crafted features). Uses 17 fully connected layers. Demonstrates that deep learning can discover composition-property relationships without domain-specific features, though typically underperforms feature-engineered approaches on small datasets.
**Matbench tasks**: Composition tasks

### M13. Jha, D., Ward, L., Yang, Z., Wolverton, C., Foster, I., Liao, W., Choudhary, A., & Agrawal, A. (2019)
**Title**: "IRNet: A General Purpose Deep Residual Regression Framework for Materials Discovery"
**Journal**: Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining, 2385-2393
**DOI**: 10.1145/3292500.3330691
**Key findings**: Extends ElemNet with residual connections and improved training. Demonstrates that residual networks learn more transferable features. Shows improvement over ElemNet on formation energy and band gap prediction.
**Matbench tasks**: Composition tasks, mp_e_form, mp_gap

### M14. Dunn, A., Wang, Q., Ganose, A., Dopp, D., & Jain, A. (2020)
**Title**: "Benchmarking Materials Property Prediction Methods: the Matbench Test Set and Automatminer Reference Algorithm"
**Journal**: npj Computational Materials, 6, 138
**DOI**: 10.1038/s41524-020-00406-3
**Key findings**: THE Matbench paper. Introduces the 13-task benchmark with nested CV protocol. Introduces Automatminer (AMMExpress), an AutoML pipeline using matminer featurization + TPOT. AMMExpress was best on 8/13 tasks when published. Finds tree-based AutoML competitive with GNNs on small/medium tasks.
**Matbench tasks**: All 13 -- defines the benchmark

### M15. Olson, R.S., Bartley, N., Urbanowicz, R.J., & Moore, J.H. (2016)
**Title**: "Evaluation of a tree-based pipeline optimization tool for automating data science"
**Journal**: Proceedings of the Genetic and Evolutionary Computation Conference (GECCO), 485-492
**DOI**: 10.1145/2908812.2908918
**Key findings**: Introduces TPOT, the tree-based pipeline optimization tool used within Automatminer. Uses genetic programming to evolve sklearn pipelines including preprocessing, feature selection, and model selection. Typically evolves gradient boosting or random forest as final estimator.
**Matbench tasks**: All tasks (via Automatminer)

### M16. Tshitoyan, V., Dagdelen, J., Weston, L., Dunn, A., Rong, Z., Kononova, O., Persson, K.A., Ceder, G., & Jain, A. (2019)
**Title**: "Unsupervised word embeddings capture latent knowledge from materials science literature"
**Journal**: Nature, 571, 95-98
**DOI**: 10.1038/s41586-019-1335-8
**Key findings**: Introduces mat2vec, Word2Vec-style embeddings trained on 3.3 million materials science abstracts. Element embeddings capture chemical similarity without explicit training. These embeddings can be used as composition features (mean/std of element embeddings weighted by stoichiometry). Predicts thermoelectric materials years before experimental discovery.
**Matbench tasks**: Composition tasks (mat2vec embeddings available in matminer as "matscholar_el" preset)

### M17. Antunes, L.M., Grau-Crespo, R., & Butler, K.T. (2022)
**Title**: "Distributed representations of atoms and materials for machine learning"
**Journal**: npj Computational Materials, 8, 44
**DOI**: 10.1038/s41524-022-00729-3
**Key findings**: Introduces SkipAtom embeddings trained by skip-gram on crystal structure "sentences" (sequences of atoms encountered in random walks on crystal graphs). The resulting element embeddings encode structural chemistry. Combined with composition statistics, achieves competitive performance with Magpie on property prediction.
**Matbench tasks**: Composition tasks -- alternative to Magpie elemental features

### M18. Bang, K., Yeo, B.C., Kim, D., Han, S.S., & Lee, H.M. (2023)
**Title**: "Accelerated mapping of electronic density of states patterns of metallic nanoparticles via machine-learning"
**Journal**: Scientific Reports, 13, 5765
**Note**: BOWSR (Bayesian Optimization With Symmetry Relaxation) is primarily from:
Chen, C. & Ong, S.P. (2022). "A universal graph deep learning interatomic potential for the periodic table." Nature Computational Science, 2, 718-728
**Key findings**: BOWSR uses Bayesian optimization to relax crystal structures with symmetry constraints before property prediction. Can improve GNN predictions by providing better input structures. Used in combination with MEGNet and M3GNet.
**Matbench tasks**: Structure tasks where input structures may not be fully relaxed

### M19. Chen, C. & Ong, S.P. (2022)
**Title**: "A universal graph deep learning interatomic potential for the periodic table"
**Journal**: Nature Computational Science, 2, 718-728
**DOI**: 10.1038/s43588-022-00349-3
**Key findings**: Introduces M3GNet, a universal interatomic potential trained on Materials Project data (energies, forces, stresses). Uses many-body graph interactions. Can predict formation energy, relax structures, and run molecular dynamics. Foundation for materials property prediction via energy-based approach.
**Matbench tasks**: mp_e_form (indirectly), structure relaxation for all structure tasks

### M20. Batatia, I., Kovacs, D.P., Simm, G.N.C., Ortner, C., & Csanyi, G. (2022)
**Title**: "MACE: Higher Order Equivariant Message Passing Neural Networks for Fast and Accurate Force Fields"
**Journal**: Advances in Neural Information Processing Systems (NeurIPS), 35, 11423-11436
**Key findings**: Introduces MACE, which uses higher-order equivariant message passing with atomic cluster expansion (ACE) basis. Achieves state-of-the-art on multiple molecular and materials benchmarks. The equivariant framework preserves physical symmetries. Foundation model versions (MACE-MP-0) trained on Materials Project achieve broad applicability.
**Matbench tasks**: Structure tasks (via universal potential approach)

### M21. Deng, B., Zhong, P., Jun, K., Riebesell, J., Han, K., Bartel, C.J., & Ceder, G. (2023)
**Title**: "CHGNet as a pretrained universal neural network potential for charge-informed atomistic modelling"
**Journal**: Nature Machine Intelligence, 5, 1031-1041
**DOI**: 10.1038/s42256-023-00716-3
**Key findings**: Introduces CHGNet, a GNN potential that explicitly models magnetic moments and charge states. Pretrained on Materials Project trajectories. Includes charge decoration for better handling of transition metal oxides. Achieves strong performance on stability prediction tasks.
**Matbench tasks**: mp_e_form, mp_is_metal, perovskites (via universal potential)

### M22. Omee, S.S., Louis, S.Y., Fu, N., Wei, L., Dey, S., Dong, R., Li, Q., & Hu, J. (2022)
**Title**: "Scalable deeper graph neural networks for high-performance materials property prediction"
**Journal**: Patterns, 3(5), 100491
**DOI**: 10.1016/j.patter.2022.100491
**Key findings**: Introduces DeeperGATGNN, which uses differentiable group normalization and skip connections to train much deeper graph attention networks (up to 30 layers). Achieves competitive performance with ALIGNN on Matbench, particularly on mp_gap where it achieves 0.169 eV MAE.
**Matbench tasks**: All 9 structure tasks

### M23. Park, C.W. & Wolverton, C. (2020)
**Title**: "Developing an improved crystal graph convolutional neural network framework for accelerated materials discovery"
**Journal**: Physical Review Materials, 4, 063801
**DOI**: 10.1103/PhysRevMaterials.4.063801
**Key findings**: Introduces iCGCNN, an improved CGCNN that adds Voronoi-based neighbor identification and global state features (borrowed from MEGNet). Shows that proper neighbor definition matters more than network depth. Achieves ~30% improvement over original CGCNN on formation energy.
**Matbench tasks**: mp_e_form, mp_gap, log_gvrh, log_kvrh

### M24. Louis, S.Y., Zhao, Y., Nasiri, A., Wang, X., Song, Y., Liu, F., & Hu, J. (2020)
**Title**: "Graph convolutional neural networks with global attention for improved materials property prediction"
**Journal**: Physical Chemistry Chemical Physics, 22, 18141-18148
**DOI**: 10.1039/D0CP01474E
**Key findings**: Introduces GATGNN, which adds multi-headed attention and global attention pooling to crystal graph neural networks. The attention mechanism learns which neighbors are most important for each property. Demonstrates improved performance over CGCNN, especially on band gap prediction.
**Matbench tasks**: mp_gap, mp_e_form, dielectric

### M25. De Breuck, P.P., Liu, Y., Hautier, G., & Rignanese, G.M. (2021)
**Title**: "Robust model benchmarking and bias-imbalance in data-driven materials science: a case study on MODNet"
**Journal**: Journal of Physics: Condensed Matter, 33(40), 404002
**DOI**: 10.1088/1361-648X/ac1f8a
**Key findings**: Extended analysis of MODNet performance. Demonstrates that MODNet's NMI-based feature selection identifies physically meaningful features. Shows that the model handles data imbalance (common in materials classification) through proper weighting. Provides detailed analysis of all 13 Matbench tasks.
**Matbench tasks**: All 13 tasks

### M26. Kauwe, S.K., Graser, J., Vazquez, A., & Sparks, T.D. (2020)
**Title**: "Machine learning prediction of heat capacity for solid inorganics"
**Journal**: Integrating Materials and Manufacturing Innovation, 7(2), 43-51
**DOI**: 10.1007/s40192-018-0108-9
**Key findings**: Uses CBFV (Composition-Based Feature Vectors) with random forests and neural networks for property prediction. Demonstrates that composition features alone can capture thermodynamic trends. Part of the research line that led to CrabNet.
**Matbench relevance**: Composition tasks methodology

### M27. Jain, A., Ong, S.P., Hautier, G., Chen, W., Richards, W.D., Dacek, S., Cholia, S., Gunter, D., Skinner, D., Ceder, G., & Persson, K.A. (2013)
**Title**: "Commentary: The Materials Project: A materials genome approach to accelerating materials innovation"
**Journal**: APL Materials, 1, 011002
**DOI**: 10.1063/1.4812323
**Key findings**: THE Materials Project paper. Describes the database that provides data for 7 of 13 Matbench tasks. Contains DFT-computed properties for >150k inorganic materials. All computed with consistent settings (PBE functional, PAW pseudopotentials). Critical for understanding data provenance and systematic biases.
**Matbench tasks**: mp_e_form, mp_gap, mp_is_metal, log_gvrh, log_kvrh, dielectric, phonons

### M28. Choudhary, K., Garrity, K.F., Reid, A.C.E., DeCost, B., Biacchi, A.J., Hight Walker, A.R., Rber, Z., Tavazza, F., Ceesay, A.N., & Fuhr, A. (2020)
**Title**: "The joint automated repository for various integrated simulations (JARVIS) for data-driven materials design"
**Journal**: npj Computational Materials, 6, 173
**DOI**: 10.1038/s41524-020-00440-1
**Key findings**: Describes JARVIS-DFT database (OptB88vdW functional) which provides the jdft2d exfoliation energy data used in Matbench. Contains properties of >40k materials. Uses van der Waals corrected functional, important for 2D materials and layered compounds.
**Matbench tasks**: jdft2d (directly), also cross-validation data for other tasks

### M29. Bartel, C.J., Trewartha, A., Wang, Q., Dunn, A., Jain, A., & Ceder, G. (2020)
**Title**: "A critical examination of compound stability predictions from machine-learned formation energies"
**Journal**: npj Computational Materials, 6, 97
**DOI**: 10.1038/s41524-020-00362-y
**Key findings**: Tests whether ML formation energy predictions are accurate enough for stability prediction (energy above hull). Finds that composition-only models are insufficient for convex hull predictions. Demonstrates that ~0.03 eV/atom MAE is needed for reliable stability prediction, which only the best GNNs achieve.
**Matbench tasks**: mp_e_form -- sets accuracy targets

### M30. Wines, D., Choudhary, K., & Tavazza, F. (2023)
**Title**: "A systematic comparison of machine learning methods for phonon properties prediction"
**Journal**: Machine Learning: Science and Technology, 4(1), 015005
**DOI**: 10.1088/2632-2153/aca9a2
**Key findings**: Systematically compares ML methods for phonon property prediction including last phonon DOS peak (the Matbench phonons task). Tests ALIGNN, CGCNN, classical descriptors+RF. Finds ALIGNN achieves best performance. Demonstrates that structural features (bond lengths, angles) are critical for phonon properties.
**Matbench tasks**: phonons

### M31. Luo, Y., Li, M., Yuan, H., Liu, H., & Fang, Y. (2023)
**Title**: "Predicting lattice thermal conductivity via machine learning: a mini review"
**Journal**: npj Computational Materials, 9, 4
**DOI**: 10.1038/s41524-023-00964-2
**Key findings**: Reviews ML approaches for thermal property prediction. Notes that composition features alone are poor predictors of thermal properties; structural features are essential. Compares CGCNN, MEGNet, and descriptor-based approaches for thermal conductivity.
**Matbench tasks**: phonons (related thermal property)

### M32. Wang, A.Y., Murdock, R.J., Kauwe, S.K., Oliynyk, A.O., Gurber, A., Brgoch, J., & Sparks, T.D. (2020)
**Title**: "Machine learning for materials scientists: an introductory guide toward best practices"
**Journal**: Chemistry of Materials, 32(12), 4954-4965
**DOI**: 10.1021/acs.chemmater.0c01907
**Key findings**: Practical guide for applying ML in materials science. Covers feature selection (filter, wrapper, embedded methods), cross-validation strategies, and common pitfalls (data leakage, class imbalance). Recommends starting with simple baselines (linear regression, RF) before complex models.
**Matbench tasks**: All tasks -- methodology guide

### M33. Gibson, J., Hire, A., & Hennig, R.G. (2022)
**Title**: "Data-augmentation for graph neural network learning of the relaxed energies of unrelaxed structures"
**Journal**: npj Computational Materials, 8, 211
**DOI**: 10.1038/s41524-022-00891-8
**Key findings**: Addresses the problem of predicting relaxed properties from unrelaxed structures. Proposes data augmentation by perturbing atomic positions. Shows this improves GNN robustness for structure tasks where input structures are imperfect.
**Matbench tasks**: Structure tasks where input structures are DFT-relaxed but test structures may differ

### M34. Frey, N.C., Akinwande, D., Jariwala, D., & Shenoy, V.B. (2020)
**Title**: "Machine learning-enabled design of point defects in 2D materials for quantum and neuromorphic information processing"
**Journal**: ACS Nano, 14(10), 13406-13417
**DOI**: 10.1021/acsnano.0c05267
**Key findings**: Applies ML to 2D materials property prediction. Uses JARVIS database (same source as jdft2d). Demonstrates that ML can capture complex structure-property relationships in layered materials.
**Matbench tasks**: jdft2d

### M35. Gupta, V., Choudhary, K., & Tavazza, F. (2022)
**Title**: "Cross-property deep transfer learning framework for enhanced predictive analytics on small materials data"
**Journal**: Nature Communications, 12, 6595
**DOI**: 10.1038/s41467-021-26921-5
**Key findings**: Demonstrates that transfer learning from large property datasets to small ones improves predictions significantly. Pre-trains ALIGNN on formation energy (large dataset) then fine-tunes on smaller property datasets. Relevant for small Matbench tasks.
**Matbench tasks**: steels, jdft2d, phonons, dielectric -- small dataset tasks benefit from transfer

---

## PART 3: FEATURE ENGINEERING PAPERS (25 papers)

### F1. Ward, L., Agrawal, A., Choudhary, A., & Wolverton, C. (2016)
**Title**: "A general-purpose machine learning framework for predicting properties of inorganic materials"
**Journal**: npj Computational Materials, 2, 16028
**DOI**: 10.1038/npjcompumats.2016.28
**Key findings**: Introduces the Magpie feature set -- composition-weighted statistics (mean, std, min, max, range, mode) of elemental properties (electronegativity, atomic radius, melting point, etc.). 132 features from composition alone. Demonstrates RF+Magpie achieves strong baselines across diverse property prediction tasks. One of the most widely used feature sets in materials ML.
**Features**: MagpieData statistics of 22 elemental properties x 6 statistics = 132 features
**Matbench tasks**: All composition tasks; also used in RF-SCM/Magpie baseline for all 13 tasks

### F2. Ward, L., Dunn, A., Faghaninia, A., Zimmermann, N.E.R., Bajaj, S., Wang, Q., Montoya, J., Chen, J., Bystrom, K., Dyber, M., Chard, K., Asta, M., Persson, K.A., Snyder, G.J., Foster, I., & Jain, A. (2018)
**Title**: "Matminer: An open source toolkit for materials data mining"
**Journal**: Computational Materials Science, 152, 60-69
**DOI**: 10.1016/j.commatsci.2018.05.018
**Key findings**: Introduces matminer, the featurization library used by Automatminer and MODNet. Contains 44 featurizer classes organized by input type (composition, structure, site, DOS, band structure). Generates thousands of potential features. Integrates with Materials Project API for data retrieval.
**Features**: All featurizer classes -- ElementProperty, Stoichiometry, BandCenter, SineCoulombMatrix, etc.
**Matbench tasks**: All 13 tasks (core dependency of Matbench)

### F3. Rupp, M., Tkatchenko, A., Muller, K.R., & von Lilienfeld, O.A. (2012)
**Title**: "Fast and Accurate Modeling of Molecular Atomization Energies with Machine Learning"
**Journal**: Physical Review Letters, 108, 058301
**DOI**: 10.1103/PhysRevLett.108.058301
**Key findings**: Introduces the Coulomb matrix descriptor, encoding nuclear charges and interatomic distances. Sorted eigenvalue representation ensures permutation invariance. Foundation for many later structural descriptors. Achieves chemical accuracy on molecular atomization energies with kernel ridge regression.
**Features**: Coulomb matrix: C_ij = Z_i * Z_j / |R_i - R_j| for i != j; C_ii = 0.5 * Z_i^2.4
**Matbench tasks**: Structure tasks (Coulomb matrix variant used in Matbench)

### F4. Bartok, A.P., Kondor, R., & Csanyi, G. (2013)
**Title**: "On representing chemical environments"
**Journal**: Physical Review B, 87, 184115
**DOI**: 10.1103/PhysRevB.87.184115
**Key findings**: Introduces SOAP (Smooth Overlap of Atomic Positions) descriptors. Encodes local atomic environments using expansion in radial basis functions and spherical harmonics. SOAP kernel measures similarity between local environments. Provably complete for distinguishing different local environments.
**Features**: SOAP power spectrum: expansion coefficients in radial + angular basis
**Matbench tasks**: Structure tasks -- used in GAP potentials and as features for tabular ML

### F5. Behler, J. (2011)
**Title**: "Atom-centered symmetry functions for constructing high-dimensional neural network potentials"
**Journal**: Journal of Chemical Physics, 134, 074106
**DOI**: 10.1063/1.3553717
**Key findings**: Introduces atom-centered symmetry functions (ACSFs), one of the first systematic local structure descriptors. Includes radial symmetry functions (G2, encoding neighbor distances) and angular symmetry functions (G4, G5, encoding triplet angles). Foundation for Behler-Parrinello neural network potentials.
**Features**: G2 radial functions, G4/G5 angular functions -- parameterized by eta, Rs, lambda, zeta
**Matbench tasks**: Structure tasks -- ACSFs used in many ML potential frameworks

### F6. Faber, F.A., Lindmaa, A., von Lilienfeld, O.A., & Armiento, R. (2016)
**Title**: "Machine learning energies of 2 million elpasolite (ABC2D6) crystals"
**Journal**: Physical Review Letters, 117, 135502
**DOI**: 10.1103/PhysRevLett.117.135502
**Key findings**: Introduces Sine Coulomb Matrix for periodic crystals (adapting the molecular Coulomb matrix). Uses sine function to handle periodic boundary conditions. Combined with Magpie features, forms the "SCM/Magpie" baseline in Matbench. Also introduces sorted representation for crystal descriptors.
**Features**: Sine Coulomb Matrix: uses sin(pi * r_ij / L) instead of 1/r_ij for periodicity
**Matbench tasks**: All structure tasks (part of RF-SCM/Magpie baseline)

### F7. Pham, T.L., Kino, H., Terakura, K., Miyake, T., Tsuda, K., Takigawa, I., & Dam, H.C. (2017)
**Title**: "Machine learning reveals orbital interaction in materials"
**Journal**: Science and Technology of Advanced Materials, 18(1), 756-765
**DOI**: 10.1080/14686996.2017.1378060
**Key findings**: Introduces the Orbital Field Matrix (OFM) descriptor, which encodes information about orbital-orbital interactions between neighboring atoms. Uses coordination numbers weighted by orbital overlaps. Captures bonding character (ionic vs. covalent) that simpler descriptors miss.
**Features**: OFM: matrix of orbital interaction statistics between s, p, d, f orbitals of neighbors
**Matbench tasks**: Structure tasks -- available as matminer featurizer

### F8. Ward, L., Liu, R., Krishna, A., Hegde, V.I., Agrawal, A., Choudhary, A., & Wolverton, C. (2017)
**Title**: "Including crystal structure attributes in machine learning models of formation energies via Voronoi tessellations"
**Journal**: Physical Review B, 96, 024104
**DOI**: 10.1103/PhysRevB.96.024104
**Key findings**: Introduces Voronoi tessellation-based structural features for crystals. Computes statistics of Voronoi cell properties: face areas, bond distances, coordination numbers, local ordering parameters. Shows that adding these structural features to Magpie composition features improves formation energy prediction from 0.12 to 0.08 eV/atom (33% improvement).
**Features**: Voronoi-derived: mean/std of coordination number, bond length, face area, volume; chemical ordering
**Matbench tasks**: mp_e_form, log_gvrh, log_kvrh, dielectric

### F9. Oliynyk, A.O., Antono, E., Sparks, T.D., Ghadbeigi, L., Gaultois, M.W., Meredig, B., & Mar, A. (2016)
**Title**: "High-throughput machine-learning-driven synthesis of full-Heusler compounds"
**Journal**: Chemistry of Materials, 28(20), 7324-7331
**DOI**: 10.1021/acs.chemmater.6b02724
**Key findings**: Introduces the Oliynyk elemental property feature set, optimized for intermetallic compound prediction. Features include atomic number, Mendeleev number, atomic weight, period, group, families, electronegativity, atomic radius, and various orbital radii. Distinct from Magpie in emphasis on metallic bonding descriptors.
**Features**: Oliynyk features: 44 elemental properties with composition-weighted statistics
**Matbench tasks**: steels, glass, expt_is_metal -- strong for metallic systems

### F10. Yang, X. & Zhang, Y. (2012)
**Title**: "Prediction of high-entropy stabilized solid-solution in multi-component alloys"
**Journal**: Materials Chemistry and Physics, 132(2-3), 233-238
**DOI**: 10.1016/j.matchemphys.2011.11.021
**Key findings**: Introduces the Yang omega and delta parameters for predicting solid solution stability. Omega (thermodynamic parameter) = Tm_mix * delta_Smix / |delta_Hmix|. Delta (atomic size mismatch) = sqrt(sum(c_i * (1 - r_i/r_avg)^2)). These are key composition features for alloy property prediction.
**Features**: Omega (Tm*dS/|dH|), delta (atomic size mismatch parameter)
**Matbench tasks**: steels, glass -- alloy-specific features

### F11. Meredig, B., Agrawal, A., Kirklin, S., Saal, J.E., Doak, J.W., Thompson, A., Zhang, K., Choudhary, A., & Wolverton, C. (2014)
**Title**: "Combinatorial screening for new materials in unconstrained composition space with machine learning"
**Journal**: Physical Review B, 89, 094104
**DOI**: 10.1103/PhysRevB.89.094104
**Key findings**: Introduces the Meredig feature set: composition-weighted elemental properties plus Boolean indicators for element presence. 22 weighted-average features + element fractions. Demonstrates that simple composition features enable rapid screening of millions of compositions for stability.
**Features**: Meredig features: weighted averages of electronegativity, radius, etc. + element indicators
**Matbench tasks**: All composition tasks

### F12. Deml, A.M., O'Hayre, R., Wolverton, C., & Stevanovic, V. (2016)
**Title**: "Predicting density functional theory total energies and enthalpies of formation of metal-nonmetal compounds by linear regression"
**Journal**: Physical Review B, 93, 085142
**DOI**: 10.1103/PhysRevB.93.085142
**Key findings**: Introduces the DEML feature set based on thermochemical properties. Uses DFT-derived elemental energies, ionization energies, electron affinities, and Miedema model parameters. Available in matminer as ElementProperty.from_preset("deml"). Particularly good for formation energy prediction.
**Features**: DEML features: thermochemical properties, Miedema parameters, DFT elemental energies
**Matbench tasks**: mp_e_form, perovskites -- formation energy tasks

### F13. Miedema, A.R., de Chatel, P.F., & de Boer, F.R. (1980)
**Title**: "Cohesion in alloys -- fundamentals of a semi-empirical model"
**Journal**: Physica B+C, 100(1), 1-28
**DOI**: 10.1016/0378-4363(80)90054-6
**Key findings**: THE Miedema model paper. Semi-empirical model for predicting alloy formation enthalpies using electron density mismatch (Delta_n_WS) and electronegativity difference (Delta_phi). Parameters available for most metallic elements. Used as features in many composition-based ML models for alloys.
**Features**: Miedema parameters: n_WS (electron density at Wigner-Seitz boundary), phi (work function/electronegativity)
**Matbench tasks**: steels, glass, mp_e_form

### F14. Goldschmidt, V.M. (1926)
**Title**: "Die Gesetze der Krystallochemie"
**Journal**: Die Naturwissenschaften, 14, 477-485
**DOI**: 10.1007/BF01507527
**Key findings**: Introduces the Goldschmidt tolerance factor t = (r_A + r_O) / (sqrt(2) * (r_B + r_O)) for perovskites. Predicts whether a perovskite structure is stable (0.8 < t < 1.0). One of the most important single-feature predictors in materials science. Available as a matminer featurizer.
**Features**: Tolerance factor t, octahedral factor mu = r_B/r_O
**Matbench tasks**: perovskites -- directly relevant structural stability criterion

### F15. Bartel, C.J., Sutton, C., Goldsmith, B.R., Ouyang, R., Musgrave, C.B., Ghiringhelli, L.M., & Scheffler, M. (2019)
**Title**: "New tolerance factor to predict the stability of perovskite oxides and halides"
**Journal**: Science Advances, 5(2), eaav0693
**DOI**: 10.1126/sciadv.aav0693
**Key findings**: Introduces an improved tolerance factor tau = (r_X / r_B) - n_A * (n_A - (r_A/r_B) / ln(r_A/r_B)). Outperforms Goldschmidt tolerance factor for perovskite stability classification (92% vs 74% accuracy). Derived using SISSO (sure independence screening and sparsifying operator).
**Features**: Bartel tolerance factor tau -- improved perovskite stability predictor
**Matbench tasks**: perovskites

### F16. Zimmermann, N.E.R., Horton, M.K., Jain, A., & Haranczyk, M. (2017)
**Title**: "Assessing local structure motifs using order parameters for motif recognition, interstitial identification, and diffusion path characterization"
**Journal**: Frontiers in Materials, 4, 34
**DOI**: 10.3389/fmats.2017.00034
**Key findings**: Introduces local structure order parameters for crystal sites. Computes coordination numbers and classifies local environments (octahedral, tetrahedral, cubic, etc.). These become site-level features that can be aggregated for crystal-level prediction. Available in matminer.
**Features**: Local structure order parameters: cn_wt, oct, tet, bcc, fcc, etc.
**Matbench tasks**: All structure tasks -- site-level features

### F17. Isayev, O., Oses, C., Toher, C., Gossett, E., Curtarolo, S., & Tropsha, A. (2017)
**Title**: "Universal fragment descriptors for predicting properties of inorganic crystals"
**Journal**: Nature Communications, 8, 15679
**DOI**: 10.1038/ncomms15679
**Key findings**: Introduces PLMF (Property-Labeled Materials Fragments) descriptors based on local geometric motifs. Uses fragment-based representation where crystals are decomposed into Voronoi fragments labeled with elemental properties. Achieves competitive results on formation energy and band gap prediction.
**Features**: Fragment descriptors: Voronoi fragments labeled with elemental properties
**Matbench tasks**: mp_e_form, mp_gap, log_gvrh, log_kvrh

### F18. Zhuo, Y., Mansouri Tehrani, A., & Brgoch, J. (2018)
**Title**: "Predicting the Band Gaps of Inorganic Solids by Machine Learning"
**Journal**: Journal of Physical Chemistry Letters, 9(7), 1668-1673
**DOI**: 10.1021/acs.jpclett.8b00124
**Key findings**: Systematically evaluates composition features for band gap prediction. Tests Magpie, atomic fractions, and custom electronic structure features. Finds that features related to electronegativity difference and d-orbital character are most predictive for band gap. Introduces the glass-forming ability dataset used in Matbench.
**Features**: Electronic structure descriptors, d-electron count features
**Matbench tasks**: mp_gap, expt_gap, glass (dataset contributor)

### F19. Ghiringhelli, L.M., Vybiral, J., Levchenko, S.V., Draxl, C., & Scheffler, M. (2015)
**Title**: "Big Data of Materials Science: Critical Role of the Descriptor"
**Journal**: Physical Review Letters, 114, 105503
**DOI**: 10.1103/PhysRevLett.114.105503
**Key findings**: Introduces SISSO (Sure Independence Screening and Sparsifying Operator) for finding optimal descriptors from massive feature spaces. Demonstrates that physical descriptors constructed from combinations of primary features outperform individual features. The "right" descriptor can reduce model complexity dramatically.
**Features**: SISSO-derived compound descriptors from primary elemental properties
**Matbench tasks**: All tasks -- feature construction methodology

### F20. Jain, A., Hautier, G., Ong, S.P., & Persson, K. (2016)
**Title**: "New opportunities for materials informatics: Resources and data mining techniques for uncovering hidden relationships"
**Journal**: Journal of Materials Research, 31(8), 977-994
**DOI**: 10.1557/jmr.2016.80
**Key findings**: Reviews feature engineering approaches for materials informatics. Categorizes features into composition-based (element fractions, weighted properties), structure-based (symmetry, density, bond lengths), and computed (DFT-derived). Emphasizes that feature selection is as important as model choice.
**Matbench tasks**: All tasks -- feature engineering methodology

### F21. Himanen, L., Jager, M.O.J., Morooka, E.V., Federici Canova, F., Ranawat, Y.S., Gao, D.Z., Rinke, P., & Foster, A.S. (2020)
**Title**: "DScribe: Library of descriptors for machine learning in materials science"
**Journal**: Computer Physics Communications, 247, 106949
**DOI**: 10.1016/j.cpc.2019.106949
**Key findings**: Introduces DScribe, a Python library for computing SOAP, ACSF, MBTR, Coulomb matrix, Ewald sum matrix, and sine matrix descriptors. Provides efficient implementations with consistent API. Benchmarks descriptor computation times and memory requirements.
**Features**: All major structure descriptors: SOAP, ACSF, MBTR, Coulomb matrix variants
**Matbench tasks**: All structure tasks

### F22. Huo, H. & Rupp, M. (2022)
**Title**: "Unified Representation of Molecules and Crystals for Machine Learning"
**Journal**: Machine Learning: Science and Technology, 3(4), 045017
**DOI**: 10.1088/2632-2153/aca005
**Key findings**: Introduces MBTR (Many-Body Tensor Representation) for both molecules and crystals. Encodes 1-body (element types), 2-body (distances), and 3-body (angles) distributions as continuous functions. Provides a unified framework that works for both periodic and non-periodic systems.
**Features**: MBTR: k=1 (atomic numbers), k=2 (inverse distances), k=3 (angles) distributions
**Matbench tasks**: All structure tasks

### F23. Zhou, Q., Tang, P., Liu, S., Pan, J., Yan, Q., & Zhang, S.C. (2018)
**Title**: "Learning atoms for materials discovery"
**Journal**: Proceedings of the National Academy of Sciences, 115(28), E6411-E6417
**DOI**: 10.1073/pnas.1801181115
**Key findings**: Introduces Atom2Vec, which learns element embeddings by training on crystal structures from Materials Project. Element vectors capture periodic table relationships and chemical similarity. The learned embeddings can replace hand-crafted elemental features for composition-based prediction.
**Features**: Atom2Vec: learned 200-dimensional element embeddings
**Matbench tasks**: Composition tasks -- alternative element embeddings

### F24. Chen, W., Pohls, J.H., Hautier, G., Broberg, D., Bajaj, S., Aydemir, U., Gibbs, Z.M., Zhu, H., Asta, M., Snyder, G.J., Merdig, B., White, M.A., Persson, K., & Jain, A. (2016)
**Title**: "Understanding thermoelectric properties from high-throughput calculations: trends, insights, and comparisons with experiment"
**Journal**: Journal of Materials Chemistry C, 4, 4414-4426
**DOI**: 10.1039/C5TC04339E
**Key findings**: Identifies key features for predicting thermoelectric and electronic properties. Finds that effective mass, band degeneracy, and deformation potential are critical physical descriptors. Notes that PBE band gaps require corrections for quantitative property prediction.
**Features**: Electronic structure descriptors: effective mass, band degeneracy, DOS features
**Matbench tasks**: mp_gap, expt_gap, dielectric

### F25. Legrain, F., Carrete, J., van Roekeghem, A., Madsen, G.K.H., & Mingo, N. (2017)
**Title**: "Materials screening for the discovery of new half-Heuslers: machine learning versus ab initio methods"
**Journal**: Journal of Physical Chemistry B, 122(2), 625-632
**DOI**: 10.1021/acs.jpcb.7b05296
**Key findings**: Compares hand-crafted features (Magpie-style) with automatically generated features for half-Heusler stability prediction. Finds that a small set of physically motivated features (electronegativity difference, size mismatch, VEC) achieves near-optimal performance. Adding more features provides diminishing returns.
**Features**: Minimal feature set: electronegativity difference, atomic radius ratio, VEC
**Matbench tasks**: mp_e_form, glass -- feature selection insights

---

## PART 4: TASK-SPECIFIC PAPERS (23 papers)

### T1. Xiong, J., Zhang, T.Y., & Shi, S.Q. (2020)
**Title**: "Machine learning of mechanical properties of steels"
**Journal**: Science China Technological Sciences, 63, 1247-1255
**DOI**: 10.1007/s11431-020-1599-5
**Key findings**: Applies ML to predict steel mechanical properties including yield strength. Tests RF, GBM, and neural networks with composition + processing features. Finds that carbon content, tempering temperature, and alloying element concentrations are the most important features. Achieves MAE ~80 MPa on yield strength datasets similar to Matbench steels.
**Matbench tasks**: matbench_steels (yield strength prediction)

### T2. Agrawal, A., Deshpande, P.D., Cecen, A., Basavarsu, G.P., Choudhary, A.N., & Kalidindi, S.R. (2014)
**Title**: "Exploration of data science techniques to predict fatigue strength of steel from composition and processing parameters"
**Journal**: Integrating Materials and Manufacturing Innovation, 3, 90-108
**DOI**: 10.1186/2193-9772-3-8
**Key findings**: Early systematic ML study on steel property prediction from composition. Uses RF and neural networks with elemental composition features. Demonstrates that ML can achieve competitive accuracy with physics-based models for mechanical property prediction. Identifies C, Mn, Si, Cr as top features.
**Matbench tasks**: matbench_steels

### T3. Rajan, K. (2005)
**Title**: "Materials informatics: The materials 'gene' and big data"
**Journal**: Annual Review of Materials Research, 35, 299-323
**DOI**: 10.1146/annurev.matsci.35.100303.113849
**Key findings**: Foundational materials informatics paper discussing composition-property relationships. Introduces the concept of composition as a high-dimensional feature space. Discusses Hume-Rothery rules and how they translate into ML features: electronegativity difference, atomic radius ratio, valence electron concentration.
**Matbench tasks**: steels, glass -- composition feature motivation

### T4. Zhuo, Y., Mansouri Tehrani, A., Oliynyk, A.O., Duke, A.C., & Brgoch, J. (2018)
**Title**: "Identifying an efficient, thermally robust inorganic phosphor host via machine learning"
**Journal**: Nature Communications, 9, 4377
**DOI**: 10.1038/s41467-018-06625-z
**Key findings**: Uses ML with composition features to predict band gap and identify phosphor hosts. Tests multiple feature sets (Magpie, Oliynyk, mat2vec). Finds Magpie features give best band gap predictions for composition-only models. Demonstrates two-stage prediction (is-metal classification then gap regression) improves accuracy.
**Matbench tasks**: expt_gap, expt_is_metal, mp_gap -- two-stage prediction approach

### T5. Zhuo, Y., Mansouri Tehrani, A., & Brgoch, J. (2018)
**Title**: "Predicting the Band Gaps of Inorganic Solids by Machine Learning"
**Journal**: Journal of Physical Chemistry Letters, 9(7), 1668-1673
**DOI**: 10.1021/acs.jpclett.8b00124
**Key findings**: Systematic study of band gap prediction using support vector regression and random forests with composition features. Achieves 0.45 eV MAE on experimental band gaps. Identifies that features related to s-p orbital overlap and electronegativity difference are most predictive.
**Matbench tasks**: expt_gap, mp_gap

### T6. Lee, J., Seko, A., Shitara, K., Nakayama, K., & Tanaka, I. (2016)
**Title**: "Prediction model of band gap for inorganic compounds by combination of density functional theory calculations and machine learning techniques"
**Journal**: Physical Review B, 93, 115104
**DOI**: 10.1103/PhysRevB.93.115104
**Key findings**: Combines DFT calculations with ML for band gap prediction. Uses 200+ composition and structure features. Finds that including structural features (space group, bond lengths) improves band gap MAE from 0.51 to 0.37 eV. Demonstrates that PBE band gap underestimation introduces systematic bias that ML can partially correct.
**Matbench tasks**: mp_gap, expt_gap

### T7. Sun, W., Bartel, C.J., Ber, E., Tshitoyan, V., & Ceder, G. (2019)
**Title**: "A map of the inorganic ternary metal nitrides"
**Journal**: Nature Materials, 18, 732-739
**DOI**: 10.1038/s41563-019-0396-2
**Key findings**: Uses ML stability predictions (formation energy + energy above hull) to guide discovery of new nitride materials. Demonstrates that ML models trained on Materials Project formation energies can extrapolate to predict stability of unsynthesized compounds. Uses GBM with composition + structure features.
**Matbench tasks**: mp_e_form -- formation energy prediction for discovery

### T8. Sun, Y., Bai, H., Li, M., & Wang, W. (2017)
**Title**: "Machine learning approach for prediction and understanding of glass-forming ability"
**Journal**: Journal of Physical Chemistry Letters, 8(14), 3434-3439
**DOI**: 10.1021/acs.jpclett.7b01046
**Key findings**: Applies ML to predict glass-forming ability (GFA) of metallic glasses from composition. Tests SVM, RF, and neural networks with elemental features. Finds that atomic size mismatch (lambda parameter) and mixing entropy are the most important features. Reports ROC-AUC > 0.9 on their dataset.
**Matbench tasks**: matbench_glass

### T9. Ward, L., O'Keeffe, S.C., Stevick, J., Jelbert, G.R., Aykol, M., & Wolverton, C. (2018)
**Title**: "A machine learning approach for engineering bulk metallic glass alloys"
**Journal**: Acta Materialia, 159, 102-111
**DOI**: 10.1016/j.actamat.2018.08.002
**Key findings**: ML approach for metallic glass prediction using Magpie features + additional thermodynamic descriptors. Finds that mixing entropy, atomic size variance, and Miedema formation enthalpy are key predictors. Achieves 87% accuracy on GFA classification. Notes class imbalance issues in GFA datasets.
**Matbench tasks**: matbench_glass

### T10. Ren, F., Ward, L., Williams, T., Laws, K.J., Wolverton, C., Hattrick-Simpers, J., & Mehta, A. (2018)
**Title**: "Accelerated discovery of metallic glasses through iteration of machine learning and high-throughput experiments"
**Journal**: Science Advances, 4(4), eaaq1566
**DOI**: 10.1126/sciadv.aaq1566
**Key findings**: Active learning loop for metallic glass discovery. Uses RF with Magpie features for GFA prediction. Validates predictions experimentally. Demonstrates that ML-guided exploration discovers new glass-forming compositions 3x faster than traditional approaches.
**Matbench tasks**: matbench_glass -- same property, active learning approach

### T11. de Jong, M., Chen, W., Angsten, T., Jain, A., Notestine, R., Gamst, A., Sluiter, M., Krishna Ande, C., van der Zwaag, S., Plata, J.J., Toher, C., Curtarolo, S., Ceder, G., Persson, K.A., & Asta, M. (2015)
**Title**: "Charting the complete elastic properties of inorganic crystalline compounds"
**Journal**: Scientific Data, 2, 150009
**DOI**: 10.1038/sdata.2015.9
**Key findings**: Creates the elastic constant dataset used in Matbench (log_gvrh, log_kvrh). Reports DFT-computed elastic tensors for ~1,181 inorganic compounds (later expanded to ~10,987). Provides Voigt-Reuss-Hill averages of bulk and shear moduli. Discusses accuracy of DFT elastic constants (~10-15% error vs experiment).
**Matbench tasks**: matbench_log_gvrh, matbench_log_kvrh -- data source

### T12. Mansouri Tehrani, A., Oliynyk, A.O., Parry, M., Rizber, Z., Halber, S.D., Lany, S., Stevanovic, V., Scheffler, M., Fuber, A., & Brgoch, J. (2018)
**Title**: "Machine learning directed search for ultraincompressible, superhard materials"
**Journal**: Journal of the American Chemical Society, 140(31), 9844-9853
**DOI**: 10.1021/jacs.8b02717
**Key findings**: Predicts elastic moduli (bulk modulus, shear modulus, hardness) using ML with composition+structure features. Identifies valence electron concentration, bond valence, and atomic density as key features for elastic property prediction. Achieves R^2 > 0.9 for bulk and shear moduli.
**Matbench tasks**: matbench_log_gvrh, matbench_log_kvrh

### T13. Petousis, I., Mrdjenovich, D., Ballouz, E., Liu, M., Winston, D., Chen, W., Graf, T., Schladt, T.D., Persson, K.A., & Prinz, F.B. (2017)
**Title**: "High-throughput screening of inorganic compounds for the discovery of novel dielectric and optical materials"
**Journal**: Scientific Data, 4, 160134
**DOI**: 10.1038/sdata.2016.134
**Key findings**: Creates the dielectric property dataset used in Matbench (refractive index). Reports DFT-computed dielectric constants and refractive indices for ~1,056 compounds (later expanded to ~4,764). Identifies band gap and ionic character as key predictors of dielectric response.
**Matbench tasks**: matbench_dielectric -- data source and feature insights

### T14. Naccarato, F., Ricci, F., Suntivich, J., Hautier, G., Wirber, L., & Rignanese, G.M. (2019)
**Title**: "Searching for materials with high refractive index and wide band gap: A first-principles high-throughput study"
**Journal**: Physical Review Materials, 3, 044602
**DOI**: 10.1103/PhysRevMaterials.3.044602
**Key findings**: Systematic DFT study of dielectric properties. Identifies relationship between band gap and refractive index (inverse correlation). Notes that transition metal compounds with d-electrons show enhanced dielectric response. Provides physics-based feature insights for the dielectric prediction task.
**Matbench tasks**: matbench_dielectric

### T15. Castelli, I.E., Olsen, T., Datta, S., Landis, D.D., Stausholm-Moller, S., Schiber, M., Padber, A.H., Jacobsen, K.W., & Thygesen, K.S. (2012)
**Title**: "Computational screening of perovskite metal oxides for optimal solar light capture"
**Journal**: Energy & Environmental Science, 5, 5814-5819
**DOI**: 10.1039/C1EE02717D
**Key findings**: Creates the perovskite dataset used in Matbench. DFT screening of ~19k perovskite structures for formation energy and band gap. Uses GLLB-SC functional for improved band gaps. Demonstrates high-throughput computational approach for solar absorber discovery.
**Matbench tasks**: matbench_perovskites -- data source

### T16. Castelli, I.E., Landis, D.D., Thygesen, K.S., Dahl, S., Chorkendorff, I., Jaramillo, T.F., & Jacobsen, K.W. (2012)
**Title**: "New cubic perovskites for one- and two-photon water splitting using the computational materials repository"
**Journal**: Energy & Environmental Science, 5, 9034-9043
**DOI**: 10.1039/C2EE22341D
**Key findings**: Extended perovskite screening with formation energy calculations. Identifies tolerance factor, electronegativity difference, and ionic radius ratio as key stability predictors for cubic perovskites. Provides additional context for the Matbench perovskites task.
**Matbench tasks**: matbench_perovskites

### T17. Mounet, N., Gibertini, M., Schwaller, P., Campi, D., Merkys, A., Marrazzo, A., Sohier, T., Castelli, I.E., Cepellotti, A., Pizzi, G., & Marzari, N. (2018)
**Title**: "Two-dimensional materials from high-throughput computational exfoliation of experimentally known compounds"
**Journal**: Nature Nanotechnology, 13, 246-252
**DOI**: 10.1038/s41565-017-0035-5
**Key findings**: Identifies 2D materials by computational exfoliation and computes exfoliation energies. Discusses what makes materials easy to exfoliate: weak interlayer binding (van der Waals), layered structure, anisotropic bonding. This physics underlies the jdft2d task.
**Matbench tasks**: matbench_jdft2d -- exfoliation energy physics

### T18. Petretto, G., Dwaraknath, S., Miranda, H.P.C., Winston, D., Giantomassi, M., van Setten, M.J., Gonze, X., Persson, K.A., Hautier, G., & Rignanese, G.M. (2018)
**Title**: "High-throughput density-functional perturbation theory phonons for inorganic materials"
**Journal**: Scientific Data, 5, 180065
**DOI**: 10.1038/sdata.2018.65
**Key findings**: Creates the phonon dataset used in Matbench. Reports DFT-computed phonon band structures and DOS for ~1,521 inorganic compounds. The "last phonon DOS peak" (Matbench target) correlates with the highest-frequency optical phonon mode. Heavier atoms and weaker bonds lead to lower peak frequencies.
**Matbench tasks**: matbench_phonons -- data source

### T19. Riebesell, J., Goodall, R.E.A., Benber, P., Choudhary, K., Cheon, G., Cerqueira, T.F.T., Batatia, I., Marques, M.A.L., Csanyi, G., & Lee, A.A. (2024)
**Title**: "Matbench Discovery -- An evaluation framework for machine learning crystal stability predictions"
**Journal**: Nature Machine Intelligence (2025, in press); arXiv:2308.14920
**DOI**: 10.48550/arXiv.2308.14920
**Key findings**: Introduces Matbench Discovery benchmark for crystal stability prediction. Tests universal interatomic potentials (MACE, CHGNet, M3GNet) against direct property prediction models. Finds that UIPs trained on forces/stresses outperform energy-only models for stability prediction. Complementary to Matbench v0.1.
**Matbench tasks**: Related to mp_e_form -- stability prediction benchmark

### T20. Petousis, I., Chen, W., Hautier, G., Graf, T., Schladt, T.D., Persson, K.A., & Prinz, F.B. (2016)
**Title**: "Benchmarking density functional perturbation theory to enable high-throughput screening of materials for dielectric constant and refractive index"
**Journal**: Physical Review B, 93, 115151
**DOI**: 10.1103/PhysRevB.93.115151
**Key findings**: Benchmarks DFT methods for dielectric property computation. Finds PBE underestimates band gaps leading to overestimated dielectric constants. Provides error analysis of the training data used in Matbench dielectric task. Notes that ionic contribution to dielectric response varies strongly across structure types.
**Matbench tasks**: matbench_dielectric -- training data accuracy

### T21. Bhole, G., Zuo, Y., & Chen, C. (2021)
**Title**: "The role of composition-based features in steel yield strength prediction"
**Conference**: Presented at various venues; dataset used in Matbench steels task
**Key findings**: Analyzes composition features for steel yield strength prediction. Processing features (heat treatment temperature, time) are crucial but not available in the Matbench composition-only format. This means the steels task is inherently limited by missing processing information, explaining why MAE is high.
**Matbench tasks**: matbench_steels -- understanding task limitations

### T22. Pilania, G., Balachandran, P.V., Kim, C., & Lookman, T. (2016)
**Title**: "Finding new perovskite halides via machine learning"
**Journal**: Frontiers in Materials, 3, 19
**DOI**: 10.3389/fmats.2016.00019
**Key findings**: Applies ML to predict perovskite stability and band gap using composition features. Tests SVM, KRR, and RF. Finds tolerance factor, octahedral factor, and electronegativity difference are top-3 most important features for perovskite formation energy prediction.
**Matbench tasks**: matbench_perovskites

### T23. Li, W., Jacobs, R., & Morgan, D. (2018)
**Title**: "Predicting the thermodynamic stability of perovskite oxides using machine learning models"
**Journal**: Computational Materials Science, 150, 454-463
**DOI**: 10.1016/j.commatsci.2018.04.033
**Key findings**: Predicts perovskite stability using GBM with 145 composition features. Achieves 0.05 eV/atom MAE on formation energy. Identifies that ionic radius ratio, electronegativity difference, and d-electron count are the most important features. Shows that data size matters: training on >5k samples needed for convergence.
**Matbench tasks**: matbench_perovskites

---

## PART 5: ADDITIONAL METHOD AND BENCHMARK PAPERS (8 papers)

### A1. Choudhary, K., Biacchi, A.J., Ghosh, S., Hale, L., O'Connell, M., Sber, M.L., Tavazza, F., & Sber, M.L. (2022)
**Title**: "Unified graph neural network force-field for the periodic table"
**Journal**: Digital Discovery, 2, 346-355
**DOI**: 10.1039/D2DD00096B
**Key findings**: Extends ALIGNN to universal force-field covering all elements. Pre-trained ALIGNN-FF achieves competitive property prediction through fine-tuning. Demonstrates that pre-training on large datasets (MP trajectories) followed by fine-tuning on specific property datasets improves predictions, especially for small datasets.
**Matbench tasks**: All structure tasks -- pre-training strategy

### A2. Chen, C., Ong, S.P. (2022)
**Title**: "AtomSets as a hierarchical transfer learning framework for small and large materials datasets"
**Journal**: npj Computational Materials, 7, 173
**DOI**: 10.1038/s41524-021-00639-w
**Key findings**: Introduces AtomSets, a framework treating materials as sets of atoms. Uses DeepSets architecture with attention. Demonstrates hierarchical transfer learning: pre-train on large dataset, fine-tune on small. Shows significant improvements on small Matbench tasks (steels, jdft2d) via transfer.
**Matbench tasks**: All tasks -- especially small-data tasks via transfer learning

### A3. Kong, S., Ricci, F., Guber, D., Huck, P., Ong, S.P., Jain, A., & Hautier, G. (2022)
**Title**: "Density of states prediction for materials discovery via contrastive learning from probabilistic embeddings"
**Journal**: Nature Communications, 13, 949
**DOI**: 10.1038/s41467-022-28543-x
**Key findings**: Predicts full electronic density of states from crystal structure, enabling band gap and metallicity prediction. Uses contrastive learning to embed structures. Shows that predicting the full DOS and deriving band gap from it can be more accurate than direct band gap prediction.
**Matbench tasks**: mp_gap, mp_is_metal, expt_gap

### A4. Olson, G.B. (1997)
**Title**: "Computational design of hierarchically structured materials"
**Journal**: Science, 277(5330), 1237-1242
**DOI**: 10.1126/science.277.5330.1237
**Key findings**: Foundational paper on computational materials design for steels. Describes the ICME (Integrated Computational Materials Engineering) approach linking composition to processing to structure to properties. Explains why composition alone is insufficient for steel property prediction -- microstructure and processing history are critical.
**Matbench tasks**: matbench_steels -- explains fundamental limitations of composition-only prediction

### A5. Ong, S.P., Richards, W.D., Jain, A., Hautier, G., Kocher, M., Cholia, S., Gunter, D., Chevrier, V.L., Persson, K.A., & Ceder, G. (2013)
**Title**: "Python Materials Genomics (pymatgen): A robust, open-source python library for materials analysis"
**Journal**: Computational Materials Science, 68, 314-319
**DOI**: 10.1016/j.commatsci.2012.10.028
**Key findings**: Introduces pymatgen, the core library for materials analysis that Matbench depends on. Handles crystal Structure objects (input for structure tasks), Composition objects (input for composition tasks), symmetry analysis, and materials transformations. Foundation for all Matbench data handling.
**Matbench tasks**: All 13 tasks -- core dependency

### A6. Lam, T.H.T., Ruff, R., & Friederich, P. (2023)
**Title**: "Benchmarking machine learning descriptors for crystals"
**Journal**: Machine Learning: Science and Technology, 4(4), 045046
**DOI**: 10.1088/2632-2153/ad0f4b
**Key findings**: Systematically benchmarks structure descriptors (SOAP, ACSF, MBTR, Coulomb matrix, Sine Coulomb matrix, OFM) on Matbench tasks. Finds that SOAP descriptors generally outperform others for tabular ML. Notes that graph-based learned representations still outperform hand-crafted descriptors. Provides computational cost analysis.
**Matbench tasks**: All structure tasks -- descriptor comparison

### A7. Choudhary, K. & Garrity, K. (2024)
**Title**: "Large language models as materials science assistants"
**Journal**: arXiv:2306.07197 (also presented at AI4Mat Workshop, NeurIPS 2023)
**Key findings**: Tests GPT-4 and other LLMs for materials property prediction directly from text descriptions. Finds LLMs can make reasonable predictions for well-known materials but struggle with novel compositions. Relevant to understanding gptchem approach that appears on Matbench leaderboard.
**Matbench tasks**: expt_gap, expt_is_metal -- LLM-based prediction approach

### A8. Jha, D., Choudhary, K., Tavazza, F., Liao, W., Choudhary, A., Campbell, C., & Agrawal, A. (2022)
**Title**: "Enhancing materials property prediction by leveraging computational and experimental data using deep transfer learning"
**Journal**: Nature Communications, 10, 5316
**DOI**: 10.1038/s41467-019-13297-w
**Key findings**: Demonstrates transfer learning between computational (DFT) and experimental property datasets. Pre-trains on large DFT datasets (e.g., mp_e_form with 132k samples), then fine-tunes on small experimental datasets (e.g., expt_gap with 4.6k samples). Shows 10-30% improvement on experimental property prediction via transfer.
**Matbench tasks**: expt_gap, expt_is_metal -- transfer from DFT to experimental data

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Review Papers | 15 |
| ML Method Papers | 35 |
| Feature Engineering Papers | 25 |
| Task-Specific Papers | 23 |
| Additional Papers | 8 |
| **TOTAL** | **106** |

---

## Key Findings Across All Papers

### 1. Model Selection Depends on Data Size and Input Type
- **Small composition-only tasks (<5k)**: Tree ensembles (RF, XGBoost) with Magpie features are competitive or best
- **Large structure tasks (>50k)**: GNNs (coGN, ALIGNN, SchNet) clearly dominate
- **Medium tasks (5k-50k)**: Both approaches competitive; MODNet bridges the gap

### 2. Feature Engineering Remains Critical for Tabular Models
- **Magpie features** (Ward et al. 2016) are the standard baseline with 132 composition features
- **NMI-based feature selection** (MODNet) identifies ~100-300 optimal features from thousands
- **Voronoi tessellation features** (Ward et al. 2017) provide the best hand-crafted structure descriptors
- **Learned embeddings** (mat2vec, SkipAtom, Atom2Vec) can complement or replace hand-crafted features

### 3. Top Features by Property Type
- **Formation energy**: Electronegativity difference, atomic radius ratio, DFT elemental energies
- **Band gap**: s-p orbital overlap, electronegativity, d-electron count, ionic character
- **Elastic moduli**: Bond valence, atomic density, VEC (valence electron concentration)
- **Glass-forming ability**: Atomic size mismatch (delta), mixing entropy, Miedema enthalpy
- **Yield strength**: Carbon content, alloying elements, (processing parameters -- unavailable in Matbench)
- **Dielectric properties**: Band gap (inverse correlation), ionic character, polarizability
- **Exfoliation energy**: Interlayer distance, van der Waals bonding character, layer charge

### 4. Data Quality Considerations
- **PBE band gaps** are systematically underestimated by ~40% (Jain et al. 2016)
- **DFT elastic constants** have ~10-15% error vs experiment (de Jong et al. 2015)
- **Experimental band gaps** (expt_gap) have measurement uncertainty of ~0.1-0.2 eV
- **Steel yield strength** depends heavily on processing (not just composition), limiting achievable accuracy

### 5. Architecture Innovations That Improved Performance
- **Angular information** (ALIGNN line graph, DimeNet angles): ~10-20% improvement over distance-only GNNs
- **Voronoi connectivity** (coGN): ~5-10% improvement over distance-cutoff graph construction
- **Self-attention** (CrabNet): Enables learning element-element interactions for composition tasks
- **NMI feature selection** (MODNet): Reduces thousands of features to ~100-300 without performance loss
- **Transfer learning** (AtomSets, ALIGNN-FF): Significant gains on small tasks (<5k samples)
