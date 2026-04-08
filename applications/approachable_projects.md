# Approachable HDR Project Candidates

**Generated**: 2026-04-02
**Total candidates**: 120
**Selection criteria**: Published benchmarks exist, GPU-computable on RTX 3060 12GB, rich design space, room for novelty, publicly available tools/data, approachable by generalists.

---

## Summary Table: Top 40 Candidates Ranked by (Novelty x Approachability x Feasibility)

| Rank | # | Problem | Domain | Novelty | Approachability | Feasibility | Score |
|------|---|---------|--------|---------|-----------------|-------------|-------|
| 1 | 11 | Concrete Mix Design Optimisation | Materials | HIGH | 5 | 5 | 25 |
| 2 | 3 | Traffic Signal Timing Optimisation | Transportation | HIGH | 5 | 5 | 25 |
| 3 | 56 | 3D Printing Parameter Optimisation | Manufacturing | HIGH | 5 | 5 | 25 |
| 4 | 1 | Building Energy Consumption Prediction | Energy | HIGH | 5 | 5 | 25 |
| 5 | 39 | Wine Quality Prediction & Optimisation | Food | HIGH | 5 | 5 | 25 |
| 6 | 80 | Bike-Sharing Demand Rebalancing | Transportation | HIGH | 5 | 5 | 25 |
| 7 | 27 | Wildfire Risk Prediction | Environment | HIGH | 5 | 5 | 25 |
| 8 | 63 | Solar Panel Tilt Angle Optimisation | Energy | MEDIUM | 5 | 5 | 20 |
| 9 | 30 | Crop Yield Prediction | Agriculture | HIGH | 5 | 4 | 20 |
| 10 | 19 | Customer Churn Prediction | Business | MEDIUM | 5 | 5 | 20 |
| 11 | 20 | Credit Card Fraud Detection | Business | MEDIUM | 5 | 5 | 20 |
| 12 | 35 | Flight Delay Prediction | Transportation | MEDIUM | 5 | 5 | 20 |
| 13 | 37 | Student Performance Prediction | Education | MEDIUM | 5 | 5 | 20 |
| 14 | 47 | Waste Sorting Image Classification | Environment | HIGH | 5 | 4 | 20 |
| 15 | 24 | House Price Prediction | Business | MEDIUM | 5 | 5 | 20 |
| 16 | 42 | Soil Quality Prediction | Agriculture | HIGH | 5 | 4 | 20 |
| 17 | 67 | F1 Race Strategy Optimisation | Sports | HIGH | 5 | 4 | 20 |
| 18 | 68 | Football Player Valuation | Sports | MEDIUM | 5 | 5 | 20 |
| 19 | 60 | Battery State-of-Health Prediction | Energy | HIGH | 4 | 5 | 20 |
| 20 | 51 | Renewable Energy Output Forecasting | Energy | HIGH | 4 | 5 | 20 |
| 21 | 85 | Inventory Demand Forecasting | Business | MEDIUM | 5 | 5 | 20 |
| 22 | 73 | Dynamic Pricing Optimisation | Business | HIGH | 4 | 5 | 20 |
| 23 | 44 | Pest & Disease Detection in Plants | Agriculture | HIGH | 5 | 4 | 20 |
| 24 | 76 | Startup Success Prediction | Business | MEDIUM | 5 | 5 | 20 |
| 25 | 12 | Welding Parameter Optimisation | Manufacturing | HIGH | 4 | 5 | 20 |
| 26 | 50 | Urban Noise Pollution Mapping | Social/Urban | MEDIUM | 5 | 4 | 16 |
| 27 | 82 | Parking Availability Prediction | Social/Urban | MEDIUM | 5 | 4 | 16 |
| 28 | 14 | Sleep Quality Prediction | Health | MEDIUM | 5 | 4 | 16 |
| 29 | 36 | Air Quality Prediction | Environment | MEDIUM | 5 | 4 | 16 |
| 30 | 59 | Smart Grid Load Forecasting | Energy | MEDIUM | 4 | 5 | 16 |
| 31 | 28 | Flood Prediction | Environment | MEDIUM | 5 | 4 | 16 |
| 32 | 21 | Credit Scoring | Business | MEDIUM | 5 | 4 | 16 |
| 33 | 53 | Recipe Nutrition Optimisation | Food | MEDIUM | 5 | 4 | 16 |
| 34 | 46 | Deforestation Detection | Environment | MEDIUM | 4 | 4 | 12 |
| 35 | 16 | Skin Lesion Classification | Health | MEDIUM | 4 | 5 | 16 |
| 36 | 9 | Antenna Design Optimisation | Engineering | HIGH | 3 | 4 | 12 |
| 37 | 64 | Crime Hotspot Prediction | Social/Urban | MEDIUM | 4 | 4 | 12 |
| 38 | 2 | Vehicle Aerodynamics Surrogate | Engineering | HIGH | 3 | 3 | 9 |
| 39 | 5 | Wind Turbine Blade Optimisation | Engineering | HIGH | 3 | 3 | 9 |
| 40 | 15 | Protein Function Prediction | Biology | HIGH | 2 | 4 | 8 |

---

## Engineering & Design

### 1. Building Energy Consumption Prediction
- **Domain**: Building engineering / Energy
- **Objective**: Predict hourly/daily energy load of buildings from weather, occupancy, and building features
- **Data/Tool**: BuildingsBench (900K buildings, NREL), ASHRAE Great Energy Predictor III (Kaggle), UCI Energy Efficiency dataset
- **Novelty potential**: HIGH -- current best R2~0.91, rich feature engineering space
- **Approachability**: 5

### 2. Vehicle Aerodynamics Surrogate Model
- **Domain**: Automotive engineering
- **Objective**: Train a surrogate model to predict drag/lift coefficients from vehicle shape parameters, replacing expensive CFD
- **Data/Tool**: SU2 (open-source CFD), SHIFT-SUV model (Honda/NVIDIA), NeuralCFD dataset
- **Novelty potential**: HIGH -- active research area with new deep learning surrogates
- **Approachability**: 3

### 3. Traffic Signal Timing Optimisation
- **Domain**: Transportation engineering
- **Objective**: Optimise traffic light timing to minimise average wait time and congestion
- **Data/Tool**: SUMO simulator (open source), sumo-rl (Gymnasium/PettingZoo RL envs), LightSim benchmark (19 scenarios)
- **Novelty potential**: HIGH -- RL approaches still improving rapidly over classical methods
- **Approachability**: 5

### 4. HVAC System Energy Optimisation
- **Domain**: Building systems
- **Objective**: Optimise heating/cooling schedules to minimise energy use while maintaining comfort
- **Data/Tool**: AlphaBuilding synthetic dataset (DOE), EnergyPlus simulator (open source), Berkeley building dataset
- **Novelty potential**: MEDIUM -- DRL methods showed 21% energy savings, but room for improvement
- **Approachability**: 4

