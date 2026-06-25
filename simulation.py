import random
import matplotlib.pyplot as plt
import numpy as np

# -------------------------
# Employee (Agent)
# -------------------------
class Employee:
    def __init__(self):
        # Separate awareness into knowledge vs vigilance
        self.knowledge = random.uniform(0.3, 0.9)
        self.vigilance = random.uniform(0.3, 0.9)
        self.stress = random.uniform(0.1, 0.7)

        # Personality traits
        self.risk_tolerance = random.uniform(0, 1)
        self.conscientiousness = random.uniform(0, 1)

        # Track repeat behavior
        self.click_history = 0
        self.needs_training = False

        # History for analysis
        self.awareness_history = []
        self.click_log = []

    @property
    def awareness(self):
        # Composite: knowledge is retained, vigilance is state-dependent
        return 0.5 * self.knowledge + 0.5 * self.vigilance

    def will_click(self, email):
        repeat_risk = min(self.click_history * 0.05, 0.3)

        # Normalized weights (sum to 1.0)
        raw_score = (
            0.20 * (1 - self.knowledge) +
            0.15 * (1 - self.vigilance) +
            0.10 * self.stress +
            0.10 * self.risk_tolerance +
            0.10 * (1 - self.conscientiousness) +
            0.15 * email["urgency"] * self.stress +
            0.15 * email["authority"] * (1 - self.knowledge) +
            0.05 * repeat_risk
        )

        probability = min(max(raw_score, 0), 1)
        return random.random() < probability

    def train(self):
        # Training improves knowledge (retained) more than vigilance
        knowledge_gain = 0.06 * (1 - self.knowledge) * (0.5 + self.conscientiousness)
        vigilance_gain = 0.04 * (1 - self.vigilance) * (0.5 + self.conscientiousness)

        self.knowledge = min(self.knowledge + knowledge_gain, 1.0)
        self.vigilance = min(self.vigilance + vigilance_gain, 1.0)
        self.needs_training = False

    def decay(self):
        # Knowledge decays slowly, vigilance decays faster
        if self.knowledge > 0.6:
            self.knowledge -= 0.002
        if self.vigilance > 0.5:
            self.vigilance -= 0.008

        self.knowledge = max(self.knowledge, 0)
        self.vigilance = max(self.vigilance, 0)

    def log_state(self, week, clicked):
        self.awareness_history.append(self.awareness)
        self.click_log.append(clicked)


# -------------------------
# SOC Detection Layer
# -------------------------
def soc_detect(email, base_detection_rate=0.4):
    # Higher urgency/authority emails are more anomalous → easier to detect
    detection_rate = base_detection_rate + 0.2 * email["urgency"] + 0.1 * email["authority"]
    return random.random() < min(detection_rate, 0.95)


# -------------------------
# Email Types
# -------------------------
email_types = [
    {"name": "generic",      "urgency": 0.2, "authority": 0.2},
    {"name": "urgent",       "urgency": 0.8, "authority": 0.3},
    {"name": "boss_request", "urgency": 0.6, "authority": 0.9},
]

# -------------------------
# Simulation Setup
# -------------------------
num_employees = 100
weeks = 12

employees = [Employee() for _ in range(num_employees)]

# Per-week tracking
click_results = []
detected_results = []
click_by_email_type = {e["name"]: [] for e in email_types}
weekly_email_log = []

# -------------------------
# Simulation Loop
# -------------------------
for week in range(weeks):

    # Stress fluctuations — bounded before use
    for emp in employees:
        if week in [4, 8]:
            emp.stress += 0.3
        else:
            emp.stress += random.uniform(-0.05, 0.05)
        emp.stress -= 0.1 * emp.conscientiousness
        emp.stress = min(max(emp.stress, 0), 1)

    # Weighted email selection
    email = random.choices(email_types, weights=[0.5, 0.3, 0.2])[0]
    weekly_email_log.append(email["name"])

    clicks = 0
    detected = 0
    high_risk_clicks = 0
    low_conscientious_clicks = 0

    for emp in employees:
        clicked = emp.will_click(email)

        if clicked:
            clicks += 1
            emp.click_history += 1
            emp.needs_training = True

            if soc_detect(email):
                detected += 1

            if emp.risk_tolerance > 0.7:
                high_risk_clicks += 1
            if emp.conscientiousness < 0.3:
                low_conscientious_clicks += 1

        # Event-driven training: only train if flagged
        if emp.needs_training:
            emp.train()
        emp.decay()
        emp.log_state(week, clicked)

    click_results.append(clicks)
    detected_results.append(detected)

    # Track clicks per email type
    for e in email_types:
        if e["name"] == email["name"]:
            click_by_email_type[e["name"]].append(clicks)
        else:
            click_by_email_type[e["name"]].append(0)

    print(f"Week {week+1} [{email['name']:>12}]: {clicks:>3} clicks | SOC detected: {detected:>3} | "
          f"High-risk: {high_risk_clicks} | Low-conscientious: {low_conscientious_clicks}")


# -------------------------
# Plot Results
# -------------------------
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Phishing Simulation Results", fontsize=14, fontweight="bold")

# 1. Click rate over time
axes[0, 0].plot(range(1, weeks + 1), click_results, marker="o", color="crimson")
axes[0, 0].set_title("Total Phishing Clicks Over Time")
axes[0, 0].set_xlabel("Week")
axes[0, 0].set_ylabel("Clicks")
axes[0, 0].set_xticks(range(1, weeks + 1))

# 2. Clicks by email type (stacked area)
bottom = np.zeros(weeks)
colors = ["steelblue", "orange", "green"]
for (etype, vals), color in zip(click_by_email_type.items(), colors):
    axes[0, 1].bar(range(1, weeks + 1), vals, bottom=bottom, label=etype, color=color, alpha=0.8)
    bottom += np.array(vals)
axes[0, 1].set_title("Clicks by Email Type")
axes[0, 1].set_xlabel("Week")
axes[0, 1].set_ylabel("Clicks")
axes[0, 1].legend()
axes[0, 1].set_xticks(range(1, weeks + 1))

# 3. Final awareness score distribution
final_awareness = [emp.awareness for emp in employees]
axes[1, 0].hist(final_awareness, bins=20, color="mediumseagreen", edgecolor="black")
axes[1, 0].set_title("Final Awareness Score Distribution")
axes[1, 0].set_xlabel("Awareness Score")
axes[1, 0].set_ylabel("Number of Employees")

# 4. Risk tolerance vs conscientiousness heatmap (colored by click rate)
rt_vals = [emp.risk_tolerance for emp in employees]
con_vals = [emp.conscientiousness for emp in employees]
total_clicks = [sum(emp.click_log) for emp in employees]

sc = axes[1, 1].scatter(rt_vals, con_vals, c=total_clicks, cmap="YlOrRd", edgecolors="gray", alpha=0.8)
fig.colorbar(sc, ax=axes[1, 1], label="Total Clicks")
axes[1, 1].set_title("Risk Tolerance vs Conscientiousness\n(color = total clicks)")
axes[1, 1].set_xlabel("Risk Tolerance")
axes[1, 1].set_ylabel("Conscientiousness")

plt.tight_layout()
plt.savefig("phishing_simulation_results.png", dpi=150)
plt.show()
