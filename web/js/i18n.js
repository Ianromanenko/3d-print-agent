const translations = {
  en: {
    next: 'Next →',
    back: '← Back',
    skip: 'Skip',
    done: 'Done',
    retry: 'Try again',
    help: 'Need help?',
    loading: 'Loading…',
    error: 'Something went wrong',
    search_placeholder: 'Describe what you want to print…',
    search_button: 'Search',
    confirm_print: 'Send to printer',
    setup_complete: 'Setup already done',
    redo_setup: 'Redo hardware setup',
  },
};

let lang = localStorage.getItem('lang') || 'en';

export const i18n = {
  t: (key) => translations[lang]?.[key] ?? translations.en[key] ?? key,
  setLang: (l) => { lang = l; localStorage.setItem('lang', l); },
  getLang: () => lang,
};
