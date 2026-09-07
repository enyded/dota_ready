(function () {
  'use strict';

  var apiUrl = 'https://api.re-accept.com/v1/attribution/sessions';
  var consentKey = 'reaccept_google_measurement_consent';
  var sessionKey = 'reaccept_attribution_session';
  var inFlight = false;

  function readStorage(key) {
    try {
      return window.localStorage.getItem(key);
    } catch (error) {
      return null;
    }
  }

  function writeStorage(key, value) {
    try {
      window.localStorage.setItem(key, value);
    } catch (error) {
      // Attribution remains best-effort when browser storage is unavailable.
    }
  }

  function capture() {
    if (inFlight || readStorage(consentKey) !== 'granted' || readStorage(sessionKey)) {
      return;
    }
    var params = new URLSearchParams(window.location.search);
    var clickNames = ['gclid', 'gbraid', 'wbraid'];
    var clickName = clickNames.find(function (name) { return params.has(name); });
    if (!clickName) {
      return;
    }
    var payload = {
      consent_status: 'granted',
      consent_policy_version: '2026-09-07',
      landing_path: window.location.pathname
    };
    payload[clickName] = params.get(clickName);
    ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'].forEach(
      function (name) {
        if (params.has(name)) {
          payload[name] = params.get(name);
        }
      }
    );
    inFlight = true;
    window.fetch(apiUrl, {
      method: 'POST',
      mode: 'cors',
      credentials: 'omit',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    }).then(function (response) {
      if (!response.ok) {
        return null;
      }
      return response.json();
    }).then(function (body) {
      if (body && typeof body.session_token === 'string') {
        writeStorage(sessionKey, body.session_token);
      }
    }).catch(function () {
      // Never block the landing page when attribution is unavailable.
    }).finally(function () {
      inFlight = false;
    });
  }

  window.reacceptCaptureAttribution = capture;
  capture();
}());