### 5. Wind Turbine Blade Shape Optimisation
- **Domain**: Renewable energy engineering
- **Objective**: Optimise blade airfoil shape and twist distribution to maximise power output
- **Data/Tool**: QBlade (open source, GPU-accelerated), OpenFOAM + DAKOTA, XFOIL
- **Novelty potential**: HIGH -- multi-objective aerostructural optimisation still advancing
- **Approachability**: 3

### 6. Solar Panel Tilt Angle Optimisation
- **Domain**: Solar energy
- **Objective**: Predict and optimise panel tilt/azimuth angles to maximise annual energy yield per location
- **Data/Tool**: NSRDB (satellite irradiance data), PVGIS, NASA POWER datasets
- **Novelty potential**: MEDIUM -- ML models achieve <1 degree error but generalization is open
- **Approachability**: 5

### 7. Heat Exchanger Design Optimisation
- **Domain**: Thermal engineering
- **Objective**: Optimise tube geometry and flow parameters to maximise heat transfer while minimising pressure drop
- **Data/Tool**: CFD-generated datasets (645 geometries typical), OpenFOAM simulations
- **Novelty potential**: MEDIUM -- ML surrogates reduce design time from hours to minutes
- **Approachability**: 3

### 8. Speaker/Acoustic Design Optimisation
- **Domain**: Acoustics engineering
- **Objective**: Optimise speaker enclosure shape and port parameters to flatten frequency response
- **Data/Tool**: COMSOL (academic license), custom FEM solvers, measurement datasets
- **Novelty potential**: MEDIUM -- differentiable acoustics simulation is nascent
- **Approachability**: 4

### 9. Antenna Design Optimisation
- **Domain**: Electromagnetics
- **Objective**: Optimise patch antenna geometry for target frequency response and radiation pattern
- **Data/Tool**: gprMax (open-source EM simulator, GPU-accelerated), FDTDX (JAX-based)
- **Novelty potential**: HIGH -- GPU simulation enables large-scale design space exploration
- **Approachability**: 3

### 10. Packaging Strength-to-Weight Optimisation
- **Domain**: Structural engineering
- **Objective**: Optimise corrugated box geometry to maximise crush strength while minimising material
- **Data/Tool**: FEA simulators (FEniCS, open source), custom datasets from industry papers
- **Novelty potential**: MEDIUM -- topology optimisation with ML surrogates is growing
- **Approachability**: 4

---

## Health & Biology

### 11. Concrete Mix Design Optimisation
- **Domain**: Civil engineering / Materials
- **Objective**: Optimise cement, water, aggregate ratios to maximise compressive strength while minimising cost/CO2
- **Data/Tool**: UCI Concrete Compressive Strength dataset (1030 samples), extended datasets (1507 samples from 23 studies)
- **Novelty potential**: HIGH -- multi-objective optimisation (strength vs CO2 vs cost) is novel
- **Approachability**: 5

### 12. Welding Parameter Optimisation
- **Domain**: Manufacturing
- **Objective**: Optimise welding speed, temperature, voltage to maximise joint strength and minimise defects
- **Data/Tool**: Published datasets (309 records from literature), IEEE experimental datasets
- **Novelty potential**: HIGH -- small-data ML with augmentation is an active frontier
- **Approachability**: 4

### 13. Drug Dosage Personalisation (Warfarin)
- **Domain**: Pharmacology
- **Objective**: Predict optimal warfarin dose from patient genetics and demographics
- **Data/Tool**: International Warfarin Pharmacogenetics Consortium dataset (public)
- **Novelty potential**: MEDIUM -- well-studied but multi-drug generalization is open
- **Approachability**: 4

### 14. Sleep Quality Prediction from Wearables
- **Domain**: Digital health
- **Objective**: Predict self-reported sleep quality from accelerometer/heart rate wearable data
- **Data/Tool**: TILES-2018 benchmark (6000+ sleep recordings, 139 subjects), NetHealth dataset (698 students)
- **Novelty potential**: MEDIUM -- temporal models and feature engineering still improving
- **Approachability**: 5

### 15. Protein Function Prediction
- **Domain**: Bioinformatics
- **Objective**: Predict Gene Ontology / Enzyme Commission function labels from amino acid sequence
- **Data/Tool**: CAFA5 benchmark, Protein Annotation Dataset (PAD), UniProt database
- **Novelty potential**: HIGH -- protein language models vs sequence alignment is active frontier
- **Approachability**: 2

### 16. Skin Lesion Classification
- **Domain**: Medical imaging
- **Objective**: Classify dermoscopic images into skin disease categories (melanoma vs benign)
- **Data/Tool**: HAM10000 (10K images), MedMNIST DermaMNIST, ISIC challenge datasets
- **Novelty potential**: MEDIUM -- gap between lab (99%) and field (85%) accuracy persists
- **Approachability**: 4

### 17. Chest X-Ray Pneumonia Detection
- **Domain**: Medical imaging
- **Objective**: Classify chest X-ray images as normal vs pneumonia
- **Data/Tool**: Kaggle Chest X-Ray dataset (5000+ images), CheXpert (Stanford), MIMIC-CXR
- **Novelty potential**: MEDIUM -- data augmentation and few-shot learning approaches improving
- **Approachability**: 4

### 18. Disease Outbreak Prediction
- **Domain**: Epidemiology
- **Objective**: Predict likelihood and timing of infectious disease outbreaks from historical/environmental data
- **Data/Tool**: WHO FluNet, COVID-19 Global Forecasting (Kaggle), outbreak data from 43 diseases in 206 countries
- **Novelty potential**: MEDIUM -- integrating climate + social media + mobility data is novel
- **Approachability**: 4

---

## Business & Economics

### 19. Customer Churn Prediction
- **Domain**: Telecom / SaaS
- **Objective**: Predict which customers will cancel their subscription from usage and demographic data
- **Data/Tool**: Kaggle Telco Customer Churn dataset, Bank Marketing dataset (UCI)
- **Novelty potential**: MEDIUM -- class imbalance handling and explainability are open problems
- **Approachability**: 5

### 20. Credit Card Fraud Detection
- **Domain**: Financial services
- **Objective**: Detect fraudulent transactions from transaction features under extreme class imbalance
- **Data/Tool**: Kaggle Credit Card Fraud dataset (284K transactions), Amazon Fraud Dataset Benchmark (FDB)
- **Novelty potential**: MEDIUM -- temporal graph methods and real-time detection are advancing
- **Approachability**: 5

### 21. Credit Scoring
- **Domain**: Banking / Finance
- **Objective**: Predict loan default probability from applicant features
- **Data/Tool**: Kaggle Home Credit dataset (356K individuals), HMEQ dataset, Taiwan credit card dataset (UCI)
- **Novelty potential**: MEDIUM -- fairness-aware models and alternative data are novel angles
- **Approachability**: 5

