module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',
        'fix',
        'docs',
        'style',
        'refactor',
        'perf',
        'test',
        'chore',
        'ci',
        'revert',
      ],
    ],
    'type-case': [2, 'always', 'lower-case'],
    'subject-case': [2, 'never', ['sentence-case', 'start-case', 'pascal-case']],
    'subject-empty': [2, 'never'],
    'subject-full-stop': [2, 'never', '.'],
    'body-leading-blank': [1, 'always'],
    'footer-leading-blank': [1, 'always'],
    // disabled: Dependabot commit bodies carry changelog URLs that cannot be wrapped
    'body-max-line-length': [0, 'always'],
  },
  // ignore Release Please related messages, customizations, and own bot trailers
  ignores: [
    (commit) => /Release Please|release-please|Co-authored-by: maibot-app/i.test(commit),
  ],
};
