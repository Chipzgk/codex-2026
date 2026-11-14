// Format: type(scope): subject   — vd: feat(web): add login page
// Thêm scope mới vào SCOPE_TYPE_MAP khi repo có thêm app/package.
const ALL = ['feat', 'fix', 'perf', 'refactor', 'style', 'test', 'docs', 'chore', 'revert'];
const SCOPE_TYPE_MAP = {
  repo: ['build', 'chore', 'ci', 'docs', 'refactor', 'test', 'revert'],
  web: ALL,
  api: ALL,
  ai: ALL,
  mobile: ALL,
  docs: ['docs', 'chore']
};

const allScopes = Object.keys(SCOPE_TYPE_MAP);
const allTypes = Array.from(new Set(Object.values(SCOPE_TYPE_MAP).flat()));

function scopeTypeMapping(parsed, _when = 'always', mapping = SCOPE_TYPE_MAP) {
  const { scope, type } = parsed;
  if (!scope || !type) return [false, 'commit must include both type and scope, format: type(scope): subject'];
  const allowed = mapping[scope];
  if (!allowed) return [false, `scope "${scope}" is not allowed. Use one of: ${Object.keys(mapping).join(', ')}`];
  if (!allowed.includes(type)) return [false, `type "${type}" is not allowed for scope "${scope}". Allowed: ${allowed.join(', ')}`];
  return [true, ''];
}

module.exports = {
  extends: ['@commitlint/config-conventional'],
  plugins: [{ rules: { 'scope-type-mapping': scopeTypeMapping } }],
  rules: {
    'scope-empty': [2, 'never'],
    'scope-enum': [2, 'always', allScopes],
    'type-enum': [2, 'always', allTypes],
    'scope-type-mapping': [2, 'always', SCOPE_TYPE_MAP],
    'subject-case': [0]
  }
};