### 22. Dynamic Pricing Optimisation
- **Domain**: E-commerce / Retail
- **Objective**: Optimise product prices in real-time to maximise revenue given demand elasticity
- **Data/Tool**: Kaggle Retail Price Optimization dataset, Alibaba pricing data, OpenAI Gym environments
- **Novelty potential**: HIGH -- DRL approaches show 14-21% revenue improvement
- **Approachability**: 4

### 23. Supply Chain Demand Forecasting
- **Domain**: Logistics
- **Objective**: Forecast product demand across supply chain nodes to minimise stockouts and overstock
- **Data/Tool**: SupplyGraph (FMCG benchmark), M5 Walmart dataset, Grupo Bimbo (Kaggle)
- **Novelty potential**: MEDIUM -- graph neural networks on supply chains are novel
- **Approachability**: 4

### 24. House Price Prediction
- **Domain**: Real estate
- **Objective**: Predict residential property sale prices from property features, location, and market data
- **Data/Tool**: Kaggle House Prices (Ames, 79 features), California Housing (sklearn), Shanghai dataset (175K records)
- **Novelty potential**: MEDIUM -- spatial feature engineering and temporal trends still improving
- **Approachability**: 5

### 25. Startup Success Prediction
- **Domain**: Venture capital
- **Objective**: Predict whether a startup will be acquired, IPO, or fail from funding/team/market features
- **Data/Tool**: Kaggle Startup Success dataset (923 startups, 48 features), Crunchbase data
- **Novelty potential**: MEDIUM -- temporal funding trajectory features are novel
- **Approachability**: 5

### 26. Inventory Demand Forecasting
- **Domain**: Retail / Supply chain
- **Objective**: Predict SKU-level demand to optimise stock levels and reduce waste
- **Data/Tool**: M5 Competition Walmart dataset, Grupo Bimbo (Kaggle), Store Sales forecasting (Kaggle)
- **Novelty potential**: MEDIUM -- hierarchical temporal fusion transformers are advancing
- **Approachability**: 5

---

## Environment & Sustainability

### 27. Wildfire Risk Prediction
- **Domain**: Environmental science
- **Objective**: Predict wildfire occurrence and spread from weather, vegetation, and terrain data
- **Data/Tool**: BCWildfire (25-year, 38 covariates), Next Day Wildfire Spread (Google), California 1984-2025 dataset
- **Novelty potential**: HIGH -- multimodal satellite + weather integration is frontier
- **Approachability**: 5

### 28. Flood Prediction
- **Domain**: Hydrology
- **Objective**: Predict river water levels and flood events from rainfall and terrain data
- **Data/Tool**: FloodCastBench (4 major events, 30m resolution), ERA5/GloFAS reanalysis data
- **Novelty potential**: MEDIUM -- spatio-temporal deep learning models improving rapidly
- **Approachability**: 5

### 29. Air Quality Index Prediction
- **Domain**: Environmental monitoring
- **Objective**: Predict air quality index from meteorological and pollutant sensor data
- **Data/Tool**: UCI Air Quality dataset, Delhi AQI dataset (Kaggle), EPA historical data
- **Novelty potential**: MEDIUM -- hybrid CNN-LSTM models show promise but interpretability lacking
- **Approachability**: 5

### 30. Crop Yield Prediction
- **Domain**: Agriculture
- **Objective**: Predict county/regional crop yields from satellite imagery, weather, and soil data
- **Data/Tool**: CropNet (terabyte-scale, Sentinel-2 + weather), CY-Bench, SustainBench, YieldSAT
- **Novelty potential**: HIGH -- multi-modal fusion (satellite + weather + soil) is frontier
- **Approachability**: 5

### 31. Water Quality Prediction
- **Domain**: Environmental science
- **Objective**: Predict water quality index / potability from sensor measurements
- **Data/Tool**: UCI Water Quality dataset (36 sites), Kaggle water potability dataset (8K samples)
- **Novelty potential**: MEDIUM -- sparse data handling and temporal models are open problems
- **Approachability**: 5

### 32. Deforestation Detection from Satellite
- **Domain**: Environmental monitoring
- **Objective**: Detect and classify deforestation events from satellite imagery
- **Data/Tool**: ForestNet (2756 annotated images), EuroSAT (27K images), Sentinel-2 data
- **Novelty potential**: MEDIUM -- driver attribution (why deforestation?) is novel angle
- **Approachability**: 4

### 33. Bird Species Identification (Audio)
- **Domain**: Ecology / Conservation
- **Objective**: Identify bird species from audio recordings in natural soundscapes
- **Data/Tool**: BirdCLEF competition datasets (50K+ recordings, 659 species), Birds525 images (90K)
- **Novelty potential**: MEDIUM -- noisy real-world soundscapes vs clean recordings gap persists
- **Approachability**: 4

### 34. Renewable Energy Output Forecasting
- **Domain**: Energy / Environment
- **Objective**: Forecast solar and wind farm power output from weather data
- **Data/Tool**: French wind/solar dataset (2012-2023, ERA5 weather), NSRDB, Chinese State Grid competition data
- **Novelty potential**: HIGH -- image-based (weather maps as images) models outperform time series
- **Approachability**: 4

### 35. Urban Heat Island Prediction
- **Domain**: Urban climate
- **Objective**: Predict urban heat island intensity from land use, building density, and weather data
- **Data/Tool**: Sentinel-2/Landsat imagery, ERA5-Land data, ESRI land use classifications
- **Novelty potential**: MEDIUM -- 216-city global models still have MAE~0.86C room to improve
- **Approachability**: 4

---

## Transportation

### 36. Flight Delay Prediction
- **Domain**: Aviation
- **Objective**: Predict flight arrival delays from airline, route, weather, and schedule features
- **Data/Tool**: Kaggle Flight Delay 2018-2024 dataset, BTS On-Time Performance data
- **Novelty potential**: MEDIUM -- weather integration and cascading delay modeling are novel
- **Approachability**: 5

### 37. EV Charging Station Placement
- **Domain**: Urban planning / Energy
- **Objective**: Optimise locations for new EV charging stations to maximise coverage and utilisation
- **Data/Tool**: Palo Alto/Boulder charging event data, OpenStreetMap, census data
- **Novelty potential**: HIGH -- DRL with geospatial data integration is advancing
- **Approachability**: 4

### 38. Bike-Sharing Demand Prediction & Rebalancing
- **Domain**: Urban transportation
- **Objective**: Predict station-level bike demand and optimise rebalancing truck routes
- **Data/Tool**: Divvy Chicago (multi-year), NYC Citi Bike, Suzhou datasets
- **Novelty potential**: HIGH -- spatio-temporal graph neural networks are frontier
- **Approachability**: 5

