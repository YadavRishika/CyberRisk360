const API = "/api";
let trendChart = null;
let contributorsChart = null;
let currentOrgId = null;
let activeAlertId = null;

const bandClass = (band) => `band-${(band || "").toLowerCase()}`;

async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || `Request failed: ${res.status}`);
  }
  return res.json();
}

function money(n) {
  return "\u20b9" + Number(n).toLocaleString("en-IN", { maximumFractionDigits: 0 });
}

async function loadOrganizations() {
  const orgs = await fetchJSON(`${API}/organizations`);
  const select = document.getElementById("org-select");
  select.innerHTML = "";
  orgs.forEach((org) => {
    const opt = document.createElement("option");
    opt.value = org.org_id;
    opt.textContent = org.name;
    select.appendChild(opt);
  });
  if (orgs.length) {
    currentOrgId = orgs[0].org_id;
    select.value = currentOrgId;
    await loadDashboard(currentOrgId);
  }
}

async function loadDashboard(orgId) {
  const data = await fetchJSON(`${API}/dashboard/${orgId}`);
  renderCaseSummary(data);
  renderTrendChart(data.trend);
  renderExplanation(data.explanation);
  renderSignal(data.latest_signal);
  renderGaps(data.coverage_gaps);
  renderAlerts(data.alerts);
  await renderHistory(data.alerts);
  document.getElementById("disclaimer-bar").textContent = data.disclaimer;
}

function renderCaseSummary(data) {
  const { organization, current_assessment, pending_review_count } = data;
  document.getElementById("org-name").textContent = organization.name;
  document.getElementById("org-industry").textContent = organization.industry;
  document.getElementById("org-size").textContent = organization.size_category;
  document.getElementById("org-last-date").textContent = current_assessment.assessment_date;
  document.getElementById("org-pending").textContent = pending_review_count;

  const scoreEl = document.getElementById("risk-score");
  scoreEl.textContent = current_assessment.risk_score;
  scoreEl.className = "score-number band-text-" + current_assessment.risk_band.toLowerCase();

  const bandEl = document.getElementById("risk-band");
  bandEl.textContent = current_assessment.risk_band + " risk";
  bandEl.className = "score-band " + bandClass(current_assessment.risk_band);
}

function renderTrendChart(trend) {
  const ctx = document.getElementById("trend-chart");
  const labels = trend.map((t) => t.date);
  const scores = trend.map((t) => t.score);

  if (trendChart) trendChart.destroy();
  trendChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [{
        label: "Risk score",
        data: scores,
        borderColor: "#1F6F78",
        backgroundColor: "#1F6F7822",
        tension: 0.25,
        fill: true,
        pointRadius: 3,
      }],
    },
    options: {
      plugins: { legend: { display: false }, title: { display: true, text: "Risk score trend" } },
      scales: { y: { min: 0, max: 100 } },
    },
  });
}

function renderExplanation(explanation) {
  document.getElementById("explain-headline").textContent = explanation.headline;
  document.getElementById("recommended-action").textContent = "Recommended action: " + explanation.recommended_action;

  const tbody = document.querySelector("#contributors-table tbody");
  tbody.innerHTML = "";
  explanation.main_contributors.forEach((c) => {
    const tr = document.createElement("tr");
    const changeClass = c.point_change > 0 ? "pos" : "neg";
    tr.innerHTML = `<td>${c.factor}</td><td class="${changeClass}">${c.point_change > 0 ? "+" : ""}${c.point_change}</td><td>${c.direction}</td>`;
    tbody.appendChild(tr);
  });

  const ctx = document.getElementById("contributors-chart");
  if (contributorsChart) contributorsChart.destroy();
  contributorsChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: explanation.main_contributors.map((c) => c.factor),
      datasets: [{
        label: "Point change",
        data: explanation.main_contributors.map((c) => c.point_change),
        backgroundColor: explanation.main_contributors.map((c) => (c.point_change > 0 ? "#C4572A" : "#2E7D5B")),
      }],
    },
    options: {
      indexAxis: "y",
      plugins: { legend: { display: false }, title: { display: true, text: "Main risk contributors" } },
    },
  });
}

