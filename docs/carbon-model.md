# Cloud Energy & Scope-2 Carbon Model

## 1. Cloud Server Energy Calculation
Energy consumption is modeled using cloud runner power characteristics and Power Usage Effectiveness (PUE):

$$\text{Power (Watts)} = P_{\text{idle}} + (P_{\text{max}} - P_{\text{idle}}) \times \text{CPU\_Utilization}$$

$$E (\text{kWh}) = \frac{\text{Power (Watts)} \times \left(\frac{\text{Duration (seconds)}}{3600}\right) \times \text{PUE}}{1000}$$

### Default Parameters
- $P_{\text{idle}}$: 10.0 Watts (Standard 2-core Linux runner)
- $P_{\text{max}}$: 50.0 Watts (Peak utilization)
- $\text{CPU\_Utilization}$: 0.70 (70% mean during test execution)
- $\text{PUE}$: 1.150 (Modern hyperscale cloud data center efficiency)

## 2. Scope-2 Carbon Emissions Calculation
Emissions represent the electricity-grid generation footprint:

$$\text{CO}_2\text{e (grams)} = E (\text{kWh}) \times \text{Grid\_Carbon\_Intensity} (\text{gCO}_2\text{e/kWh})$$

## 3. Electricity Maps Regional Integration & Caching
- **Cache**: Cached in Redis for 60 minutes (`TTL = 3600s`).
- **Resilience**: If the external API is unreachable or rate-limited, stale cached readings are utilized with `stale=True`. If no cache is present, regional baselines are applied with clear metadata warnings.