### 39. Route Optimisation (Vehicle Routing)
- **Domain**: Logistics
- **Objective**: Find optimal delivery routes for a fleet of vehicles with capacity and time window constraints
- **Data/Tool**: VROOM (open source), OR-Tools (Google), PyVRP, SVRPBench, Solomon benchmark instances
- **Novelty potential**: MEDIUM -- ML-enhanced heuristics beating classical optimisers
- **Approachability**: 4

### 40. Drone Delivery Path Planning
- **Domain**: Autonomous systems
- **Objective**: Optimise drone delivery routes considering energy, wind, obstacles, and time
- **Data/Tool**: UavSim (open source), PLANE framework, DRL environments
- **Novelty potential**: HIGH -- physics-aware ML for trajectory optimisation is novel
- **Approachability**: 4

### 41. Shipping Container Loading
- **Domain**: Logistics
- **Objective**: Maximise container volume utilisation while satisfying weight/stability constraints
- **Data/Tool**: RoboBPP benchmark (real industrial data, open source), Bischoff/Ratcliff instances
- **Novelty potential**: MEDIUM -- RL-based packing approaching 90% utilisation
- **Approachability**: 4

---

## Food & Agriculture

### 42. Wine Quality Prediction & Optimisation
- **Domain**: Food science
- **Objective**: Predict wine quality scores from physicochemical properties and suggest optimal blending
- **Data/Tool**: UCI Wine Quality dataset (6497 samples, 11 features), Kaggle wine datasets
- **Novelty potential**: HIGH -- inverse optimisation (what chemistry makes best wine?) is novel
- **Approachability**: 5

### 43. Soil Quality Prediction
- **Domain**: Agriculture
- **Objective**: Predict soil nutrient levels (N, P, K, pH) from satellite imagery and sensor data
- **Data/Tool**: LUCAS Soil dataset, SoilGrid, Sentinel-2 satellite imagery
- **Novelty potential**: HIGH -- satellite-to-soil-nutrient mapping using deep learning is frontier
- **Approachability**: 5

### 44. Food Shelf Life Prediction
- **Domain**: Food technology
- **Objective**: Predict remaining shelf life of perishable foods from sensor/image data
- **Data/Tool**: Custom gas sensor datasets, fruit maturity image datasets (700+ images per class)
- **Novelty potential**: MEDIUM -- CNN-LSTM vs classical Arrhenius models is active comparison
- **Approachability**: 4

### 45. Pest & Disease Detection in Plants
- **Domain**: Agriculture
- **Objective**: Classify crop disease and pest damage from leaf/fruit images
- **Data/Tool**: PlantVillage (54K images, 38 classes), DLCPD-25 (222K images, 203 classes), IP102 pest dataset
- **Novelty potential**: HIGH -- lab-to-field accuracy gap (99% to 70%) is the challenge
- **Approachability**: 5

### 46. Crop Rotation Planning
- **Domain**: Agriculture
- **Objective**: Optimise multi-year crop rotation sequences to maximise yield and soil health
- **Data/Tool**: USDA crop data, FAO AgroEnvironmental datasets, custom simulation models
- **Novelty potential**: MEDIUM -- multi-season optimisation with soil feedback loops is novel
- **Approachability**: 4

### 47. Precision Fertiliser Application
- **Domain**: Agriculture
- **Objective**: Predict optimal fertiliser type and amount per field zone from soil/yield data
- **Data/Tool**: Kaggle Optimal Fertilizer Prediction dataset, soil sensor data, NDVI satellite imagery
- **Novelty potential**: MEDIUM -- variable-rate application maps via ML are advancing
- **Approachability**: 5

### 48. Recipe Nutrition Optimisation
- **Domain**: Food science
- **Objective**: Optimise recipe ingredients to hit nutritional targets while maximising predicted taste
- **Data/Tool**: Recipe1M+ (1M recipes), USDA FoodData Central, FlavorDB, TASTEset (700 recipes)
- **Novelty potential**: MEDIUM -- multi-objective taste-nutrition-cost optimisation is novel
- **Approachability**: 5

---

## Sports & Games

### 49. Football Match Outcome Prediction
- **Domain**: Sports analytics
- **Objective**: Predict match results (win/draw/loss) from team statistics and player data
- **Data/Tool**: European Soccer Database (Kaggle, 25K+ matches), FBref xG data, football-data.co.uk
- **Novelty potential**: MEDIUM -- hybrid CNN-Transformer approaches reaching 75-80% accuracy
- **Approachability**: 5

### 50. Football Player Market Valuation
- **Domain**: Sports economics
- **Objective**: Predict transfer market value of players from performance statistics
- **Data/Tool**: FIFA game dataset (16K+ players), Transfermarkt scraped data, Big Five leagues data
- **Novelty potential**: MEDIUM -- temporal trajectory features and interpretable models are novel
- **Approachability**: 5

### 51. F1 Race Strategy Optimisation
- **Domain**: Motorsport
- **Objective**: Optimise pit stop timing and tyre compound selection to minimise race time
- **Data/Tool**: FastF1 Python library (lap-by-lap data), 2024 season datasets, Monte Carlo race simulator
- **Novelty potential**: HIGH -- explainable RL for race strategy is new research direction
- **Approachability**: 5

### 52. Fantasy Sports Portfolio Optimisation
- **Domain**: Sports analytics
- **Objective**: Select optimal fantasy team roster given salary cap and predicted player performance
- **Data/Tool**: FPL (Fantasy Premier League) API data, DraftKings/FanDuel historical data
- **Novelty potential**: MEDIUM -- combinatorial optimisation with uncertain predictions
- **Approachability**: 5

### 53. Basketball Player Performance Prediction
- **Domain**: Sports analytics
- **Objective**: Predict NBA player performance metrics (PER, Win Shares) from game statistics
- **Data/Tool**: Basketball-Reference data, NBA Stats API (free tier), Kaggle NBA datasets
- **Novelty potential**: MEDIUM -- injury-aware and fatigue-adjusted models are novel
- **Approachability**: 5

### 54. Esports Match Prediction
- **Domain**: Competitive gaming
- **Objective**: Predict match outcomes in competitive games (LoL, CS2, Dota 2) from team/player stats
- **Data/Tool**: OpenDota API, Riot Games API, HLTV statistics, Kaggle esports datasets
- **Novelty potential**: MEDIUM -- real-time draft/pick phase optimisation is novel
- **Approachability**: 5

---

## Waste Sorting & Recycling

### 55. Waste Sorting Image Classification
- **Domain**: Environmental / Recycling
- **Objective**: Classify waste items into recyclable categories from images
- **Data/Tool**: TrashNet (2527 images, 6 classes), RealWaste (4752 images, 9 classes), WasteNet (3M images)
- **Novelty potential**: HIGH -- three-stage hierarchical classification (binary -> 9 -> 36 classes) is novel
- **Approachability**: 5