function renderSignal(signal) {
  const tbody = document.querySelector("#signal-table tbody");
  tbody.innerHTML = "";
  if (!signal) return;
  const rows = [
    ["Critical vulnerabilities", signal.critical_vulnerabilities],
    ["Patch compliance", signal.patch_compliance_pct + "%"],
    ["MFA coverage", signal.mfa_coverage_pct + "%"],
    ["Security incidents", signal.security_incidents],
    ["Backup compliance", signal.backup_compliance_pct + "%"],
    ["Endpoint protection", signal.endpoint_protection_pct + "%"],
    ["Security training compliance", signal.training_compliance_pct + "%"],
    ["Avg. vulnerability remediation time", signal.avg_remediation_days + " days"],
  ];
  rows.forEach(([label, value]) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${label}</td><td>${value}</td>`;
    tbody.appendChild(tr);
  });
}

function renderGaps(gaps) {
  const tbody = document.querySelector("#gap-table tbody");
  tbody.innerHTML = "";
  gaps.forEach((g) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${g.category}</td>
      <td>${money(g.estimated_exposure)}</td>
      <td>${money(g.existing_coverage)}</td>
      <td class="${g.gap_detected ? "gap-yes" : "gap-no"}">${g.gap_detected ? money(g.gap_amount) : "—"}</td>
      <td class="${g.gap_detected ? "gap-yes" : "gap-no"}">${g.gap_detected ? "Gap detected" : "Adequate"}</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderAlerts(alerts) {
  const container = document.getElementById("alerts-list");
  container.innerHTML = "";
  if (!alerts.length) {
    container.innerHTML = '<p class="subtle">No alerts generated for this account yet.</p>';
    return;
  }
  alerts.forEach((a) => {
    const statusClass = {
      "Pending Analyst Review": "status-pending",
      "Approved": "status-approved",
      "Rejected": "status-rejected",
      "Info Requested": "status-info",
    }[a.status];
    const badgeColor = {
      "Pending Analyst Review": "var(--high)",
      "Approved": "var(--low)",
      "Rejected": "var(--critical)",
      "Info Requested": "var(--medium)",
    }[a.status];

    const card = document.createElement("div");
    card.className = `alert-card ${statusClass}`;
    card.innerHTML = `
      <div class="alert-top">
        <span class="alert-id">Alert #${a.alert_id} — ${a.previous_score ?? "—"} \u2192 ${a.current_score}</span>
        <span class="alert-status" style="background:${badgeColor}">${a.status}</span>
      </div>
      <p class="alert-reason">${a.main_reason}</p>
      <p class="alert-recommendation">${a.recommendation}</p>
      ${a.status === "Pending Analyst Review" ? `<div class="alert-actions"><button class="btn btn-review" data-alert-id="${a.alert_id}">Review</button></div>` : ""}
    `;
    container.appendChild(card);
  });

  container.querySelectorAll(".btn-review").forEach((btn) => {
    btn.addEventListener("click", () => openReviewModal(btn.dataset.alertId, alerts));
  });
}

async function renderHistory(alerts) {
  const tbody = document.querySelector("#history-table tbody");
  tbody.innerHTML = "";
  for (const a of alerts) {
    const { history } = await fetchJSON(`${API}/alerts/${a.alert_id}/history`);
    history.forEach((h) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td>${new Date(h.action_at).toLocaleString()}</td><td>#${a.alert_id}</td><td>${h.action}</td><td>${h.notes ?? ""}</td>`;
      tbody.appendChild(tr);
    });
  }
}

function openReviewModal(alertId, alerts) {
  activeAlertId = alertId;
  const alert = alerts.find((a) => String(a.alert_id) === String(alertId));
  document.getElementById("modal-alert-id").textContent = alertId;
  document.getElementById("modal-alert-reason").textContent = alert.main_reason;
  document.getElementById("analyst-name").value = "";
  document.getElementById("analyst-comments").value = "";
  document.getElementById("review-modal").classList.add("open");
}

function closeReviewModal() {
  document.getElementById("review-modal").classList.remove("open");
  activeAlertId = null;
}

async function submitReview(decision) {
  const analystName = document.getElementById("analyst-name").value.trim();
  const comments = document.getElementById("analyst-comments").value.trim();
  if (!analystName) {
    alert("Analyst name is required before submitting a decision.");
    return;
  }
  await fetchJSON(`${API}/alerts/${activeAlertId}/review`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ analyst_name: analystName, decision, comments }),
  });
  closeReviewModal();
  await loadDashboard(currentOrgId);
}

async function simulateSnapshot(direction) {
  await fetchJSON(`${API}/simulate/${currentOrgId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ direction }),
  });
  await loadDashboard(currentOrgId);
}

document.addEventListener("DOMContentLoaded", () => {
  loadOrganizations();

  document.getElementById("org-select").addEventListener("change", (e) => {
    currentOrgId = e.target.value;
    loadDashboard(currentOrgId);
  });

  document.getElementById("simulate-worsen").addEventListener("click", () => simulateSnapshot("worsen"));
  document.getElementById("simulate-improve").addEventListener("click", () => simulateSnapshot("improve"));

  document.getElementById("modal-close").addEventListener("click", closeReviewModal);
  document.querySelectorAll(".modal-actions .btn").forEach((btn) => {
    btn.addEventListener("click", () => submitReview(btn.dataset.decision));
  });
});
