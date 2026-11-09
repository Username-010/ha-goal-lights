const CARD = "goal-lights-card";

class GoalLightsCard extends HTMLElement {
  constructor() {
    super();
    this._config = {};
    this.attachShadow({ mode: "open" });
  }

  setConfig(config) {
    if (!config || !config.tracker) throw new Error("Set tracker to a Team Tracker sensor");
    this._config = config;
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  getCardSize() {
    return 4;
  }

  static getStubConfig() {
    return { tracker: "", team: "" };
  }

  _call(domain, service, data) {
    this._hass.callService(domain, service, data);
  }

  _render() {
    const hass = this._hass;
    const cfg = this._config || {};
    if (!hass) return;
    const st = hass.states[cfg.tracker];
    const a = (st && st.attributes) || {};
    const teamName = a.team_name || a.team_abbr || cfg.team || "Team";
    const opp = a.opponent_name || a.opponent_abbr || "Opponent";
    const us = a.team_score ?? "–";
    const them = a.opponent_score ?? "–";
    const clock = a.clock || st?.state || "";
    const kick = a.kickoff_in || a.date || "";
    const event = a.event_name || `${teamName} vs ${opp}`;
    const state = st ? st.state : "unknown";
    const live = state === "IN";
    const accent = cfg.outline_color || cfg.accent || "#c8102e";
    const watchEid = cfg.watch;
    const watchOn = watchEid && hass.states[watchEid] ? hass.states[watchEid].state === "on" : true;
    const team = cfg.team || "";

    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        ha-card { padding: 14px 14px 10px; }
        .row { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
        .event { font-size: 0.85rem; color: var(--secondary-text-color); margin-bottom: 6px; }
        .score { font-size: 2rem; font-weight: 800; letter-spacing: -0.03em; }
        .names { display: flex; justify-content: space-between; font-weight: 600; margin-top: 2px; }
        .badge {
          font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 999px;
          background: ${live ? accent : "var(--divider-color)"}; color: ${live ? "#fff" : "var(--secondary-text-color)"};
        }
        .actions { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; margin-top: 12px; }
        button {
          border: 1px solid var(--divider-color); background: var(--secondary-background-color);
          color: var(--primary-text-color); border-radius: 10px; padding: 8px 6px; cursor: pointer; font: inherit;
        }
        button:active { transform: scale(0.98); }
        .watch {
          display: flex; align-items: center; gap: 8px; margin-top: 10px; font-size: 0.9rem;
        }
        input[type=checkbox] { width: 18px; height: 18px; }
        .meta { color: var(--secondary-text-color); font-size: 0.85rem; margin-top: 4px; }
      </style>
      <ha-card>
        <div class="row">
          <div class="event">${event}</div>
          <span class="badge">${live ? clock || "LIVE" : state}</span>
        </div>
        <div class="score">${us} – ${them}</div>
        <div class="names"><span>${teamName}</span><span>${opp}</span></div>
        <div class="meta">${kick ? "Kick-off " + kick : ""}</div>
        ${watchEid ? `<label class="watch"><input type="checkbox" id="w" ${watchOn ? "checked" : ""}/> Watch (flash + goaltune)</label>` : ""}
        <div class="actions">
          <button id="g">Test goal</button>
          <button id="k">Kick-off</button>
          <button id="h">2nd half</button>
        </div>
      </ha-card>
    `;
    const w = this.shadowRoot.getElementById("w");
    if (w && watchEid) {
      w.addEventListener("change", () => {
        this._call("switch", w.checked ? "turn_on" : "turn_off", { entity_id: watchEid });
      });
    }
    const fire = (event) => {
      const data = { event };
      if (team) data.team = team;
      this._call("goal_lights", "test", data);
    };
    this.shadowRoot.getElementById("g")?.addEventListener("click", () => fire("goal"));
    this.shadowRoot.getElementById("k")?.addEventListener("click", () => fire("kickoff"));
    this.shadowRoot.getElementById("h")?.addEventListener("click", () => fire("second_half"));
  }
}

customElements.define(CARD, GoalLightsCard);
window.customCards = window.customCards || [];
window.customCards.push({
  type: CARD,
  name: "Goal Lights",
  description: "Score, watch toggle, test goal — flash + YouTube or local goaltune.",
});