---

## Manufacturing & Materials

### 56. 3D Printing Parameter Optimisation
- **Domain**: Additive manufacturing
- **Objective**: Optimise FDM print settings (temp, speed, infill) to maximise part strength and quality
- **Data/Tool**: IEEE FDM dataset (500+ samples), SQ-3DP dataset, Kaggle 3D Printer dataset
- **Novelty potential**: HIGH -- multi-objective (strength + surface quality + time) optimisation
- **Approachability**: 5

### 57. Alloy Composition Optimisation
- **Domain**: Materials science
- **Objective**: Predict mechanical properties from alloy composition and suggest optimal formulations
- **Data/Tool**: Zinc alloy databases, Al alloy datasets (277 samples), High-entropy alloy data (181 samples)
- **Novelty potential**: HIGH -- AlloyGPT and inverse design approaches are frontier
- **Approachability**: 3

### 58. Paint/Coating Formulation Optimisation
- **Domain**: Chemical engineering
- **Objective**: Optimise coating ingredient ratios for target gloss, hardness, and durability
- **Data/Tool**: Zenodo lacquer dataset (DOI: 10.5281/zenodo.13742098), Bayesian optimisation frameworks
- **Novelty potential**: HIGH -- high-throughput + Bayesian optimisation reduces dev time 6x
- **Approachability**: 3

### 59. Textile Fabric Property Prediction
- **Domain**: Textile engineering
- **Objective**: Predict fabric GSM, tensile strength, and drape from yarn/weave parameters
- **Data/Tool**: FabricNET dataset, knitted fabric database, published textile datasets
- **Novelty potential**: MEDIUM -- prescriptive (inverse) design of fabrics is novel
- **Approachability**: 3

---

## Energy

### 60. Battery State-of-Health Prediction
- **Domain**: Energy storage
- **Objective**: Predict remaining useful life of lithium-ion batteries from charge/discharge curves
- **Data/Tool**: BatteryLife benchmark (16 datasets, 8 formats), NASA PCoE dataset, Stanford-MIT aging data
- **Novelty potential**: HIGH -- transfer learning across battery chemistries is novel
- **Approachability**: 4

### 61. Solar Irradiance Forecasting
- **Domain**: Solar energy
- **Objective**: Forecast solar irradiance at a location using weather data and sky images
- **Data/Tool**: SuryaBench, NSRDB, Folsom PLC dataset, sky image datasets (multiple locations)
- **Novelty potential**: HIGH -- sky image + weather fusion models outperform time series
- **Approachability**: 4

### 62. Wind Speed Prediction
- **Domain**: Wind energy
- **Objective**: Forecast wind speed at turbine hub height from weather station data
- **Data/Tool**: ERA5 reanalysis data, NREL Wind Toolkit, GFS weather data (public)
- **Novelty potential**: MEDIUM -- spatial interpolation with GNNs is improving
- **Approachability**: 4

### 63. Smart Grid Load Forecasting
- **Domain**: Power systems
- **Objective**: Predict electricity demand at grid nodes to enable better dispatch and storage scheduling
- **Data/Tool**: PSML multi-scale dataset, UCI Electrical Grid Stability dataset, Elia (Belgium) load data
- **Novelty potential**: MEDIUM -- hybrid LSTM-XGBoost frameworks improving accuracy
- **Approachability**: 4

### 64. Solar Panel Placement Optimisation
- **Domain**: Solar energy
- **Objective**: Optimise placement and tilt of solar panels on rooftops to maximise annual generation
- **Data/Tool**: PVGIS (European Commission), Google Sunroof data, NSRDB, LiDAR elevation data
- **Novelty potential**: MEDIUM -- shadow analysis + seasonal optimisation is growing area
- **Approachability**: 5

### 65. Energy Storage Scheduling
- **Domain**: Grid management
- **Objective**: Optimise charge/discharge schedule of battery storage to maximise value from price spreads
- **Data/Tool**: Electricity price datasets (ERCOT, PJM, Nordpool - public), OpenAI Gym environments
- **Novelty potential**: HIGH -- RL for battery arbitrage with renewable uncertainty
- **Approachability**: 4

---

## Social & Urban

### 66. Crime Hotspot Prediction
- **Domain**: Public safety
- **Objective**: Predict spatial-temporal crime density from historical crime, weather, and urban features
- **Data/Tool**: Chicago Crime dataset (public, millions of records), San Francisco Crime (Kaggle), Vancouver dataset
- **Novelty potential**: MEDIUM -- graph convolutional networks achieving 88% accuracy
- **Approachability**: 4

### 67. Parking Availability Prediction
- **Domain**: Smart cities
- **Objective**: Predict parking space availability at street/lot level from historical and real-time data
- **Data/Tool**: SINPA Singapore dataset (1687 lots), CNRPark+EXT (visual), PKLot dataset
- **Novelty potential**: MEDIUM -- multi-source IoT fusion for prediction is growing
- **Approachability**: 5

### 68. Urban Noise Pollution Mapping
- **Domain**: Urban planning
- **Objective**: Predict noise levels across a city from traffic, land use, and building features
- **Data/Tool**: UrbanSound8K (8732 audio clips), Madrid City Council noise data, walking survey datasets
- **Novelty potential**: MEDIUM -- remote sensing imagery for noise prediction is novel
- **Approachability**: 5

### 69. Housing Demand Forecasting
- **Domain**: Urban planning
- **Objective**: Forecast housing demand at neighbourhood level from economic and demographic data
- **Data/Tool**: U.S. Census ACS data, Zillow datasets, satellite imagery for LULC
- **Approachability**: 4
- **Novelty potential**: MEDIUM -- satellite-based urban morphogenesis prediction is emerging

### 70. Emergency Response Optimisation
- **Domain**: Public safety
- **Objective**: Optimise ambulance/fire station locations and dispatch to minimise response times
- **Data/Tool**: Kaggle ambulance route dataset (605 files), Chicago/NYC 911 call data (public)
- **Novelty potential**: MEDIUM -- DRL for dynamic dispatch with real-time traffic is novel
- **Approachability**: 4

---

## Education

### 71. Student Performance Prediction
- **Domain**: Education analytics
- **Objective**: Predict student grades/outcomes from demographic, attendance, and engagement features
- **Data/Tool**: UCI Student Performance dataset (649 samples, 33 features), Kaggle student datasets (50K records)
- **Novelty potential**: MEDIUM -- early warning systems with interpretable models are valuable
- **Approachability**: 5

### 72. Question Difficulty Estimation
- **Domain**: Educational technology
- **Objective**: Predict how difficult a question is from its text content
- **Data/Tool**: Easy2Hard-Bench (NeurIPS 2024, 6 datasets), university exam question datasets
- **Novelty potential**: MEDIUM -- LLM-based estimation vs professor judgment is novel comparison
- **Approachability**: 4

