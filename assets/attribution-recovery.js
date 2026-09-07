(function () {
  'use strict';

  var sessionKey = 'reaccept_attribution_session';
  var status = document.querySelector('[data-attribution-status]');
  var handoff = new URLSearchParams(window.location.hash.slice(1)).get('h');
  window.history.replaceState(null, '', window.location.pathname);

  function readSession() {
    try {
      return window.localStorage.getItem(sessionKey);
    } catch (error) {
      return null;
    }
  }

  function clearSession() {
    try {
      window.localStorage.removeItem(sessionKey);
    } catch (error) {
      // Nothing else to clean up when storage is unavailable.
    }
  }

  var session = readSession();
  if (!handoff || !session) {
    status.textContent = 'Desktop app installed. You can return to ReAccept.';
    return;
  }

  window.fetch('https://api.re-accept.com/v1/attribution/claims', {
    method: 'POST',
    mode: 'cors',
    credentials: 'omit',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({session_token: session, handoff_token: handoff})
  }).then(function (response) {
    if (!response.ok) {
      throw new Error('claim failed');
    }
    clearSession();
    status.textContent = 'Desktop setup completed.';
  }).catch(function () {
    status.textContent = 'Desktop app installed. You can return to ReAccept.';
  });
}());
