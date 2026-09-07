(function () {
  'use strict';

  var storageKey = 'reaccept_google_measurement_consent';
  var banner = document.querySelector('[data-consent-banner]');

  if (!banner) {
    return;
  }

  function readChoice() {
    try {
      return window.localStorage.getItem(storageKey);
    } catch (error) {
      return null;
    }
  }

  function saveChoice(choice) {
    try {
      window.localStorage.setItem(storageKey, choice);
    } catch (error) {
      // Consent still applies to this page even when storage is unavailable.
    }
  }

  function updateConsent(choice) {
    var granted = choice === 'granted' ? 'granted' : 'denied';
    window.gtag('consent', 'update', {
      'ad_storage': granted,
      'analytics_storage': granted,
      'ad_user_data': granted,
      'ad_personalization': 'denied'
    });
  }

  banner.querySelectorAll('[data-consent-choice]').forEach(function (button) {
    button.addEventListener('click', function () {
      var choice = button.getAttribute('data-consent-choice');
      saveChoice(choice);
      updateConsent(choice);
      banner.hidden = true;
    });
  });

  document.querySelectorAll('[data-consent-settings]').forEach(function (button) {
    button.addEventListener('click', function () {
      banner.hidden = false;
      banner.querySelector('[data-consent-choice="granted"]').focus();
    });
  });

  if (readChoice() === null) {
    banner.hidden = false;
  }
}());