### 73. Learning Path Personalisation
- **Domain**: Educational technology
- **Objective**: Optimise sequence of learning materials for individual students to maximise retention
- **Data/Tool**: EdNet dataset (131M interactions), ASSISTments dataset, Khan Academy data
- **Novelty potential**: HIGH -- knowledge tracing + RL for curriculum optimisation
- **Approachability**: 4

---

## Creative & Media

### 74. Music Recommendation
- **Domain**: Entertainment / AI
- **Objective**: Recommend songs to users based on listening history and audio features
- **Data/Tool**: Million Song Dataset, Spotify dataset (Kaggle), Last.fm data (400K users)
- **Novelty potential**: MEDIUM -- LLM-based recommendation disrupting classical approaches
- **Approachability**: 5

### 75. Image Style Transfer
- **Domain**: Computer vision / Art
- **Objective**: Transfer artistic style from one image to another while preserving content
- **Data/Tool**: MS-COCO, CelebA datasets, pre-trained VGG/ResNet models
- **Novelty potential**: MEDIUM -- diffusion-based style transfer is advancing
- **Approachability**: 4

### 76. Color Palette Generation
- **Domain**: Design / AI
- **Objective**: Generate harmonious color palettes from input constraints or reference images
- **Data/Tool**: Adobe Color data, Dribbble palette scraped data, Colormind datasets
- **Novelty potential**: MEDIUM -- diffusion models for palette generation are novel
- **Approachability**: 5

### 77. Text Summarisation
- **Domain**: NLP
- **Objective**: Generate concise summaries of long documents
- **Data/Tool**: CNN/DailyMail (300K articles), SAMSum (16K dialogues), ArXiv (203K papers)
- **Novelty potential**: MEDIUM -- domain-specific fine-tuning and evaluation metrics are open
- **Approachability**: 4

---

## Additional Engineering Problems (Simulation-Based)

### 78. Soft Robot Locomotion Optimisation
- **Domain**: Robotics
- **Objective**: Optimise soft robot morphology and control for fastest locomotion
- **Data/Tool**: DiffTaichi (differentiable physics, GPU), NVIDIA Warp, Taichi framework
- **Novelty potential**: HIGH -- co-optimisation of shape and control via differentiable sim
- **Approachability**: 4

### 79. Fluid Mixing Optimisation
- **Domain**: Chemical engineering
- **Objective**: Optimise stirrer geometry and speed to minimise mixing time
- **Data/Tool**: DiffTaichi fluid simulator, PhiFlow (differentiable CFD in JAX/PyTorch)
- **Novelty potential**: HIGH -- gradient-based fluid design optimisation is emerging
- **Approachability**: 3

### 80. Elastic Object Shape Optimisation
- **Domain**: Mechanical engineering
- **Objective**: Optimise shape of deformable objects (grippers, springs) for target force-displacement curves
- **Data/Tool**: DiffTaichi ChainQueen (188x faster than TensorFlow), NVIDIA Warp
- **Novelty potential**: HIGH -- differentiable elastic simulation for design is novel
- **Approachability**: 3

### 81. Bridge Topology Optimisation
- **Domain**: Structural engineering
- **Objective**: Optimise truss/beam layout to minimise weight while meeting load requirements
- **Data/Tool**: FEniCS (open-source FEM), TopOpt (topology optimisation tools), SIMP method implementations
- **Novelty potential**: MEDIUM -- ML-accelerated topology optimisation is growing
- **Approachability**: 4

### 82. Water Distribution Network Design
- **Domain**: Civil engineering
- **Objective**: Optimise pipe sizing and layout to minimise cost while maintaining pressure requirements
- **Data/Tool**: EPANET (open-source hydraulic simulator), benchmark networks (Hanoi, BakRyan, Anytown)
- **Novelty potential**: MEDIUM -- RL and surrogate-assisted optimisation are novel approaches
- **Approachability**: 4

---

## Additional Dataset Problems

### 83. Concrete Crack Detection from Images
- **Domain**: Infrastructure inspection
- **Objective**: Detect and classify cracks in concrete surfaces from images
- **Data/Tool**: SDNET2018 (56K images), Kaggle concrete crack dataset, custom bridge inspection datasets
- **Novelty potential**: MEDIUM -- edge deployment and few-shot learning are active areas
- **Approachability**: 5

### 84. Movie Box Office Prediction
- **Domain**: Entertainment
- **Objective**: Predict movie revenue from cast, genre, budget, release date, and social media buzz
- **Data/Tool**: TMDB dataset (Kaggle), IMDB datasets, Box Office Mojo data
- **Novelty potential**: MEDIUM -- social media sentiment integration is novel angle
- **Approachability**: 5

### 85. Taxi Trip Duration Prediction
- **Domain**: Urban transportation
- **Objective**: Predict taxi trip duration from pickup/dropoff location, time, and weather
- **Data/Tool**: NYC Taxi (billions of trips, public), Kaggle NYC Taxi Trip Duration competition
- **Novelty potential**: MEDIUM -- graph-based spatial models improving over baselines
- **Approachability**: 5

### 86. Customer Lifetime Value Prediction
- **Domain**: Marketing
- **Objective**: Predict total future revenue from a customer based on transaction history
- **Data/Tool**: UCI Online Retail dataset, Kaggle e-commerce datasets, RFM analysis frameworks
- **Novelty potential**: MEDIUM -- probabilistic models (BG/NBD) vs deep learning is active area
- **Approachability**: 5

### 87. Job Resume Matching
- **Domain**: HR technology
- **Objective**: Score candidate-job fit from resume text and job description features
- **Data/Tool**: Kaggle Resume Dataset, LinkedIn job posting datasets, O*NET occupational data
- **Novelty potential**: MEDIUM -- fairness-aware matching is an important open problem
- **Approachability**: 4

### 88. Ad Click-Through Rate Prediction
- **Domain**: Digital advertising
- **Objective**: Predict probability of user clicking on an ad given user and ad features
- **Data/Tool**: Criteo CTR dataset (45M rows), Avazu CTR (Kaggle), KDD Cup 2012
- **Novelty potential**: MEDIUM -- feature interaction models (DeepFM, DCN) still improving
- **Approachability**: 4

### 89. Hospital Length-of-Stay Prediction
- **Domain**: Healthcare operations
- **Objective**: Predict how many days a patient will stay from admission features
- **Data/Tool**: MIMIC-IV dataset (public, MIT), Kaggle hospital LOS datasets
- **Novelty potential**: MEDIUM -- temporal event models and survival analysis are improving
- **Approachability**: 4

### 90. Sentiment Analysis for Product Reviews
- **Domain**: NLP / E-commerce
- **Objective**: Classify product review sentiment and extract aspect-level opinions
- **Data/Tool**: Amazon Product Reviews (millions), Yelp reviews (Kaggle), SST-2 benchmark
- **Novelty potential**: MEDIUM -- aspect-based + multimodal (text + images) is novel
- **Approachability**: 5

---

## Additional Simulation Problems

### 91. Airfoil Shape Optimisation
- **Domain**: Aerospace
- **Objective**: Optimise 2D airfoil shape to maximise lift-to-drag ratio at given Reynolds number
- **Data/Tool**: XFOIL (open-source), SU2 (CFD), UIUC Airfoil Database (1600+ airfoils)
- **Novelty potential**: HIGH -- differentiable RANS solvers are emerging
- **Approachability**: 3

### 92. Acoustic Room Design
- **Domain**: Architectural acoustics
- **Objective**: Optimise room shape and surface materials to achieve target reverberation time
- **Data/Tool**: Pyroomacoustics (open-source), openPSTD, room impulse response datasets
- **Novelty potential**: MEDIUM -- differentiable room acoustics simulation is nascent
- **Approachability**: 4

### 93. PCB Thermal Management
- **Domain**: Electronics
- **Objective**: Optimise component placement on PCB to minimise hotspot temperatures
- **Data/Tool**: OpenFOAM (thermal simulation), KiCad (open-source PCB), thermal imaging datasets
- **Novelty potential**: MEDIUM -- ML surrogate for thermal simulation is growing
- **Approachability**: 3

### 94. Spring/Damper System Optimisation
- **Domain**: Mechanical engineering
- **Objective**: Optimise spring-damper parameters for target vibration isolation characteristics
- **Data/Tool**: DiffTaichi, custom ODE solvers (scipy/JAX), automotive suspension datasets
- **Novelty potential**: MEDIUM -- differentiable dynamics for vibration design
- **Approachability**: 4

---

## Additional Approachable Problems

### 95. Diabetes Prediction
- **Domain**: Healthcare
- **Objective**: Predict diabetes onset from health metrics (BMI, glucose, blood pressure)
- **Data/Tool**: Pima Indians Diabetes dataset (UCI/Kaggle, 768 samples), NHANES data
- **Novelty potential**: LOW -- well-studied but novel feature combinations possible
- **Approachability**: 5

### 96. Heart Disease Prediction
- **Domain**: Healthcare
- **Objective**: Predict heart disease presence from clinical measurements
- **Data/Tool**: UCI Heart Disease dataset, Cleveland/Hungarian datasets, Kaggle heart datasets
- **Novelty potential**: LOW -- classic benchmark but interpretability is valued
- **Approachability**: 5

### 97. Titanic Survival Prediction (Meta-ML)
- **Domain**: Meta-learning
- **Objective**: Use as a testbed for novel AutoML/meta-learning approaches that generalize
- **Data/Tool**: Kaggle Titanic dataset (891 training samples, 12 features)
- **Novelty potential**: LOW -- novel only as meta-learning benchmark
- **Approachability**: 5

### 98. Mushroom Edibility Classification
- **Domain**: Biology
- **Objective**: Classify mushrooms as edible or poisonous from physical features
- **Data/Tool**: UCI Mushroom dataset (8124 samples, 22 features), expanded Kaggle versions
- **Novelty potential**: LOW -- near-perfect accuracy achieved, but uncertainty quantification novel
- **Approachability**: 5

### 99. Electric Vehicle Range Prediction
- **Domain**: Automotive
- **Objective**: Predict remaining driving range from battery state, driving style, and weather
- **Data/Tool**: MyElectricVehicle dataset, open EV fleet data, Kaggle EV datasets
- **Novelty potential**: MEDIUM -- route-aware range prediction incorporating terrain is novel
- **Approachability**: 5

### 100. Earthquake Damage Prediction
- **Domain**: Civil engineering
- **Objective**: Predict building damage grade from building features and earthquake characteristics
- **Data/Tool**: DrivenData Earthquake Damage competition (260K buildings), USGS earthquake data
- **Novelty potential**: MEDIUM -- ordinal regression approaches and spatial features are open
- **Approachability**: 5

---

## Bonus Candidates (101-120)

### 101. Steel Plate Defect Classification
- **Domain**: Manufacturing QC
- **Objective**: Classify steel plate surface defects from sensor measurements
- **Data/Tool**: UCI Steel Plates Faults dataset (1941 samples, 27 features, 7 fault types)
- **Novelty potential**: MEDIUM -- multi-label classification with imbalanced classes
- **Approachability**: 4

### 102. Forest Cover Type Prediction
- **Domain**: Ecology
- **Objective**: Predict forest cover type from cartographic variables
- **Data/Tool**: UCI/Kaggle Forest Cover Type dataset (581K samples, 54 features, 7 classes)
- **Novelty potential**: LOW -- classic benchmark but spatial modeling is novel angle
- **Approachability**: 5

### 103. Taxi Fare Prediction
- **Domain**: Transportation
- **Objective**: Predict taxi fare from route and time features
- **Data/Tool**: NYC Taxi Fare Prediction (Kaggle, 55M rows)
- **Novelty potential**: LOW -- massive scale makes novel architectures interesting
- **Approachability**: 5

### 104. Used Car Price Prediction
- **Domain**: Automotive retail
- **Objective**: Predict resale price of used cars from make, model, mileage, and condition
- **Data/Tool**: Kaggle used car datasets (multiple), AutoTrader scraped data
- **Novelty potential**: MEDIUM -- regional market dynamics and depreciation curves
- **Approachability**: 5

### 105. Spotify Song Popularity Prediction
- **Domain**: Music analytics
- **Objective**: Predict song popularity score from audio features (tempo, energy, danceability)
- **Data/Tool**: Spotify Audio Features dataset (Kaggle), Spotify API
- **Novelty potential**: MEDIUM -- temporal trending patterns and genre evolution
- **Approachability**: 5

### 106. Aquaculture Fish Growth Prediction
- **Domain**: Aquaculture
- **Objective**: Predict fish growth rates from water quality, feed, and environmental parameters
- **Data/Tool**: FAO aquaculture datasets, published fish farm studies, Kaggle fish datasets
- **Novelty potential**: MEDIUM -- multi-species transfer learning is novel
- **Approachability**: 4

### 107. Optical Network Design
- **Domain**: Telecommunications
- **Objective**: Optimise fiber optic network topology to minimise cost and maximise throughput
- **Data/Tool**: SNDlib (network design benchmark instances, public)
- **Novelty potential**: MEDIUM -- GNN-based topology optimisation is emerging
- **Approachability**: 3

### 108. Hotel Booking Cancellation Prediction
- **Domain**: Hospitality
- **Objective**: Predict whether a hotel booking will be cancelled from reservation features
- **Data/Tool**: Kaggle Hotel Booking Demand dataset (119K bookings)
- **Novelty potential**: MEDIUM -- temporal patterns and pricing interaction effects
- **Approachability**: 5

### 109. Kickstarter Success Prediction
- **Domain**: Crowdfunding
- **Objective**: Predict whether a Kickstarter project will reach its funding goal
- **Data/Tool**: Kaggle Kickstarter dataset (378K projects), Web Robots Kickstarter data
- **Novelty potential**: MEDIUM -- NLP on project descriptions + temporal funding curves
- **Approachability**: 5

### 110. Bike Frame Structural Optimisation
- **Domain**: Product design
- **Objective**: Optimise bicycle frame tube dimensions to minimise weight while meeting stiffness targets
- **Data/Tool**: FEniCS (open-source FEM), published frame geometry datasets
- **Novelty potential**: MEDIUM -- topology optimisation for bicycle frames is underexplored
- **Approachability**: 4

### 111. Restaurant Health Inspection Score Prediction
- **Domain**: Public health
- **Objective**: Predict restaurant inspection scores from review text and historical violations
- **Data/Tool**: Yelp dataset challenge (6M reviews), NYC DOHMH inspection results (public)
- **Novelty potential**: MEDIUM -- NLP sentiment as proxy for food safety is novel
- **Approachability**: 5

### 112. Rainfall Prediction
- **Domain**: Meteorology
- **Objective**: Predict daily rainfall from atmospheric and satellite measurements
- **Data/Tool**: Kaggle Rain in Australia dataset, ERA5 reanalysis, CHIRPS rainfall data
- **Novelty potential**: MEDIUM -- satellite image + station data fusion is improving
- **Approachability**: 5

### 113. Solar Cell Efficiency Optimisation
- **Domain**: Photovoltaics
- **Objective**: Optimise thin-film solar cell layer thicknesses to maximise power conversion efficiency
- **Data/Tool**: FDTDX (differentiable FDTD in JAX), published solar cell datasets, SCAPS simulator
- **Novelty potential**: HIGH -- differentiable optical simulation for cell design
- **Approachability**: 3

### 114. Insurance Claim Prediction
- **Domain**: Insurance
- **Objective**: Predict insurance claim amount or probability from policyholder features
- **Data/Tool**: Kaggle Allstate Claims Severity, Porto Seguro Safe Driver, Prudential Life Insurance datasets
- **Novelty potential**: MEDIUM -- zero-inflated models and fairness constraints
- **Approachability**: 5

### 115. Power Plant Energy Output Prediction
- **Domain**: Energy
- **Objective**: Predict power plant hourly output from ambient conditions
- **Data/Tool**: UCI Combined Cycle Power Plant dataset (9568 samples, 4 features)
- **Novelty potential**: LOW -- well-studied but transfer across plant types is open
- **Approachability**: 5

### 116. Taxi Demand Hotspot Prediction
- **Domain**: Urban mobility
- **Objective**: Predict spatial-temporal taxi demand patterns across city zones
- **Data/Tool**: NYC TLC trip data (billions of records, public), Singapore taxi datasets
- **Novelty potential**: MEDIUM -- multi-resolution spatio-temporal models
- **Approachability**: 5

### 117. Carbon Footprint Estimation
- **Domain**: Sustainability
- **Objective**: Predict product/process carbon footprint from ingredient/process parameters
- **Data/Tool**: Carbon Disclosure Project data, EPA emissions datasets, LCA databases (ecoinvent)
- **Novelty potential**: MEDIUM -- ML-based rapid LCA is an emerging area
- **Approachability**: 4

### 118. Employee Attrition Prediction
- **Domain**: Human resources
- **Objective**: Predict which employees are likely to leave from HR metrics and survey data
- **Data/Tool**: IBM HR Analytics dataset (Kaggle, 1470 samples), Kaggle employee attrition datasets
- **Novelty potential**: LOW -- small datasets but interpretability and fairness are novel angles
- **Approachability**: 5

### 119. Calorie Burn Prediction
- **Domain**: Fitness / Health
- **Objective**: Predict calories burned during exercise from biometric and activity data
- **Data/Tool**: Kaggle Playground S5E5 (calorie burn prediction), Fitbit/wearable datasets
- **Novelty potential**: LOW -- well-studied but personalised models are improving
- **Approachability**: 5

### 120. Public Transit Scheduling Optimisation
- **Domain**: Urban transportation
- **Objective**: Optimise bus/train schedules to minimise passenger wait times and operational costs
- **Data/Tool**: MATSim (open source), SUMO, GTFS public transit data (standard format, global availability)
- **Novelty potential**: MEDIUM -- multi-objective (service quality vs cost) with demand uncertainty
- **Approachability**: 4

---

## Key Open-Source Frameworks Referenced

| Framework | Type | GPU | Link |
|-----------|------|-----|------|
| DiffTaichi | Differentiable physics simulation | Yes | github.com/taichi-dev/difftaichi |
| NVIDIA Warp | Differentiable graphics/physics | Yes | github.com/NVIDIA/warp |
| PhiFlow | Differentiable fluid simulation | Yes (JAX/PyTorch) | github.com/tum-pbs/PhiFlow |
| FDTDX | Differentiable FDTD (optics) | Yes (JAX) | github.com/fdtdx |
| SUMO | Traffic simulation | CPU | eclipse.dev/sumo |
| QBlade | Wind turbine simulation | Yes | qblade.org |
| SU2 | CFD (adjoint-capable) | CPU | su2code.github.io |
| EnergyPlus | Building energy simulation | CPU | energyplus.net |
| FEniCS | Finite element method | CPU | fenicsproject.org |
| EPANET | Hydraulic network simulation | CPU | epanet.org |
| OR-Tools | Optimisation/routing | CPU | developers.google.com/optimization |
| gprMax | EM simulation | Yes | gprmax.com |
| OpenFOAM | General CFD | CPU/GPU | openfoam.org |
| MATSim | Transport simulation | CPU | matsim.org |

---

## Recommended Starting Points

For someone new to HDR, these five problems offer the best combination of easy entry, clear benchmarks, and publication potential:

1. **Concrete Mix Design Optimisation (#11)** -- UCI dataset, clear multi-objective (strength vs cost vs CO2), rich feature space
2. **3D Printing Parameter Optimisation (#56)** -- Tabular data, clear physical objectives, small datasets that benefit from clever ML
3. **Traffic Signal Timing (#3)** -- SUMO-RL gives plug-and-play RL environment, 19 benchmark scenarios
4. **Wine Quality Optimisation (#42)** -- Classic dataset but inverse design angle is novel and publishable
5. **Wildfire Risk Prediction (#27)** -- Large-scale multimodal dataset, high societal impact, clear room for improvement
